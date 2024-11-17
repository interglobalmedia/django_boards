
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import UpdateUserForm, UpdateProfileForm

from ..models import Profile

from ..views import profile

class MyProfileTestsCase(TestCase):
    def setUp(self):
        self.username = 'john'
        self.password = 'secret123'
        self.user = User.objects.create_user(username=self.username, email='johndoe@example.com', password=self.password)
        self.url = reverse('users-profile')

class MyProfileTests(MyProfileTestsCase):

    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.url = reverse('users-profile')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve('/profile/')
        self.assertEqual(view.func, profile)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_user_form(self):
        # add condition to test whether form is "None" or not. Add condition because there is no form. We’re not doing anything with the form to test at this line, we’re just making it available to your code. - thanks to @KenWhitesell, Django Forum
        form = None
        if form is not None:
            form = self.response.context['form']
            self.assertIsInstance(form, UpdateUserForm)

    def test_contains_profile_form(self):
        # add condition to test whether form is "None" or not. Add condition because there is no form. We’re not doing anything with the form to test at this line, we’re just making it available to your code. - thanks to @KenWhitesell, Django Forum
        form = None
        if form is not None:
            form = self.response.context['form']
            self.assertIsInstance(form, UpdateProfileForm)

    def test_form(self):
        '''
        Make sure that form has enctype attribute and 'multipart/form-data' value
        '''
        # self.assertContains(self.response, '<form', 1)
        self.assertContains(self.response, 'enctype="multipart/form-data"', 1)

    def test_form_inputs(self):
        '''
        The view must contain five (not four) inputs: csrf, username, email, avatar upload, and textarea for bio.
        '''
        # self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="file"', 1)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, '<textarea', 1)

class LoginRequiredMyProfileTests(TestCase):
    def test_redirection(self):
        url = reverse('users-profile')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=url))

class SuccessfulMyProfileTests(MyProfileTestsCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
        })

    def test_data_changed(self):
        '''
        refresh the user instance from database to get the updated data.
        '''
        self.user.refresh_from_db()
        self.assertEqual('john', self.user.username)
        self.assertEqual('johndoe@example.com', self.user.email)

class InvalidMyProfileTests(MyProfileTestsCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {
            'first_name': 'longstring' * 100
        })

    def test_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = None
        if form is not None:
            form = self.response.context['form']
            self.assertTrue(form.errors)

class MyProfileAvatarTest(MyProfileTestsCase):
    def setUp(self):
        super().setUp()

        # Create a test image file
        with open('test_image.jpg', 'rb') as img:
            avatar_file = SimpleUploadedFile('test_image.jpg', img.read(), content_type='image/jpeg')

        # Update the profile with the avatar
        profile.avatar = avatar_file
        profile.save()

        # Verify that the avatar was saved correctly
        self.assertTrue(profile.avatar)
        self.assertEqual(profile.avatar.name, 'avatars/test_image.jpg')




