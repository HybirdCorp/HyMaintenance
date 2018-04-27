import os
from shutil import rmtree
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import (
    IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceContractFactory, MaintenanceIssueFactory, create_project,
    get_default_maintenance_type
)


def create_temporary_file(content=b"I am not empty", directory=None):
    tmp_file = NamedTemporaryFile(dir=directory, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


class IssueCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.tmp_directory = TemporaryDirectory(prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, 'upload/'))
        cls.company, contract1, _contract2, _contract3 = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})
        cls.maintenance_type = contract1.maintenance_type
        MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

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
        subject = "Subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.user.email, password="azerty")
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
        test_file_content = b"I'm not empty"
        subject = "Subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)
        with create_temporary_file(test_file_content) as context_file, create_temporary_file(test_file_content) as resolution_file:
            dict_for_post['context_description_file'] = context_file
            dict_for_post['resolution_description_file'] = resolution_file

            self.client.login(username=self.user.email, password="azerty")
            response = self.client.post('/high_ui/issue/%s/add/' % self.company.slug_name,
                                        dict_for_post, follow=True)

            issues = MaintenanceIssue.objects.filter(company=self.company)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
            self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())
            self.assertRedirects(response, self.company.get_absolute_url())


class IssueUpdateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.tmp_directory = TemporaryDirectory(prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, 'upload/'))
        cls.company = CompanyFactory(name=os.path.basename(cls.tmp_directory.name))
        cls.maintenance_type = get_default_maintenance_type()
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)
        cls.contract = MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, maintenance_type=self.maintenance_type)
        self.url_post = reverse('high_ui:change_issue', kwargs={'company_name': self.issue.company.slug_name,
                                                                'company_issue_number': self.issue.company_issue_number})

    def tearDown(self):
        rmtree(os.path.join(settings.MEDIA_ROOT, "upload/", self.company.slug_name, "issue-" + str(self.issue.company_issue_number)), ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_i_can_post_and_form_to_modify_a_issue(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.url_post,
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

        response = self.client.post(self.url_post,
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

    @classmethod
    def setUpTestData(cls):
        cls.tmp_directory = TemporaryDirectory(prefix="issue-details-view-", dir=os.path.join(settings.MEDIA_ROOT, 'upload/'))
        cls.company, contract1, _contract2, _contract3 = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty", company=cls.company)
        cls.maintenance_type = contract1.maintenance_type
        MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, maintenance_type=self.maintenance_type)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_user_can_seen_issues_of_this_company(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:issue-details', kwargs={'company_name': self.company.slug_name,
                                                                            'company_issue_number': self.issue.company_issue_number}))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_seen_issues_of_other_company(self):
        other_company = CompanyFactory()
        MaintenanceContractFactory(company=other_company, maintenance_type=self.maintenance_type)
        issue = MaintenanceIssueFactory(company=other_company, maintenance_type=self.maintenance_type)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:issue-details', kwargs={'company_name': issue.company.slug_name,
                                                                            'company_issue_number': issue.company_issue_number}))
        self.assertEqual(response.status_code, 403)

    def test_user_can_seen_issue_context_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.context_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(reverse('high_ui:issue-details', kwargs={'company_name': self.company.slug_name,
                                                                                'company_issue_number': self.issue.company_issue_number}))

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.context_description_file.name))

    def test_user_can_seen_issue_resolution_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.resolution_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(reverse('high_ui:issue-details', kwargs={'company_name': self.company.slug_name,
                                                                                'company_issue_number': self.issue.company_issue_number}))

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.resolution_description_file.name))
