from orders_app.models import Order
from offers_app.models import Offer, OfferDetail
from profiles_app.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class TestOrders(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pw123456')
        self.customer_user = User.objects.create_user(username='cust', password='pw123456')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')

        self.offer = Offer.objects.create(
            user=self.business_user,
            title='Test Offer',
            description='An offer for testing.',
        )
        self.detail = OfferDetail.objects.create(
            offer=self.offer,
            title='Basic Package',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Feature 1', 'Feature 2'],
            offer_type='basic',
        )

        self.order = Order.objects.create(
            customer_user=self.customer_user,
            business_user=self.business_user,
            title='Test Order',
            revisions=2,
            delivery_time_in_days=5,
            price=100,
            features=['Feature 1', 'Feature 2'],
            offer_type='basic',
        )

    def test_list_orders(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_order_as_customer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post('/api/orders/', data={
            'offer_detail_id': self.detail.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

    def test_create_order_as_business_forbidden(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post('/api/orders/', data={
            'offer_detail_id': self.detail.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_order_unauthenticated(self):
        response = self.client.post('/api/orders/', data={
            'offer_detail_id': self.detail.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_invalid_offer_detail(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post('/api/orders/', data={
            'offer_detail_id': 9999,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_order_status_as_business(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.patch(f'/api/orders/{self.order.id}/', data={
            'status': 'completed'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'completed')

    def test_patch_order_as_customer_forbidden(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.patch(f'/api/orders/{self.order.id}/', data={
            'status': 'completed'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'in_progress')

    def test_delete_order_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    def test_delete_order_as_non_admin(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 1)

    def test_order_count(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f'/api/order-count/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_count'], 1)

    def test_completed_order_count(self):
        self.order.status = 'completed'
        self.order.save()
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f'/api/completed-order-count/{self.business_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['completed_order_count'], 1)
