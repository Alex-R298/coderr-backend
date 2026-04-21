from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from profiles_app.api.permissions import IsOwnerOrReadOnly
from profiles_app.api.serializers import (
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
    ProfileSerializer,
)
from profiles_app.models import UserProfile


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a user profile by user id."""

    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'


class BusinessProfileListView(generics.ListAPIView):
    """List all business profiles."""

    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='business')


class CustomerProfileListView(generics.ListAPIView):
    """List all customer profiles."""

    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type='customer')
