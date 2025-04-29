from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from login.models import Profile, Notification
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.librarian = User.objects.create_user(username='libuser', password='libpass')
        self.librarian.profile.role = 'librarian'
        self.librarian.profile.save()

        self.social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id='dummy-client-id',
            secret='dummy-secret'
        )
        current_site = Site.objects.get_current()
        self.social_app.sites.add(current_site)

        self.client = Client()

    def test_home_accessible(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_profile_created(self):
        self.assertIsNotNone(self.user.profile)
        self.assertEqual(str(self.user.profile), f"{self.user.username} - patron")

    def test_profile_picture_upload_view_accessible(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('upload_profile_picture'))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirect(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, "/")

    def test_post_login_redirect(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('post_login_redirect'))
        self.assertRedirects(response, reverse('home'))

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(reverse('profile'))
        self.assertContains(response, "You must be logged in to view your profile.")

    def test_unauthenticated_profile_picture_upload_denied(self):
        response = self.client.get(reverse('upload_profile_picture'))
        self.assertContains(response, "You must be logged in to upload a profile picture.")

    def test_request_librarian_creates_notification(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('request_librarian'))
        self.assertRedirects(response, reverse('home'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.role, 'pending')
        self.assertTrue(Notification.objects.filter(user=self.librarian).exists())

    def test_notifications_view_authenticated(self):
        Notification.objects.create(user=self.user, message="Test note")
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test note")

    def test_notifications_view_unauthenticated(self):
        response = self.client.get(reverse('notifications'))
        self.assertContains(response, "You must be logged in to view your notifications.")
