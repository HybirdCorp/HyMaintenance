from django.test import TestCase
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory

from ...models import MaintenanceIssue
from ..factories import IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceIssueFactory, create_project, get_default_maintenance_type


class MaintenanceIssueTestCase(TestCase):

    def test_i_can_create_a_maintenance_issue(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        channel = IncomingChannelFactory()
        user = MaintenanceUserFactory()
        consumer = MaintenanceConsumerFactory()

        MaintenanceIssue.objects.create(company=company,
                                        consumer_who_ask=consumer,
                                        user_who_fix=user,
                                        incoming_channel=channel,
                                        subject="It's not working",
                                        date=now().date(),
                                        maintenance_type=maintenance_type,
                                        number_minutes=12,
                                        answer="Have you tried turning it off and on again?")
        self.assertEqual(1, MaintenanceIssue.objects.count())

    def test_get_hours(self):
        issue = MaintenanceIssueFactory(number_minutes=60)
        self.assertEqual(1, issue.get_hours())

    def test_who_ask(self):
        consumer = MaintenanceConsumerFactory(name="Mrs. Reynholm")
        issue = MaintenanceIssueFactory(consumer_who_ask=consumer)
        self.assertEqual("Mrs. Reynholm", issue.who_ask())

    def test_issue_number_with_one_company(self):
        company, contract1, _contract2, _contract3 = create_project()
        issue = MaintenanceIssueFactory(company=company,
                                        maintenance_type=contract1.maintenance_type)
        self.assertEqual(1, issue.company_issue_number)
        issue = MaintenanceIssueFactory(company=company,
                                        maintenance_type=contract1.maintenance_type)
        self.assertEqual(2, issue.company_issue_number)

    def test_issue_number_when_one_company_already_exists(self):
        company, contract1, _contract2, _contract3 = create_project()
        MaintenanceIssueFactory(company=company,
                                maintenance_type=contract1.maintenance_type)
        company2, contract4, _contract5, _contract6 = create_project()
        issue = MaintenanceIssueFactory(company=company2,
                                        maintenance_type=contract4.maintenance_type)
        self.assertEqual(1, issue.company_issue_number)
