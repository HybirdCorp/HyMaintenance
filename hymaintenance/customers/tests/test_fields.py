
from django.test import SimpleTestCase

from ..fields import LowerCaseEmailField


class LowerCaseEmailFieldTestCase(SimpleTestCase):

    def test_when_none_value_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual(None, email_field.get_prep_value(None))

    def test_when_empty_string_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual("", email_field.get_prep_value(""))

    def test_when_value_already_lower_case_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual("robot@example.com", email_field.get_prep_value("robot@example.com"))

    def test_when_value_are_higher_case_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual("robot@example.com", email_field.get_prep_value("ROBOT@EXAMPLE.COM"))

    def test_when_value_have_mulitple_case_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual("robot@example.com", email_field.get_prep_value("RobOt@exAmPle.com"))

    def test_when_value_have_figure_if_it_works(self):
        email_field = LowerCaseEmailField()
        self.assertEqual("r0b0t@example.com", email_field.get_prep_value("R0b0t@exAmPle.com"))
