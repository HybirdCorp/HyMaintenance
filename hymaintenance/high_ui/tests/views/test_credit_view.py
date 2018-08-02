from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import create_project

from ...views.credit import CreditCreateView


class CreditCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(
            contract1={"total_type": AVAILABLE_TOTAL_TIME},
            contract2={"total_type": AVAILABLE_TOTAL_TIME},
            contract3={"total_type": CONSUMMED_TOTAL_TIME},
        )
        cls.form_url = reverse("high_ui:project-create_credit", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = CreditCreateView()
        view.request = request
        view.company = self.company
        view.object = self.company
        view.hours_step = 8
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual([8, 16, 24, 32, 40], list(context["hours_numbers"]))
        self.assertIn(self.c1, context["available_time_contracts"])
        self.assertIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_get_create_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_create_a_project(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.form_url, {"hours_number": 16, "contract": 1}, follow=True)

        self.assertRedirects(
            response, reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        )

        self.assertEqual(16, MaintenanceCredit.objects.filter(contract=1, company=self.company).first().hours_number)
