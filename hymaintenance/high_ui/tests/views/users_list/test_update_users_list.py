from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.models import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceConsumer
from maintenance.tests.factories import MaintenanceConsumerFactory

from ....views.users_list.update_users_list import OperatorUsersListUpdateView
from ....views.users_list.update_users_list import OperatorUsersListUpdateViewWithCompany


class ConsumersListUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-update_consumers", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_post_consumers_list_update_form(self):
        consumer1 = MaintenanceConsumerFactory(is_used=True, company=self.company)
        consumer2 = MaintenanceConsumerFactory(is_used=False, company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.post(self.form_url, {"users": consumer2.id}, follow=True)

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertFalse(MaintenanceConsumer.objects.get(id=consumer1.id).is_used)
        self.assertTrue(MaintenanceConsumer.objects.get(id=consumer2.id).is_used)


class ManagerUsersListUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.manager = ManagerUserFactory(company=cls.company)
        cls.form_url = reverse("high_ui:project-update_managers", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_other_company_cannot_get_update_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_company_managers_form(self):
        manager1 = ManagerUserFactory(is_active=True, company=self.company)
        manager2 = ManagerUserFactory(is_active=False, company=self.company)

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"users": manager2.id}, follow=True)

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertFalse(MaintenanceUser.objects.get(id=manager1.id).is_active)
        self.assertTrue(MaintenanceUser.objects.get(id=manager2.id).is_active)


class OperatorUsersListUpdateViewWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-update_operators", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        op1 = OperatorUserFactory(is_active=True)
        op1.operator_for.add(self.company)
        op2 = OperatorUserFactory(is_active=False)
        op2.operator_for.add(self.company)
        OperatorUserFactory(is_active=False)

        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUsersListUpdateViewWithCompany()
        view.request = request
        view.user = self.admin
        view.company = self.company

        context = view.get_context_data()
        self.assertIn("operators_number", context.keys())
        self.assertEqual(2, context["operators_number"])

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_update_company_operators_form(self):
        operator = OperatorUserFactory(is_active=True, company=self.company)
        OperatorUserFactory(is_active=True, company=self.company)

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"users": operator.id}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertEqual(list(self.company.managed_by.all()), [operator])


class OperatorUsersListUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:update_operators")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        OperatorUserFactory(is_active=True)
        OperatorUserFactory(is_active=False)

        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUsersListUpdateView()
        view.request = request
        view.user = self.admin
        view.company = self.company

        context = view.get_context_data()
        self.assertIn("active_operators_number", context.keys())
        self.assertEqual(2, context["active_operators_number"])
        self.assertIn("archived_operators_number", context.keys())
        self.assertEqual(1, context["archived_operators_number"])
        self.assertIn("archive_form", context.keys())
        self.assertIn("unarchive_form", context.keys())

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_post_archive_operators_form(self):
        op_id = 2
        op_email = "chell@aperture-science.com"
        OperatorUserFactory(email=op_email, password="azerty", is_active=True, id=op_id)

        self.client.login(username=self.admin.email, password="azerty")
        archive_url = reverse("high_ui:archive_operators")
        response = self.client.post(archive_url, {"active_operators": op_id}, follow=True)

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        operators = MaintenanceUser.objects.filter(email=op_email, is_active=False)
        self.assertEqual(1, operators.count())

    def test_post_unarchive_operators_form(self):
        op_id = 2
        op_email = "chell@aperture-science.com"
        OperatorUserFactory(email=op_email, password="azerty", is_active=False, id=op_id)

        self.client.login(username=self.admin.email, password="azerty")
        unarchive_url = reverse("high_ui:unarchive_operators")
        response = self.client.post(unarchive_url, {"inactive_operators": op_id}, follow=True)

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        operators = MaintenanceUser.objects.filter(email=op_email, is_active=True)
        self.assertEqual(1, operators.count())
