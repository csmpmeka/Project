from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from home.models import Advertisement


class TestAdvertisementObject(TestCase):
    def setUp(self):
        self.ad_obj = Advertisement.objects.create(title='test_obj',
                                                   description='xyz',
                                                   negotiable=False)

    def test_login(self):
        self.assertEqual(self.ad_obj.title, 'test_obj')


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'admin'
        self.password = 'admin'
        self.user = User.objects.create_user(self.username, password=self.password)

    def test_login_view(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertRedirects(response, reverse('home'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {'username': self.username, 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Invalid login')  # Check for error message


class LogoutTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'admin'
        self.password = 'admin'
        self.user = User.objects.create_user(self.username, password=self.password)

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)  # Login the user
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertRedirects(response, reverse('home'))  # Check that user is redirected to the correct page
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertRedirects(response, reverse('login'))  # Check that user is redirected to the login page

    def test_logout_failure(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertRedirects(response, reverse('login'))  # Check that user is redirected to the login page


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'Pest'
        self.password = 'Test@123'

    def test_registration_view(self):
        response = self.client.post(reverse('register'),
                                    {'username': self.username, 'password1': self.password, 'password2': self.password})
        self.assertEqual(response.status_code, 302)  # Redirect to success page
        self.assertEqual(User.objects.count(), 1)  # Check that the user was created
        user = User.objects.get(username=self.username)
        self.assertEqual(user.username, self.username)  # Check that the user's username was set correctly

    def test_registration_failure(self):
        response = self.client.post(reverse('register'), {'username': self.username, 'password1': self.password,
                                                          'password2': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)  # Stay on registration page
        self.assertContains(response, 'The two password fields didn&#x27;t match.')  # Check for error message
        self.assertEqual(User.objects.count(), 0)  # Check that the user was not created
