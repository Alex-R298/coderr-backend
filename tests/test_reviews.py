from reviews_app.models import Review
from profiles_app.models import UserProfile
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class TestReviews(APITestCase):
    def setUp(self):
        self.business_user = User.objects.create_user(username='biz', password='pw123456')
        self.customer_user = User.objects.create_user(username='cust', password='pw123456')
        self.other_customer = User.objects.create_user(username='cust2', password='pw123456')
        UserProfile.objects.create(user=self.business_user, type='business')
        UserProfile.objects.create(user=self.customer_user, type='customer')
        UserProfile.objects.create(user=self.other_customer, type='customer')
        self.review = Review.objects.create(
            business_user=self.business_user,
            reviewer=self.customer_user,
            rating=4,
            description='Great service!',
        )

    def test_list_reviews_authenticated(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reviews_unauthenticated(self):
        response = self.client.get('/api/reviews/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_filter_by_business_user_id(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f'/api/reviews/?business_user_id={self.business_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_filter_by_reviewer_id(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(f'/api/reviews/?reviewer_id={self.customer_user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_ordering_by_rating(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get('/api/reviews/?ordering=rating')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_review_as_customer(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.post('/api/reviews/', data={
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Excellent!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 2)

    def test_create_review_as_business_forbidden(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post('/api/reviews/', data={
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Excellent!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_review_unauthenticated(self):
        response = self.client.post('/api/reviews/', data={
            'business_user': self.business_user.id,
            'rating': 5,
            'description': 'Excellent!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_duplicate_review_forbidden(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post('/api/reviews/', data={
            'business_user': self.business_user.id,
            'rating': 3,
            'description': 'Again',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_review_as_reviewer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.patch(f'/api/reviews/{self.review.id}/', data={
            'rating': 2,
            'description': 'Changed my mind',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 2)

    def test_patch_review_as_other_user_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.patch(f'/api/reviews/{self.review.id}/', data={
            'rating': 1,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_review_unauthenticated(self):
        response = self.client.patch(f'/api/reviews/{self.review.id}/', data={
            'rating': 1,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_review_as_reviewer(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)

    def test_delete_review_as_other_user_forbidden(self):
        self.client.force_authenticate(user=self.other_customer)
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_review_unauthenticated(self):
        response = self.client.delete(f'/api/reviews/{self.review.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
