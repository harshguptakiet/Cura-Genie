from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from core.auth import (
    authenticate_user, create_access_token, get_password_hash,
    get_user_by_email, get_user_by_username, get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from db.database import get_db
from db.auth_models import User, PatientProfile
from schemas.auth_schemas import (
    UserCreate, UserLogin, Token, User as UserSchema, SocialAuth,
    ForgotPassword, ResetPassword
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=UserSchema)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if email already exists
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create patient profile if role is patient
    if user_data.role == "patient":
        patient_profile = PatientProfile(
            user_id=db_user.id,
            first_name=user_data.first_name or "",
            last_name=user_data.last_name or "",
            phone=user_data.phone
        )
        db.add(patient_profile)
        db.commit()
    
    return db_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role.value
    )

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.put("/change-password")
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not authenticate_user(db, current_user.email, current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/logout")
def logout():
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}

@router.delete("/delete-account")
def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account"""
    
    # Verify password before deletion
    if not authenticate_user(db, current_user.email, password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect"
        )
    
    # Deactivate user instead of deleting
    current_user.is_active = False
    db.commit()
    
    return {"message": "Account deactivated successfully"}

@router.post("/social-auth", response_model=Token)
def social_auth(auth_data: SocialAuth, db: Session = Depends(get_db)):
    """Social authentication (Google, Facebook, etc.)"""
    
    # Check if user exists
    user = get_user_by_email(db, auth_data.email)
    
    if not user:
        # Create new user from social auth
        username = auth_data.email.split('@')[0]  # Use email prefix as username
        counter = 1
        original_username = username
        
        # Ensure username is unique
        while get_user_by_username(db, username):
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User(
            email=auth_data.email,
            username=username,
            hashed_password="",  # No password for social auth
            role="patient",
            is_verified=True  # Social accounts are pre-verified
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create patient profile
        names = auth_data.name.split(' ', 1)
        first_name = names[0] if names else ""
        last_name = names[1] if len(names) > 1 else ""
        
        patient_profile = PatientProfile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            avatar_url=auth_data.avatar_url
        )
        db.add(patient_profile)
        db.commit()
    
    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=user.role.value
    )

@router.post("/forgot-password")
def forgot_password(request: ForgotPassword, db: Session = Depends(get_db)):
    """Send password reset email"""
    
    user = get_user_by_email(db, request.email)
    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent."}
    
    # In a real implementation, you would:
    # 1. Generate a secure reset token
    # 2. Store it with expiration in database
    # 3. Send email with reset link
    
    # For now, just return success message
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: ResetPassword, db: Session = Depends(get_db)):
    """Reset password using token"""
    
    # In a real implementation, you would:
    # 1. Verify the reset token
    # 2. Check if it's not expired
    # 3. Get user associated with the token
    # 4. Update their password
    
    # For now, just return error as tokens aren't implemented
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password reset functionality not fully implemented yet"
    )

@router.post("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    
    # In a real implementation, you would:
    # 1. Verify the email verification token
    # 2. Mark user as verified
    
    return {"message": "Email verification functionality not implemented yet"}

@router.post("/resend-verification")
def resend_verification(
    email: str,
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already verified"
        )
    
    # In a real implementation, send verification email
    return {"message": "Verification email sent"}
