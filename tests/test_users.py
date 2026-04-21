from rest_framework.test import APITestCase
from rest_framework import status


class RegisterUserTestCase(APITestCase):
    def test_register_user(self):
        response = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_password_mismatch(self):
        response = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "differentPassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        # First registration should succeed
        response1 = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second registration with the same username should fail
        response2 = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "another@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_type(self):
        response = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        response = self.client.post('/api/registration/', data={
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_returns_token_and_user_data(self):
        response = self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('user_id', response.data)


class LoginUserTestCase(APITestCase):
    def setUp(self):
        self.client.post('/api/registration/', data={
            "username": "exampleUsername",
            "email": "example@mail.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer"
        }, format='json')

    def test_login_valid_credentials(self):
        response = self.client.post('/api/login/', data={
            "username": "exampleUsername",
            "password": "examplePassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertIn('user_id', response.data)

    def test_login_wrong_password(self):
        response = self.client.post('/api/login/', data={
            "username": "exampleUsername",
            "password": "wrongPassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_username(self):
        response = self.client.post('/api/login/', data={
            "username": "unknownUser",
            "password": "examplePassword"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)