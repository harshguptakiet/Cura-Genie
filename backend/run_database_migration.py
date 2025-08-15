#!/usr/bin/env python3
"""
Database Migration CLI Tool for CuraGenie

This script provides a command-line interface for:
- Running database migrations
- Analyzing current schema
- Creating backups
- Rolling back migrations
- Checking migration status

Usage:
    python run_database_migration.py [command] [options]

Commands:
    analyze     - Analyze current database schema
    migrate     - Run full migration process
    backup      - Create database backup only
    rollback    - Rollback last migration
    status      - Show migration status
    dedupe      - Run data deduplication
    test        - Test database connection
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from core.logging_config import setup_logging
from services.database_migration_service import migration_service
from services.data_deduplication import deduplication_service
from db.database_manager import db_manager

def setup_logging_cli():
    """Setup logging for CLI"""
    setup_logging()
    return logging.getLogger(__name__)

def analyze_schema():
    """Analyze current database schema"""
    logger = setup_logging_cli()
    logger.info("🔍 Analyzing current database schema...")
    
    try:
        analysis = migration_service.analyze_current_schema()
        
        print("\n" + "="*60)
        print("DATABASE SCHEMA ANALYSIS")
        print("="*60)
        
        print(f"📊 Database Type: {analysis['database_type']}")
        print(f"🕒 Analysis Time: {analysis['timestamp']}")
        
        print(f"\n📋 Existing Tables ({len(analysis['existing_tables'])}):")
        for table in analysis['existing_tables']:
            count = analysis['data_counts'].get(table, 'N/A')
            print(f"   • {table}: {count} records")
        
        if analysis['missing_tables']:
            print(f"\n❌ Missing Tables ({len(analysis['missing_tables'])}):")
            for table in analysis['missing_tables']:
                print(f"   • {table}")
        
        if analysis['schema_issues']:
            print(f"\n⚠️  Schema Issues ({len(analysis['schema_issues'])}):")
            for issue in analysis['schema_issues']:
                print(f"   • {issue}")
        
        if not analysis['missing_tables'] and not analysis['schema_issues']:
            print("\n✅ Database schema is up to date!")
        
        return analysis
        
    except Exception as e:
        logger.error(f"❌ Schema analysis failed: {e}")
        print(f"❌ Error: {e}")
        return None

def run_migration(create_backup=True, force=False):
    """Run the full migration process"""
    logger = setup_logging_cli()
    
    if not force:
        print("⚠️  WARNING: This will modify your database schema!")
        print("   Make sure you have a backup of your data.")
        response = input("\nDo you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Migration cancelled.")
            return None
    
    logger.info("🚀 Starting database migration...")
    print("🚀 Starting database migration...")
    
    try:
        results = migration_service.run_full_migration(create_backup=create_backup)
        
        print("\n" + "="*60)
        print("MIGRATION RESULTS")
        print("="*60)
        
        print(f"🕒 Migration Time: {results['timestamp']}")
        print(f"💾 Backup Created: {'✅ Yes' if results['backup_created'] else '❌ No'}")
        if results['backup_created']:
            print(f"   Backup Path: {results['backup_path']}")
        
        print(f"🔑 Passwords Migrated: {results['password_migration']}")
        
        if results['data_migration']:
            print(f"📊 Tables Migrated: {len(results['data_migration']['tables_migrated'])}")
            for table in results['data_migration']['tables_migrated']:
                print(f"   • {table}")
        
        if results['warnings']:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"   • {warning}")
        
        if results['errors']:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"   • {error}")
        
        if results['success']:
            print("\n🎉 Migration completed successfully!")
        else:
            print("\n⚠️  Migration completed with issues. Check the errors above.")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return None

def create_backup():
    """Create database backup only"""
    logger = setup_logging_cli()
    logger.info("💾 Creating database backup...")
    print("💾 Creating database backup...")
    
    try:
        backup_path = migration_service.create_backup()
        if backup_path:
            print(f"✅ Backup created successfully: {backup_path}")
            return backup_path
        else:
            print("❌ Backup creation failed")
            return None
    except Exception as e:
        logger.error(f"❌ Backup creation failed: {e}")
        print(f"❌ Error: {e}")
        return None

def rollback_migration():
    """Rollback the last migration"""
    logger = setup_logging_cli()
    
    print("⚠️  WARNING: This will restore your database from backup!")
    print("   All changes since the backup will be lost.")
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Rollback cancelled.")
        return False
    
    logger.info("🔄 Rolling back migration...")
    print("🔄 Rolling back migration...")
    
    try:
        success = migration_service.rollback_migration()
        if success:
            print("✅ Rollback completed successfully!")
        else:
            print("❌ Rollback failed")
        return success
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        print(f"❌ Error: {e}")
        return False

def show_status():
    """Show migration status"""
    logger = setup_logging_cli()
    logger.info("📊 Getting migration status...")
    
    try:
        status = migration_service.get_migration_status()
        
        print("\n" + "="*60)
        print("MIGRATION STATUS")
        print("="*60)
        
        print(f"🕒 Status Time: {status['timestamp']}")
        print(f"💾 Backup Available: {'✅ Yes' if status['backup_available'] else '❌ No'}")
        if status['backup_available']:
            print(f"   Backup Path: {status['backup_path']}")
        
        if 'current_schema' in status:
            schema = status['current_schema']
            print(f"📊 Database Type: {schema.get('database_type', 'Unknown')}")
            print(f"📋 Tables: {len(schema.get('existing_tables', []))}")
            print(f"❌ Missing: {len(schema.get('missing_tables', []))}")
            print(f"⚠️  Issues: {len(schema.get('schema_issues', []))}")
        
        if 'error' in status:
            print(f"❌ Error: {status['error']}")
        
        return status
        
    except Exception as e:
        logger.error(f"❌ Failed to get status: {e}")
        print(f"❌ Error: {e}")
        return None

def run_deduplication():
    """Run data deduplication"""
    logger = setup_logging_cli()
    logger.info("🧹 Running data deduplication...")
    print("🧹 Running data deduplication...")
    
    try:
        # First, get a report on potential duplicates
        report = deduplication_service.get_duplication_report()
        
        print("\n" + "="*60)
        print("DUPLICATION ANALYSIS")
        print("="*60)
        
        for entity, data in report['potential_duplicates'].items():
            total = data['total']
            duplicates = data['duplicates']
            print(f"📊 {entity.replace('_', ' ').title()}:")
            print(f"   Total Records: {total}")
            print(f"   Potential Duplicates: {duplicates}")
            if duplicates > 0:
                print(f"   Duplication Rate: {(duplicates/total*100):.1f}%")
        
        if any(data['duplicates'] > 0 for data in report['potential_duplicates'].values()):
            print(f"\n🧹 Found potential duplicates. Running deduplication...")
            
            results = deduplication_service.run_full_deduplication()
            
            print("\n" + "="*60)
            print("DEDUPLICATION RESULTS")
            print("="*60)
            
            print(f"🕒 Completed: {results['timestamp']}")
            print(f"🎯 Total Deduplicated: {results['total_deduplicated']}")
            
            for entity, data in results.items():
                if entity not in ['total_deduplicated', 'timestamp']:
                    deduped = data.get('deduplicated', 0)
                    kept = data.get('kept', 0)
                    print(f"📊 {entity.replace('_', ' ').title()}:")
                    print(f"   Deduplicated: {deduped}")
                    print(f"   Kept: {kept}")
        else:
            print("\n✅ No duplicates found!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Deduplication failed: {e}")
        print(f"❌ Error: {e}")
        return False

def test_connection():
    """Test database connection"""
    logger = setup_logging_cli()
    logger.info("🔍 Testing database connection...")
    print("🔍 Testing database connection...")
    
    try:
        success = db_manager.test_connection()
        if success:
            print("✅ Database connection successful!")
            
            # Get connection info
            info = db_manager.get_connection_info()
            print(f"📊 Database Type: {info['database_type']}")
            print(f"🔗 Connection URL: {info['database_url']}")
            
            if info['database_type'] == 'postgresql':
                print(f"🏊 Pool Size: {info['pool_size']}")
                print(f"🌊 Pool Overflow: {info['pool_overflow']}")
                print(f"📥 Checked In: {info['pool_checked_in']}")
                print(f"📤 Checked Out: {info['pool_checked_out']}")
            
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        print(f"❌ Error: {e}")
        return False

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Database Migration CLI Tool for CuraGenie",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_database_migration.py analyze
  python run_database_migration.py migrate --force
  python run_database_migration.py backup
  python run_database_migration.py rollback
  python run_database_migration.py status
  python run_database_migration.py dedupe
  python run_database_migration.py test
        """
    )
    
    parser.add_argument(
        'command',
        choices=['analyze', 'migrate', 'backup', 'rollback', 'status', 'dedupe', 'test'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts (use with caution)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation during migration'
    )
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'analyze':
        analyze_schema()
    elif args.command == 'migrate':
        run_migration(create_backup=not args.no_backup, force=args.force)
    elif args.command == 'backup':
        create_backup()
    elif args.command == 'rollback':
        rollback_migration()
    elif args.command == 'status':
        show_status()
    elif args.command == 'dedupe':
        run_deduplication()
    elif args.command == 'test':
        test_connection()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
