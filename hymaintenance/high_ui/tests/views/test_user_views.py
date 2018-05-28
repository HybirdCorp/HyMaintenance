
from django.test import TestCase
from django.urls import reverse

from customers.models import MaintenanceUser
from customers.tests.factories import CompanyFactory, ManagerUserFactory, OperatorUserFactory


class CreateUsersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "note_existing_company_slug_name"
        response = self.client.get(reverse('high_ui:company-add_manager',
                                           kwargs={'company_name': not_used_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_get_create_manager_form(self):
        response = self.client.get(reverse('high_ui:company-add_manager',
                                           kwargs={'company_name': self.company.slug_name}),
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
        response = self.client.get(reverse('high_ui:company-add_operator',
                                           kwargs={'company_name': self.company.slug_name}),
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


class UpdateOperatorUsersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                            password="azerty",
                            id=1)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_update_operators_form(self):
        response = self.client.get(reverse('high_ui:change_operators'),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_get_update_operators_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(reverse('high_ui:change_operators'),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_archive_operators_form(self):
        op_id = 2
        op_email = "chell@aperture-science.com"
        OperatorUserFactory(email=op_email,
                            password="azerty",
                            is_active=True,
                            id=op_id)

        response = self.client.post(reverse("high_ui:archive_operators"),
                                    {"active_operators": op_id,
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=op_email,
                                                           is_active=False).count())

    def test_post_unarchive_operators_form(self):
        op_id = 2
        op_email = "chell@aperture-science.com"
        OperatorUserFactory(email=op_email,
                            password="azerty",
                            is_active=False,
                            id=op_id)

        response = self.client.post(reverse("high_ui:unarchive_operators"),
                                    {"inactive_operators": op_id,
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=op_email,
                                                           is_active=True).count())


class UpdateManagerUsersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                   password="azerty")
        cls.company = CompanyFactory()
        user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_update_company_consumers_form(self):
        response = self.client.get(reverse('high_ui:company-change_managers',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_get_update_company_consumers_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(reverse('high_ui:company-change_managers',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_archive_company_consumers_form(self):
        manager1 = ManagerUserFactory(is_active=True, company=self.company)
        manager2 = ManagerUserFactory(is_active=False, company=self.company)

        response = self.client.post(reverse("high_ui:company-change_managers",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"users": manager2.id,
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:home'))
        self.assertFalse(MaintenanceUser.objects.get(id=manager1.id).is_active)
        self.assertTrue(MaintenanceUser.objects.get(id=manager2.id).is_active)
