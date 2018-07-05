from django.test import TestCase

from customers.tests.factories import CompanyFactory

from ...forms.credit import MaintenanceCreditCreateForm
from ...models import MaintenanceCredit


class MaintenanceCreditModelFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def test_create_credit_with_model_form(self):
        hours_number = 10
        maintenance_type = 1
        form = MaintenanceCreditCreateForm(
            company=self.company,
            hours_number_initial=8,
            data={"hours_number": hours_number, "maintenance_type": maintenance_type},
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(
            1, MaintenanceCredit.objects.filter(company=self.company, maintenance_type=maintenance_type).count()
        )
