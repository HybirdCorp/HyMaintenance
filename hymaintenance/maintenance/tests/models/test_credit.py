from django.test import TestCase
from django.utils.timezone import now

from ...models import MaintenanceCredit
from ..factories import create_project


class MaintenanceCreditTestCase(TestCase):
    def test_i_can_create_a_maintenance_credit(self):
        company, contract, _, _ = create_project()
        MaintenanceCredit.objects.create(company=company, date=now(), contract=contract, hours_number=40)
        self.assertEqual(1, MaintenanceCredit.objects.count())
