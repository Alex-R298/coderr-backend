from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full offer detail serializer."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferDetailHyperlinkSerializer(serializers.ModelSerializer):
    """Slim offer detail representation with id and URL."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f'/offerdetails/{obj.id}/'


class OfferListSerializer(serializers.ModelSerializer):
    """Paginated list serializer with min_price, min_delivery_time, user_details."""

    details = OfferDetailHyperlinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details',
        ]

    def get_min_price(self, obj):
        prices = [d.price for d in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = [d.delivery_time_in_days for d in obj.details.all()]
        return min(times) if times else None

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """Retrieve serializer for a single offer with hyperlinked details."""

    details = OfferDetailHyperlinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time',
        ]

    def get_min_price(self, obj):
        prices = [d.price for d in obj.details.all()]
        return min(prices) if prices else None

    def get_min_delivery_time(self, obj):
        times = [d.delivery_time_in_days for d in obj.details.all()]
        return min(times) if times else None


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/update serializer with nested details."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError('An offer must contain exactly 3 details.')
        types = {d.get('offer_type') for d in value}
        if types != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError(
                'Offer details must include basic, standard and premium.'
            )
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if details_data is not None:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        for detail in details_data:
            offer_type = detail.get('offer_type')
            OfferDetail.objects.filter(
                offer=instance, offer_type=offer_type
            ).update(**detail)
