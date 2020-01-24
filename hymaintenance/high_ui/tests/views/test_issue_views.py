import os
from shutil import rmtree
from tempfile import TemporaryDirectory
from tempfile import TemporaryFile
from urllib.parse import urljoin

from django.conf import settings
from django.core.files import File
from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import IncomingChannelFactory
from maintenance.tests.factories import MaintenanceConsumerFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project
from toolkit.tests import create_temporary_file
from toolkit.tests import create_temporary_image

from ...views.issue import IssueCreateView
from ...views.issue import IssueListUnarchiveView
from ...views.issue import IssueUpdateView
from ..utils import SetDjangoLanguage


class IssueCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )

        cls.company, cls.contract, _, _ = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

        cls.form_url = reverse("high_ui:project-create_issue", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def __get_dict_for_post(self, subject, description):
        return {
            "consumer_who_ask": self.consumer.pk,
            "incoming_channel": self.channel.pk,
            "subject": subject,
            "date": now().date(),
            "contract": self.contract.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 2,
        }

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = IssueCreateView()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = MaintenanceIssue

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_post_a_form_to_create_a_new_issue(self):
        subject = "Subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, self.__get_dict_for_post(subject, description), follow=True)

        self.assertRedirects(response, self.company.get_absolute_url())

        issues = MaintenanceIssue.objects.filter(
            company=self.company,
            consumer_who_ask=self.consumer,
            incoming_channel=self.channel,
            subject=subject,
            contract=self.contract,
            number_minutes=120,
            description=description,
        )

        self.assertEqual(1, issues.count())

    def test_i_can_post_a_form_to_create_a_new_issue_with_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "Subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        f1 = create_temporary_file(test_file_content)
        f2 = create_temporary_file(test_file_content)
        with f1 as context_file, f2 as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(self.form_url, dict_for_post, follow=True)

            issues = MaintenanceIssue.objects.filter(company=self.company)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
            self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())
            self.assertRedirects(response, self.company.get_absolute_url())

    def test_there_are_attachment_reset_buttons(self):
        self.client.login(username=self.admin.email, password="azerty")
        with SetDjangoLanguage("en"):
            response = self.client.get(self.form_url, follow=True)
            self.assertContains(
                response,
                '<input type="button" id="id_context_description_file-reset" value="Reset" style="float: right;"/>',
            )
            self.assertContains(
                response,
                '<input type="button" id="id_resolution_description_file-reset" value="Reset" style="float: right;"/>',
            )


class IssueUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )

        cls.company, cls.contract, _, _ = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def setUp(self):

        self.issue = MaintenanceIssueFactory(company=self.company, contract=self.contract)
        self.form_url = reverse(
            "high_ui:project-update_issue",
            kwargs={
                "company_name": self.issue.company.slug_name,
                "company_issue_number": self.issue.company_issue_number,
            },
        )

        self.login_url = reverse("login") + "?next=" + self.form_url

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

    def __get_dict_for_post(self, subject, description):
        return {
            "consumer_who_ask": self.consumer.pk,
            "incoming_channel": self.channel.pk,
            "subject": subject,
            "date": "2017-03-22",
            "contract": self.contract.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 2,
        }

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = IssueUpdateView()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = self.issue

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_get_form_of_archived_issue(self):
        self.issue.archive()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 404)

    def test_admin_cannot_update_archived_issue(self):
        self.issue.archive()
        subject = "subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.admin.email, password="azerty")

        response = self.client.post(self.form_url, self.__get_dict_for_post(subject, description), follow=True)

        self.assertEqual(response.status_code, 404)

    def test_admin_update_a_issue(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        self.client.login(username=self.admin.email, password="azerty")

        response = self.client.post(self.form_url, self.__get_dict_for_post(subject, description), follow=True)

        self.assertEqual(response.status_code, 200)
        success_url = reverse(
            "high_ui:project-issue_details",
            kwargs={
                "company_name": self.issue.company.slug_name,
                "company_issue_number": self.issue.company_issue_number,
            },
        )
        self.assertRedirects(response, expected_url=success_url)
        issues = MaintenanceIssue.objects.filter(
            company=self.company,
            consumer_who_ask=self.consumer,
            incoming_channel=self.channel,
            subject=subject,
            contract=self.contract,
            number_minutes=120,
            description=description,
        )
        self.assertEqual(1, issues.count())

    def test_there_are_attachment_reset_buttons(self):
        self.client.login(username=self.admin.email, password="azerty")
        with SetDjangoLanguage("en"):
            response = self.client.get(self.form_url, follow=True)
            self.assertContains(
                response,
                '<input type="button" id="id_context_description_file-reset" value="Reset" style="float: right;"/>',
            )
            self.assertContains(
                response,
                '<input type="button" id="id_resolution_description_file-reset" value="Reset" style="float: right;"/>',
            )

    def test_there_are_attachment_delete_checkbox(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.context_description_file.save(test_file_name, File(tmp_file), save=True)
            self.issue.resolution_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.get(self.form_url, follow=True)
            self.assertContains(
                response,
                '<input type="checkbox" name="context_description_file-clear" id="context_description_file-clear_id" />',  # noqa : E501
            )
            self.assertContains(
                response,
                '<input type="checkbox" name="resolution_description_file-clear" id="resolution_description_file-clear_id" />',  # noqa : E501
            )


class IssueDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.tmp_directory = TemporaryDirectory(
            prefix="issue_details-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company, cls.contract, _, _ = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})

        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, contract=self.contract)
        self.view_url = reverse(
            "high_ui:project-issue_details",
            kwargs={"company_name": self.company.slug_name, "company_issue_number": self.issue.company_issue_number},
        )
        self.login_url = reverse("login") + "?next=" + self.view_url

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.view_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_can_see_issue_details(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_the_company_can_see_issue_details(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_see_issue_details(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_see_issue_details(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_cannot_see_archived_issue_details(self):
        self.issue.archive()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 404)

    def test_user_can_see_issue_context_attachment_of_this_company(self):

        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.context_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.get(self.view_url)

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.context_description_file.name))

    def test_user_can_see_issue_resolution_attachment_of_this_company(self):
        test_file_name = "the_cake.lie"
        with TemporaryFile() as tmp_file:
            self.issue.resolution_description_file.save(test_file_name, File(tmp_file), save=True)

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.get(self.view_url)

            self.assertContains(response, test_file_name)
            self.assertContains(response, urljoin(settings.MEDIA_URL, self.issue.resolution_description_file.name))

    def test_admin_can_see_modify_issue_button(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.view_url)

        self.assertContains(response, _("Modify"))

    def test_operator_can_see_modify_issue_button(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertContains(response, _("Modify"))

    def test_manager_cannot_see_modify_issue_button(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertNotContains(response, _("Modify"))


class IssueArchiveViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.contract, _, _ = create_project()

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, contract=self.contract)
        self.view_url = reverse(
            "high_ui:project-archive_issue",
            kwargs={"company_name": self.company.slug_name, "company_issue_number": self.issue.company_issue_number},
        )
        self.login_url = reverse("login") + "?next=" + self.view_url
        self.success_url = reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.view_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_archive_issue(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(MaintenanceIssue.objects.get(pk=self.issue.pk).is_deleted)

    def test_operator_of_the_company_can_archive_issue(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertRedirects(response, self.success_url, 301)
        self.assertTrue(MaintenanceIssue.objects.get(pk=self.issue.pk).is_deleted)

    def test_operator_of_other_company_cannot_archive_issue(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(MaintenanceIssue.objects.get(pk=self.issue.pk).is_deleted)

    def test_admin_can_archive_issue(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url)

        self.assertRedirects(response, self.success_url, 301)
        self.assertTrue(MaintenanceIssue.objects.get(pk=self.issue.pk).is_deleted)


class IssueListUnunarchiveViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.contract, _, _ = create_project()
        cls.form_url = reverse("high_ui:admin-project-unarchive_issues", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def setUp(self):
        self.issue1 = MaintenanceIssueFactory(subject="archive", company=self.company, is_deleted=True)
        self.issue2 = MaintenanceIssueFactory(subject="active", company=self.company)

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = IssueListUnarchiveView()
        view.request = request
        view.user = self.admin
        view.company = self.company

        context = view.get_context_data()
        self.assertIn("issues_number", context.keys())
        self.assertEqual(1, context["issues_number"])
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_issue_unarchive_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"issues": self.issue1.pk}, follow=True)

        self.assertRedirects(response, reverse("high_ui:admin"))
        issues = MaintenanceIssue.objects.filter(is_deleted=False)
        self.assertEqual(2, issues.count())
        self.assertIn(self.issue1, issues)


class IssueHeaderTestCase(TestCase):
    def setUp(self):
        self.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.company, self.contract, _, _ = create_project()
        self.issue = MaintenanceIssueFactory(company=self.company, contract=self.contract)
        self.view_url = reverse(
            "high_ui:project-issue_details",
            kwargs={"company_name": self.company.slug_name, "company_issue_number": self.issue.company_issue_number},
        )
        self.login_url = reverse("login") + "?next=" + self.view_url

    def test_default_display(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="dashboard type-maintenance" >')
        self.assertNotContains(response, '<div class="dashboard-logo">')

    def test_dark_font_and_custom_color_and_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = True
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard dark" style="background:#000;">')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_light_font_and_custom_color_and_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = False
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard light" style="background:#000;">')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_default_color_with_logo_display(self):
        with create_temporary_image() as tmp_file:
            self.company.logo.save(os.path.basename(tmp_file.name), File(tmp_file))
            self.company.save()
            self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
            response = self.client.get(self.view_url, follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<div class="dashboard type-maintenance" >')
            self.assertContains(
                response, '<div class="dashboard-logo"><img src="{}"/></div>'.format(self.company.logo.url)
            )

    def test_light_font_and_custom_color_without_logo_display(self):
        self.company.color = "#000"
        self.company.dark_font_color = False
        self.company.save()
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.view_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="dashboard light" style="background:#000;">')
        self.assertNotContains(response, '<div class="dashboard-logo">')
