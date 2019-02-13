from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from ...forms.credit import MaintenanceCreditCreateForm
from ...forms.credit import MaintenanceCreditUpdateForm
from ...models import MaintenanceCredit
from ..factories import MaintenanceCreditFactory
from ..factories import create_project


class MaintenanceCreditCreateFormTestCase(TestCase):
    def setUp(self):
        self.company, self.contract, _, _ = create_project(contract1={"credit_counter": True})

    def test_create_form_maintenance_type_initial_values(self):
        form = MaintenanceCreditCreateForm(company=self.company)
        self.assertEqual(8, form.get_initial_for_field(form.fields["hours_number"], "hours_number"))

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceCreditCreateForm(company=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"contract": [expected], "hours_number": [expected]})

    def test_create_credit_with_create_form(self):
        self.assertEqual(20, self.contract.number_hours)
        self.assertEqual(1, MaintenanceCredit.objects.filter(company=self.company, contract=self.contract).count())
        hours_number = 10
        form = MaintenanceCreditCreateForm(
            company=self.company, data={"hours_number": hours_number, "contract": self.contract.pk}
        )
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.contract.refresh_from_db()
        self.assertEqual(30, self.contract.number_hours)
        self.assertEqual(2, MaintenanceCredit.objects.filter(company=self.company, contract=self.contract).count())


class MaintenanceCreditUpdateFormTestCase(TestCase):
    def test_update_credit_with_update_form(self):
        company, c1, c2, _ = create_project(contract1={"credit_counter": True}, contract2={"credit_counter": True})
        credit = MaintenanceCreditFactory(company=company, contract=c1)
        hours_number = 10
        form = MaintenanceCreditUpdateForm(instance=credit, data={"hours_number": hours_number, "contract": c2.pk})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        updated_credit = MaintenanceCredit.objects.get(pk=credit.pk)
        self.assertEqual(hours_number, updated_credit.hours_number)
        self.assertEqual(c2, updated_credit.contract)
        c2.refresh_from_db()
        self.assertEqual(30, c2.number_hours)
