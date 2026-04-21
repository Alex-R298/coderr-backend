from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from profiles_app.models import UserProfile


class ProfileDetailTestCase(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(
            username='business_user', email='biz@mail.de', password='pw123456'
        )
        self.customer_user = User.objects.create_user(
            username='customer_user', email='cust@mail.de', password='pw123456'
        )
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.business_token = Token.objects.create(user=self.business_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_get_profile_authenticated(self):
        self.authenticate(self.business_token)
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.business_user.id)
        self.assertEqual(response.data['type'], 'business')

    def test_get_profile_unauthenticated(self):
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_not_found(self):
        self.authenticate(self.business_token)
        response = self.client.get('/api/profile/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_empty_fields_are_empty_string(self):
        self.authenticate(self.business_token)
        response = self.client.get(f'/api/profile/{self.business_user.id}/')
        for field in ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']:
            self.assertEqual(response.data[field], '')

    def test_patch_own_profile(self):
        self.authenticate(self.business_token)
        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            data={'first_name': 'Max', 'location': 'Berlin'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Max')
        self.assertEqual(response.data['location'], 'Berlin')

    def test_patch_foreign_profile_forbidden(self):
        self.authenticate(self.business_token)
        response = self.client.patch(
            f'/api/profile/{self.customer_user.id}/',
            data={'first_name': 'Hacked'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_profile_unauthenticated(self):
        response = self.client.patch(
            f'/api/profile/{self.business_user.id}/',
            data={'first_name': 'Max'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessProfileListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pw123456')
        self.business_user = User.objects.create_user(username='biz', password='pw123456')
        self.customer_user = User.objects.create_user(username='cust', password='pw123456')
        UserProfile.objects.create(user=self.user, type='customer')
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.token = Token.objects.create(user=self.user)

    def test_list_business_profiles_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'business')

    def test_list_business_profiles_unauthenticated(self):
        response = self.client.get('/api/profiles/business/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CustomerProfileListTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pw123456')
        self.business_user = User.objects.create_user(username='biz', password='pw123456')
        self.customer_user = User.objects.create_user(username='cust', password='pw123456')
        UserProfile.objects.create(user=self.user, type='business')
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.token = Token.objects.create(user=self.user)

    def test_list_customer_profiles_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['type'], 'customer')

    def test_list_customer_profiles_unauthenticated(self):
        response = self.client.get('/api/profiles/customer/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)