
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, OperatorUserFactory
from maintenance.models import MaintenanceConsumer


class ConsumerCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_form(self):
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "not_used_company_slug_name"
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_name': not_used_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_form_when_user_doesnt_operate_the_company(self):
        other_company = CompanyFactory()
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_name': other_company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_create_maintenance_consumer_with_form(self):
        name = "Wheatley"

        response = self.client.post(reverse("high_ui:company-add_consumer",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"name": name},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceConsumer.objects.filter(company=self.company, name=name).count())
