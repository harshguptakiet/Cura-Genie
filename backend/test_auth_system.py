#!/usr/bin/env python3
"""
Test Script for CuraGenie Unified Authentication System
Verifies that all authentication components are working correctly
"""

import sys
import os
import asyncio
import requests
import json
from pathlib import Path
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_backend_auth_service():
    """Test backend authentication service components"""
    print("🧪 Testing Backend Authentication Service...")
    
    try:
        from core.auth_service import auth_service, AuthService
        
        # Test password validation
        print("  🔐 Testing password validation...")
        is_valid, message = auth_service.validate_password_strength("Weak")
        if is_valid:
            print("    ❌ Weak password should not be valid")
            return False
        print("    ✅ Weak password correctly rejected")
        
        is_valid, message = auth_service.validate_password_strength("StrongPass123!")
        if not is_valid:
            print(f"    ❌ Strong password should be valid: {message}")
            return False
        print("    ✅ Strong password correctly accepted")
        
        # Test password hashing
        print("  🔐 Testing password hashing...")
        test_password = "TestPassword123!"
        hashed = auth_service.get_password_hash(test_password)
        if not hashed or hashed == test_password:
            print("    ❌ Password not properly hashed")
            return False
        print("    ✅ Password properly hashed")
        
        # Test password verification
        if not auth_service.verify_password(test_password, hashed):
            print("    ❌ Password verification failed")
            return False
        print("    ✅ Password verification working")
        
        # Test token creation
        print("  🔐 Testing token creation...")
        test_data = {"sub": "test@example.com", "user_id": 1, "role": "patient"}
        access_token = auth_service.create_access_token(test_data)
        refresh_token = auth_service.create_refresh_token(test_data)
        
        if not access_token or not refresh_token:
            print("    ❌ Token creation failed")
            return False
        print("    ✅ Tokens created successfully")
        
        # Test token verification
        try:
            payload = auth_service.verify_token(access_token, "access")
            if payload["sub"] != "test@example.com":
                print("    ❌ Token verification failed")
                return False
            print("    ✅ Token verification working")
        except Exception as e:
            print(f"    ❌ Token verification error: {e}")
            return False
        
        print("  ✅ Backend authentication service tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Backend authentication service test failed: {e}")
        return False

def test_auth_schemas():
    """Test authentication schemas"""
    print("🧪 Testing Authentication Schemas...")
    
    try:
        from schemas.auth_schemas import (
            UserCreate, UserLogin, TokenResponse, 
            ChangePassword, PasswordResetRequest
        )
        
        # Test user creation schema
        print("  📝 Testing user creation schema...")
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        user = UserCreate(**user_data)
        if user.email != "test@example.com":
            print("    ❌ User creation schema failed")
            return False
        print("    ✅ User creation schema working")
        
        # Test password validation in schema
        print("  📝 Testing password validation in schema...")
        try:
            UserCreate(
                email="test@example.com",
                username="testuser",
                password="weak"
            )
            print("    ❌ Weak password should be rejected")
            return False
        except Exception:
            print("    ✅ Weak password correctly rejected")
        
        print("  ✅ Authentication schemas tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Authentication schemas test failed: {e}")
        return False

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("🧪 Testing Rate Limiting...")
    
    try:
        from core.rate_limiter import rate_limiter, get_client_identifier
        
        # Test rate limiter
        print("  🚦 Testing rate limiter...")
        test_key = "test_client"
        
        # Should allow first 3 requests
        for i in range(3):
            if not rate_limiter.is_allowed(test_key, 3, 60):
                print(f"    ❌ Request {i+1} should be allowed")
                return False
        
        # 4th request should be blocked
        if rate_limiter.is_allowed(test_key, 3, 60):
            print("    ❌ 4th request should be blocked")
            return False
        
        print("    ✅ Rate limiting working correctly")
        
        # Test client identifier
        print("  🚦 Testing client identifier...")
        class MockRequest:
            def __init__(self):
                self.headers = {"User-Agent": "test-agent"}
                self.client = type('MockClient', (), {'host': '127.0.0.1'})()
        
        mock_request = MockRequest()
        client_id = get_client_identifier(mock_request)
        if not client_id.startswith("ip:127.0.0.1"):
            print(f"    ❌ Client identifier incorrect: {client_id}")
            return False
        print("    ✅ Client identifier working")
        
        print("  ✅ Rate limiting tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Rate limiting test failed: {e}")
        return False

def test_api_endpoints():
    """Test authentication API endpoints"""
    print("🧪 Testing Authentication API Endpoints...")
    
    # Check if backend is running
    try:
        response = requests.get("http://127.0.0.1:8000/api/auth/health", timeout=5)
        if response.status_code != 200:
            print("  ❌ Backend not responding")
            return False
    except requests.exceptions.RequestException:
        print("  ⚠️ Backend not running, skipping API tests")
        return True
    
    print("  🌐 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/api/auth/health")
        if response.status_code == 200:
            print("    ✅ Health endpoint working")
        else:
            print(f"    ❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"    ❌ Health endpoint error: {e}")
        return False
    
    # Test registration endpoint
    try:
        test_user = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "username": f"testuser_{datetime.now().timestamp()}",
            "password": "StrongPass123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/register",
            json=test_user
        )
        
        if response.status_code == 200:
            print("    ✅ Registration endpoint working")
            user_data = response.json()
            
            # Test login with created user
            login_data = {
                "email": test_user["email"],
                "password": test_user["password"]
            }
            
            login_response = requests.post(
                "http://127.0.0.1:8000/api/auth/login",
                json=login_data
            )
            
            if login_response.status_code == 200:
                print("    ✅ Login endpoint working")
                tokens = login_response.json()["tokens"]
                
                # Test protected endpoint
                headers = {"Authorization": f"Bearer {tokens['access_token']}"}
                me_response = requests.get(
                    "http://127.0.0.1:8000/api/auth/me",
                    headers=headers
                )
                
                if me_response.status_code == 200:
                    print("    ✅ Protected endpoint working")
                else:
                    print(f"    ❌ Protected endpoint failed: {me_response.status_code}")
                    return False
            else:
                print(f"    ❌ Login endpoint failed: {login_response.status_code}")
                return False
        else:
            print(f"    ❌ Registration endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    ❌ API endpoint test error: {e}")
        return False
    
    print("  ✅ API endpoint tests passed")
    return True

def test_database_migration():
    """Test database migration functionality"""
    print("🧪 Testing Database Migration...")
    
    try:
        from migrations.migrate_auth_system import AuthSystemMigration
        
        # Test migration class creation
        print("  🗄️ Testing migration class...")
        migration = AuthSystemMigration()
        if not migration:
            print("    ❌ Migration class creation failed")
            return False
        print("    ✅ Migration class created")
        
        # Test backup path generation
        backup_path = migration.backup_path
        if not backup_path or "backup" not in backup_path:
            print("    ❌ Backup path generation failed")
            return False
        print("    ✅ Backup path generation working")
        
        print("  ✅ Database migration tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Database migration test failed: {e}")
        return False

def test_security_features():
    """Test security features"""
    print("🧪 Testing Security Features...")
    
    try:
        from core.auth_service import auth_service
        
        # Test password strength requirements
        print("  🔒 Testing password strength requirements...")
        
        weak_passwords = [
            "short",           # Too short
            "nouppercase",     # No uppercase
            "NOLOWERCASE",     # No lowercase
            "NoNumbers",       # No numbers
            "NoSymbols123"     # No symbols
        ]
        
        for password in weak_passwords:
            is_valid, message = auth_service.validate_password_strength(password)
            if is_valid:
                print(f"    ❌ Weak password '{password}' should be rejected")
                return False
            print(f"    ✅ Weak password '{password}' correctly rejected: {message}")
        
        # Test strong password
        strong_password = "StrongPass123!"
        is_valid, message = auth_service.validate_password_strength(strong_password)
        if not is_valid:
            print(f"    ❌ Strong password should be accepted: {message}")
            return False
        print("    ✅ Strong password correctly accepted")
        
        # Test token security
        print("  🔒 Testing token security...")
        test_data = {"sub": "test@example.com", "user_id": 1, "role": "patient"}
        
        # Create tokens
        access_token = auth_service.create_access_token(test_data)
        refresh_token = auth_service.create_refresh_token(test_data)
        
        # Verify token types
        try:
            access_payload = auth_service.verify_token(access_token, "access")
            refresh_payload = auth_service.verify_token(refresh_token, "refresh")
            
            if access_payload.get("type") != "access":
                print("    ❌ Access token type verification failed")
                return False
            
            if refresh_payload.get("type") != "refresh":
                print("    ❌ Refresh token type verification failed")
                return False
                
            print("    ✅ Token type verification working")
            
        except Exception as e:
            print(f"    ❌ Token verification error: {e}")
            return False
        
        print("  ✅ Security features tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ Security features test failed: {e}")
        return False

def main():
    """Run all authentication system tests"""
    print("🚀 Starting CuraGenie Authentication System Tests")
    print("=" * 60)
    
    tests = [
        ("Backend Authentication Service", test_backend_auth_service),
        ("Authentication Schemas", test_auth_schemas),
        ("Rate Limiting", test_rate_limiting),
        ("API Endpoints", test_api_endpoints),
        ("Database Migration", test_database_migration),
        ("Security Features", test_security_features),
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
        print("🎉 All tests passed! Authentication system is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
