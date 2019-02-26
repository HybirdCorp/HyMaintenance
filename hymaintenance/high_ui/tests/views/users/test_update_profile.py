from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from customers.models import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory

from ....views.users.update_profile import UserUpdateView
from ...utils import SetDjangoLanguage


class UpdateProfileTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory(name="Black Mesa")
        cls.form_url = reverse("high_ui:update_user")

    def test_manager_can_get_update_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_previous_page(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = UserUpdateView()
        view.request = request
        view.user = self.admin

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_staff_company_display_update_form_header(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            '<span class="dashboard-value"><a href="/high_ui/" class="home-link" title="{}">Black Mesa</a></span>'.format(  # noqa : E501
                _("Return to dashboard")
            ),
        )
        self.assertNotContains(response, '<span class="dashboard-title">Black Mesa</span>')
        self.assertContains(
            response,
            '<span class="dashboard-value"><a href="/high_ui/" class="home-link" title="{}">company</a></span>'.format(
                _("Return to dashboard")
            ),
        )
        self.assertContains(response, '<span class="dashboard-title">company</span>')

    def test_manager_company_display_update_form_header(self):
        user = ManagerUserFactory(email="glados@aperture-science.com", password="azerty", company=self.company)
        self.client.login(username=user.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="dashboard-value"><a href="/high_ui/" class="home-link" title="{}">Black Mesa</a></span>'.format(  # noqa : E501
                _("Return to dashboard")
            ),
        )
        self.assertContains(response, '<span class="dashboard-title">Black Mesa</span>')
        self.assertNotContains(
            response,
            '<span class="dashboard-value"><a href="/high_ui/" class="home-link" title="{}">company</a></span>'.format(
                _("Return to dashboard")
            ),
        )
        self.assertNotContains(response, '<span class="dashboard-title">company</span>')

    def test_staff_update_profile_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"
        phone = "+336 06 06 06 06"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "phone": phone,
                "confirm_password": "azerty",
                "form-mod": "profile",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Modifications have been registered!"))
        self.assertEqual(self.admin.pk, MaintenanceUser.objects.get(email=email, phone=phone).pk)

    def test_manager_update_profile_form(self):
        user = ManagerUserFactory(email="glados@aperture-science.com", password="azerty")
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        self.client.login(username=user.email, password="azerty")
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
        self.assertContains(response, _("Modifications have been registered!"))
        self.assertEqual(user.pk, MaintenanceUser.objects.get(email=email).pk)

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
        with SetDjangoLanguage("en"):
            password = "qwertyuiop"
            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {
                    "old_password": "azerty",
                    "new_password1": password,
                    "new_password2": password,
                    "form-mod": "password",
                },
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))

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
