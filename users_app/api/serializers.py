
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from profiles_app.models import UserProfile


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates and creates a new user account."""

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Checks password match and applies Django's built-in password validators."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        """Creates user, profile and auth token."""
        profile_type = validated_data.pop('type')
        validated_data.pop('repeated_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        Token.objects.create(user=user)
        UserProfile.objects.create(user=user, type=profile_type)
        return user


class LoginSerializer(serializers.Serializer):
    """Validates login credentials and returns the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticates user with given credentials."""
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError({'non_field_errors': 'Invalid credentials.'})
        attrs['user'] = user
        return attrs
