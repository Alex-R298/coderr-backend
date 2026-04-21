# Third-party
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

# Local
from users_app.api.serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """Creates a new user and returns an auth token."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Handles user registration."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticates a user and returns an auth token."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Handles user login."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id,
        }, status=status.HTTP_200_OK)
