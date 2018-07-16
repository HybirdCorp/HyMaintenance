from django.test import TestCase
from django.urls import reverse

from customers.models import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory


class UpdateAccountTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.form_url = reverse("high_ui:update_user")

    def test_manager_can_get_update_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_update_profile_form(self):
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
                "confirm_password": "azerty",
                "form-mod": "profile",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Les modifications ont bien été prises en compte!")
        self.assertEqual(self.admin.pk, MaintenanceUser.objects.get(email=email).pk)

    def test_errors_using_update_profile_form(self):
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
                "confirm_password": "qwerty",
                "form-mod": "profile",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_update_password_form(self):
        password = "qwertyuiop"
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"old_password": "azerty", "new_password1": password, "new_password2": password, "form-mod": "password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Les modifications ont bien été prises en compte!")

        self.assertTrue(MaintenanceUser.objects.get(pk=self.admin.pk).check_password(password))

    def test_update_wrong_keyword_form(self):
        password = "qwertyuiop"
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"old_password": "azerty", "new_password1": password, "new_password2": password, "form-mod": "wrong"},
            follow=True,
        )

        self.assertEqual(response.status_code, 400)

    def test_errors_using_update_password_form(self):
        password = "qwertyuiop"
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"old_password": "qwerty", "new_password1": password, "new_password2": password, "form-mod": "password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")
