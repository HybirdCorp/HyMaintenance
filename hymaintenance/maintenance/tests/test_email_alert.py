from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.timezone import now

from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from high_ui.models import GeneralInformation
from high_ui.tests.utils import SetDjangoLanguage
from toolkit.email import create_email_alert
from toolkit.email import is_number_hours_min_exceeded

from ..forms.issue import MaintenanceIssueCreateForm
from ..models.contract import AVAILABLE_TOTAL_TIME
from ..models.contract import CONSUMMED_TOTAL_TIME
from .factories import IncomingChannelFactory
from .factories import MaintenanceConsumerFactory
from .factories import MaintenanceIssueFactory
from .factories import create_project


class IsNumberHoursMinExceededTestCase(TestCase):
    def test_when_credited_hours_is_under_min(self):
        _, contract, _, _ = create_project(
            contract1={
                "number_hours": 10,
                "number_hours_min": 20,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": True,
            }
        )
        self.assertTrue(is_number_hours_min_exceeded(contract))

    def test_when_credited_hours_equals_min(self):
        _, contract, _, _ = create_project(
            contract1={
                "number_hours": 10,
                "number_hours_min": 10,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": True,
            }
        )
        self.assertTrue(is_number_hours_min_exceeded(contract))

    def test_when_remaining_hours_reachs_min(self):
        company, contract, _, _ = create_project(
            contract1={
                "number_hours": 12,
                "number_hours_min": 10,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": True,
            }
        )
        MaintenanceIssueFactory(company=company, contract=contract, number_minutes=120)
        self.assertTrue(is_number_hours_min_exceeded(contract))

    def test_when_credited_hours_is_under_min_but_not_alert(self):
        _, contract, _, _ = create_project(
            contract1={
                "number_hours": 10,
                "number_hours_min": 20,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": False,
            }
        )
        self.assertFalse(is_number_hours_min_exceeded(contract))

    def test_when_credited_hours_is_over_min(self):
        _, contract, _, _ = create_project(
            contract1={
                "number_hours": 20,
                "number_hours_min": 10,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": True,
            }
        )
        self.assertFalse(is_number_hours_min_exceeded(contract))

    def test_when_contract_is_consummed_total_type(self):
        _, contract, _, _ = create_project(
            contract1={"number_hours": 0, "number_hours_min": 0, "total_type": CONSUMMED_TOTAL_TIME}
        )
        self.assertFalse(is_number_hours_min_exceeded(contract))

    def test_when_contract_is_consummed_total_type_with_wrong_parameters(self):
        _, contract, _, _ = create_project(
            contract1={"number_hours": 10, "number_hours_min": 20, "total_type": CONSUMMED_TOTAL_TIME}
        )
        self.assertFalse(is_number_hours_min_exceeded(contract))


class CreateEmailAlertTestCase(TestCase):
    def test_there_is_contact(self):
        with SetDjangoLanguage("en"):
            operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
            company, contract, _, _ = create_project(contract1={"number_hours": 10}, company={"contact": operator})
            MaintenanceIssueFactory(company=company, contract=contract, number_minutes=20)
            manager = ManagerUserFactory(
                email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
            )
            contract.recipient = manager
            contract.save()

            email = create_email_alert(contract)
            self.assertEqual("company HyMaintenance, there are 9h40 left on your Maintenance contract", email.subject)
            self.assertEqual(
                """Hello Cave Johnson,

There are 9h40 hours left on you Maintenance contract.
Please contact gordon.freeman@blackmesa.com to add credits on your contract.

company team""",
                email.body,
            )
            self.assertEqual([manager.email], email.to)
            self.assertEqual(operator.email, email.from_email)

    def test_there_is_not_contact(self):
        with SetDjangoLanguage("en"):
            company, contract, _, _ = create_project(contract1={"number_hours": 10})
            MaintenanceIssueFactory(company=company, contract=contract, number_minutes=20)
            manager = ManagerUserFactory(
                email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
            )
            contract.recipient = manager
            contract.save()

            email = create_email_alert(contract)
            self.assertEqual("company HyMaintenance, there are 9h40 left on your Maintenance contract", email.subject)
            self.assertEqual(
                """Hello Cave Johnson,

There are 9h40 hours left on you Maintenance contract.
Please contact company@email.com to add credits on your contract.

company team""",
                email.body,
            )
            self.assertEqual([manager.email], email.to)
            general_info = GeneralInformation.objects.all().first()
            self.assertEqual(general_info.email, email.from_email)


class SendEmailAlertTestCase(TestCase):
    def setUp(self):
        self.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.company, self.contract, _, _ = create_project(
            contract1={
                "number_hours": 20,
                "number_hours_min": 10,
                "total_type": AVAILABLE_TOTAL_TIME,
                "email_alert": True,
            }
        )
        self.channel = IncomingChannelFactory()
        self.consumer = MaintenanceConsumerFactory(company=self.company)
        self.manager = ManagerUserFactory(
            email="cave.johnson@aperture-science.com", first_name="Cave", last_name="Johnson", password="azerty"
        )
        self.contract.recipient = self.manager
        self.contract.save()

    def __get_dict_for_post(self, subject, description):
        return {
            "consumer_who_ask": self.consumer.pk,
            "user_who_fix": self.user.pk,
            "incoming_channel": self.channel.pk,
            "subject": subject,
            "date": now().date(),
            "contract": self.contract.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 11,
        }

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_if_email_alert_is_sended_when_minimum_is_reached(self):
        subject = "subject of the issue"
        description = None
        dict_for_post = self.__get_dict_for_post(subject, description)

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertNotEqual(0, len(mail.outbox))

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_if_email_alert_is_not_sended_when_minimum_is_not_reached(self):
        subject = "subject of the issue"
        description = None
        dict_for_post = self.__get_dict_for_post(subject, description)
        dict_for_post["duration"] = 9

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        self.assertEqual(0, len(mail.outbox))
