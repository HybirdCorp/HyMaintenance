import os
from tempfile import TemporaryDirectory
from tempfile import TemporaryFile

from customers.tests.factories import OperatorUserFactory
from freezegun import freeze_time

from django.conf import settings
from django.core.files import File
from django.test import TestCase
from django.utils.timezone import datetime
from django.utils.timezone import now

from ...models import MaintenanceIssue
from ..factories import IncomingChannelFactory
from ..factories import MaintenanceConsumerFactory
from ..factories import MaintenanceIssueFactory
from ..factories import create_project


class MaintenanceIssueTestCase(TestCase):
    def test_i_can_create_a_maintenance_issue(self):
        company, contract, _, _ = create_project()
        channel = IncomingChannelFactory()
        user = OperatorUserFactory()
        consumer = MaintenanceConsumerFactory()

        MaintenanceIssue.objects.create(
            company=company,
            consumer_who_ask=consumer,
            user_who_fix=user,
            incoming_channel=channel,
            subject="It's not working",
            date=now().date(),
            contract=contract,
            number_minutes=12,
            answer="Have you tried turning it off and on again?",
        )
        self.assertEqual(1, MaintenanceIssue.objects.count())

    def test_get_hours(self):
        issue = MaintenanceIssueFactory(number_minutes=60)
        self.assertEqual(1, issue.get_hours())

    def test_who_ask(self):
        consumer = MaintenanceConsumerFactory(name="Mrs. Reynholm")
        issue = MaintenanceIssueFactory(consumer_who_ask=consumer)
        self.assertEqual("Mrs. Reynholm", issue.who_ask())

    def test_who_ask_when_not_resigned(self):
        issue = MaintenanceIssueFactory(consumer_who_ask=None)
        self.assertEqual("", issue.who_ask())

    def test_issue_number_with_one_company(self):
        company, contract, _, _ = create_project()
        issue = MaintenanceIssueFactory(company=company, contract=contract)
        self.assertEqual(1, issue.company_issue_number)
        issue = MaintenanceIssueFactory(company=company, contract=contract)
        self.assertEqual(2, issue.company_issue_number)

    def test_issue_number_when_one_company_already_exists(self):
        company, contract, _, _ = create_project()
        MaintenanceIssueFactory(company=company, contract=contract)
        company2, contract2, _, _ = create_project()
        issue = MaintenanceIssueFactory(company=company2, contract=contract2)
        self.assertEqual(1, issue.company_issue_number)

    def test_upload_to_function(self):
        company, contract, _, _ = create_project()
        issue = MaintenanceIssueFactory(company=company, contract=contract)
        self.assertEqual(
            os.path.join("upload", company.slug_name, "issue-" + str(issue.company_issue_number), "context", "my_file"),
            issue._meta.get_field("context_description_file").generate_filename(issue, "my_file"),
        )
        self.assertEqual(
            os.path.join(
                "upload", company.slug_name, "issue-" + str(issue.company_issue_number), "resolution", "my_file"
            ),
            issue._meta.get_field("resolution_description_file").generate_filename(issue, "my_file"),
        )

    def test_upload_to_function_when_a_same_named_file_already_exists(self):
        tmp_directory = TemporaryDirectory(prefix="test-issue-", dir=os.path.join(settings.MEDIA_ROOT, "upload/"))
        company, contract, _, _ = create_project(company={"name": os.path.basename(tmp_directory.name)})

        issue = MaintenanceIssueFactory(company=company, contract=contract)
        with TemporaryFile() as tmp_file:
            issue.context_description_file.save("my_file", File(tmp_file), save=True)
            issue.resolution_description_file.save("my_file", File(tmp_file), save=True)
            self.assertEqual(
                os.path.join(
                    "upload", company.slug_name, "issue-" + str(issue.company_issue_number), "context", "my_file"
                ),
                issue.context_description_file.name,
            )
            self.assertEqual(
                os.path.join(
                    "upload", company.slug_name, "issue-" + str(issue.company_issue_number), "resolution", "my_file"
                ),
                issue.resolution_description_file.name,
            )

    def test_archive(self):
        issue = MaintenanceIssueFactory(consumer_who_ask=None)
        self.assertFalse(issue.is_deleted)
        issue.archive()
        self.assertTrue(MaintenanceIssue.objects.get(pk=issue.pk).is_deleted)

    def test_contract_consumed_minutes_update(self):
        company, contract, _, _ = create_project()
        self.assertEqual(0, contract.consumed_minutes)

        issue = MaintenanceIssue.objects.create(company=company, date=now(), contract=contract, number_minutes=40)
        contract.refresh_from_db()
        self.assertEqual(40, contract.consumed_minutes)

        issue.number_minutes = 80
        issue.save()
        contract.refresh_from_db()
        self.assertEqual(80, contract.consumed_minutes)

        issue.delete()
        contract.refresh_from_db()
        self.assertEqual(0, contract.consumed_minutes)

    @freeze_time("2019-04-04")
    def test_contract_consumed_minutes_update_when_old_issues(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=19, month=1, year=2021)
        company, contract, _, _ = create_project(contract1={"annual_recurrence": True, "reset_date": time1})

        MaintenanceIssue.objects.create(company=company, date=time1, contract=contract, number_minutes=40)
        MaintenanceIssue.objects.create(company=company, date=time2, contract=contract, number_minutes=20 * 60 + 40)
        contract.refresh_from_db()
        self.assertEqual(80, contract.consumed_minutes)
