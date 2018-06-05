import datetime

from django.test import TestCase
from django.urls import reverse

from customers.models import Company
from customers.tests.factories import AdminUserFactory, ManagerUserFactory, OperatorUserFactory
from maintenance.forms.project import INACTIF_CONTRACT_INPUT
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME, CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import create_project


class ProjectCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com",
                         password="azerty")
        cls.form_url = reverse("high_ui:create_project")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_get_create_form(self):
        OperatorUserFactory(email="chell@aperture-science.com",
                            password="azerty")

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_create_a_project(self):
        company_name = "Black Mesa"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.form_url,
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

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertEqual(1, Company.objects.filter(name=company_name).count())
        company = Company.objects.get(name=company_name)
        contracts = MaintenanceContract.objects.filter(company_id=company.id)
        self.assertEqual(3, contracts.count())


class ProjectUpdateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        AdminUserFactory(email="gordon.freeman@blackmesa.com",
                         password="azerty")
        cls.company, _, _, _ = create_project()

        cls.form_url = reverse('high_ui:update_project',
                               kwargs={'company_name': cls.company.slug_name})
        cls.login_url = reverse('login') + "?next=" + cls.form_url

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com",
                          password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)

    def test_i_can_post_and_form_to_update_a_project(self):
        company_name = "Aperture Science"
        # No support contract
        contract1_visible = INACTIF_CONTRACT_INPUT
        contract1_total_type = 0
        contract1_number_hours = 0

        # maintenance contract, not visible for manager,
        # available total time with 80 credited hours
        contract2_visible = 0  # FALSE
        contract2_total_type = AVAILABLE_TOTAL_TIME
        contract2_number_hours = 80

        # correction contract, visible for manager, consummed total time
        contract3_visible = 1  # TRUE
        contract3_total_type = CONSUMMED_TOTAL_TIME
        contract3_number_hours = 0

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.form_url,
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

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        self.assertTrue(Company.objects.get(name=company_name, pk=self.company.pk))
        contracts = MaintenanceContract.objects.filter(company_id=self.company.id)
        self.assertEqual(3, contracts.count())


class ProjectDetailsViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.company, _, _, _ = create_project()
        cls.form_url = reverse("high_ui:project_details", args=[cls.company.slug_name])
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_when_the_company_does_not_exist(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(reverse('high_ui:project_details',
                                           args=["the-cake-is-a-lie"]))

        self.assertEqual(response.status_code, 404)

    def test_manager_can_seen_his_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com",
                           password="azerty",
                           company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_seen_his_company(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com",
                                       password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_seen_other_company(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_seen_a_company(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)
