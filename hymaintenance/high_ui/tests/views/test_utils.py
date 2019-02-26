from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminOperatorUserFactory
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.tests.factories import create_project

from ...views.base import get_context_data_dashboard_header
from ...views.base import get_context_data_project_header
from ...views.base import get_context_previous_page
from ...views.base import get_maintenance_types


class GetMaintenanceTypesTestCase(TestCase):
    def test_get_all_maintenance_types(self):
        context = get_maintenance_types()
        self.assertEqual(3, context["maintenance_types"].count())


class PreviousPageFunctiorTestCase(TestCase):
    def test_default_previous_page(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        factory = RequestFactory()
        request = factory.get(reverse("high_ui:create_operator"))
        request.user = admin
        context = get_context_previous_page(request)

        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_previous_page(self):
        previous_page = reverse("high_ui:admin")
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        factory = RequestFactory()
        request = factory.get(reverse("high_ui:create_operator"))
        request.user = admin
        request.META["HTTP_REFERER"] = previous_page
        context = get_context_previous_page(request)

        self.assertEqual(previous_page, context["previous_page"])


class DashboardGetContextDataFunctionsTestCase(TestCase):
    def test_admin_gets_all_company_and_operators(self):
        user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        AdminOperatorUserFactory()
        OperatorUserFactory()
        ManagerUserFactory()

        _, _, _, _ = create_project()

        context = get_context_data_dashboard_header(user)
        self.assertEqual(1, context["companies_number"])
        self.assertEqual(2, context["all_types_operators_number"])

    def test_operator_dont_gets_other_company(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        company, _, _, _ = create_project()
        user.operator_for.add(company)

        _, _, _, _ = create_project()

        context = get_context_data_dashboard_header(user)
        self.assertEqual(1, context["companies_number"])

    def test_dont_gets_desactivate_operator(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", is_active=False)
        user = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        context = get_context_data_dashboard_header(user)
        self.assertEqual(1, context["all_types_operators_number"])


class ProjectGetContextDataFunctionsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(contract1={"disabled": True}, contract2={"visible": False})

    def test_admin_gets_all_enabled_contracts(self):
        user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        context = get_context_data_project_header(user, self.company)
        self.assertEqual(self.company.name, context["company"].name)
        self.assertEqual(2, context["contracts"].count())
        self.assertNotIn(self.c1, context["contracts"])
        self.assertIn(self.c2, context["contracts"])
        self.assertIn(self.c3, context["contracts"])

    def test_operator_gets_all_enabled_contracts(self):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        context = get_context_data_project_header(user, self.company)
        self.assertEqual(self.company.name, context["company"].name)
        self.assertEqual(2, context["contracts"].count())
        self.assertNotIn(self.c1, context["contracts"])
        self.assertIn(self.c2, context["contracts"])
        self.assertIn(self.c3, context["contracts"])

    def test_manager_gets_only_enabled_and_visible_contracts(self):
        user = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        context = get_context_data_project_header(user, self.company)
        self.assertEqual(self.company.name, context["company"].name)
        self.assertEqual(1, context["contracts"].count())
        self.assertNotIn(self.c1, context["contracts"])
        self.assertNotIn(self.c2, context["contracts"])
        self.assertIn(self.c3, context["contracts"])
