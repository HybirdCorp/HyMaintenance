from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceContract
from maintenance.tests.factories import create_project

from ...views.project import EmailAlertUpdateView


class EmailAlertUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, cls.contract1, cls.contract2, cls.contract3 = create_project(
            contract1={"email_alert": False, "disabled": False, "credit_counter": True},
            contract2={"email_alert": False, "disabled": True},
            contract3={"email_alert": False, "credit_counter": True, "visible": False},
        )
        cls.operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse("high_ui:project-update_email_alert", args=[cls.company.slug_name])
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.operator
        view = EmailAlertUpdateView()
        view.request = request
        view.company = self.company
        view.user = self.operator

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_can_seen_his_company_email_alert(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_manager_cannot_seen_other_company_email_alert(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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

        self.assertEqual(response.status_code, 403)

    def test_admin_can_seen_a_company_email_alert(self):
        AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_formset_displays_the_right_contract_to_staff(self):
        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(
            response, '<input type="hidden" name="form-TOTAL_FORMS" value="2" id="id_form-TOTAL_FORMS">'
        )
        self.assertContains(
            response,
            '<input type="hidden" name="form-0-id" value="{}" readonly id="id_form-0-id">'.format(self.contract1.id),
        )
        self.assertContains(
            response,
            '<input type="hidden" name="form-1-id" value="{}" readonly id="id_form-1-id">'.format(self.contract3.id),
        )

    def test_formset_displays_the_right_contract_to_manager(self):
        ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", company=self.company)
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertContains(
            response, '<input type="hidden" name="form-TOTAL_FORMS" value="1" id="id_form-TOTAL_FORMS">'
        )
        self.assertContains(
            response,
            '<input type="hidden" name="form-0-id" value="{}" readonly id="id_form-0-id">'.format(self.contract1.id),
        )

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
                "form-0-id": self.contract1.id,
                "form-0-email_alert": True,
                "form-0-credited_hours_min": hours_min,
                "form-0-recipient": manager.id,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:dashboard"))
        contract = MaintenanceContract.objects.get(id=self.contract1.id)
        self.assertTrue(contract.email_alert)
        self.assertEqual(manager, contract.recipient)
        self.assertEqual(hours_min, contract.credited_hours_min)
