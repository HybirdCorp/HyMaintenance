import datetime

from django.test import TestCase
from django.utils.timezone import now

from ...models import MaintenanceCredit
from ...models.credit import MaintenanceCreditChoices
from ..factories import create_project


class MaintenanceCreditTestCase(TestCase):
    def test_i_can_create_a_maintenance_credit(self):
        company, contract, _, _ = create_project()
        MaintenanceCredit.objects.create(company=company, date=now(), contract=contract, hours_number=40)
        self.assertEqual(1, MaintenanceCredit.objects.count())

    def test_print_maintenance_credit(self):
        company, contract, _, _ = create_project(contract1={"start": datetime.date(2012, 12, 21), "number_hours": 40})
        self.assertEqual(1, MaintenanceCredit.objects.count())
        self.assertEqual(
            "Black Mesa, the 21/12/2012 for Black Mesa , Maintenance and 40 hours",
            str(MaintenanceCredit.objects.all().first()),
        )

    def test_print_maintenance_credit_choices(self):
        choice = MaintenanceCreditChoices.objects.all().first()
        self.assertEqual("8", str(choice))
