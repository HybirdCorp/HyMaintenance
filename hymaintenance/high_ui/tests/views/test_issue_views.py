import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from urllib.parse import urljoin

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import (
    IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceContractFactory, MaintenanceIssueFactory, get_default_maintenance_type
)


def create_temporary_file(content, directory=None):
    tmp_file = NamedTemporaryFile(dir=directory, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


class IssueCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.temp_directory = TemporaryDirectory(prefix="create-issue-view-", dir=os.path.join(*[settings.MEDIA_ROOT, 'upload/']))
        cls.company = CompanyFactory(name=os.path.basename(cls.temp_directory.name))
        cls.maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)
        cls.client = Client()

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

    def test_i_can_post_a_form_to_create_a_new_issue(self):
        self.client.login(username=self.user.email, password="azerty")
        subject = "Subject of the issue"
        description = "Description of the Issue"

        response = self.client.post('/high_ui/issue/%s/add/' % self.company.slug_name,
                                    self.__get_dict_for_post(subject, description), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.company.get_absolute_url())
        self.assertEqual(1, MaintenanceIssue.objects.filter(company=self.company,
                                                            consumer_who_ask=self.consumer,
                                                            user_who_fix=self.user,
                                                            incoming_channel=self.channel,
                                                            subject=subject,
                                                            maintenance_type=self.maintenance_type,
                                                            number_minutes=120,
                                                            description=description).count())

    def test_i_can_post_a_form_to_create_a_new_issue_with_attachments(self):
        self.client.login(username=self.user.email, password="azerty")
        subject = "Subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)
        context_file = create_temporary_file(b"I'm not empty")
        resolution_file = create_temporary_file(b"I'm not empty")
        dict_for_post['context_description_file'] = context_file
        dict_for_post['resolution_description_file'] = resolution_file

        response = self.client.post('/high_ui/issue/%s/add/' % self.company.slug_name,
                                    dict_for_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.company.get_absolute_url())
        issues = MaintenanceIssue.objects.filter(company=self.company,
                                                 consumer_who_ask=self.consumer,
                                                 user_who_fix=self.user,
                                                 incoming_channel=self.channel,
                                                 subject=subject,
                                                 maintenance_type=self.maintenance_type,
                                                 number_minutes=120,
                                                 description=description)
        self.assertEqual(1, issues.count())
        issue = issues.first()
        self.assertTrue(os.path.exists(issue.context_description_file.path))
        self.assertTrue(os.path.exists(issue.resolution_description_file.path))
        self.assertEqual(b"I'm not empty", open(issue.context_description_file.path, "rb").read())
        self.assertEqual(b"I'm not empty", open(issue.resolution_description_file.path, "rb").read())


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
        cls.url_post = reverse('high_ui:change_issue', kwargs={'company_name': cls.issue.company.slug_name,
                                                               'company_issue_number': cls.issue.company_issue_number})

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
        self.assertRedirects(response, expected_url=reverse('high_ui:issue-details', kwargs={'company_name': self.issue.company.slug_name,
                                                            'company_issue_number': self.issue.company_issue_number}))
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
        response = client.get(reverse('high_ui:issue-details', kwargs={'company_name': issue.company.slug_name,
                                                                       'company_issue_number': issue.company_issue_number}))

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
        response = client.get(reverse('high_ui:issue-details', kwargs={'company_name': issue.company.slug_name,
                                                                       'company_issue_number': issue.company_issue_number}))
        self.assertEqual(response.status_code, 403)

    def test_user_can_seen_issue_context_attachment_of_this_company(self):
        temp_directory = TemporaryDirectory(prefix="details-issue-view-", dir=os.path.join(*[settings.MEDIA_ROOT, 'upload/']))
        context_file = create_temporary_file(b"I'm not empty", temp_directory.name)
        context_file_path = os.path.join(*['upload/', os.path.basename(temp_directory.name), os.path.basename(context_file.name)])

        company = CompanyFactory(name=os.path.basename(temp_directory.name))
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=company)
        maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=company, maintenance_type=maintenance_type)
        issue = MaintenanceIssueFactory(company=company, maintenance_type=maintenance_type,
                                        context_description_file=context_file_path)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:issue-details', kwargs={'company_name': issue.company.slug_name,
                                                                       'company_issue_number': issue.company_issue_number}))

        self.assertContains(response, os.path.basename(issue.context_description_file.name))
        self.assertContains(response, urljoin(settings.MEDIA_URL, issue.context_description_file.name))

    def test_user_can_seen_issue_resolution_attachment_of_this_company(self):
        temp_directory = TemporaryDirectory(prefix="details-issue-view-", dir=os.path.join(*[settings.MEDIA_ROOT, 'upload/']))
        resolution_file = create_temporary_file(b"I'm not empty", temp_directory.name)
        resolution_file_path = os.path.join(*['upload/', os.path.basename(temp_directory.name), os.path.basename(resolution_file.name)])

        company = CompanyFactory(name=os.path.basename(temp_directory.name))
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=company)
        maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=company, maintenance_type=maintenance_type)
        issue = MaintenanceIssueFactory(company=company, maintenance_type=maintenance_type,
                                        resolution_description_file=resolution_file_path)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:issue-details', kwargs={'company_name': issue.company.slug_name,
                                                                       'company_issue_number': issue.company_issue_number}))

        self.assertContains(response, os.path.basename(issue.resolution_description_file.name))
        self.assertContains(response, urljoin(settings.MEDIA_URL, issue.resolution_description_file.name))
