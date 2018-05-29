
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, ManagerUserFactory, OperatorUserFactory
from maintenance.models import MaintenanceConsumer
from maintenance.tests.factories import MaintenanceConsumerFactory


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
        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertEqual(1, MaintenanceConsumer.objects.filter(company=self.company, name=name).count())


class UpdateMaintenanceConsumersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                   password="azerty")
        cls.company = CompanyFactory()
        user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_update_company_consumers_form(self):
        response = self.client.get(reverse('high_ui:company-change_consumers',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_get_update_company_consumers_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(reverse('high_ui:company-change_consumers',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_archive_company_consumers_form(self):
        consumer1 = MaintenanceConsumerFactory(is_used=True, company=self.company)
        consumer2 = MaintenanceConsumerFactory(is_used=False, company=self.company)

        response = self.client.post(reverse("high_ui:company-change_consumers",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"users": consumer2.id,
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertFalse(MaintenanceConsumer.objects.get(id=consumer1.id).is_used)
        self.assertTrue(MaintenanceConsumer.objects.get(id=consumer2.id).is_used)
