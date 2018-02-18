
from django.test import Client, TestCase
from django.urls import reverse

from customers.models import Company
from customers.tests.factories import CompanyFactory, MaintenanceUserFactory


class CreateCompanyViewTestCase(TestCase):
    def test_create_company_with_form(self):
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        name = "Black Mesa GG-3883 Experiment"
        name_for_site = "Black Mesa"
        maintenance_contact = "Gordon F."

        response = client.post('/high_ui/company/add/',
                               {"name": name,
                                "name_for_site": name_for_site,
                                "maintenance_contact": maintenance_contact}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Company.objects.filter(name=name, name_for_site=name_for_site, maintenance_contact=maintenance_contact).count())


class CompanyDetailViewTestCase(TestCase):
    def test_user_can_seen_this_company(self):
        first_company = CompanyFactory(name="First Company", name_for_site='First Company !!')
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[first_company.pk]))

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_seen_other_company(self):
        first_company = CompanyFactory(name="First Company", name_for_site='First Company !!')
        MaintenanceUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=first_company)
        black_mesa = CompanyFactory()
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:company-details', args=[black_mesa.pk]))

        self.assertEqual(response.status_code, 404)
