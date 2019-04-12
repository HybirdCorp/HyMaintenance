from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import datetime

from ...forms.recurrence import check_authorized_recurrence_start_date


class RecurrenceContractsModelFormTestCase(TestCase):
    def test_check_authorized_recurrence_start_date(self):
        time1 = datetime(day=2, month=12, year=2021).date()
        time2 = datetime(day=2, month=11, year=2020).date()
        with self.assertRaises(ValidationError):
            check_authorized_recurrence_start_date(time2, time1)
