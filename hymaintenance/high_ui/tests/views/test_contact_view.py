from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.tests.factories import create_project

from ...models import GeneralInformation


class ContactViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, _, _, _ = create_project()
        cls.operator = OperatorUserFactory(
            email="chell@aperture-science.com", password="azerty", first_name="Chell", phone="00 00 00 00 00"
        )
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse("high_ui:project-contact", args=[cls.company.slug_name])
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_can_seen_his_company_contact(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company_contact(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_seen_his_company_contact(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_seen_other_company_contact(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_seen_a_company_contact(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_contact_info_is_displayed(self):
        self.company.contact = self.operator
        self.company.save()

        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(response, self.operator.first_name)
        self.assertContains(response, self.operator.email)
        self.assertContains(response, self.operator.phone)

    def test_general_info_is_displayed(self):
        self.company.contact = None
        self.company.save()
        general_info = GeneralInformation.objects.all().first()

        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(response, general_info.name)
        self.assertContains(response, general_info.email)
        self.assertContains(response, general_info.phone)
