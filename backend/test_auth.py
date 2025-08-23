#!/usr/bin/env python3
"""
Simple test script to verify authentication endpoints work
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health Check: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        return response.ok
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "patient"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        print(f"Registration: {response.status_code}")
        if response.ok:
            print(f"Registration successful: {response.json()}")
        else:
            print(f"Registration failed: {response.text}")
        return response.ok
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login: {response.status_code}")
        if response.ok:
            data = response.json()
            print(f"Login successful: {data}")
            return data.get("access_token")
        else:
            print(f"Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_me(token):
    """Test getting current user info"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"User info: {response.status_code}")
        if response.ok:
            print(f"User info: {response.json()}")
        else:
            print(f"User info failed: {response.text}")
        return response.ok
    except Exception as e:
        print(f"User info error: {e}")
        return False

if __name__ == "__main__":
    print("Testing CuraGenie Authentication...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Backend is not running!")
        exit(1)
    
    print()
    
    # Test registration
    test_register()
    print()
    
    # Test login
    token = test_login()
    print()
    
    # Test user info
    if token:
        test_me(token)
    
    print("=" * 50)
    print("Test completed!")
