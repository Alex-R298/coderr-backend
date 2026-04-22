from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from core.pagination import LargeResultsSetPagination
from offers_app.api.permissions import IsBusinessUser, IsOfferOwner
from offers_app.api.serializers import (
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferListSerializer,
    OfferRetrieveSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferListCreateView(generics.ListCreateAPIView):
    """List all offers (public) or create a new offer (business only)."""

    queryset = Offer.objects.all()
    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user']
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def get_queryset(self):
        queryset = Offer.objects.all()
        creator_id = self.request.query_params.get('creator_id')
        if creator_id:
            queryset = queryset.filter(user_id=creator_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a single offer."""

    queryset = Offer.objects.all()
    permission_classes = [IsAuthenticated, IsOfferOwner]

    def get_serializer_class(self):
        if self.request.method in ('PATCH', 'PUT'):
            return OfferCreateUpdateSerializer
        return OfferRetrieveSerializer


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """Retrieve a single offer detail."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
