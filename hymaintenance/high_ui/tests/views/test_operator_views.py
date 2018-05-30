
from django.test import TestCase
from django.urls import reverse

from customers.models import MaintenanceUser
from customers.tests.factories import CompanyFactory, ManagerUserFactory, OperatorUserFactory


class CreateOperatorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_create_operator_form(self):
        response = self.client.get(reverse('high_ui:project-create_operator',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = self.client.post(reverse("high_ui:project-create_operator",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"first_name": first_name,
                                     "last_name": last_name,
                                     "email": email,
                                     "password": "letmein"
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email,
                                                           first_name=first_name,
                                                           last_name=last_name,
                                                           company__isnull=True).count())


class UpdateOperatorWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_create_operator_form(self):
        response = self.client.get(reverse('high_ui:project-update_operator',
                                           kwargs={'company_name': self.company.slug_name,
                                                   'pk': self.operator.pk}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = self.client.post(reverse("high_ui:project-update_operator",
                                            kwargs={'company_name': self.company.slug_name,
                                                    'pk': self.operator.pk}),
                                    {"first_name": first_name,
                                     "last_name": last_name,
                                     "email": email,
                                     "password": "letmein"
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:project-update_operators',
                                               kwargs={'company_name': self.company.slug_name}))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email,
                                                           first_name=first_name,
                                                           last_name=last_name,
                                                           pk=self.operator.pk).count())


class UpdateOperatorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        cls.company = CompanyFactory()
        cls.user.operator_for.add(cls.company)
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_create_operator_form(self):
        response = self.client.get(reverse('high_ui:update_operator',
                                           kwargs={'pk': self.operator.pk}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_create_operator_with_form(self):
        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = self.client.post(reverse("high_ui:update_operator",
                                            kwargs={'pk': self.operator.pk}),
                                    {"first_name": first_name,
                                     "last_name": last_name,
                                     "email": email,
                                     "password": "letmein"
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:update_operators'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email,
                                                           first_name=first_name,
                                                           last_name=last_name,
                                                           pk=self.operator.pk).count())


class UpdateOperatorUsersTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                            password="azerty",
                            id=1)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_update_operators_form(self):
        response = self.client.get(reverse('high_ui:update_operators'),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_get_update_operators_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(reverse('high_ui:update_operators'),
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
        self.assertRedirects(response, reverse('high_ui:dashboard'))
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
        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertEqual(1, MaintenanceUser.objects.filter(email=op_email,
                                                           is_active=True).count())


class UpdateOperatorUsersWithCompanyTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                   password="azerty")
        cls.company = CompanyFactory()
        user.operator_for.add(cls.company)

    def setUp(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

    def test_get_update_company_operators_form(self):
        response = self.client.get(reverse('high_ui:project-update_operators',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_get_update_company_operators_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(reverse('high_ui:project-update_operators',
                                           kwargs={'company_name': self.company.slug_name}),
                                   follow=True)

        self.assertEqual(response.status_code, 404)

    def test_post_update_company_operators_form(self):
        operator = OperatorUserFactory(is_active=True, company=self.company)
        OperatorUserFactory(is_active=True, company=self.company)

        response = self.client.post(reverse("high_ui:project-update_operators",
                                            kwargs={'company_name': self.company.slug_name}),
                                    {"users": operator.id,
                                     }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('high_ui:dashboard'))
        self.assertEqual(list(self.company.managed_by.all()), [operator])
