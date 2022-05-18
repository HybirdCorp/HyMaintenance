from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from high_ui.views.maintenance_type import MaintenanceTypeUpdateView
from maintenance.models.other_models import MaintenanceType

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse


class MaintenanceTypeUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:update_maintenance_types")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = MaintenanceTypeUpdateView()
        view.request = request
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        manager = ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username=self.user.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_update_maintenance_types_names(self):
        self.client.login(username=self.user.email, password="azerty")

        names = []
        dict_to_post = {
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "3",
            "form-MAX_NUM_FORMS": "3",
        }
        maintenance_types = MaintenanceType.objects.order_by("id")
        for count, maintenance_type in enumerate(maintenance_types):
            name = "a" * (count + 1)
            names.append(name)
            dict_to_post[f"form-{count}-name"] = name
            dict_to_post[f"form-{count}-id"] = maintenance_type.id

        response = self.client.post(self.form_url, dict_to_post, follow=True)

        self.assertRedirects(response, reverse("high_ui:admin"))

        maintenance_types = MaintenanceType.objects.order_by("id")
        for count, maintenance_type in enumerate(maintenance_types):
            self.assertEqual(names[count], maintenance_type.name)
