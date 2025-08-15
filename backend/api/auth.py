"""
Unified Authentication API Endpoints
Replaces inconsistent authentication systems with secure, standardized endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from core.auth_service import auth_service, get_current_user, require_role
from core.errors import AuthenticationError, ValidationError, DatabaseError
from db.database import get_db
from db.auth_models import User, UserRole
from schemas.auth_schemas import (
    UserCreate, UserLogin, TokenResponse, TokenRefresh, AuthResponse,
    ChangePassword, PasswordResetRequest, PasswordResetConfirm,
    PasswordChangeResponse, PasswordResetResponse, User as UserSchema
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Rate limiting for authentication endpoints
from core.rate_limiter import rate_limit

@router.post("/register", response_model=AuthResponse)
@rate_limit(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Register a new user with secure password hashing
    """
    try:
        # Create user with hashed password
        user = await auth_service.create_user(db, user_data)
        
        # Create authentication tokens
        tokens = auth_service.create_tokens(user)
        
        # Create patient profile if first_name and last_name provided
        if user_data.first_name and user_data.last_name:
            from db.auth_models import PatientProfile
            profile = PatientProfile(
                user_id=user.id,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                phone=user_data.phone
            )
            db.add(profile)
            db.commit()
        
        logger.info(f"User registered successfully: {user.email}")
        
        return AuthResponse(
            user=UserSchema.from_orm(user),
            tokens=tokens,
            message="User registered successfully"
        )
        
    except ValidationError as e:
        logger.warning(f"Registration validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

@router.post("/login", response_model=AuthResponse)
@rate_limit(max_requests=10, window_seconds=300)  # 10 requests per 5 minutes
async def login_user(
    user_credentials: UserLogin,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Authenticate user and return JWT tokens
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            db, 
            user_credentials.email, 
            user_credentials.password
        )
        
        if not user:
            logger.warning(f"Failed login attempt for email: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create authentication tokens
        tokens = auth_service.create_tokens(user)
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return AuthResponse(
            user=UserSchema.from_orm(user),
            tokens=tokens,
            message="Login successful"
        )
        
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    token_data: TokenRefresh,
    request: Request = None
):
    """
    Refresh access token using refresh token
    """
    try:
        new_access_token = await auth_service.refresh_access_token(token_data.refresh_token)
        
        # Decode the new token to get user info
        payload = auth_service.verify_token(new_access_token, "access")
        
        # Create new token response
        tokens = TokenResponse(
            access_token=new_access_token,
            refresh_token=token_data.refresh_token,  # Keep existing refresh token
            token_type="bearer",
            expires_in=15 * 60,  # 15 minutes
            user_id=payload["user_id"],
            role=payload["role"],
            email=payload["email"]
        )
        
        logger.info(f"Access token refreshed for user: {payload['email']}")
        return tokens
        
    except AuthenticationError as e:
        logger.warning(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed. Please try again."
        )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Logout user (invalidate tokens)
    Note: In a production system, you would blacklist the tokens
    """
    try:
        # TODO: Implement token blacklisting
        logger.info(f"User logged out: {current_user.email}")
        
        return {
            "message": "Logout successful",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Change user password
    """
    try:
        success = await auth_service.change_password(
            db,
            current_user.id,
            password_data.current_password,
            password_data.new_password
        )
        
        if success:
            logger.info(f"Password changed successfully for user: {current_user.email}")
            return PasswordChangeResponse(
                message="Password changed successfully",
                timestamp=datetime.utcnow()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
        
    except ValidationError as e:
        logger.warning(f"Password change validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except AuthenticationError as e:
        logger.warning(f"Password change authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during password change: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )

@router.post("/forgot-password", response_model=PasswordResetResponse)
@rate_limit(max_requests=3, window_seconds=3600)  # 3 requests per hour
async def forgot_password(
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Request password reset
    """
    try:
        reset_token = await auth_service.request_password_reset(db, password_reset.email)
        
        # TODO: Send email with reset token
        logger.info(f"Password reset requested for email: {password_reset.email}")
        
        return PasswordResetResponse(
            message="If an account with that email exists, a password reset link has been sent.",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error during password reset request: {e}")
        # Don't reveal if email exists or not
        return PasswordResetResponse(
            message="If an account with that email exists, a password reset link has been sent.",
            timestamp=datetime.utcnow()
        )

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Reset password using reset token
    """
    try:
        success = await auth_service.reset_password_with_token(
            db,
            reset_data.email,
            reset_data.reset_token,
            reset_data.new_password
        )
        
        if success:
            logger.info(f"Password reset successfully for email: {reset_data.email}")
            return {
                "message": "Password reset successfully",
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password"
            )
        
    except ValidationError as e:
        logger.warning(f"Password reset validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during password reset: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Get current user information
    """
    try:
        return UserSchema.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Error getting current user info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )

@router.post("/verify-email")
async def verify_email(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Verify user email address
    """
    try:
        # TODO: Implement email verification logic
        current_user.is_verified = True
        db.commit()
        
        logger.info(f"Email verified for user: {current_user.email}")
        
        return {
            "message": "Email verified successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Error during email verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

# Admin-only endpoints
@router.get("/users", response_model=list[UserSchema])
async def get_all_users(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Get all users (admin only)
    """
    try:
        users = db.query(User).all()
        return [UserSchema.from_orm(user) for user in users]
        
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Activate/deactivate user (admin only)
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = not user.is_active
        db.commit()
        
        status_text = "activated" if user.is_active else "deactivated"
        logger.info(f"User {user.email} {status_text} by admin {current_user.email}")
        
        return {
            "message": f"User {status_text} successfully",
            "user_id": user_id,
            "is_active": user.is_active,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating/deactivating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )

# Health check endpoint
@router.get("/health")
async def auth_health_check():
    """
    Authentication service health check
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow()
    }
