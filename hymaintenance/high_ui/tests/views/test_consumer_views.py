
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import (
    CompanyFactory, ManagerUserFactory, OperatorUserFactory, AdminUserFactory)
from maintenance.models import MaintenanceConsumer
from maintenance.tests.factories import MaintenanceConsumerFactory


class ConsumerCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com",
                         password="azerty")
        cls.company = CompanyFactory()
        cls.form_url = reverse(
            "high_ui:project-create_consumer",
            kwargs={'company_name': cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "not_used_company_slug_name"
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        test_url = reverse("high_ui:project-create_consumer",
                           kwargs={'company_name': not_used_name})
        response = self.client.get(test_url)

        self.assertEqual(response.status_code, 404)

    def test_create_maintenance_consumer_with_form(self):
        name = "Wheatley"

        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.post(self.form_url, {"name": name})

        self.assertRedirects(response, reverse('high_ui:dashboard'))
        consumers = MaintenanceConsumer.objects.filter(company=self.company,
                                                       name=name)
        self.assertEqual(1, consumers.count())


class ConsumerUpdateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com",
                         password="azerty")
        cls.company = CompanyFactory()
        cls.consumer = MaintenanceConsumerFactory(name="Chell",
                                                  company=cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_consumer",
            kwargs={'company_name': cls.company.slug_name,
                    'pk': cls.consumer.pk})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "not_used_company_slug_name"
        test_url = reverse("high_ui:project-update_consumer",
                           kwargs={'company_name': not_used_name,
                                   'pk': self.consumer.pk})
        response = self.client.get(test_url)

        self.assertEqual(response.status_code, 404)

    def test_update_maintenance_consumer_with_form(self):
        name = "Wheatley"

        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.post(self.form_url,
                                    {"name": name},
                                    follow=True)

        success_url = reverse(
            'high_ui:project-update_consumers',
            kwargs={'company_name': self.company.slug_name})
        self.assertRedirects(response, success_url)
        consumers = MaintenanceConsumer.objects.filter(pk=self.consumer.pk,
                                                       name=name)
        self.assertEqual(1, consumers.count())


class UpdateMaintenanceConsumersListTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com",
                         password="azerty")
        cls.company = CompanyFactory()
        cls.form_url = reverse(
            "high_ui:project-update_consumers",
            kwargs={'company_name': cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_post_consumers_list_update_form(self):
        consumer1 = MaintenanceConsumerFactory(is_used=True,
                                               company=self.company)
        consumer2 = MaintenanceConsumerFactory(is_used=False,
                                               company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.post(self.form_url,
                                    {"users": consumer2.id},
                                    follow=True)

        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertFalse(
            MaintenanceConsumer.objects.get(id=consumer1.id).is_used)
        self.assertTrue(
            MaintenanceConsumer.objects.get(id=consumer2.id).is_used)
