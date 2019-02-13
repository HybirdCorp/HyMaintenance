import datetime

from django.test import TestCase
from django.utils.timezone import now

from ...models import MaintenanceCredit
from ...models.credit import MaintenanceCreditChoices
from ..factories import create_project


class MaintenanceCreditTestCase(TestCase):
    def test_i_can_create_a_maintenance_credit(self):
        company, contract, _, _ = create_project(contract1={"credit_counter": True})
        MaintenanceCredit.objects.create(company=company, date=now(), contract=contract, hours_number=40)
        self.assertEqual(2, MaintenanceCredit.objects.count())

    def test_print_maintenance_credit(self):
        company, contract, _, _ = create_project(
            contract1={"start": datetime.date(2012, 12, 21), "credit_counter": True}
        )
        self.assertEqual(1, MaintenanceCredit.objects.count())
        self.assertEqual(
            "Black Mesa, the 21/12/2012 for Black Mesa , Maintenance and 20 hours",
            str(MaintenanceCredit.objects.all().first()),
        )

    def test_print_maintenance_credit_choices(self):
        choice = MaintenanceCreditChoices.objects.all().first()
        self.assertEqual("8", str(choice))
