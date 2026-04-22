from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class TestOffers(APITestCase):

    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pw123456')
        self.customer_user = User.objects.create_user(username='cust', password='pw123456')
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Test Offer',
            image=None,
            description='This is a test offer.',
        )
        self.detail_basic = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Design',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Logo Design', 'Visitenkarte'],
            offer_type='basic',
        )
        self.detail_standard = OfferDetail.objects.create(
            offer=self.offer,
            title='Standard Design',
            revisions=5,
            delivery_time_in_days=7,
            price=200,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier'],
            offer_type='standard',
        )
        self.detail_premium = OfferDetail.objects.create(
            offer=self.offer,
            title='Premium Design',
            revisions=10,
            delivery_time_in_days=10,
            price=500,
            features=['Logo Design', 'Visitenkarte', 'Briefpapier', 'Flyer'],
            offer_type='premium',
        )
        self.valid_offer_payload = {
            'title': 'New Offer',
            'description': 'This is a new offer.',
            'image': None,
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 2,
                    'delivery_time_in_days': 5,
                    'price': 100,
                    'features': ['A'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 5,
                    'delivery_time_in_days': 7,
                    'price': 200,
                    'features': ['A', 'B'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 10,
                    'delivery_time_in_days': 10,
                    'price': 500,
                    'features': ['A', 'B', 'C'],
                    'offer_type': 'premium',
                },
            ],
        }

    def test_offer_list(self):
        response = self.client.get('/api/offers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_offer_retrieval(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.offer.id)

    def test_offer_create_as_business(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post('/api/offers/', self.valid_offer_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)

    def test_offer_create_as_customer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post('/api/offers/', self.valid_offer_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_offer_create_unauthenticated(self):
        response = self.client.post('/api/offers/', self.valid_offer_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_own_offer(self):
        self.client.force_authenticate(user=self.business_user)
        data = {'description': 'Updated offer description.'}
        response = self.client.patch(f'/api/offers/{self.offer.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.description, 'Updated offer description.')

    def test_patch_foreign_offer(self):
        self.client.force_authenticate(user=self.customer_user)
        data = {'description': 'Malicious update attempt.'}
        response = self.client.patch(f'/api/offers/{self.offer.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.offer.refresh_from_db()
        self.assertNotEqual(self.offer.description, 'Malicious update attempt.')

    def test_delete_own_offer(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Offer.objects.filter(id=self.offer.id).exists())

    def test_delete_foreign_offer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.delete(f'/api/offers/{self.offer.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Offer.objects.filter(id=self.offer.id).exists())

    def test_get_offerdetail(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(f'/api/offerdetails/{self.detail_basic.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.detail_basic.id)
        self.assertEqual(response.data['offer_type'], 'basic')
