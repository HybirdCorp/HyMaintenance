
from django.test import TestCase
from django.urls import reverse

from customers.models import Company
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory
from maintenance.models import MaintenanceConsumer


class CreateConsumerViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_form(self):
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_id': self.company.pk}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_id = Company.objects.all().count() + 1
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_id': not_used_id}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_form_when_user_doesnt_operate_the_company(self):
        other_company = CompanyFactory()
        response = self.client.get(reverse("high_ui:company-add_consumer",
                                           kwargs={'company_id': other_company.pk}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_create_maintenance_consumer_with_form(self):
        name = "Wheatley"

        response = self.client.post(reverse("high_ui:company-add_consumer",
                                            kwargs={'company_id': self.company.pk}),
                                    {"name": name},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceConsumer.objects.filter(company=self.company, name=name).count())
