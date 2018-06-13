
from django.test import TestCase
from django.urls import reverse

from customers.models import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory


class CreateOperatorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-create_operator", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_cannot_get_create_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_create_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"first_name": first_name, "last_name": last_name, "email": email, "password": "letmein"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("high_ui:dashboard"))

        issues = MaintenanceUser.objects.filter(
            email=email, first_name=first_name, last_name=last_name, company__isnull=True
        )
        self.assertEqual(1, issues.count())


class UpdateOperatorWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_operator", kwargs={"company_name": cls.company.slug_name, "pk": cls.operator.pk}
        )
        cls.login_url = reverse("login") + "?next=" + cls.form_url

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

    def test_update_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"first_name": first_name, "last_name": last_name, "email": email, "password": "letmein"},
            follow=True,
        )

        success_url = reverse("high_ui:project-update_operators", kwargs={"company_name": self.company.slug_name})
        self.assertRedirects(response, success_url)
        operators = MaintenanceUser.objects.filter(
            email=email, first_name=first_name, last_name=last_name, pk=self.operator.pk
        )
        self.assertEqual(1, operators.count())


class UpdateOperatorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse("high_ui:update_operator", kwargs={"pk": cls.operator.pk})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

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

    def test_admin_can_get_update_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_update_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"first_name": first_name, "last_name": last_name, "email": email, "password": "letmein"},
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:update_operators"))
        operators = MaintenanceUser.objects.filter(
            email=email, first_name=first_name, last_name=last_name, pk=self.operator.pk
        )
        self.assertEqual(1, operators.count())


class UpdateOperatorUsersTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:update_operators")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

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


class UpdateOperatorUsersWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-update_operators", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

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
