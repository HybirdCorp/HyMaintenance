
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from high_ui.views.general_information import GeneralInformationUpdateView

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from ...models import GeneralInformation


class GeneralInformationUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="barney.calhoun@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:update_infos")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = GeneralInformationUpdateView()
        view.request = request
        view.user = self.admin
        view.object = GeneralInformation.objects.all().first()

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_see_update_general_info_form(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_see_update_general_info_form(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_see_update_general_info_form(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_update_general_information_with_form(self):
        name = "Aperture Science"
        email = "contact@aperture-science.com"
        address = "the secret postal address"
        phone = "00 00 00 00 00"
        website = "https://aperture-science.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"name": name, "address": address, "email": email, "phone": phone, "website": website},
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:admin"))
        infos = GeneralInformation.objects.all().first()
        self.assertEqual(name, infos.name)
        self.assertEqual(email, infos.email)
        self.assertEqual(address, infos.address)
        self.assertEqual(phone, infos.phone)
        self.assertEqual(website, infos.website)
