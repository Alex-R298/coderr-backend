from rest_framework import serializers

from profiles_app.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """Full profile serializer with username, email and empty-string fallbacks."""

    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]
        read_only_fields = ['user', 'created_at', 'type']

    def update(self, instance, validated_data):
        """Updates profile fields and related user email."""
        user_data = validated_data.pop('user', {})
        email = user_data.get('email')
        if email is not None:
            instance.user.email = email
            instance.user.save()
        return super().update(instance, validated_data)


class BusinessProfileListSerializer(serializers.ModelSerializer):
    """List serializer for business profiles."""

    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
        ]


class CustomerProfileListSerializer(serializers.ModelSerializer):
    """List serializer for customer profiles."""

    username = serializers.CharField(source='user.username', read_only=True)
    uploaded_at = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'uploaded_at', 'type']
