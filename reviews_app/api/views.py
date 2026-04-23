from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from reviews_app.models import Review
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.api.permissions import IsCustomerForCreate, IsReviewerOrReadOnly


class ReviewListCreateView(generics.ListCreateAPIView):
    """GET list of reviews (filter/order), POST create as customer."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCustomerForCreate]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['business_user_id', 'reviewer_id']
    ordering_fields = ['updated_at', 'rating']
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE a single review (reviewer only for write)."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewerOrReadOnly]

    def get_serializer(self, *args, **kwargs):
        serializer = super().get_serializer(*args, **kwargs)
        if self.request.method == 'PATCH':
            for field_name in list(serializer.fields):
                if field_name not in ('rating', 'description'):
                    serializer.fields[field_name].read_only = True
        return serializer
