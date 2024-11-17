from django.test import TestCase
from ..forms import UpdateProfileForm

class UpdateProfileFormTest(TestCase):
    def test_form_has_fields(self):
        form = UpdateProfileForm()
        expected = ['avatar', 'bio', ]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)