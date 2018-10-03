from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceContract
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.tests.factories import create_project


class EmailAlertUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.counter_name = "Experiments"
        cls.company, cls.contract, _, _ = create_project(
            contract1={
                "email_alert": False,
                "disabled": False,
                "total_type": AVAILABLE_TOTAL_TIME,
                "counter_name": cls.counter_name,
            },
            contract2={"email_alert": False, "disabled": False, "total_type": CONSUMMED_TOTAL_TIME},
            contract3={"email_alert": False, "disabled": True},
        )
        cls.operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse("high_ui:project-update_email_alert", args=[cls.company.slug_name])
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_manager_can_seen_his_company_email_alert(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company_email_alert(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_seen_his_company_email_alert(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_cannot_seen_other_company_email_alert(self):
        OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_seen_a_company_email_alert(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_formset_displays_the_right_contract(self):
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(
            response, '<input type="hidden" name="form-TOTAL_FORMS" value="1" id="id_form-TOTAL_FORMS" />'
        )
        self.assertContains(response, self.counter_name)

    def test_update_right_contract_with_the_formset(self):
        hours_min = 10
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.post(
            self.form_url,
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MAX_NUM_FORMS": "",
                "form-0-id": self.contract.id,
                "form-0-email_alert": True,
                "form-0-number_hours_min": hours_min,
                "form-0-recipient": manager.id,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        contract = MaintenanceContract.objects.get(id=self.contract.id)
        self.assertTrue(contract.email_alert)
        self.assertEqual(manager, contract.recipient)
        self.assertEqual(hours_min, contract.number_hours_min)
