from django.test import TestCase
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.tests.factories import IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceTypeFactory

from ...forms import MaintenanceIssueCreateForm


class IssueCreateFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")

        cls.company = CompanyFactory()
        cls.maintenance_type = MaintenanceTypeFactory()
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def __get_dict_for_post(self, subject, description):
        return {"consumer_who_ask": self.consumer.pk,
                "user_who_fix": self.user.pk,
                "incoming_channel": self.channel.pk,
                "subject": subject,
                "date": now().date(),
                "maintenance_type": self.maintenance_type.pk,
                "description": description,
                "duration_type": "hours",
                "duration": 2}

    def test_when_i_bound_a_form_with_invalid_duration_type_i_have_an_error(self):

        subject = "subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration_type"] = "years"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration type: 'years'")

    def test_when_i_bound_a_form_with_invalid_duration_i_have_an_error(self):

        subject = "subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "0"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration: '0'")
