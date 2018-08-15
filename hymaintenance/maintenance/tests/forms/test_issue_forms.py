import os
from shutil import rmtree
from tempfile import NamedTemporaryFile
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import now
from django.utils.translation import gettext as _

from customers.tests.factories import OperatorUserFactory
from high_ui.tests.utils import SetDjangoLanguage
from maintenance.models import MaintenanceIssue
from maintenance.tests.factories import IncomingChannelFactory
from maintenance.tests.factories import MaintenanceConsumerFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from ...forms.issue import MaintenanceIssueCreateForm
from ...forms.issue import MaintenanceIssueUpdateForm
from ...forms.issue import duration_in_minutes


def create_temporary_file(content=b"I am not empty", directory=None):
    tmp_file = NamedTemporaryFile(dir=directory, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


class DurationFunctionTestCase(TestCase):
    def test_when_i_pass_hours_duration_time(self):
        self.assertEqual(60, duration_in_minutes(1, "hours"))

    def test_when_i_pass_minutes_duration_time(self):
        self.assertEqual(60, duration_in_minutes(60, "minutes"))


class IssueCreateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company, cls.contract, _, _ = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})
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
            "contract": self.contract.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 2,
        }

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceIssueCreateForm(company=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "subject": [expected],
                "date": [expected],
                "contract": [expected],
                "duration": [expected],
                "duration_type": [expected],
            },
        )

    def test_when_i_bound_a_create_form_with_invalid_duration_type_i_have_an_error(self):
        with SetDjangoLanguage("en"):
            subject = "subject of the issue"
            description = "Description of the Issue"

            dict_for_post = self.__get_dict_for_post(subject, description)

            dict_for_post["duration_type"] = "years"

            form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
            self.assertFalse(form.is_valid())
            self.assertEqual(1, len(form.errors))
            expected = _("Invalid duration type: '%s'") % dict_for_post["duration_type"]
            self.assertEqual(form.errors["duration"], [expected])

    def test_when_i_bound_a_create_form_with_under_min_duration_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"

        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "0"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 1}
        self.assertEqual(form.errors["duration"], [expected])

    def test_when_i_bound_a_create_form_with_string_as_duration_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "I'm a duration"

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["duration"], [expected])

    def test_if_create_form_works_when_i_send_all_required_field(self):
        subject = "subject of the issue"
        description = None
        dict_for_post = self.__get_dict_for_post(subject, description)
        dict_for_post["user_who_fix"] = None
        dict_for_post["incoming_channel"] = None

        form = MaintenanceIssueCreateForm(company=self.company, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject)
        self.assertEqual(1, issues.count())
        self.assertEqual(self.company, issues.first().company)
        self.assertEqual(subject, issues.first().subject)
        self.assertEqual(self.contract, issues.first().contract)
        self.assertEqual(120, issues.first().number_minutes)

    def test_if_create_form_works_when_i_send_a_attachment(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as tmp_file:
            dict_for_post["context_description_file"] = tmp_file

            form = MaintenanceIssueCreateForm(
                company=self.company,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "context_file_name", dict_for_post["context_description_file"].read()
                    )
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())

    def test_if_create_form_works_when_i_send_two_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            form = MaintenanceIssueCreateForm(
                company=self.company,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "context_file_name", dict_for_post["context_description_file"].read()
                    ),
                    "resolution_description_file": SimpleUploadedFile(
                        "resolution_file_name", dict_for_post["resolution_description_file"].read()
                    ),
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(b"I'm not empty", open(issue.context_description_file.path, "rb").read())
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(b"I'm not empty", open(issue.resolution_description_file.path, "rb").read())

    def test_if_create_form_works_when_i_send_two_attachments_with_same_name(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            form = MaintenanceIssueCreateForm(
                company=self.company,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["context_description_file"].read()
                    ),
                    "resolution_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["resolution_description_file"].read()
                    ),
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
            self.assertEqual("same_file_name", os.path.basename(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())
            self.assertEqual("same_file_name", os.path.basename(issue.resolution_description_file.path))
            os.remove(issue.context_description_file.path)
            os.remove(issue.resolution_description_file.path)


class IssueUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.tmp_directory = TemporaryDirectory(
            prefix="create-issue-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company, cls.contract, _, _ = create_project(company={"name": os.path.basename(cls.tmp_directory.name)})
        cls.channel = IncomingChannelFactory()
        cls.consumer = MaintenanceConsumerFactory(company=cls.company)

    def setUp(self):
        self.issue = MaintenanceIssueFactory(company=self.company, contract=self.contract)

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
            "user_who_fix": self.user.pk,
            "incoming_channel": self.channel.pk,
            "subject": subject,
            "date": now().date(),
            "contract": self.contract.pk,
            "description": description,
            "duration_type": "hours",
            "duration": 2,
        }

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = MaintenanceIssueUpdateForm(instance=self.issue, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "subject": [expected],
                "date": [expected],
                "contract": [expected],
                "duration": [expected],
                "duration_type": [expected],
            },
        )

    def test_when_i_bound_a_update_form_with_invalid_duration_type_i_have_an_error(self):
        with SetDjangoLanguage("en"):
            subject = "subject of the issue"
            description = "Description of the Issue"
            dict_for_post = self.__get_dict_for_post(subject, description)

            dict_for_post["duration_type"] = "years"

            form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
            self.assertFalse(form.is_valid())
            self.assertEqual(1, len(form.errors))
            expected = _("Invalid duration type: '%s'") % dict_for_post["duration_type"]
            self.assertEqual(form.errors["duration"], [expected])

    def test_when_i_bound_a_update_form_with_under_min_duration_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "0"

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Ensure this value is greater than or equal to %(limit_value)s.") % {"limit_value": 1}
        self.assertEqual(form.errors["duration"].as_text(), "* %s" % expected)

    def test_when_i_bound_a_update_form_with_string_as_duration_i_have_an_error(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        dict_for_post["duration"] = "I'm a duration"

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        expected = _("Enter a whole number.")
        self.assertEqual(form.errors["duration"], [expected])

    def test_form_is_valid_when_it_updates_instance(self):
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        form = MaintenanceIssueUpdateForm(instance=self.issue, data=dict_for_post)
        is_valid = form.is_valid()
        form.save()
        self.assertTrue(is_valid)
        self.assertEqual(0, len(form.errors))
        self.assertEqual(
            1,
            MaintenanceIssue.objects.filter(
                company=self.company,
                consumer_who_ask=self.consumer,
                user_who_fix=self.user,
                incoming_channel=self.channel,
                subject=subject,
                contract=self.contract,
                number_minutes=120,
                description=description,
            ).count(),
        )

    def test_if_update_form_works_when_i_send_a_attachment(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as tmp_file:
            dict_for_post["context_description_file"] = tmp_file

            form = MaintenanceIssueUpdateForm(
                instance=self.issue,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "context_file_name", dict_for_post["context_description_file"].read()
                    )
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())

    def test_if_update_form_works_when_i_send_two_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            form = MaintenanceIssueUpdateForm(
                instance=self.issue,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "context_file_name", dict_for_post["context_description_file"].read()
                    ),
                    "resolution_description_file": SimpleUploadedFile(
                        "resolution_file_name", dict_for_post["resolution_description_file"].read()
                    ),
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())

    def test_if_update_form_works_when_i_send_two_attachment_with_same_name(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            form = MaintenanceIssueUpdateForm(
                instance=self.issue,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["context_description_file"].read()
                    ),
                    "resolution_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["resolution_description_file"].read()
                    ),
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
            self.assertEqual(1, issues.count())
            issue = issues.first()
            self.assertTrue(os.path.exists(issue.context_description_file.path))
            self.assertEqual(b"I'm not empty", open(issue.context_description_file.path, "rb").read())
            self.assertEqual("same_file_name", os.path.basename(issue.context_description_file.path))
            self.assertTrue(os.path.exists(issue.resolution_description_file.path))
            self.assertEqual(b"I'm not empty", open(issue.resolution_description_file.path, "rb").read())
            self.assertEqual("same_file_name", os.path.basename(issue.resolution_description_file.path))

    def test_if_update_form_works_when_i_modify_all_attachments(self):
        test_file_content = b"I'm not empty"
        subject = "subject of the issue"
        description = "Description of the Issue"
        dict_for_post = self.__get_dict_for_post(subject, description)

        with create_temporary_file(test_file_content) as context_file, create_temporary_file(
            test_file_content
        ) as resolution_file:
            dict_for_post["context_description_file"] = context_file
            dict_for_post["resolution_description_file"] = resolution_file

            form = MaintenanceIssueUpdateForm(
                instance=self.issue,
                data=dict_for_post,
                files={
                    "context_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["context_description_file"].read()
                    ),
                    "resolution_description_file": SimpleUploadedFile(
                        "same_file_name", dict_for_post["resolution_description_file"].read()
                    ),
                },
            )
            form.is_valid()
            form.save()

            with create_temporary_file(test_file_content) as context_file, create_temporary_file(
                test_file_content
            ) as resolution_file:
                dict_for_post["context_description_file"] = context_file
                dict_for_post["resolution_description_file"] = resolution_file

                form = MaintenanceIssueUpdateForm(
                    instance=self.issue,
                    data=dict_for_post,
                    files={
                        "context_description_file": SimpleUploadedFile(
                            "same_file_name", dict_for_post["context_description_file"].read()
                        ),
                        "resolution_description_file": SimpleUploadedFile(
                            "same_file_name", dict_for_post["resolution_description_file"].read()
                        ),
                    },
                )

                self.assertTrue(form.is_valid())
                self.assertTrue(form.save())
                issues = MaintenanceIssue.objects.filter(company=self.company, subject=subject, description=description)
                self.assertEqual(1, issues.count())
                issue = issues.first()
                self.assertTrue(os.path.exists(issue.context_description_file.path))
                self.assertEqual(test_file_content, open(issue.context_description_file.path, "rb").read())
                self.assertEqual("same_file_name", os.path.basename(issue.context_description_file.path))
                self.assertTrue(os.path.exists(issue.resolution_description_file.path))
                self.assertEqual(test_file_content, open(issue.resolution_description_file.path, "rb").read())
                self.assertEqual("same_file_name", os.path.basename(issue.resolution_description_file.path))
