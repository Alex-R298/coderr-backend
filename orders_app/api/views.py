from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import OfferDetail
from orders_app.api.permissions import IsBusinessUserForPatch, IsCustomerUser
from orders_app.api.serializers import OrderSerializer
from orders_app.models import Order


class OrderListCreateView(generics.ListCreateAPIView):
    """List orders for current user or create a new order from an offer detail."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerUser]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def create(self, request, *args, **kwargs):
        """Creates an order based on the given offer_detail_id."""
        offer_detail_id = request.data.get('offer_detail_id')
        if not offer_detail_id:
            return Response(
                {'offer_detail_id': 'This field is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            detail_pk = int(offer_detail_id)
        except (TypeError, ValueError):
            return Response(
                {'offer_detail_id': 'Must be a valid integer.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        detail = get_object_or_404(OfferDetail, pk=detail_pk)
        order = Order.objects.create(
            customer_user=request.user,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update (status) or delete a single order."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsBusinessUserForPatch]


class OrderCountView(APIView):
    """Returns count of in-progress orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(User, pk=business_user_id, profile__type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='in_progress'
        ).count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """Returns count of completed orders for a business user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        get_object_or_404(User, pk=business_user_id, profile__type='business')
        count = Order.objects.filter(
            business_user_id=business_user_id, status='completed'
        ).count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)
