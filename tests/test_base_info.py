from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from profiles_app.models import UserProfile
from offers_app.models import Offer, OfferDetail
from reviews_app.models import Review


class TestBaseInfo(APITestCase):
    def setUp(self):
        self.biz1 = User.objects.create_user(username='biz1', password='pw123456')
        self.biz2 = User.objects.create_user(username='biz2', password='pw123456')
        self.cust1 = User.objects.create_user(username='cust1', password='pw123456')
        self.cust2 = User.objects.create_user(username='cust2', password='pw123456')
        UserProfile.objects.create(user=self.biz1, type='business')
        UserProfile.objects.create(user=self.biz2, type='business')
        UserProfile.objects.create(user=self.cust1, type='customer')
        UserProfile.objects.create(user=self.cust2, type='customer')

        Offer.objects.create(user=self.biz1, title='Offer 1', description='desc')
        Offer.objects.create(user=self.biz2, title='Offer 2', description='desc')

        Review.objects.create(business_user=self.biz1, reviewer=self.cust1, rating=4, description='ok')
        Review.objects.create(business_user=self.biz1, reviewer=self.cust2, rating=5, description='top')
        Review.objects.create(business_user=self.biz2, reviewer=self.cust1, rating=3, description='mid')

    def test_base_info_returns_200_without_auth(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_base_info_contains_all_keys(self):
        response = self.client.get('/api/base-info/')
        self.assertIn('review_count', response.data)
        self.assertIn('average_rating', response.data)
        self.assertIn('business_profile_count', response.data)
        self.assertIn('offer_count', response.data)

    def test_base_info_review_count(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['review_count'], 3)

    def test_base_info_average_rating(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['average_rating'], 4.0)

    def test_base_info_business_profile_count(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['business_profile_count'], 2)

    def test_base_info_offer_count(self):
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['offer_count'], 2)

    def test_base_info_empty_db_average_rating_zero(self):
        Review.objects.all().delete()
        response = self.client.get('/api/base-info/')
        self.assertEqual(response.data['average_rating'], 0.0)
