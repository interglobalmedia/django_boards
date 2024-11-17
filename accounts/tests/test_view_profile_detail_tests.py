from django.forms import ModelForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Profile

from ..views import profile_detail

class MyProfileDetailTestsCase(TestCase):
    def setUp(self):
        self.username = 'john'
        self.password = 'secret123'
        self.user = User.objects.create_user(username=self.username, email='johndoe@example.com', password=self.password)
        self.url = reverse('users-profile')

class MyProfileDetailTests(MyProfileDetailTestsCase):

    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.url = reverse('users-profile')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve('/profile-detail/1/')
        self.assertEqual(view.func, profile_detail)

class LoginRequiredMyProfileDetailTests(TestCase):
    def test_redirection(self):
        url = reverse('users-profile')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=url))

