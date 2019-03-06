from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from customers.tests.factories import ManagerUserFactory

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
