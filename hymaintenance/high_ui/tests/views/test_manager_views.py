
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from customers.models import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory


class CreateManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:project-create_manager", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_other_company_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

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


class UpdateManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.manager = ManagerUserFactory(company=cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_manager", kwargs={"company_name": cls.company.slug_name, "pk": cls.manager.pk}
        )
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

    def test_update_manager_profile_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Les modifications ont bien été prises en compte!"))
        managers = MaintenanceUser.objects.filter(
            email=email, first_name=first_name, last_name=last_name, company=self.company, pk=self.manager.pk
        )
        self.assertEqual(1, managers.count())

    def test_errors_on_update_manager_profile(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"first_name": "Chell", "form-mod": "profile"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_update_manager_password_with_form(self):
        password = "my safe password"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url, {"new_password1": password, "new_password2": password, "form-mod": "password"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Les modifications ont bien été prises en compte!"))
        self.assertTrue(MaintenanceUser.objects.get(pk=self.manager.pk).check_password(password))

    def test_errors_on_update_manager_password(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"new_password1": "my safe password", "new_password2": "my password", "form-mod": "password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_update_wrong_keyword_form(self):
        password = "qwertyuiop"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url, {"new_password1": password, "new_password2": password, "form-mod": "wrong"}, follow=True
        )

        self.assertEqual(response.status_code, 400)


class UpdateManagerUsersTestCase(TestCase):
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
