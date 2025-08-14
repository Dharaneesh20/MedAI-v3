from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm',
                 'date_of_birth', 'phone_number', 'emergency_contact', 'emergency_phone',
                 'age', 'weight', 'height', 'allergies', 'medical_conditions')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password confirmation doesn't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'date_of_birth',
                 'phone_number', 'emergency_contact', 'emergency_phone', 'age', 'weight', 
                 'height', 'allergies', 'medical_conditions', 'current_medications', 
                 'medical_notes', 'profile_picture', 'profile')
        read_only_fields = ('id', 'email')

    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'share_medical_history': profile.share_medical_history,
                'receive_notifications': profile.receive_notifications,
                'preferred_language': profile.preferred_language,
                'timezone': profile.timezone,
            }
        except UserProfile.DoesNotExist:
            return {}


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    share_medical_history = serializers.BooleanField(source='profile.share_medical_history')
    receive_notifications = serializers.BooleanField(source='profile.receive_notifications')
    preferred_language = serializers.CharField(source='profile.preferred_language')
    timezone = serializers.CharField(source='profile.timezone')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'date_of_birth', 'phone_number',
                 'emergency_contact', 'emergency_phone', 'age', 'weight', 'height',
                 'allergies', 'medical_conditions', 'current_medications', 'medical_notes', 
                 'profile_picture', 'share_medical_history', 'receive_notifications', 
                 'preferred_language', 'timezone')

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile, created = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
