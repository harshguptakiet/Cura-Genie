#!/usr/bin/env python3
"""
Database Migration Script for CuraGenie Authentication System
Migrates existing plain text passwords to secure hashed passwords
Updates database schema for new authentication system
"""

import sys
import os
import sqlite3
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.auth_service import auth_service
from core.config import settings
from db.database import engine, SessionLocal
from db.auth_models import Base, User, UserRole
from sqlalchemy import text, inspect

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AuthSystemMigration:
    """Handles migration of authentication system"""
    
    def __init__(self):
        self.db_path = settings.database_url.replace('sqlite:///', '')
        self.backup_path = f"{self.db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.migration_log = []
    
    def backup_database(self) -> bool:
        """Create backup of existing database"""
        try:
            if os.path.exists(self.db_path):
                import shutil
                shutil.copy2(self.db_path, self.backup_path)
                logger.info(f"✅ Database backed up to: {self.backup_path}")
                self.migration_log.append(f"Database backed up to: {self.backup_path}")
                return True
            else:
                logger.warning("⚠️ Database file not found, skipping backup")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to backup database: {e}")
            return False
    
    def check_database_schema(self) -> dict:
        """Check current database schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {}
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table});")
                columns = cursor.fetchall()
                schema_info[table] = {
                    'columns': [col[1] for col in columns],
                    'types': [col[2] for col in columns]
                }
            
            conn.close()
            
            logger.info("✅ Database schema analyzed")
            return schema_info
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze database schema: {e}")
            return {}
    
    def create_new_tables(self) -> bool:
        """Create new tables using SQLAlchemy models"""
        try:
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("✅ New tables created successfully")
            self.migration_log.append("New tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create new tables: {e}")
            return False
    
    def migrate_existing_users(self) -> Tuple[int, int]:
        """Migrate existing users from old schema to new schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if old users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
            if not cursor.fetchone():
                logger.info("ℹ️ No existing users table found")
                conn.close()
                return 0, 0
            
            # Get existing users
            cursor.execute("SELECT * FROM users;")
            old_users = cursor.fetchall()
            
            if not old_users:
                logger.info("ℹ️ No existing users found")
                conn.close()
                return 0, 0
            
            # Get column names
            cursor.execute("PRAGMA table_info(users);")
            columns = [col[1] for col in cursor.fetchall()]
            
            logger.info(f"📊 Found {len(old_users)} existing users to migrate")
            
            # Create new database session
            db = SessionLocal()
            migrated_count = 0
            skipped_count = 0
            
            for user_data in old_users:
                try:
                    # Map old data to new structure
                    user_dict = dict(zip(columns, user_data))
                    
                    # Check if user already exists in new system
                    existing_user = db.query(User).filter(User.email == user_dict.get('email')).first()
                    if existing_user:
                        logger.info(f"ℹ️ User {user_dict.get('email')} already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Create new user with hashed password
                    if 'password' in user_dict and user_dict['password']:
                        # Check if password is already hashed (bcrypt hashes start with $2b$)
                        if user_dict['password'].startswith('$2b$'):
                            hashed_password = user_dict['password']
                            logger.info(f"ℹ️ Password for {user_dict.get('email')} already hashed")
                        else:
                            # Hash plain text password
                            hashed_password = auth_service.get_password_hash(user_dict['password'])
                            logger.info(f"🔐 Migrated plain text password for {user_dict.get('email')}")
                    else:
                        # Generate random password for users without password
                        import secrets
                        import string
                        random_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                        hashed_password = auth_service.get_password_hash(random_password)
                        logger.warning(f"⚠️ Generated random password for {user_dict.get('email')}")
                    
                    # Create new user
                    new_user = User(
                        email=user_dict.get('email', f"user_{migrated_count}@migrated.com"),
                        username=user_dict.get('username', f"user_{migrated_count}"),
                        hashed_password=hashed_password,
                        role=UserRole.PATIENT,  # Default role
                        is_active=user_dict.get('is_active', True),
                        is_verified=user_dict.get('is_verified', False)
                    )
                    
                    db.add(new_user)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"❌ Failed to migrate user {user_dict.get('email', 'unknown')}: {e}")
                    skipped_count += 1
            
            # Commit changes
            db.commit()
            db.close()
            conn.close()
            
            logger.info(f"✅ Successfully migrated {migrated_count} users")
            logger.info(f"⚠️ Skipped {skipped_count} users")
            
            self.migration_log.append(f"Migrated {migrated_count} users")
            self.migration_log.append(f"Skipped {skipped_count} users")
            
            return migrated_count, skipped_count
            
        except Exception as e:
            logger.error(f"❌ Failed to migrate users: {e}")
            return 0, 0
    
    def update_database_indexes(self) -> bool:
        """Create database indexes for better performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create indexes for authentication queries
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
                "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);",
                "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);",
                "CREATE INDEX IF NOT EXISTS idx_patient_profiles_user_id ON patient_profiles(user_id);",
                "CREATE INDEX IF NOT EXISTS idx_medical_reports_user_id ON medical_reports(user_id);"
            ]
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    logger.info(f"✅ Created index: {index_sql}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create index: {e}")
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Database indexes updated")
            self.migration_log.append("Database indexes updated")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update database indexes: {e}")
            return False
    
    def verify_migration(self) -> bool:
        """Verify that migration was successful"""
        try:
            db = SessionLocal()
            
            # Check if new tables exist
            inspector = inspect(engine)
            required_tables = ['users', 'patient_profiles', 'medical_reports']
            
            for table in required_tables:
                if not inspector.has_table(table):
                    logger.error(f"❌ Required table '{table}' not found")
                    return False
            
            # Check if users can be queried
            user_count = db.query(User).count()
            logger.info(f"✅ Found {user_count} users in new system")
            
            # Check if password hashing works
            test_user = db.query(User).first()
            if test_user:
                # Try to verify a dummy password (should fail)
                if auth_service.verify_password("dummy_password", test_user.hashed_password):
                    logger.warning("⚠️ Password verification may not be working correctly")
                else:
                    logger.info("✅ Password verification working correctly")
            
            db.close()
            
            logger.info("✅ Migration verification completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
    
    def rollback_migration(self) -> bool:
        """Rollback migration by restoring backup"""
        try:
            if os.path.exists(self.backup_path):
                import shutil
                shutil.copy2(self.backup_path, self.db_path)
                logger.info(f"✅ Migration rolled back, restored from: {self.backup_path}")
                return True
            else:
                logger.error("❌ No backup found for rollback")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to rollback migration: {e}")
            return False
    
    def run_migration(self) -> bool:
        """Run complete migration process"""
        logger.info("🚀 Starting CuraGenie Authentication System Migration")
        logger.info("=" * 60)
        
        try:
            # Step 1: Backup database
            if not self.backup_database():
                logger.error("❌ Migration failed: Could not backup database")
                return False
            
            # Step 2: Check current schema
            schema_info = self.check_database_schema()
            if not schema_info:
                logger.warning("⚠️ Could not analyze current schema, proceeding anyway")
            
            # Step 3: Create new tables
            if not self.create_new_tables():
                logger.error("❌ Migration failed: Could not create new tables")
                return False
            
            # Step 4: Migrate existing users
            migrated, skipped = self.migrate_existing_users()
            if migrated == 0 and skipped == 0:
                logger.info("ℹ️ No users to migrate")
            
            # Step 5: Update database indexes
            if not self.update_database_indexes():
                logger.warning("⚠️ Failed to update database indexes")
            
            # Step 6: Verify migration
            if not self.verify_migration():
                logger.error("❌ Migration verification failed")
                logger.info("🔄 Rolling back migration...")
                self.rollback_migration()
                return False
            
            logger.info("=" * 60)
            logger.info("🎉 Migration completed successfully!")
            logger.info(f"📊 Migration Summary:")
            logger.info(f"   - Users migrated: {migrated}")
            logger.info(f"   - Users skipped: {skipped}")
            logger.info(f"   - Backup created: {self.backup_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed with error: {e}")
            logger.info("🔄 Rolling back migration...")
            self.rollback_migration()
            return False
    
    def generate_migration_report(self) -> str:
        """Generate detailed migration report"""
        report = f"""
# CuraGenie Authentication System Migration Report

**Migration Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Status:** {'✅ SUCCESS' if self.migration_log else '❌ FAILED'}

## Migration Steps Completed:
"""
        
        for step in self.migration_log:
            report += f"- {step}\n"
        
        report += f"""
## Database Backup:
- **Backup Location:** {self.backup_path}
- **Backup Size:** {os.path.getsize(self.backup_path) if os.path.exists(self.backup_path) else 'N/A'} bytes

## Next Steps:
1. Test the new authentication system
2. Update application configuration
3. Remove old authentication code
4. Monitor system performance

## Rollback Instructions:
If you need to rollback this migration, run:
```python
migration = AuthSystemMigration()
migration.rollback_migration()
```

---
*Generated by CuraGenie Migration System*
"""
        
        return report

def main():
    """Main migration function"""
    try:
        migration = AuthSystemMigration()
        
        # Run migration
        success = migration.run_migration()
        
        # Generate report
        report = migration.generate_migration_report()
        
        # Save report
        report_path = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Migration report saved to: {report_path}")
        
        if success:
            logger.info("🎉 Migration completed successfully!")
            logger.info(f"📄 See {report_path} for detailed report")
            return 0
        else:
            logger.error("❌ Migration failed!")
            logger.info(f"📄 See {report_path} for detailed report")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Migration script failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
