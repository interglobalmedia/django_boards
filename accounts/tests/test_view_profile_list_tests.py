from django.test import TestCase
from django.urls import resolve, reverse
from django.contrib.auth.models import User

from ..views import ProfileListView

class ProfileListTestCase(TestCase):
    
    def setUp(self):
        self.username = 'john'
        self.password = 'secret123'
        self.user = User.objects.create_user(username=self.username, email='johndoe@example.com', password=self.password)
        self.url = reverse('users-profile-list')
        self.response = self.client.get(self.url)

class LoginRequiredProfileListTests(TestCase):
    
    def test_redirection(self):
        url = reverse('users-profile-list')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=url))

class ProfileListTests(ProfileListTestCase):

    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.url = reverse('users-profile-list')
        self.response = self.client.get(self.url)

    def test_profiles_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_profiles_url_resolves_profiles_view(self):
        view = resolve('/profiles/')
        self.assertEqual(view.func.view_class, ProfileListView)
