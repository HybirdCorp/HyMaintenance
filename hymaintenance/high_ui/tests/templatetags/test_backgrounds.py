from django.test import SimpleTestCase

from ...templatetags.backgrounds import random_background


class RandomBackgroundTestCase(SimpleTestCase):

    def test_values_return_by_random_background_are_between_1_and_7(self):
        for _ in range(100):
            value = random_background()
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 7)
