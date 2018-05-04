import datetime

from django.test import Client, TestCase

from customers.models import Company
from maintenance.forms import INACTIF_CONTRACT_INPUT
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME, CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import MaintenanceUserFactory, create_project


class ProjectCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")

    def test_i_can_get_create_form(self):
        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.get(f"/high_ui/project/add/")
        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_create_a_project(self):
        company_name = "Black Mesa"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager, available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        client = Client()
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = client.post('/high_ui/project/add/',
                               {"company_name": company_name,
                                "contract1_visible": contract1_visible,
                                "contract1_total_type": contract1_total_type,
                                "contract1_number_hours": contract1_number_hours,
                                "contract1_counter_name": "Maintenance",
                                "contract1_date": datetime.date.today(),
                                "contract2_visible": contract2_visible,
                                "contract2_total_type": contract2_total_type,
                                "contract2_number_hours": contract2_number_hours,
                                "contract2_counter_name": "Support",
                                "contract2_date": datetime.date.today(),
                                "contract3_visible": contract3_visible,
                                "contract3_total_type": contract3_total_type,
                                "contract3_number_hours": contract3_number_hours,
                                "contract3_counter_name": "Corrective",
                                "contract3_date": datetime.date.today()}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/high_ui/')
        self.assertEqual(1, Company.objects.filter(name=company_name).count())
        company = Company.objects.get(name=company_name)
        self.assertEqual(2, MaintenanceContract.objects.filter(company_id=company.id, disabled=False).count())


class ProjectUpdateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        cls.company, contract1, contract2, contract3 = create_project()
        cls.user.operator_for.add(cls.company)

    def test_i_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(f"/high_ui/project/{self.company.slug_name}/change/")
        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_update_a_project(self):
        company_name = "Black Mesa"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager, available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(f"/high_ui/project/{self.company.slug_name}/change/",
                                    {"company_name": company_name,
                                     "contract1_visible": contract1_visible,
                                     "contract1_total_type": contract1_total_type,
                                     "contract1_number_hours": contract1_number_hours,
                                     "contract1_counter_name": "Maintenance",
                                     "contract1_date": datetime.date.today(),
                                     "contract2_visible": contract2_visible,
                                     "contract2_total_type": contract2_total_type,
                                     "contract2_number_hours": contract2_number_hours,
                                     "contract2_counter_name": "Support",
                                     "contract2_date": datetime.date.today(),
                                     "contract3_visible": contract3_visible,
                                     "contract3_total_type": contract3_total_type,
                                     "contract3_number_hours": contract3_number_hours,
                                     "contract3_counter_name": "Corrective",
                                     "contract3_date": datetime.date.today()}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/high_ui/')
        self.assertEqual(1, Company.objects.filter(name=company_name).count())
        company = Company.objects.get(name=company_name)
        self.assertEqual(2, MaintenanceContract.objects.filter(company_id=company.id, disabled=False).count())
