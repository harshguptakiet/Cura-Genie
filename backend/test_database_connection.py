#!/usr/bin/env python3
"""
Test script for Neon PostgreSQL database connection

This script tests the database connection configuration and helps verify
that your Neon PostgreSQL database is properly configured.

Usage:
    python test_database_connection.py
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment_setup():
    """Test if environment variables are properly set"""
    print("🔍 Testing environment setup...")
    
    # Check if DATABASE_URL is set
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL found: {database_url[:30]}...")
        
        # Check if it's a valid PostgreSQL URL
        if database_url.startswith('postgresql://'):
            print("✅ Valid PostgreSQL URL format")
        else:
            print("⚠️  DATABASE_URL should start with 'postgresql://'")
            return False
    else:
        print("❌ DATABASE_URL environment variable not set")
        print("   Please set it with your Neon PostgreSQL URL")
        return False
    
    return True

def test_database_imports():
    """Test if database modules can be imported"""
    print("\n🔍 Testing database module imports...")
    
    try:
        from core.config import settings
        print("✅ Core config imported successfully")
        
        from db.database import get_database_url, test_database_connection
        print("✅ Database modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_connection():
    """Test the actual database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from db.database import get_database_url, test_database_connection
        
        database_url = get_database_url()
        print(f"📊 Database URL: {database_url[:50]}...")
        
        if test_database_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
        return False

def test_database_schema():
    """Test if database tables can be created"""
    print("\n🔍 Testing database schema creation...")
    
    try:
        from db.database import create_tables
        
        create_tables()
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions"""
    print("\n" + "="*60)
    print("🚀 Neon PostgreSQL Setup Instructions")
    print("="*60)
    print("1. Set your Neon database URL as an environment variable:")
    print("   export DATABASE_URL='your_neon_postgresql_url_here'")
    print()
    print("2. Or create a .env file in the backend directory with:")
    print("   DATABASE_URL=your_neon_postgresql_url_here")
    print()
    print("3. Your Neon URL should look like:")
    print("   postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database")
    print()
    print("4. Make sure you have the required dependencies:")
    print("   pip install psycopg2-binary sqlalchemy")
    print()
    print("5. Restart your application after setting the environment variable")
    print("="*60)

def main():
    """Run all database tests"""
    print("🚀 Starting CuraGenie Database Connection Tests")
    print("=" * 60)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Module Imports", test_database_imports),
        ("Database Connection", test_database_connection),
        ("Schema Creation", test_database_schema),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your Neon PostgreSQL database is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the setup instructions below.")
        print_setup_instructions()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
