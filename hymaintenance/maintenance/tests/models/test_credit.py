from django.test import TestCase
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory

from ...models import MaintenanceCredit
from ..factories import MaintenanceTypeFactory


class MaintenanceCreditTestCase(TestCase):

    def test_i_can_create_a_maintenance_credit(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceTypeFactory()
        MaintenanceCredit.objects.create(company=company,
                                         date=now(),
                                         maintenance_type=maintenance_type,
                                         hours_number=40
                                         )
        self.assertEqual(1, MaintenanceCredit.objects.count())
