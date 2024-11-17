from django.test import TestCase
from ..signals import create_profile, save_profile

class SignalTests(TestCase):
    def test_create_profile_handler_success(sender, **kwargs):
        sender.assertTrue(create_profile)

    def test_create_profile_handler_fail(sender, **kwargs):
        if not sender:
            sender.assertFalse(create_profile)

    def test_save_profile_handler_success(sender, **kwargs):
        sender.assertTrue(save_profile)

    def test_save_profile_handler_fail(sender, **kwargs):
        if not sender:
            assertFalse(save_profile)

