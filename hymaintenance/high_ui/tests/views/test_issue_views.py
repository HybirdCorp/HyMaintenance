import os
from shutil import rmtree
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import AdminUserFactory, ManagerUserFactory, OperatorUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceIssueFactory, create_project


def create_temporary_file(content=b"I am not empty", directory=None):
    tmp_file = NamedTemporaryFile(dir=directory, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


class IssueCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com",
                                     password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-",
            dir=os.path.join(settings.MEDIA_ROOT,
                             'upload/'))

        cls.company, contract1, _, _ = create_project(
            company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.maintenance_type = contract1.maintenance_type
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

        cls.form_url = reverse(
            'high_ui:project-create_issue',
            kwargs={'company_name': cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def __get_dict_for_post(self, subject, description):
        return {"consumer_who_ask": self.consumer.pk,
                "incoming_channel": self.channel.pk,
                "subject": subject,
                "date": now().date(),
                "maintenance_type": self.maintenance_type.pk,
                "description": description,
                "duration_type": "hours",
                "duration": 2}

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com",
                            password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_post_a_form_to_create_a_new_issue(self):
        subject = "Subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            self.__get_dict_for_post(subject, description),
            follow=True)

        self.assertRedirects(response, self.company.get_absolute_url())
        issues = MaintenanceIssue.objects.filter(
            company=self.company,
            consumer_who_ask=self.consumer,
            incoming_channel=self.channel,
            subject=subject,
            maintenance_type=self.maintenance_type,
            number_minutes=120,
            description=description)

        self.assertEqual(1, issues.count())

    def test_i_can_post_a_form_to_create_a_new_issue_with_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "Subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)
        f1 = create_temporary_file(test_file_content)
        f2 = create_temporary_file(test_file_content)
        with f1 as context_file, f2 as resolution_file:
            dict_for_post['context_description_file'] = context_file
            dict_for_post['resolution_description_file'] = resolution_file

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(self.form_url,
                                        dict_for_post, follow=True)

            issues = MaintenanceIssue.objects.filter(company=self.company)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content,
                             open(issue.context_description_file.path, "rb").read())
            self.assertEqual(test_file_content,
                             open(issue.resolution_description_file.path, "rb").read())
            self.assertRedirects(response, self.company.get_absolute_url())


class IssueUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com",
                                     password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-",
            dir=os.path.join(settings.MEDIA_ROOT,
                             'upload/'))

        cls.company, contract1, _, _ = create_project(
            company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.maintenance_type = contract1.maintenance_type
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(
            company=self.company,
            maintenance_type=self.maintenance_type)
        self.form_url = reverse(
            'high_ui:project-update_issue',
            kwargs={
                'company_name': self.issue.company.slug_name,
                'company_issue_number': self.issue.company_issue_number})
        self.login_url = reverse("login") + "?next=" + self.form_url

    def tearDown(self):
        rmtree(
            os.path.join(
                settings.MEDIA_ROOT,
                "upload/",
                self.company.slug_name,
                "issue-" + str(self.issue.company_issue_number)),
            ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com",
                            password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_update_a_issue(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.admin.email, password="azerty")

        response = self.client.post(self.form_url,
                                    {"consumer_who_ask": self.consumer.pk,
                                     "incoming_channel": self.channel.pk,
                                     "subject": subject,
                                     "date": "2017-03-22",
                                     "maintenance_type": self.maintenance_type.pk,
                                     "description": description,
                                     "duration_type": "hours",
                                     "duration": 2}, follow=True)

        self.assertEqual(response.status_code, 200)
        success_url = reverse(
            'high_ui:project-issue_details',
            kwargs={'company_name': self.issue.company.slug_name,
                    'company_issue_number': self.issue.company_issue_number})
        self.assertRedirects(response,
                             expected_url=success_url)
        issues = MaintenanceIssue.objects.filter(company=self.company,
                                                 consumer_who_ask=self.consumer,
                                                 incoming_channel=self.channel,
                                                 subject=subject,
                                                 maintenance_type=self.maintenance_type,
                                                 number_minutes=120,
                                                 description=description)
        self.assertEqual(1, issues.count())


class IssueDetailViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com",
                                     password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="issue_details-view-",
            dir=os.path.join(settings.MEDIA_ROOT,
                             'upload/'))
        cls.company, contract1, _, _ = create_project(
            company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.maintenance_type = contract1.maintenance_type
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company,
                                             maintenance_type=self.maintenance_type)
        self.view_url = reverse(
            'high_ui:project-issue_details',
            kwargs={
                'company_name': self.company.slug_name,
                'company_issue_number': self.issue.company_issue_number})
        self.login_url = reverse("login") + "?next=" + self.view_url

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_manager_can_see_issue_details(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_the_company_can_see_issue_details(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_see_issue_details(self):
        OperatorUserFactory(email="chell@aperture-science.com",
                            password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.view_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_see_issue_details(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_user_can_see_issue_context_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.context_description_file.save(
                test_file_name,
                File(tmp_file),
                save=True)

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.get(self.view_url)

            self.assertContains(response, test_file_name)
            self.assertContains(
                response,
                urljoin(
                    settings.MEDIA_URL,
                    self.issue.context_description_file.name))

    def test_user_can_see_issue_resolution_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.resolution_description_file.save(
                test_file_name,
                File(tmp_file),
                save=True)

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.get(self.view_url)

            self.assertContains(response, test_file_name)
            self.assertContains(
                response,
                urljoin(
                    settings.MEDIA_URL,
                    self.issue.resolution_description_file.name))
