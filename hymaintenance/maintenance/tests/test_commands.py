from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.timezone import datetime
from django.utils.timezone import now
from django.utils.timezone import utc

from customers.tests.factories import ManagerUserFactory

from ..management.commands.recurrence import check_and_apply_credit_recurrence
from ..models.contract import AVAILABLE_TOTAL_TIME
from .factories import create_project


class SendEmailAlertsCommandTestCase(TestCase):
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_if_email_alert_is_sended_when_minimum_is_reached(self):
        manager = ManagerUserFactory(
            email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
        )
        _, contract, _, _ = create_project(
            contract1={
                "credited_hours": 10,
                "credited_hours_min": 20,
                "total_type": AVAILABLE_TOTAL_TIME,
                "recipient": manager,
                "email_alert": True,
            }
        )
        call_command("send_email_alerts")

        self.assertEqual(1, len(mail.outbox))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_if_email_alerts_are_sended_when_minimum_is_reached_multiple_contracts(self):
        manager = ManagerUserFactory(
            email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
        )
        _, _, _, _ = create_project(
            contract1={
                "credited_hours": 10,
                "credited_hours_min": 20,
                "total_type": AVAILABLE_TOTAL_TIME,
                "recipient": manager,
                "email_alert": True,
            }
        )
        _, _, _, _ = create_project(
            contract1={
                "credited_hours": 10,
                "credited_hours_min": 20,
                "total_type": AVAILABLE_TOTAL_TIME,
                "recipient": manager,
                "email_alert": True,
            }
        )
        call_command("send_email_alerts")

        self.assertEqual(2, len(mail.outbox))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_if_email_alert_is_not_sended_when_minimum_is_not_reached(self):
        manager = ManagerUserFactory(
            email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
        )
        _, _, _, _ = create_project(
            contract1={
                "credited_hours": 20,
                "credited_hours_min": 10,
                "total_type": AVAILABLE_TOTAL_TIME,
                "recipient": manager,
            }
        )
        call_command("send_email_alerts")

        self.assertEqual(0, len(mail.outbox))


class RecurrenceCommandTestCase(TestCase):
    def test_annual_recurrence_reached(self):
        time = datetime(day=1, month=2, year=2021, tzinfo=utc)
        _, contract, _, _ = create_project(contract1={"annual_recurrence": True, "recurrence_start_date": time.date()})
        check_and_apply_credit_recurrence(time.date())
        contract.refresh_from_db()

        self.assertEqual(1, contract.recurrence_next_date.day)
        self.assertEqual(2, contract.recurrence_next_date.month)
        self.assertEqual(2022, contract.recurrence_next_date.year)

    def test_monthly_recurrence_reached(self):
        time = datetime(day=1, month=2, year=2021, tzinfo=utc)
        _, contract, _, _ = create_project(contract1={"monthly_recurrence": True, "recurrence_start_date": time.date()})
        check_and_apply_credit_recurrence(time.date())
        contract.refresh_from_db()

        self.assertEqual(1, contract.recurrence_next_date.day)
        self.assertEqual(3, contract.recurrence_next_date.month)
        self.assertEqual(2021, contract.recurrence_next_date.year)

    def test_annual_monthly_recurrence_not_reached(self):
        time1 = datetime(day=1, month=2, year=2021, tzinfo=utc)
        time2 = datetime(day=19, month=1, year=2021, tzinfo=utc)
        _, contract1, contract2, _ = create_project(
            contract1={"annual_recurrence": True, "recurrence_start_date": time1.date()},
            contract2={"monthly_recurrence": True, "recurrence_start_date": time1.date()},
        )
        check_and_apply_credit_recurrence(time2.date())
        contract1.refresh_from_db()
        contract2.refresh_from_db()

        self.assertEqual(time1.date(), contract1.recurrence_next_date)
        self.assertEqual(time1.date(), contract2.recurrence_next_date)

    def test_run_recurrence_command(self):
        now_date = now().date()
        _, contract, _, _ = create_project(contract1={"annual_recurrence": True, "recurrence_start_date": now_date})
        call_command("recurrence")
        contract.refresh_from_db()

        self.assertEqual(now_date.day, contract.recurrence_next_date.day)
        self.assertEqual(now_date.month, contract.recurrence_next_date.month)
        self.assertEqual(now_date.year + 1, contract.recurrence_next_date.year)
