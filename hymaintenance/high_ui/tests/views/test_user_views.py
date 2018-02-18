
from django.test import Client, TestCase

from customers.models import MaintenanceUser
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory


class CreateUsersTestCase(TestCase):
    def test_create_maintenance_manager_with_form(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        company = CompanyFactory()

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = client.post('/high_ui/manager/add/%s/' % company.pk,
                               {"first_name": first_name,
                                "last_name": last_name,
                                "email": email,
                                "password": "letmein"
                                }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email, first_name=first_name, last_name=last_name, company=company).count())

    def test_create_maintainer_with_form(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        company = CompanyFactory()

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        first_name = "Barney"
        last_name = "Calhoun"
        email = "barney.calhoun@blackmesa.com"

        response = client.post('/high_ui/maintainer/add/%s/' % company.pk,
                               {"first_name": first_name,
                                "last_name": last_name,
                                "email": email,
                                "password": "letmein"
                                }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, MaintenanceUser.objects.filter(email=email, first_name=first_name, last_name=last_name, company__isnull=True).count())
