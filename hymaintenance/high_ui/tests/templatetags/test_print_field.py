from django.test import SimpleTestCase

from ...templatetags.print_fields import pretty_print_minutes


class PrettyPrintMinutesTestCase(SimpleTestCase):

    def test_pretty_print_minutes_if_value_is_blank(self):
        self.assertEqual("", pretty_print_minutes(""))

    def test_pretty_print_minutes_with_hours_and_no_minutes(self):
        self.assertEqual("3h", pretty_print_minutes(180))

    def test_pretty_print_minutes_with_hours_and_minutes(self):
        self.assertEqual("3h10", pretty_print_minutes(190))

    def test_pretty_print_minutes_with_only_minutes(self):
        self.assertEqual("40m", pretty_print_minutes(40))

    def test_pretty_print_minutes_with_only_minutes_and_long_format(self):
        self.assertEqual("40 mins", pretty_print_minutes(40,
                                                         use_long_minute_format=True))

    def test_negative_pretty_print_minutes_with_hours_and_no_minutes(self):
        self.assertEqual("-3h", pretty_print_minutes(-180))

    def test_negative_pretty_print_minutes_with_hours_and_minutes(self):
        self.assertEqual("-3h10", pretty_print_minutes(-190))

    def test_negative_pretty_print_minutes_with_only_minutes(self):
        self.assertEqual("-40m", pretty_print_minutes(-40))

    def test_negative_pretty_print_minutes_with_only_minutes_and_long_format(self):
        self.assertEqual("-40 mins", pretty_print_minutes(-40,
                                                          use_long_minute_format=True))
