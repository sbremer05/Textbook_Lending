from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from login.models import Profile
from allauth.socialaccount.models import SocialApp
class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='dummy-client-id',
            secret='dummy-secret'
        )
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current()
        self.social_app.sites.add(current_site)
        self.client = Client()

    def test_home_accessible(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_profile_created(self):
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(str(self.user.profile), f"{self.user.username} - No Role Selected")

    def test_profile_picture_upload_view_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('upload_profile_picture'))
        self.assertEqual(response.status_code, 200)

