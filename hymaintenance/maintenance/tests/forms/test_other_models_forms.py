from customers.tests.factories import AdminUserFactory
from maintenance.forms.other_models import MaintenanceTypeNameUpdateForm
from maintenance.models import MaintenanceType

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _


class MaintenanceTypeUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

    def test_form_label_initial(self):
        maintenance_types = MaintenanceType.objects.order_by("id")
        self.assertEqual(3, maintenance_types.count())

        for count, maintenance_type in enumerate(maintenance_types):
            form = MaintenanceTypeNameUpdateForm(instance=maintenance_type)
            self.assertEqual(MaintenanceType.FORM_LABELS[count], form.fields["form_label"].initial)

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceTypeNameUpdateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"name": [expected], })
