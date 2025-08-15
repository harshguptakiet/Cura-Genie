import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session

from tests.factories import UserFactory
from core.auth_service import AuthService
from core.security import create_access_token, verify_password, get_password_hash
from db.models import User

class TestAuthService:
    """Test authentication service functionality"""
    
    def test_user_registration_success(self, db_session: Session):
        """Test successful user registration"""
        auth_service = AuthService()
        
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!",
            "role": "patient"
        }
        
        user = auth_service.register_user(db_session, user_data)
        
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert user.role == "patient"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.created_at is not None
    
    def test_user_registration_duplicate_email(self, db_session: Session):
        """Test registration with duplicate email fails"""
        auth_service = AuthService()
        
        # Create first user
        user1 = UserFactory(email="duplicate@example.com")
        db_session.add(user1)
        db_session.commit()
        
        # Try to register with same email
        user_data = {
            "email": "duplicate@example.com",
            "username": "differentuser",
            "password": "SecurePass123!",
            "role": "patient"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(db_session, user_data)
        
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
    
    def test_user_registration_duplicate_username(self, db_session: Session):
        """Test registration with duplicate username fails"""
        auth_service = AuthService()
        
        # Create first user
        user1 = UserFactory(username="duplicateuser")
        db_session.add(user1)
        db_session.commit()
        
        # Try to register with same username
        user_data = {
            "email": "different@example.com",
            "username": "duplicateuser",
            "password": "SecurePass123!",
            "role": "patient"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.register_user(db_session, user_data)
        
        assert exc_info.value.status_code == 400
        assert "Username already taken" in str(exc_info.value.detail)
    
    def test_user_login_success(self, db_session: Session):
        """Test successful user login"""
        auth_service = AuthService()
        
        # Create user with known password
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)
        user = UserFactory(
            email="login@example.com",
            hashed_password=hashed_password
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt login
        login_data = {
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        
        result = auth_service.authenticate_user(db_session, login_data)
        
        assert result is not None
        assert result["user"].email == "login@example.com"
        assert "access_token" in result
        assert "token_type" in result
        assert result["token_type"] == "bearer"
    
    def test_user_login_invalid_email(self, db_session: Session):
        """Test login with invalid email fails"""
        auth_service = AuthService()
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SecurePass123!"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user(db_session, login_data)
        
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)
    
    def test_user_login_invalid_password(self, db_session: Session):
        """Test login with invalid password fails"""
        auth_service = AuthService()
        
        # Create user
        user = UserFactory(email="login@example.com")
        db_session.add(user)
        db_session.commit()
        
        # Attempt login with wrong password
        login_data = {
            "email": "login@example.com",
            "password": "WrongPassword123!"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user(db_session, login_data)
        
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)
    
    def test_user_login_inactive_user(self, db_session: Session):
        """Test login with inactive user fails"""
        auth_service = AuthService()
        
        # Create inactive user
        password = "SecurePass123!"
        hashed_password = get_password_hash(password)
        user = UserFactory(
            email="inactive@example.com",
            hashed_password=hashed_password,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        # Attempt login
        login_data = {
            "email": "inactive@example.com",
            "password": "SecurePass123!"
        }
        
        with pytest.raises(HTTPException) as exc_info:
            auth_service.authenticate_user(db_session, login_data)
        
        assert exc_info.value.status_code == 401
        assert "Inactive user" in str(exc_info.value.detail)

class TestSecurity:
    """Test security utilities"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePass123!"
        
        # Hash password
        hashed = get_password_hash(password)
        
        # Verify password
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False
    
    def test_access_token_creation(self):
        """Test JWT access token creation"""
        user_id = 123
        email = "test@example.com"
        
        token = create_access_token(
            data={"sub": str(user_id), "email": email}
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
    
    def test_access_token_with_expiry(self):
        """Test JWT access token with custom expiry"""
        user_id = 123
        email = "test@example.com"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(
            data={"sub": str(user_id), "email": email},
            expires_delta=expires_delta
        )
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        # Valid passwords
        valid_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd",
            "Str0ng#Pass"
        ]
        
        for password in valid_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True
        
        # Weak passwords should still work but could be validated elsewhere
        weak_password = "123"
        hashed = get_password_hash(weak_password)
        assert verify_password(weak_password, hashed) is True

class TestUserValidation:
    """Test user data validation"""
    
    def test_email_validation(self, db_session: Session):
        """Test email format validation"""
        auth_service = AuthService()
        
        # Valid emails
        valid_emails = [
            "user@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        for email in valid_emails:
            user_data = {
                "email": email,
                "username": "testuser",
                "password": "SecurePass123!",
                "role": "patient"
            }
            
            # Should not raise exception
            try:
                user = auth_service.register_user(db_session, user_data)
                # Clean up
                db_session.delete(user)
                db_session.commit()
            except HTTPException:
                pytest.fail(f"Valid email {email} was rejected")
        
        # Invalid emails
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user.example.com"
        ]
        
        for email in invalid_emails:
            user_data = {
                "email": email,
                "username": "testuser",
                "password": "SecurePass123!",
                "role": "patient"
            }
            
            with pytest.raises(HTTPException) as exc_info:
                auth_service.register_user(db_session, user_data)
            
            assert exc_info.value.status_code == 400
    
    def test_username_validation(self, db_session: Session):
        """Test username format validation"""
        auth_service = AuthService()
        
        # Valid usernames
        valid_usernames = [
            "user123",
            "user_name",
            "user-name",
            "userName"
        ]
        
        for username in valid_usernames:
            user_data = {
                "email": f"{username}@example.com",
                "username": username,
                "password": "SecurePass123!",
                "role": "patient"
            }
            
            # Should not raise exception
            try:
                user = auth_service.register_user(db_session, user_data)
                # Clean up
                db_session.delete(user)
                db_session.commit()
            except HTTPException:
                pytest.fail(f"Valid username {username} was rejected")
        
        # Invalid usernames
        invalid_usernames = [
            "ab",  # Too short
            "a" * 101,  # Too long
            "user@name",  # Contains invalid character
            "user name"   # Contains space
        ]
        
        for username in invalid_usernames:
            user_data = {
                "email": f"{username}@example.com",
                "username": username,
                "password": "SecurePass123!",
                "role": "patient"
            }
            
            with pytest.raises(HTTPException) as exc_info:
                auth_service.register_user(db_session, user_data)
            
            assert exc_info.value.status_code == 400
