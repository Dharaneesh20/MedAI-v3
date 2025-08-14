from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medai.settings')
django.setup()

from authentication.models import User, UserProfile
from authentication.serializers import UserRegistrationSerializer, UserLoginSerializer
from authentication.authentication import generate_jwt_token, JWTAuthentication

router = APIRouter()
security = HTTPBearer()


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    password: str
    password_confirm: str
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None
    phone_number: Optional[str] = None


class TokenResponse(BaseModel):
    message: str
    token: str
    user: UserResponse


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    
    try:
        auth = JWTAuthentication()
        # Create a mock request object with the authorization header
        class MockRequest:
            def __init__(self, token):
                self.META = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
        request = MockRequest(token)
        result = auth.authenticate(request)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user, _ = result
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )


@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegistration):
    """Register a new user"""
    try:
        # Convert Pydantic model to dict
        data = user_data.dict()
        
        # Create Django serializer
        serializer = UserRegistrationSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            token = generate_jwt_token(user)
            
            return TokenResponse(
                message="User registered successfully",
                token=token,
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    date_of_birth=str(user.date_of_birth) if user.date_of_birth else None,
                    phone_number=user.phone_number
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=serializer.errors
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin):
    """Login user"""
    try:
        # Convert Pydantic model to dict
        data = user_credentials.dict()
        
        # Create Django serializer
        serializer = UserLoginSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = generate_jwt_token(user)
            
            return TokenResponse(
                message="Login successful",
                token=token,
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    date_of_birth=str(user.date_of_birth) if user.date_of_birth else None,
                    phone_number=user.phone_number
                )
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=serializer.errors
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        date_of_birth=str(current_user.date_of_birth) if current_user.date_of_birth else None,
        phone_number=current_user.phone_number
    )


@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user"""
    return {"message": "Logout successful"}
