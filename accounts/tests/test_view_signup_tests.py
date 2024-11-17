from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import SignUpForm
from ..views import signup

import bs4
import soupsieve as sv


class SignUpTests(TestCase):
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve("/signup/")
        self.assertEqual(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        """
        The view must contain 9 inputs: csrf, username, first_name, last_name, email, password1, password2, two usable passwords of type radio (for pass 1 and 2).
        """
        self.assertContains(self.response, "<input", 9)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="password"', 2)
        self.assertContains(self.response, 'type="radio"', 2)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="hidden"', 1)

        # added to the bottom of the (refactored) test_form_inputs test: (updated when added first_name and last_name fields)
        self.response = self.client.get(reverse("signup"))
        text = """
        <form method="post" novalidate="" class="signup-form" data-np-autofill-form-type="register" data-np-checked="1" data-np-watching="1">
              <input type="hidden" name="csrfmiddlewaretoken" value="N1N8NuHlxLGYqrCqAkwC2j99tiARRQ5htL0FI2EGdc7UB5AAKBD7jtidAPkf5s8t">
            <div class="form-group">
                <label for="id_username">Username:</label>
                <input type="text" name="username" maxlength="150" autofocus="" class="form-control " required="" aria-describedby="id_username_helptext" id="id_username" data-np-autofill-field-type="username">
                <small class="form-text text-muted">
                    Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.
                </small>
            </div>
            <div class="form-group">
                <label for="id_first_name">First name:</label>
                <input type="text" name="first_name" maxlength="150" class="form-control " id="id_first_name" data-np-autofill-field-type="firstName" data-np-uid="a3d58e8d-be55-45b1-9d84-73a239b6c11b">
            </div>
            <div class="form-group">
                <label for="id_last_name">Last name:</label>
                <input type="text" name="last_name" maxlength="150" class="form-control " id="id_last_name" data-np-autofill-field-type="lastName" data-np-uid="1d73b343-32f7-4783-bd03-12afb46acd5f">
            </div>
            <div class="form-group">
                <label for="id_email">Email:</label>
                <input type="email" name="email" maxlength="254" class="form-control " required="" id="id_email" data-np-autofill-field-type="email" data-np-uid="344e0c21-2743-4de5-81f0-a338aa099518">
            </div>
            <div class="form-group">
                <label for="id_password1">Password:</label>
                <input type="password" name="password1" autocomplete="new-password" class="form-control " aria-describedby="id_password1_helptext" id="id_password1" data-np-autofill-field-type="newPassword" data-np-uid="bb806b1d-8c41-4c6f-842c-9d98e4b7d338">
                <small class="form-text text-muted">
                    <ul><li>Your password can’t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can’t be a commonly used password.</li><li>Your password can’t be entirely numeric.</li></ul>
                </small>
            </div>
            <div class="form-group">
                <label for="id_password2">Password confirmation:</label>
                <input type="password" name="password2" autocomplete="new-password" class="form-control " aria-describedby="id_password2_helptext" id="id_password2" data-np-autofill-field-type="newPassword" data-np-uid="4423502f-ac5e-426a-95b0-f06b3ce13f72">
                
                <small class="form-text text-muted">
                    Enter the same password as before, for verification.
                </small>
            </div>
            <div class="form-group">
                <label>Password-based authentication:</label>
                <div id="id_usable_password" class="form-control "><div>
                <label for="id_usable_password_0"><input type="radio" name="usable_password" value="true" class="form-control " id="id_usable_password_0" checked="">
            Enabled</label>
            </div>
            <div>
                <label for="id_usable_password_1"><input type="radio" name="usable_password" value="false" class="form-control " id="id_usable_password_1">
            Disabled</label>

            </div>
        </div>
    
            <small class="form-text text-muted">
                Whether the user will be able to authenticate using a password or not. If disabled, they may still be able to authenticate using other backends, such as Single Sign-On or LDAP.
            </small>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Create an account</button>
    </form>
        """
        soup = bs4.BeautifulSoup(text, "html5lib")
        sv.select(
                "form:is(.signup-form)",
                soup,
        )
        print(
            sv.select(
                "form:is(.signup-form)",
                soup,
            )
        )
        for tag in soup.find_all('input'):
            print(tag)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse("signup")
        data = {
            "username": "john",
            "email": "john@doe.com",
            "password1": "abcdef123456",
            "password2": "abcdef123456",
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse("index")

    def test_redirection(self):
        """
        A valid form submission should redirect the user to the home page
        """
        self.assertRedirects(self.response, self.index_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        """
        Create a new request to an arbitrary page.
        The resulting response should now have an `user` to its context, after a successful sign up.
        """
        response = self.client.get(self.index_url)
        user = response.context.get("user")
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse("signup")
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_signup_status_code(self):
        """
        An invalid form submission should return to the same page
        """
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get("form")
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())
