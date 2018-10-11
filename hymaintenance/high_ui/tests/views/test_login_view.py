from django.test import TestCase
from django.urls import reverse

from maintenance.tests.factories import create_project

from ...models import GeneralInformation


class LoginViewTestCase(TestCase):
    def test_general_info_is_displayed(self):
        self.company, _, _, _ = create_project()
        self.login_url = reverse("login")

        self.company.contact = None
        self.company.save()
        general_info = GeneralInformation.objects.all().first()

        response = self.client.get(self.login_url)

        self.assertContains(response, general_info.name)
        self.assertContains(response, general_info.email)
        self.assertContains(response, general_info.phone)
