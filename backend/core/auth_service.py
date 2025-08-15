"""
Unified Authentication Service for CuraGenie Platform
Replaces inconsistent authentication systems with secure, standardized approach
"""

import jwt
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from core.config import settings
from core.errors import AuthenticationError, ValidationError, DatabaseError
from db.database import get_db
from db.auth_models import User, UserRole
from schemas.auth_schemas import TokenData, TokenResponse, UserCreate, PasswordResetRequest

logger = logging.getLogger(__name__)

# Security configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived for security
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Long-lived with rotation

# Password requirements
MIN_PASSWORD_LENGTH = 8
PASSWORD_REQUIREMENTS = {
    "min_length": MIN_PASSWORD_LENGTH,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_numbers": True,
    "require_symbols": True
}

class AuthService:
    """Unified authentication service"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return self.pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password with bcrypt"""
        return self.pwd_context.hash(password)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < PASSWORD_REQUIREMENTS["min_length"]:
            return False, f"Password must be at least {PASSWORD_REQUIREMENTS['min_length']} characters long"
        
        if PASSWORD_REQUIREMENTS["require_uppercase"] and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if PASSWORD_REQUIREMENTS["require_lowercase"] and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if PASSWORD_REQUIREMENTS["require_numbers"] and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if PASSWORD_REQUIREMENTS["require_symbols"] and not any(c in string.punctuation for c in password):
            return False, "Password must contain at least one symbol"
        
        return True, "Password meets requirements"
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise AuthenticationError("Failed to create access token")
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise AuthenticationError("Failed to create refresh token")
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise AuthenticationError(f"Invalid token type. Expected: {token_type}")
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise AuthenticationError("Token has expired")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.JWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise AuthenticationError("Invalid token")
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise AuthenticationError("Token verification failed")
    
    async def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        try:
            user = self.get_user_by_email(db, email)
            if not user:
                return None
            
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {email}")
                return None
            
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Failed login attempt for user: {email}")
                return None
            
            logger.info(f"Successful authentication for user: {email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error for user {email}: {e}")
            raise AuthenticationError("Authentication failed")
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email: {e}")
            raise DatabaseError("Failed to retrieve user")
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by ID: {e}")
            raise DatabaseError("Failed to retrieve user")
    
    async def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create new user with hashed password"""
        try:
            # Validate password strength
            is_valid, message = self.validate_password_strength(user_data.password)
            if not is_valid:
                raise ValidationError(f"Password validation failed: {message}")
            
            # Check if user already exists
            existing_user = self.get_user_by_email(db, user_data.email)
            if existing_user:
                raise ValidationError("User with this email already exists")
            
            # Hash password
            hashed_password = self.get_password_hash(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                role=user_data.role or UserRole.PATIENT,
                is_active=True,
                is_verified=False
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created successfully: {user_data.email}")
            return user
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user: {e}")
            raise DatabaseError("Failed to create user")
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    async def change_password(self, db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValidationError("User not found")
            
            # Verify current password
            if not self.verify_password(current_password, user.hashed_password):
                raise AuthenticationError("Current password is incorrect")
            
            # Validate new password strength
            is_valid, message = self.validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(f"New password validation failed: {message}")
            
            # Hash new password
            user.hashed_password = self.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Password changed successfully for user: {user.email}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error changing password: {e}")
            raise DatabaseError("Failed to change password")
        except Exception as e:
            db.rollback()
            logger.error(f"Error changing password: {e}")
            raise
    
    def create_tokens(self, user: User) -> TokenResponse:
        """Create access and refresh tokens for user"""
        try:
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "role": user.role.value,
                "email": user.email
            }
            
            access_token = self.create_access_token(token_data)
            refresh_token = self.create_refresh_token({
                "sub": user.email,
                "user_id": user.id
            })
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Error creating tokens for user {user.email}: {e}")
            raise AuthenticationError("Failed to create authentication tokens")
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token, "refresh")
            
            # Get user from database
            db = next(get_db())
            user = self.get_user_by_email(db, payload["sub"])
            
            if not user or not user.is_active:
                raise AuthenticationError("Invalid refresh token")
            
            # Create new access token
            token_data = {
                "sub": user.email,
                "user_id": user.id,
                "role": user.role.value,
                "email": user.email
            }
            
            new_access_token = self.create_access_token(token_data)
            logger.info(f"Access token refreshed for user: {user.email}")
            
            return new_access_token
            
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}")
            raise AuthenticationError("Failed to refresh access token")
    
    def generate_password_reset_token(self) -> str:
        """Generate secure password reset token"""
        return secrets.token_urlsafe(32)
    
    async def request_password_reset(self, db: Session, email: str) -> str:
        """Request password reset and return reset token"""
        try:
            user = self.get_user_by_email(db, email)
            if not user:
                # Don't reveal if user exists
                logger.info(f"Password reset requested for email: {email}")
                return "reset_token_placeholder"
            
            # Generate reset token
            reset_token = self.generate_password_reset_token()
            
            # Store reset token in user record (you might want to add a reset_token field)
            # For now, we'll just log it
            logger.info(f"Password reset token generated for user: {email}")
            
            # TODO: Store reset token in database and send email
            return reset_token
            
        except Exception as e:
            logger.error(f"Error requesting password reset: {e}")
            raise AuthenticationError("Failed to process password reset request")
    
    async def reset_password_with_token(self, db: Session, email: str, reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            user = self.get_user_by_email(db, email)
            if not user:
                raise ValidationError("User not found")
            
            # TODO: Verify reset token from database
            
            # Validate new password strength
            is_valid, message = self.validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(f"New password validation failed: {message}")
            
            # Hash new password
            user.hashed_password = self.get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Password reset successfully for user: {email}")
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error resetting password: {e}")
            raise DatabaseError("Failed to reset password")
        except Exception as e:
            db.rollback()
            logger.error(f"Error resetting password: {e}")
            raise

# Global auth service instance
auth_service = AuthService()

# Dependency functions for FastAPI
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token, "access")
        
        user = auth_service.get_user_by_email(db, payload["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_active_patient(current_user: User = Depends(get_current_user)) -> User:
    """Get current active patient user"""
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Patient access required."
        )
    return current_user

def get_current_active_doctor(current_user: User = Depends(get_current_user)) -> User:
    """Get current active doctor user"""
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Doctor access required."
        )
    return current_user

def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """Get current active admin user"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

def require_role(required_role: UserRole):
    """Dependency to require specific user role"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. {required_role.value.title()} access required."
            )
        return current_user
    return role_checker
