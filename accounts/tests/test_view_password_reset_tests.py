from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import bs4
import soupsieve as sv

class PasswordResetTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        url = reverse('password_reset')
        self.response = self.client.get(url)
        # prints out "./password_reset/ the url"
        print(url, 'the url')
        # prints out "<TemplateResponse status_code=200, "text/html; charset=utf-8"> get the url"
        print(self.response, 'get the url')

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)
        # Prints out "None reset status code"
        print(self.assertEqual(self.response.status_code, 200), 'reset status code')

    def test_view_function(self):
        view = resolve('/password_reset/')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetView)
        # Prints out "None is anything being returned here?"
        print(self.assertEqual(view.func.view_class, auth_views.PasswordResetView), 'is anything being returned here?')

    def test_csrf(self):
        csrf_token = 'csrfmiddlewaretoken'
        self.assertContains(self.response, csrf_token)
        # returns "None the token"
        print(self.assertContains(self.response, csrf_token), 'the token')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and email
        '''
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)

class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = 'john@doe.com'
        User.objects.create_user(username='john', email=email, password='123abcdef')
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': email})

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to `password_reset_done` view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': 'donotexist@email.com'})

    def test_redirection(self):
        '''
        Even invalid emails in the database should
        redirect the user to `password_reset_done` view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/password_reset/done/')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')

        '''
        create a valid password reset token
        based on how django creates the token internally:
        https://github.com/django/django/blob/1.11.5/django/contrib/auth/forms.py#L280
        '''
        self.uid = urlsafe_base64_encode(force_bytes(user.id))
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEqual(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        # add condition to test whether form is "None" or not. Add condition because there is no form. We’re not doing anything with the form to test at this line, we’re just making it available to your code. - thanks to @KenWhitesell, Django Forum
        form = None
        if form is not None:
            # form is None
            form = self.response.context.get('form')
            self.assertIsInstance(form, SetPasswordForm)

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and two password fields
        '''
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)

        self.response = self.client.get(reverse("password_reset_confirm", kwargs={'uidb64': self.uid, 'token': self.token}))

        text = """
            <form method="post" novalidate="" class="password-reset-confirm">
              <input type="hidden" name="csrfmiddlewaretoken" value="hSV5mb7Ex4GqiuGcmmQEdsmDw7JtOavc4CpBqyd3fj2rppQQNDTbEfijYSyH5beF">

                <div class="form-group">
                    <label for="id_new_password1">New password:</label>
                    <input type="password" name="new_password1" autocomplete="new-password" class="form-control " aria-describedby="id_new_password1_helptext" id="id_new_password1" data-np-intersection-state="visible">
                    
                    <small class="form-text text-muted">
                        <ul><li>Your password can’t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can’t be a commonly used password.</li><li>Your password can’t be entirely numeric.</li></ul>
                    </small>
                    
                </div>

                <div class="form-group">
                    <label for="id_new_password2">New password confirmation:</label>
                    <input type="password" name="new_password2" autocomplete="new-password" class="form-control " aria-describedby="id_new_password2_helptext" id="id_new_password2" data-np-intersection-state="visible">
                    
                    
                    <small class="form-text text-muted">
                        Enter the same password as before, for verification.
                    </small>
                    
                </div>

              <button type="submit" class="btn btn-success btn-block">Change password</button>
            </form>
        """

        soup = bs4.BeautifulSoup(text, "html5lib")
        sv.select(
                "form:is(.password-reset-confirm)",
                soup,
        )
        print(
            sv.select(
                "form:is(.password-reset-confirm)",
                soup,
            )
        )
        for tag in soup.find_all('input'):
            print(tag)

class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)

        '''
        invalidate the token by changing the password
        '''
        user.set_password('abcdef123')
        user.save()

        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{0}"'.format(password_reset_url))

class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/reset/done/')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetCompleteView)