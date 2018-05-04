
from django.test import TestCase
from django.urls import reverse

from customers.models import Company, MaintenanceUser
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory


class CreateUsersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_form_when_company_does_not_exist(self):
        not_used_id = Company.objects.all().count() + 1
        response = self.client.get(reverse('high_ui:company-add_manager',
                                           kwargs={'company_id': not_used_id}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_create_manager_form(self):
        response = self.client.get(reverse('high_ui:company-add_manager',
                                           kwargs={'company_id': self.company.id}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_manager_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = self.client.post(reverse("high_ui:company-add_manager",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"first_name": first_name,
                                     "last_name": last_name,
                                     "email": email,
                                     "password": "letmein"
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email,
                                                           first_name=first_name,
                                                           last_name=last_name,
                                                           company=self.company).count())

    def test_get_create_operator_form(self):
        response = self.client.get(reverse('high_ui:company-add_maintainer',
                                           kwargs={'company_id': self.company.id}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = self.client.post(reverse("high_ui:company-add_operator",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"first_name": first_name,
                                     "last_name": last_name,
                                     "email": email,
                                     "password": "letmein"
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email,
                                                           first_name=first_name,
                                                           last_name=last_name,
                                                           company__isnull=True).count())
