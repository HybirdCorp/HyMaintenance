from django.test import TestCase
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceIssueFactory, MaintenanceTypeFactory

from ...forms import MaintenanceIssueCreateForm, MaintenanceIssueUpdateForm, duration_in_minutes


class DurationFunctionTestCase(TestCase):

    def test_when_i_pass_hours_duration_time(self):
        self.assertEqual(60, duration_in_minutes(1, "hours"))

    def test_when_i_pass_minutes_duration_time(self):
        self.assertEqual(60, duration_in_minutes(60, "minutes"))


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

    def test_when_i_bound_a_create_form_with_invalid_duration_type_i_have_an_error(self):

        subject = "subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration_type"] = "years"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration type: 'years'")

    def test_when_i_bound_a_create_form_with_invalid_duration_i_have_an_error(self):

        subject = "subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "0"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration: '0'")


class IssueUpdateFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")

        cls.company = CompanyFactory()
        cls.maintenance_type = MaintenanceTypeFactory()
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)
        cls.issue = MaintenanceIssueFactory(company=cls.company)

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

    def test_when_i_bound_a_update_form_with_invalid_duration_type_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration_type"] = "years"

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration type: 'years'")

    def test_when_i_bound_a_update_form_with_invalid_duration_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "0"

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertEqual(form.errors['duration'].as_text(), "* Invalid duration: '0'")

    def test_when_the_forum_is_valid_if_creates_instance(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        is_valid = form.is_valid()
        form.save()
        self.assertTrue(is_valid)
        self.assertEqual(0, len(form.errors))
        self.assertEqual(1, MaintenanceIssue.objects.filter(company=self.company,
                                                            consumer_who_ask=self.consumer,
                                                            user_who_fix=self.user,
                                                            incoming_channel=self.channel,
                                                            subject=subject,
                                                            maintenance_type=self.maintenance_type,
                                                            number_minutes=120,
                                                            description=description).count())
