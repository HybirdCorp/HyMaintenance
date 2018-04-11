from django.test import TestCase
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory

from ...models import MaintenanceIssue
from ..factories import IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceIssueFactory, get_default_maintenance_type


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
