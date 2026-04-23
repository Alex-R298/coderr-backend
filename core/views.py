from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from profiles_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """Public aggregate stats for the landing page."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        avg = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        return Response({
            'review_count': Review.objects.count(),
            'average_rating': round(float(avg), 1),
            'business_profile_count': UserProfile.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count(),
        })
