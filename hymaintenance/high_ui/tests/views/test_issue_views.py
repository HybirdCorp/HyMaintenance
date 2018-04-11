
from django.test import Client, TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import (
    IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceContractFactory, MaintenanceIssueFactory, get_default_maintenance_type
)


class IssueCreateViewTestCase(TestCase):

    def test_i_can_post_and_form_to_create_a_new_issue(self):
        user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                      password="azerty")
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        channel = IncomingChannelFactory()
        consumer = MaintenanceConsumerFactory(company=company)

        subject = "subject of the issue"
        description = "Description of the Issue"

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.post('/high_ui/issue/add/%s/' % company.pk,
                               {"consumer_who_ask": consumer.pk,
                                "user_who_fix": user.pk,
                                "incoming_channel": channel.pk,
                                "subject": subject,
                                "date": "2017-03-22",
                                "maintenance_type": maintenance_type.pk,
                                "description": description,
                                "duration_type": "hours",
                                "duration": 2}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, company.get_absolute_url())
        self.assertEqual(1, MaintenanceIssue.objects.filter(company=company,
                                                            consumer_who_ask=consumer,
                                                            user_who_fix=user,
                                                            incoming_channel=channel,
                                                            subject=subject,
                                                            maintenance_type=maintenance_type,
                                                            number_minutes=120,
                                                            description=description).count())


class IssueUpdateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.company = CompanyFactory()
        cls.maintenance_type = get_default_maintenance_type()
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)
        cls.contract = MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)
        cls.issue = MaintenanceIssueFactory(company=cls.company, maintenance_type=cls.maintenance_type)
        cls.url_post = reverse("high_ui:change_issue", args=[cls.issue.pk])

    def test_i_can_post_and_form_to_modify_a_issue(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.post(self.url_post,
                               {"consumer_who_ask": self.consumer.pk,
                                "user_who_fix": self.user.pk,
                                "incoming_channel": self.channel.pk,
                                "subject": subject,
                                "date": "2017-03-22",
                                "maintenance_type": self.maintenance_type.pk,
                                "description": description,
                                "duration_type": "hours",
                                "duration": 2}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, expected_url=reverse('high_ui:issue-details', args=[self.issue.pk]))
        self.assertEqual(1, MaintenanceIssue.objects.filter(company=self.company,
                                                            consumer_who_ask=self.consumer,
                                                            user_who_fix=self.user,
                                                            incoming_channel=self.channel,
                                                            subject=subject,
                                                            maintenance_type=self.maintenance_type,
                                                            number_minutes=120,
                                                            description=description).count())

    def test_i_cannot_post_and_form_to_modify_a_issue_unlog(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        client = Client()

        response = client.post(self.url_post,
                               {"consumer_who_ask": self.consumer.pk,
                                "user_who_fix": self.user.pk,
                                "incoming_channel": self.channel.pk,
                                "subject": subject,
                                "date": "2017-03-22",
                                "maintenance_type": self.maintenance_type.pk,
                                "description": description,
                                "duration_type": "hours",
                                "duration": 2}, follow=True)
        url_login = reverse("login")
        self.assertRedirects(response, expected_url=f"{url_login}?next={self.url_post}")
        self.assertEqual(0, MaintenanceIssue.objects.filter(company=self.company,
                                                            consumer_who_ask=self.consumer,
                                                            user_who_fix=self.user,
                                                            incoming_channel=self.channel,
                                                            subject=subject,
                                                            maintenance_type=self.maintenance_type,
                                                            number_minutes=120,
                                                            description=description).count())


class IssueDetailViewTestCase(TestCase):
    def test_user_can_seen_issues_of_this_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=first_company, maintenance_type=maintenance_type)
        issue = MaintenanceIssueFactory(company=first_company, maintenance_type=maintenance_type)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:issue-details', args=[issue.pk]))

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_seen_issues_of_other_company(self):
        first_company = CompanyFactory(name="First Company")
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        black_mesa = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=black_mesa, maintenance_type=maintenance_type)
        issue = MaintenanceIssueFactory(company=black_mesa, maintenance_type=maintenance_type)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:issue-details', args=[issue.pk]))

        self.assertEqual(response.status_code, 404)
