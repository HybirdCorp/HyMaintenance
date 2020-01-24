from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.models.user import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from high_ui.views.users.create_user import AdminUserCreateView
from high_ui.views.users.create_user import ConsumerCreateView
from high_ui.views.users.create_user import ManagerUserCreateView
from high_ui.views.users.create_user import OperatorUserCreateView
from high_ui.views.users.create_user import OperatorUserCreateViewWithCompany
from maintenance.models import MaintenanceConsumer


class ConsumerCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-create_consumer", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ConsumerCreateView()
        view.request = request
        view.user = self.admin
        view.object = MaintenanceUser
        view.company = self.company

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "not_used_company_slug_name"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        test_url = reverse("high_ui:project-create_consumer", kwargs={"company_name": not_used_name})
        response = self.client.get(test_url)

        self.assertEqual(response.status_code, 404)

    def test_create_maintenance_consumer_with_form(self):
        name = "Wheatley"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.post(self.form_url, {"name": name})

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        consumers = MaintenanceConsumer.objects.filter(company=self.company, name=name)
        self.assertEqual(1, consumers.count())


class ManagerUserCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-create_manager", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ManagerUserCreateView()
        view.request = request
        view.user = self.admin
        view.object = MaintenanceUser
        view.company = self.company

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_other_company_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_cannot_get_create_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_create_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_manager_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password1": "my safe password",
                "password2": "my safe password",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertEqual(
            1,
            MaintenanceUser.objects.filter(
                email=email, first_name=first_name, last_name=last_name, company=self.company
            ).count(),
        )


class OperatorUserCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.form_url = reverse("high_ui:create_operator")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUserCreateView()
        view.request = request
        view.user = self.admin
        view.object = MaintenanceUser

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password1": "my safe password",
                "password2": "my safe password",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("high_ui:dashboard"))

        issues = MaintenanceUser.objects.filter(email=email, first_name=first_name, last_name=last_name)
        self.assertEqual(1, issues.count())


class OperatorUserCreateViewWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-create_operator", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUserCreateViewWithCompany()
        view.request = request
        view.user = self.admin
        view.object = MaintenanceUser
        view.company = self.company

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_cannot_get_create_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password1": "my safe password",
                "password2": "my safe password",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("high_ui:dashboard"))

        issues = MaintenanceUser.objects.filter(
            email=email, first_name=first_name, last_name=last_name, company__isnull=True
        )
        self.assertEqual(1, issues.count())


class AdminUserCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="barney.calhoun@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:create_admin")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = AdminUserCreateView()
        view.request = request
        view.user = self.admin
        view.object = MaintenanceUser

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_see_the_admin_page(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_create_admin_with_form(self):
        first_name = "Gordon"
        last_name = "Freeman"
        email = "gordon.freeman@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password1": "my safe password",
                "password2": "my safe password",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:admin"))
        self.assertEqual(
            1,
            MaintenanceUser.objects.filter(
                is_superuser=True, email=email, first_name=first_name, last_name=last_name
            ).count(),
        )
