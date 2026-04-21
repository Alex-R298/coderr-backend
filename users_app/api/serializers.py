# Third-party
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validates and creates a new user account."""

    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=['customer', 'business'], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        """Checks that both passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        """Creates user, profile and auth token."""
        from profiles_app.models import UserProfile
        from rest_framework.authtoken.models import Token

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
