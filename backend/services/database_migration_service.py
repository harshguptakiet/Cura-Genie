"""
Database Migration Service for CuraGenie

This service handles:
- Migration from old database systems to new unified schema
- Data validation and integrity checks
- Rollback capabilities
- Progress tracking and reporting
"""

import logging
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db.database_manager import get_db_context, db_manager
from core.config import config_manager

logger = logging.getLogger(__name__)

class DatabaseMigrationService:
    """Service for managing database migrations and schema updates"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.migration_log = []
        self.backup_path = None
    
    def create_backup(self) -> str:
        """
        Create a backup of the current database before migration
        
        Returns:
            Path to the backup file
        """
        try:
            database_url = config_manager.get_database_url()
            
            if database_url.startswith('sqlite:///'):
                # SQLite backup
                db_path = database_url.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"{db_path}.backup_{timestamp}"
                    shutil.copy2(db_path, backup_path)
                    self.backup_path = backup_path
                    self.logger.info(f"✅ SQLite backup created: {backup_path}")
                    return backup_path
                else:
                    self.logger.warning("⚠️ SQLite database file not found, skipping backup")
                    return ""
            else:
                # PostgreSQL backup (using pg_dump)
                self.logger.info("🔄 Creating PostgreSQL backup...")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"postgresql_backup_{timestamp}.sql"
                
                # Extract connection details from URL
                # postgresql://user:pass@host:port/dbname
                url_parts = database_url.replace('postgresql://', '').split('@')
                if len(url_parts) == 2:
                    auth_part = url_parts[0]
                    host_part = url_parts[1]
                    
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                    else:
                        username = auth_part
                        password = ""
                    
                    if ':' in host_part:
                        host_port, dbname = host_part.split('/', 1)
                        if ':' in host_port:
                            host, port = host_port.split(':', 1)
                        else:
                            host = host_port
                            port = "5432"
                    else:
                        host = host_part
                        port = "5432"
                        dbname = "postgres"
                    
                    # Create pg_dump command
                    env_vars = os.environ.copy()
                    if password:
                        env_vars['PGPASSWORD'] = password
                    
                    import subprocess
                    cmd = [
                        'pg_dump',
                        '-h', host,
                        '-p', port,
                        '-U', username,
                        '-d', dbname,
                        '-f', backup_path,
                        '--verbose'
                    ]
                    
                    result = subprocess.run(cmd, env=env_vars, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.backup_path = backup_path
                        self.logger.info(f"✅ PostgreSQL backup created: {backup_path}")
                        return backup_path
                    else:
                        self.logger.error(f"❌ PostgreSQL backup failed: {result.stderr}")
                        return ""
                else:
                    self.logger.error("❌ Invalid PostgreSQL URL format")
                    return ""
                    
        except Exception as e:
            self.logger.error(f"❌ Backup creation failed: {e}")
            return ""
    
    def analyze_current_schema(self) -> Dict[str, Any]:
        """
        Analyze the current database schema to understand what needs to be migrated
        
        Returns:
            Dict with schema analysis results
        """
        try:
            with get_db_context() as session:
                inspector = inspect(db_manager.engine)
                
                analysis = {
                    "timestamp": datetime.now().isoformat(),
                    "database_type": "postgresql" if config_manager.get_database_url().startswith('postgresql://') else "sqlite",
                    "existing_tables": [],
                    "missing_tables": [],
                    "schema_issues": [],
                    "data_counts": {}
                }
                
                # Get existing tables
                existing_tables = inspector.get_table_names()
                analysis["existing_tables"] = existing_tables
                
                # Check for required tables
                required_tables = [
                    'users', 'patient_profiles', 'genomic_data', 'genomic_variants',
                    'prs_scores', 'timeline_events', 'medical_reports', 'user_sessions',
                    'password_reset_tokens'
                ]
                
                for table in required_tables:
                    if table not in existing_tables:
                        analysis["missing_tables"].append(table)
                
                # Check for old tables that need migration
                old_tables = []
                for table in existing_tables:
                    if table not in required_tables:
                        old_tables.append(table)
                
                if old_tables:
                    analysis["schema_issues"].append(f"Found {len(old_tables)} old tables that may need migration: {old_tables}")
                
                # Count data in existing tables
                for table in existing_tables:
                    try:
                        count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                        analysis["data_counts"][table] = count
                    except Exception as e:
                        analysis["data_counts"][table] = f"Error: {e}"
                
                # Check for schema inconsistencies
                if 'users' in existing_tables:
                    try:
                        columns = inspector.get_columns('users')
                        column_names = [col['name'] for col in columns]
                        
                        if 'password' in column_names and 'hashed_password' not in column_names:
                            analysis["schema_issues"].append("Users table has plain text 'password' field instead of 'hashed_password'")
                        
                        if 'role' not in column_names:
                            analysis["schema_issues"].append("Users table missing 'role' field")
                            
                    except Exception as e:
                        analysis["schema_issues"].append(f"Error analyzing users table: {e}")
                
                return analysis
                
        except Exception as e:
            self.logger.error(f"❌ Schema analysis failed: {e}")
            raise
    
    def migrate_plain_text_passwords(self) -> int:
        """
        Migrate plain text passwords to hashed passwords
        
        Returns:
            Number of passwords migrated
        """
        try:
            from core.auth_service import AuthService
            auth_service = AuthService()
            
            with get_db_context() as session:
                # Check if users table has plain text password field
                inspector = inspect(db_manager.engine)
                columns = inspector.get_columns('users')
                column_names = [col['name'] for col in columns]
                
                if 'password' not in column_names:
                    self.logger.info("✅ No plain text password field found")
                    return 0
                
                # Get users with plain text passwords
                users_query = text("SELECT id, password FROM users WHERE hashed_password IS NULL OR hashed_password = ''")
                users = session.execute(users_query).fetchall()
                
                if not users:
                    self.logger.info("✅ No plain text passwords found")
                    return 0
                
                migrated_count = 0
                for user_id, plain_password in users:
                    try:
                        # Hash the password
                        hashed_password = auth_service.get_password_hash(plain_password)
                        
                        # Update the user
                        update_query = text("UPDATE users SET hashed_password = :hash WHERE id = :id")
                        session.execute(update_query, {"hash": hashed_password, "id": user_id})
                        
                        migrated_count += 1
                        self.logger.info(f"✅ Migrated password for user {user_id}")
                        
                    except Exception as e:
                        self.logger.error(f"❌ Failed to migrate password for user {user_id}: {e}")
                        continue
                
                session.commit()
                self.logger.info(f"🎉 Successfully migrated {migrated_count} passwords")
                return migrated_count
                
        except Exception as e:
            self.logger.error(f"❌ Password migration failed: {e}")
            raise
    
    def migrate_existing_data(self) -> Dict[str, Any]:
        """
        Migrate existing data to the new schema structure
        
        Returns:
            Dict with migration results
        """
        try:
            migration_results = {
                "timestamp": datetime.now().isoformat(),
                "tables_migrated": [],
                "records_migrated": 0,
                "errors": [],
                "warnings": []
            }
            
            with get_db_context() as session:
                inspector = inspect(db_manager.engine)
                existing_tables = inspector.get_table_names()
                
                # Migrate users table if it exists
                if 'users' in existing_tables:
                    try:
                        # Check if we need to add missing columns
                        columns = inspector.get_columns('users')
                        column_names = [col['name'] for col in columns]
                        
                        if 'role' not in column_names:
                            session.execute(text("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'patient'"))
                            migration_results["warnings"].append("Added 'role' column to users table")
                        
                        if 'is_active' not in column_names:
                            session.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                            migration_results["warnings"].append("Added 'is_active' column to users table")
                        
                        if 'is_verified' not in column_names:
                            session.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
                            migration_results["warnings"].append("Added 'is_verified' column to users table")
                        
                        if 'created_at' not in column_names:
                            session.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"))
                            migration_results["warnings"].append("Added 'created_at' column to users table")
                        
                        if 'updated_at' not in column_names:
                            session.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP"))
                            migration_results["warnings"].append("Added 'updated_at' column to users table")
                        
                        migration_results["tables_migrated"].append("users")
                        
                    except Exception as e:
                        error_msg = f"Failed to migrate users table: {e}"
                        migration_results["errors"].append(error_msg)
                        self.logger.error(f"❌ {error_msg}")
                
                # Migrate other tables as needed
                # Add more migration logic here for other tables
                
                session.commit()
                
                self.logger.info(f"✅ Data migration completed. Tables migrated: {migration_results['tables_migrated']}")
                return migration_results
                
        except Exception as e:
            self.logger.error(f"❌ Data migration failed: {e}")
            raise
    
    def run_full_migration(self, create_backup: bool = True) -> Dict[str, Any]:
        """
        Run the complete migration process
        
        Args:
            create_backup: Whether to create a backup before migration
            
        Returns:
            Dict with migration results
        """
        try:
            self.logger.info("🚀 Starting full database migration...")
            
            migration_results = {
                "timestamp": datetime.now().isoformat(),
                "backup_created": False,
                "schema_analysis": {},
                "password_migration": 0,
                "data_migration": {},
                "final_validation": {},
                "success": False,
                "errors": [],
                "warnings": []
            }
            
            # Step 1: Create backup
            if create_backup:
                backup_path = self.create_backup()
                if backup_path:
                    migration_results["backup_created"] = True
                    migration_results["backup_path"] = backup_path
                else:
                    migration_results["warnings"].append("Failed to create backup, proceeding anyway")
            
            # Step 2: Analyze current schema
            try:
                migration_results["schema_analysis"] = self.analyze_current_schema()
                self.logger.info("✅ Schema analysis completed")
            except Exception as e:
                error_msg = f"Schema analysis failed: {e}"
                migration_results["errors"].append(error_msg)
                self.logger.error(f"❌ {error_msg}")
                return migration_results
            
            # Step 3: Migrate passwords
            try:
                migration_results["password_migration"] = self.migrate_plain_text_passwords()
                self.logger.info("✅ Password migration completed")
            except Exception as e:
                error_msg = f"Password migration failed: {e}"
                migration_results["errors"].append(error_msg)
                self.logger.error(f"❌ {error_msg}")
            
            # Step 4: Migrate existing data
            try:
                migration_results["data_migration"] = self.migrate_existing_data()
                self.logger.info("✅ Data migration completed")
            except Exception as e:
                error_msg = f"Data migration failed: {e}"
                migration_results["errors"].append(error_msg)
                self.logger.error(f"❌ {error_msg}")
            
            # Step 5: Final validation
            try:
                final_analysis = self.analyze_current_schema()
                migration_results["final_validation"] = final_analysis
                
                if not final_analysis["missing_tables"]:
                    migration_results["success"] = True
                    self.logger.info("🎉 Migration completed successfully!")
                else:
                    migration_results["warnings"].append(f"Some tables still missing: {final_analysis['missing_tables']}")
                    
            except Exception as e:
                error_msg = f"Final validation failed: {e}"
                migration_results["errors"].append(error_msg)
                self.logger.error(f"❌ {error_msg}")
            
            return migration_results
            
        except Exception as e:
            error_msg = f"Full migration failed: {e}"
            migration_results["errors"].append(error_msg)
            self.logger.error(f"❌ {error_msg}")
            return migration_results
    
    def rollback_migration(self) -> bool:
        """
        Rollback the migration using the backup
        
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if not self.backup_path:
                self.logger.error("❌ No backup available for rollback")
                return False
            
            database_url = config_manager.get_database_url()
            
            if database_url.startswith('sqlite:///'):
                # SQLite rollback
                db_path = database_url.replace('sqlite:///', '')
                if os.path.exists(self.backup_path):
                    shutil.copy2(self.backup_path, db_path)
                    self.logger.info(f"✅ Rollback completed using backup: {self.backup_path}")
                    return True
                else:
                    self.logger.error(f"❌ Backup file not found: {self.backup_path}")
                    return False
            else:
                # PostgreSQL rollback
                self.logger.info("🔄 Rolling back PostgreSQL database...")
                
                # Extract connection details from URL
                url_parts = database_url.replace('postgresql://', '').split('@')
                if len(url_parts) == 2:
                    auth_part = url_parts[0]
                    host_part = url_parts[1]
                    
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                    else:
                        username = auth_part
                        password = ""
                    
                    if ':' in host_part:
                        host_port, dbname = host_part.split('/', 1)
                        if ':' in host_port:
                            host, port = host_port.split(':', 1)
                        else:
                            host = host_part
                            port = "5432"
                    else:
                        host = host_part
                        port = "5432"
                        dbname = "postgres"
                    
                    # Create psql restore command
                    env_vars = os.environ.copy()
                    if password:
                        env_vars['PGPASSWORD'] = password
                    
                    import subprocess
                    cmd = [
                        'psql',
                        '-h', host,
                        '-p', port,
                        '-U', username,
                        '-d', dbname,
                        '-f', self.backup_path
                    ]
                    
                    result = subprocess.run(cmd, env=env_vars, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.logger.info(f"✅ PostgreSQL rollback completed using backup: {self.backup_path}")
                        return True
                    else:
                        self.logger.error(f"❌ PostgreSQL rollback failed: {result.stderr}")
                        return False
                else:
                    self.logger.error("❌ Invalid PostgreSQL URL format for rollback")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get the current status of the migration
        
        Returns:
            Dict with migration status information
        """
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "backup_available": bool(self.backup_path),
                "backup_path": self.backup_path,
                "migration_log": self.migration_log,
                "current_schema": self.analyze_current_schema()
            }
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get migration status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

# Global service instance
migration_service = DatabaseMigrationService()
