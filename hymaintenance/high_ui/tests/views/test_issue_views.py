import os
from shutil import rmtree
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory
from tempfile import TemporaryFile
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import IncomingChannelFactory
from maintenance.tests.factories import MaintenanceConsumerFactory
from maintenance.tests.factories import MaintenanceContractFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project
from maintenance.tests.factories import get_default_maintenance_type


def create_temporary_file(content=b"I am not empty", directory=None):
    tmp_file = NamedTemporaryFile(dir=directory, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


class IssueCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company, contract1, _contract2, _contract3 = create_project(
            company={"name": os.path.basename(cls.tmp_directory.name)}
        )
        cls.user.operator_for.add(cls.company)
        cls.maintenance_type = contract1.maintenance_type
        MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def __get_dict_for_post(self, subject, description):
        return {
            "consumer_who_ask": self.consumer.pk,
            "user_who_fix": self.user.pk,
            "incoming_channel": self.channel.pk,
            "subject": subject,
            "date": now().date(),
            "maintenance_type": self.maintenance_type.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 2,
        }

    def test_i_can_get_a_form_to_create_a_new_issue(self):
        self.client.login(username=self.user.email, password="azerty")
        response = self.client.get(
            reverse("high_ui:project-create_issue", kwargs={"company_name": self.company.slug_name}), follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_i_can_post_a_form_to_create_a_new_issue(self):
        subject = "Subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.user.email, password="azerty")
        response = self.client.post(
            reverse("high_ui:project-create_issue", kwargs={"company_name": self.company.slug_name}),
            self.__get_dict_for_post(subject, description),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.company.get_absolute_url())
        self.assertEqual(
            1,
            MaintenanceIssue.objects.filter(
                company=self.company,
                consumer_who_ask=self.consumer,
                user_who_fix=self.user,
                incoming_channel=self.channel,
                subject=subject,
                maintenance_type=self.maintenance_type,
                number_minutes=120,
                description=description,
            ).count(),
        )

    def test_i_can_post_a_form_to_create_a_new_issue_with_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "Subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)
        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            self.client.login(username=self.user.email, password="azerty")
            response = self.client.post(
                reverse("high_ui:project-create_issue", kwargs={"company_name": self.company.slug_name}),
                dict_for_post,
                follow=True,
            )

            issues = MaintenanceIssue.objects.filter(company=self.company)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
            self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())
            self.assertRedirects(response, self.company.get_absolute_url())

    def test_operator_cannot_create_a_new_issue_for_a_company_he_doesnt_manage(self):
        company = CompanyFactory()

        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            reverse("high_ui:project-create_issue", kwargs={"company_name": company.slug_name}),
            dict_for_post,
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_i_cannot_get_a_form_to_create_a_new_issue_where_i_am_not_operator(self):
        user = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        self.client.login(username=user.email, password="azerty")
        response = self.client.get(
            reverse("high_ui:project-create_issue", kwargs={"company_name": self.company.slug_name}), follow=True
        )
        self.assertEqual(response.status_code, 404)


class IssueUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company = CompanyFactory(name=os.path.basename(cls.tmp_directory.name))
        cls.maintenance_type = get_default_maintenance_type()
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)
        cls.contract = MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)

    def setUp(self):
        self.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.issue = MaintenanceIssueFactory(company=self.company, maintenance_type=self.maintenance_type)
        self.url_post = reverse(
            "high_ui:project-update_issue",
            kwargs={
                "company_name": self.issue.company.slug_name,
                "company_issue_number": self.issue.company_issue_number,
            },
        )

    def tearDown(self):
        rmtree(
            os.path.join(
                settings.MEDIA_ROOT, "upload/", self.company.slug_name, "issue-" + str(self.issue.company_issue_number)
            ),
            ignore_errors=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_i_can_get_a_form_to_update_a_issue(self):
        self.user.operator_for.add(self.company)
        self.client.login(username=self.user.email, password="azerty")
        response = self.client.get(self.url_post, follow=True)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_modify_a_issue(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        self.user.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.url_post,
            {
                "consumer_who_ask": self.consumer.pk,
                "user_who_fix": self.user.pk,
                "incoming_channel": self.channel.pk,
                "subject": subject,
                "date": "2017-03-22",
                "maintenance_type": self.maintenance_type.pk,
                "description": description,
                "duration_type": "hours",
                "duration": 2,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            expected_url=reverse(
                "high_ui:project-issue_details",
                kwargs={
                    "company_name": self.issue.company.slug_name,
                    "company_issue_number": self.issue.company_issue_number,
                },
            ),
        )
        self.assertEqual(
            1,
            MaintenanceIssue.objects.filter(
                company=self.company,
                consumer_who_ask=self.consumer,
                user_who_fix=self.user,
                incoming_channel=self.channel,
                subject=subject,
                maintenance_type=self.maintenance_type,
                number_minutes=120,
                description=description,
            ).count(),
        )

    def test_operator_cannot_modify_a_issue_of_company_he_doesnt_manage(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.url_post,
            {
                "consumer_who_ask": self.consumer.pk,
                "user_who_fix": self.user.pk,
                "incoming_channel": self.channel.pk,
                "subject": subject,
                "date": "2017-03-22",
                "maintenance_type": self.maintenance_type.pk,
                "description": description,
                "duration_type": "hours",
                "duration": 2,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 404)

    def test_i_cannot_post_and_form_to_modify_a_issue_unlog(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        response = self.client.post(
            self.url_post,
            {
                "consumer_who_ask": self.consumer.pk,
                "user_who_fix": self.user.pk,
                "incoming_channel": self.channel.pk,
                "subject": subject,
                "date": "2017-03-22",
                "maintenance_type": self.maintenance_type.pk,
                "description": description,
                "duration_type": "hours",
                "duration": 2,
            },
            follow=True,
        )
        url_login = reverse("login")
        self.assertRedirects(response, expected_url=f"{url_login}?next={self.url_post}")
        self.assertEqual(
            0,
            MaintenanceIssue.objects.filter(
                company=self.company,
                consumer_who_ask=self.consumer,
                user_who_fix=self.user,
                incoming_channel=self.channel,
                subject=subject,
                maintenance_type=self.maintenance_type,
                number_minutes=120,
                description=description,
            ).count(),
        )


class IssueDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tmp_directory = TemporaryDirectory(
            prefix="issue-details-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company, contract1, _contract2, _contract3 = create_project(
            company={"name": os.path.basename(cls.tmp_directory.name)}
        )
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=cls.company)
        cls.user.operator_for.add(cls.company)
        cls.maintenance_type = contract1.maintenance_type
        MaintenanceContractFactory(company=cls.company, maintenance_type=cls.maintenance_type)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, maintenance_type=self.maintenance_type)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_user_can_seen_issues_of_this_company(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(
            reverse(
                "high_ui:project-issue_details",
                kwargs={
                    "company_name": self.company.slug_name,
                    "company_issue_number": self.issue.company_issue_number,
                },
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_seen_issues_of_other_company(self):
        other_company = CompanyFactory()
        MaintenanceContractFactory(company=other_company, maintenance_type=self.maintenance_type)
        issue = MaintenanceIssueFactory(company=other_company, maintenance_type=self.maintenance_type)

        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(
            reverse(
                "high_ui:project-issue_details",
                kwargs={"company_name": issue.company.slug_name, "company_issue_number": issue.company_issue_number},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_seen_issues_of_other_company(self):
        black_mesa = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        MaintenanceContractFactory(company=black_mesa, maintenance_type=maintenance_type)
        issue = MaintenanceIssueFactory(company=black_mesa, maintenance_type=maintenance_type)
        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(
            reverse(
                "high_ui:project-issue_details",
                kwargs={"company_name": issue.company.slug_name, "company_issue_number": issue.company_issue_number},
            )
        )
        self.assertEqual(response.status_code, 403)

    def test_user_can_seen_issue_context_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.context_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(
                reverse(
                    "high_ui:project-issue_details",
                    kwargs={
                        "company_name": self.company.slug_name,
                        "company_issue_number": self.issue.company_issue_number,
                    },
                )
            )

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.context_description_file.name))

    def test_user_can_seen_issue_resolution_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.resolution_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(
                reverse(
                    "high_ui:project-issue_details",
                    kwargs={
                        "company_name": self.company.slug_name,
                        "company_issue_number": self.issue.company_issue_number,
                    },
                )
            )

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.resolution_description_file.name))
