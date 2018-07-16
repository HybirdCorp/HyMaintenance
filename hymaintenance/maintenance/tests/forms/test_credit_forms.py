from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from customers.tests.factories import CompanyFactory

from ...forms.credit import MaintenanceCreditCreateForm
from ...models import MaintenanceCredit


class MaintenanceCreditModelFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def test_create_form_maintenance_type_initial_values(self):
        form = MaintenanceCreditCreateForm(company=self.company, hours_number_initial=8)
        self.assertEqual(8, form.get_initial_for_field(form.fields["hours_number"], "hours_number"))

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceCreditCreateForm(company=self.company, hours_number_initial=8, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"maintenance_type": [expected], "hours_number": [expected]})

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