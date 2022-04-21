from customers.tests.factories import AdminUserFactory
from maintenance.forms.other_models import MaintenanceTypeUpdateForm
from maintenance.models import MaintenanceType

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _


class MaintenanceTypeUpdateFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

    def test_form_with_initial_args(self):
        form = MaintenanceTypeUpdateForm(initial={"maintenance_type1_name": "lala"})
        maintenance_types = MaintenanceType.objects.order_by("id")
        self.assertEqual(
            maintenance_types[0].name,
            form.get_initial_for_field(form.fields["maintenance_type1_name"], "maintenance_type1_name"),
        )
        self.assertEqual(
            maintenance_types[1].name,
            form.get_initial_for_field(form.fields["maintenance_type2_name"], "maintenance_type2_name"),
        )
        self.assertEqual(
            maintenance_types[2].name,
            form.get_initial_for_field(form.fields["maintenance_type3_name"], "maintenance_type3_name"),
        )

    def test_maintenance_type_update_form_initial_values(self):
        form = MaintenanceTypeUpdateForm()
        maintenance_types = MaintenanceType.objects.order_by("id")
        self.assertEqual(
            maintenance_types[0].name,
            form.get_initial_for_field(form.fields["maintenance_type1_name"], "maintenance_type1_name"),
        )
        self.assertEqual(
            maintenance_types[1].name,
            form.get_initial_for_field(form.fields["maintenance_type2_name"], "maintenance_type2_name"),
        )
        self.assertEqual(
            maintenance_types[2].name,
            form.get_initial_for_field(form.fields["maintenance_type3_name"], "maintenance_type3_name"),
        )

    def test_all_required_fields_by_sending_a_empty_create_form(self):
        form = MaintenanceTypeUpdateForm(data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(
            form.errors,
            {
                "maintenance_type1_name": [expected],
                "maintenance_type2_name": [expected],
                "maintenance_type3_name": [expected],
            },
        )

    def test_valid_form_to_update_maintenance_type_with_different_names(self):
        dict_for_post = {
            "maintenance_type1_name": "The cake",
            "maintenance_type2_name": "is",
            "maintenance_type3_name": "a lie.",
        }
        form = MaintenanceTypeUpdateForm(data=dict_for_post)

        is_valid = form.is_valid()
        self.assertTrue(is_valid)

        form.update_maintenance_types_names()
        self.assertEqual("The cake", MaintenanceType.objects.all().order_by("id")[0].name)
        self.assertEqual("is", MaintenanceType.objects.order_by("id")[1].name)
        self.assertEqual("a lie.", MaintenanceType.objects.order_by("id")[2].name)

    def test_valid_form_to_update_maintenance_type_with_same_names(self):
        maintenance_types = MaintenanceType.objects.all().order_by("id")
        dict_for_post = {
            "maintenance_type1_name": maintenance_types[0].name,
            "maintenance_type2_name": maintenance_types[1].name,
            "maintenance_type3_name": maintenance_types[2].name,
        }
        form = MaintenanceTypeUpdateForm(data=dict_for_post)

        is_valid = form.is_valid()
        self.assertTrue(is_valid)

        form.update_maintenance_types_names()
        self.assertEqual(maintenance_types[0].name, MaintenanceType.objects.all().order_by("id")[0].name)
        self.assertEqual(maintenance_types[1].name, MaintenanceType.objects.order_by("id")[1].name)
        self.assertEqual(maintenance_types[2].name, MaintenanceType.objects.order_by("id")[2].name)
