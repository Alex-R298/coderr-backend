from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.exceptions import ValidationError
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

    pagination_class = LargeResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateUpdateSerializer
        return OfferListSerializer

    def get_queryset(self):
        """Applies creator_id, min_price and max_delivery_time filters."""
        queryset = Offer.objects.all().annotate(
            min_price=Min('details__price'),
            min_delivery_time=Min('details__delivery_time_in_days'),
        ).order_by('-created_at')
        params = self.request.query_params
        if params.get('creator_id'):
            queryset = self._filter_int(queryset, 'user_id', params['creator_id'])
        if params.get('min_price'):
            queryset = self._filter_numeric(queryset, 'min_price__gte', params['min_price'])
        if params.get('max_delivery_time'):
            queryset = self._filter_int(queryset, 'min_delivery_time__lte', params['max_delivery_time'])
        return queryset

    def _filter_int(self, queryset, field, raw_value):
        try:
            return queryset.filter(**{field: int(raw_value)})
        except (TypeError, ValueError):
            raise ValidationError({field: 'Must be a valid integer.'})

    def _filter_numeric(self, queryset, field, raw_value):
        try:
            return queryset.filter(**{field: float(raw_value)})
        except (TypeError, ValueError):
            raise ValidationError({field: 'Must be a valid number.'})

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
