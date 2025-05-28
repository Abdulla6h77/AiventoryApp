from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product  # Import the Product model
from rest_framework import status

class AppViewsTestCase(TestCase):
    
    def test_signup_empty_fields(self):
        response = self.client.post(reverse('signup'), {
            'username': '',
            'password': ''
        })
        self.assertNotEqual(response.status_code, 200)  # Should fail or return 400

    def test_signup_duplicate_username(self):
        User.objects.create_user(username='duplicate', password='pass')
        response = self.client.post(reverse('signup'), {
            'username': 'duplicate',
            'password': 'pass'
        })
        self.assertNotEqual(response.status_code, 200)

    def test_login_missing_fields(self):
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        self.assertEqual(response.status_code, 400)  # Changed to 400

    def test_store_listing_no_products(self):
        Product.objects.all().delete()  # Clear all products
        response = self.client.get(reverse('store_listing'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Product')

    def test_search_products_empty_query(self):
        response = self.client.get(reverse('search_products'), {'query': ''})
        self.assertEqual(response.status_code, 404)  # Check the response status for 404 if it's not found
