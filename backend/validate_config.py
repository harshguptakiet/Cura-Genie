#!/usr/bin/env python3
"""
CuraGenie Configuration Validation Tool

This tool validates the configuration for different environments and provides
detailed feedback on missing or invalid configuration values.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def setup_logging():
    """Setup basic logging for the validation tool"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def validate_environment_variables(environment: str) -> Dict[str, Any]:
    """Validate environment variables for a specific environment"""
    print(f"🔍 Validating environment variables for {environment} environment...")
    
    # Define required variables for each environment
    required_vars = {
        "development": [
            "DATABASE_URL"
        ],
        "staging": [
            "DATABASE_URL", "REDIS_URL", "CORS_ORIGINS",
            "SECRET_KEY", "JWT_SECRET_KEY"
        ],
        "production": [
            "DATABASE_URL", "REDIS_URL", "CORS_ORIGINS",
            "SECRET_KEY", "JWT_SECRET_KEY"
        ]
    }
    
    # Define optional but recommended variables
    recommended_vars = [
        "OPENAI_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME", "AWS_REGION"
    ]
    
    results = {
        "environment": environment,
        "required_missing": [],
        "recommended_missing": [],
        "validation_passed": True,
        "warnings": []
    }
    
    # Check required variables
    for var in required_vars.get(environment, []):
        if not os.getenv(var):
            results["required_missing"].append(var)
            results["validation_passed"] = False
    
    # Check recommended variables
    for var in recommended_vars:
        if not os.getenv(var):
            results["recommended_missing"].append(var)
    
    # Environment-specific validations
    if environment == "production":
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if "*" in cors_origins:
            results["warnings"].append("Wildcard CORS origin (*) detected in production - security risk!")
        
        if not any(origin.startswith("https://") for origin in cors_origins.split(",")):
            results["warnings"].append("No HTTPS CORS origins detected in production")
    
    return results

def validate_secrets_strength(environment: str) -> Dict[str, Any]:
    """Validate the strength of secrets"""
    print(f"🔐 Validating secrets strength for {environment} environment...")
    
    results = {
        "weak_secrets": [],
        "validation_passed": True
    }
    
    # Check secret key strength
    secret_key = os.getenv("SECRET_KEY", "")
    if secret_key and len(secret_key) < 32:
        results["weak_secrets"].append("SECRET_KEY is too short (minimum 32 characters)")
        results["validation_passed"] = False
    
    # Check JWT secret strength
    jwt_secret = os.getenv("JWT_SECRET_KEY", "")
    if jwt_secret and len(jwt_secret) < 32:
        results["weak_secrets"].append("JWT_SECRET_KEY is too short (minimum 32 characters)")
        results["validation_passed"] = False
    
    # Check for default/example secrets
    default_secrets = [
        "your-super-secret-key-here",
        "dev-secret-key-change-in-production",
        "your-staging-secret-key-here",
        "your-production-secret-key-here"
    ]
    
    for secret in default_secrets:
        if secret in [secret_key, jwt_secret]:
            results["weak_secrets"].append(f"Default/example secret detected: {secret}")
            results["validation_passed"] = False
    
    return results

def validate_database_configuration() -> Dict[str, Any]:
    """Validate database configuration"""
    print("🗄️ Validating database configuration...")
    
    results = {
        "validation_passed": True,
        "warnings": [],
        "errors": []
    }
    
    database_url = os.getenv("DATABASE_URL", "")
    
    if not database_url:
        results["errors"].append("DATABASE_URL not set")
        results["validation_passed"] = False
    else:
        # Check database type
        if database_url.startswith("sqlite://"):
            if os.getenv("ENVIRONMENT") == "production":
                results["warnings"].append("SQLite database detected in production - consider PostgreSQL for scalability")
        elif database_url.startswith("postgresql://"):
            print("✅ PostgreSQL database detected")
        else:
            results["warnings"].append(f"Unknown database type: {database_url.split('://')[0]}")
    
    return results

def validate_cors_configuration() -> Dict[str, Any]:
    """Validate CORS configuration"""
    print("🌐 Validating CORS configuration...")
    
    results = {
        "validation_passed": True,
        "warnings": [],
        "errors": []
    }
    
    cors_origins = os.getenv("CORS_ORIGINS", "")
    environment = os.getenv("ENVIRONMENT", "development")
    
    if not cors_origins:
        results["errors"].append("CORS_ORIGINS not set")
        results["validation_passed"] = False
    else:
        origins = [origin.strip() for origin in cors_origins.split(",")]
        
        # Check for wildcard in production
        if environment == "production" and "*" in origins:
            results["errors"].append("Wildcard CORS origin (*) not allowed in production")
            results["validation_passed"] = False
        
        # Check for HTTP in production
        if environment == "production":
            http_origins = [origin for origin in origins if origin.startswith("http://")]
            if http_origins:
                results["warnings"].append(f"HTTP origins detected in production: {http_origins}")
        
        # Check for localhost in production
        if environment == "production":
            localhost_origins = [origin for origin in origins if "localhost" in origin or "127.0.0.1" in origin]
            if localhost_origins:
                results["warnings"].append(f"Localhost origins detected in production: {localhost_origins}")
    
    return results

def print_validation_results(env_results: Dict, secrets_results: Dict, db_results: Dict, cors_results: Dict):
    """Print comprehensive validation results"""
    print("\n" + "="*60)
    print("📊 Configuration Validation Results")
    print("="*60)
    
    # Environment validation
    print(f"\n🔍 Environment: {env_results['environment']}")
    if env_results['required_missing']:
        print(f"❌ Required variables missing: {', '.join(env_results['required_missing'])}")
    else:
        print("✅ All required environment variables are set")
    
    if env_results['recommended_missing']:
        print(f"⚠️  Recommended variables missing: {', '.join(env_results['recommended_missing'])}")
    
    if env_results['warnings']:
        for warning in env_results['warnings']:
            print(f"⚠️  Warning: {warning}")
    
    # Secrets validation
    print(f"\n🔐 Secrets Validation:")
    if secrets_results['weak_secrets']:
        for secret in secrets_results['weak_secrets']:
            print(f"❌ {secret}")
    else:
        print("✅ All secrets meet strength requirements")
    
    # Database validation
    print(f"\n🗄️ Database Validation:")
    if db_results['errors']:
        for error in db_results['errors']:
            print(f"❌ {error}")
    else:
        print("✅ Database configuration is valid")
    
    if db_results['warnings']:
        for warning in db_results['warnings']:
            print(f"⚠️  Warning: {warning}")
    
    # CORS validation
    print(f"\n🌐 CORS Validation:")
    if cors_results['errors']:
        for error in cors_results['errors']:
            print(f"❌ {error}")
    else:
        print("✅ CORS configuration is valid")
    
    if cors_results['warnings']:
        for warning in cors_results['warnings']:
            print(f"⚠️  Warning: {warning}")
    
    # Overall result
    overall_passed = (
        env_results['validation_passed'] and
        secrets_results['validation_passed'] and
        db_results['validation_passed'] and
        cors_results['validation_passed']
    )
    
    print("\n" + "="*60)
    if overall_passed:
        print("🎉 Configuration validation PASSED!")
        print("✅ Your configuration is ready for deployment")
    else:
        print("❌ Configuration validation FAILED!")
        print("⚠️  Please fix the issues above before deployment")
    
    return overall_passed

def generate_secret_key() -> str:
    """Generate a strong secret key"""
    return secrets.token_urlsafe(32)

def print_setup_instructions(environment: str):
    """Print setup instructions for the specified environment"""
    print(f"\n📋 Setup Instructions for {environment} environment:")
    print("="*50)
    
    if environment == "development":
        print("1. Copy env.development.template to .env.development")
        print("2. Modify values as needed")
        print("3. Run: python validate_config.py --env development")
    
    elif environment == "staging":
        print("1. Copy env.staging.template to .env.staging")
        print("2. Fill in ALL required values:")
        print("   - DATABASE_URL")
        print("   - REDIS_URL")
        print("   - CORS_ORIGINS")
        print("   - SECRET_KEY")
        print("   - JWT_SECRET_KEY")
        print("3. Run: python validate_config.py --env staging")
    
    elif environment == "production":
        print("1. Copy env.production.template to .env.production")
        print("2. Fill in ALL required values:")
        print("   - DATABASE_URL")
        print("   - REDIS_URL")
        print("   - CORS_ORIGINS (HTTPS only)")
        print("   - SECRET_KEY (generate strong key)")
        print("   - JWT_SECRET_KEY (generate strong key)")
        print("3. Generate strong secrets:")
        print(f"   SECRET_KEY={generate_secret_key()}")
        print(f"   JWT_SECRET_KEY={generate_secret_key()}")
        print("4. Run: python validate_config.py --env production")

def main():
    """Main validation function"""
    setup_logging()
    
    # Parse command line arguments
    environment = "development"
    if len(sys.argv) > 1:
        if sys.argv[1] == "--env" and len(sys.argv) > 2:
            environment = sys.argv[2]
        elif sys.argv[1] == "--help":
            print("Usage: python validate_config.py [--env ENVIRONMENT]")
            print("Environments: development, staging, production")
            print("Example: python validate_config.py --env production")
            return
    
    # Validate environment
    if environment not in ["development", "staging", "production"]:
        print(f"❌ Invalid environment: {environment}")
        print("Valid environments: development, staging, production")
        return
    
    print(f"🚀 Starting configuration validation for {environment} environment...")
    
    # Set environment variable for validation
    os.environ["ENVIRONMENT"] = environment
    
    try:
        # Run validations
        env_results = validate_environment_variables(environment)
        secrets_results = validate_secrets_strength(environment)
        db_results = validate_database_configuration()
        cors_results = validate_cors_configuration()
        
        # Print results
        overall_passed = print_validation_results(
            env_results, secrets_results, db_results, cors_results
        )
        
        # Print setup instructions if validation failed
        if not overall_passed:
            print_setup_instructions(environment)
        
        # Exit with appropriate code
        sys.exit(0 if overall_passed else 1)
        
    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
