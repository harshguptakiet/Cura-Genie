"""
Database Configuration for CuraGenie

This file contains the database configuration setup for using Neon PostgreSQL.
To use your Neon database:

1. Set the DATABASE_URL environment variable with your Neon PostgreSQL URL
2. Or create a .env file in the backend directory with:
   DATABASE_URL=your_neon_postgresql_url_here

Example Neon PostgreSQL URL format:
DATABASE_URL=postgresql://username:password@host:port/database

For Neon, it typically looks like:
DATABASE_URL=postgresql://username:password@ep-xxx-xxx-xxx.region.aws.neon.tech/database
"""

import os
from typing import Optional

def get_neon_database_url() -> Optional[str]:
    """
    Get the Neon PostgreSQL database URL from environment variables.
    
    Returns:
        str: The database URL if found, None otherwise
    """
    return os.getenv('DATABASE_URL')

def get_database_config() -> dict:
    """
    Get database configuration for Neon PostgreSQL.
    
    Returns:
        dict: Database configuration dictionary
    """
    database_url = get_neon_database_url()
    
    if not database_url:
        print("⚠️  Warning: DATABASE_URL environment variable not set")
        print("   Please set DATABASE_URL with your Neon PostgreSQL URL")
        print("   Example: export DATABASE_URL='postgresql://user:pass@host:port/db'")
        return {}
    
    if not database_url.startswith('postgresql://'):
        print("⚠️  Warning: DATABASE_URL should start with 'postgresql://'")
        return {}
    
    print(f"✅ Found Neon PostgreSQL URL: {database_url[:20]}...")
    
    return {
        'database_url': database_url,
        'database_type': 'postgresql',
        'provider': 'neon'
    }

def print_setup_instructions():
    """Print setup instructions for Neon PostgreSQL"""
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
    print("4. Restart your application after setting the environment variable")
    print("="*60)

if __name__ == "__main__":
    config = get_database_config()
    if not config:
        print_setup_instructions()
    else:
        print(f"✅ Database configuration ready: {config['database_type']}")
