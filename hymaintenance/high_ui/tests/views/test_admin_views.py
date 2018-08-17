from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from customers.models.user import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_url = reverse("high_ui:admin")
        cls.login_url = reverse("login") + "?next=" + cls.page_url

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_user_can_see_the_admin_page(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 200)


class AdminCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="barney.calhoun@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:create_admin")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

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


class AdminUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="barney.calhoun@blackmesa.com", password="azerty")
        cls.modified_admin = AdminUserFactory(email="chell@aperture-science.com")
        cls.form_url = reverse("high_ui:update_admin", kwargs={"pk": cls.modified_admin.pk})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

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
            {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Les modifications ont bien été prises en compte!"))
        self.assertEqual(email, MaintenanceUser.objects.get(pk=self.modified_admin.pk).email)
