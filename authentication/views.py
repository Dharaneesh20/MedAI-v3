from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import render
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    UserProfileUpdateSerializer
)
from .authentication import generate_jwt_token


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    if request.method == 'GET':
        # Render registration form
        return render(request, 'auth/register.html')
    
    # Handle POST request
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = generate_jwt_token(user)
        
        # Also log the user in for Django session-based authentication
        from django.contrib.auth import login
        login(request, user)
        
        return Response({
            'message': 'User registered successfully',
            'token': token,
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    if request.method == 'GET':
        # Render login form
        return render(request, 'auth/login.html')
    
    # Handle POST request
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token = generate_jwt_token(user)
        
        # Also log the user in for Django session-based authentication
        from django.contrib.auth import login
        login(request, user)
        
        return Response({
            'message': 'Login successful',
            'token': token,
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """Get user profile"""
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile"""
    serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserProfileSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def logout(request):
    """User logout endpoint"""
    if request.method == 'GET':
        # Handle logout for web interface
        from django.contrib.auth import logout
        logout(request)
        return render(request, 'auth/logout.html')
    
    # Handle logout for API
    from django.contrib.auth import logout
    logout(request)
    return Response({
        'message': 'Logout successful'
    }, status=status.HTTP_200_OK)
