from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.models.credit import MaintenanceCreditChoices
from maintenance.tests.factories import MaintenanceCreditFactory
from maintenance.tests.factories import create_project

from ...views.credit import CreditCreateView
from ...views.credit import CreditUpdateView


class CreditCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(
            contract1={"total_type": AVAILABLE_TOTAL_TIME},
            contract2={"total_type": AVAILABLE_TOTAL_TIME},
            contract3={"total_type": CONSUMMED_TOTAL_TIME},
        )
        cls.form_url = reverse("high_ui:project-create_credit", kwargs={"company_name": cls.company.slug_name})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = CreditCreateView()
        view.request = request
        view.company = self.company
        view.object = self.company
        view.hours_step = 8
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual([8, 16, 24, 32, 40], list(context["hours_numbers"]))
        self.assertIn(self.c1, context["available_time_contracts"])
        self.assertIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_get_create_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_create_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_add_credit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.form_url, {"hours_number": 16, "contract": self.c1.pk}, follow=True)

        self.assertRedirects(
            response, reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        )

        self.assertEqual(
            16, MaintenanceCredit.objects.filter(contract=self.c1.pk, company=self.company).first().hours_number
        )

    def test_create_form_has_good_contract_ids(self):
        company, c1, c2, c3 = create_project(
            company={"name": "Aperture Science"},
            contract1={"total_type": AVAILABLE_TOTAL_TIME},
            contract2={"total_type": AVAILABLE_TOTAL_TIME},
            contract3={"total_type": CONSUMMED_TOTAL_TIME},
        )
        credit = MaintenanceCreditFactory(company=company, contract=c1)
        form_url = reverse("high_ui:project-update_credit", kwargs={"company_name": company.slug_name, "pk": credit.pk})

        factory = RequestFactory()
        request = factory.get(form_url)
        request.user = self.user
        view = CreditUpdateView()
        view.request = request
        view.company = company
        view.object = company
        view.hours_step = 8
        view.user = self.user

        context = view.get_context_data()
        self.assertIn(c1, context["available_time_contracts"])
        self.assertIn(c2, context["available_time_contracts"])
        self.assertNotIn(c3, context["available_time_contracts"])
        self.assertNotIn(self.c1, context["available_time_contracts"])
        self.assertNotIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])


class CreditUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(
            contract1={"total_type": AVAILABLE_TOTAL_TIME},
            contract2={"total_type": AVAILABLE_TOTAL_TIME},
            contract3={"total_type": CONSUMMED_TOTAL_TIME},
        )

    def setUp(self):
        self.credit = MaintenanceCreditFactory(company=self.company, contract=self.c1, hours_number=8)
        self.form_url = reverse(
            "high_ui:project-update_credit", kwargs={"company_name": self.company.slug_name, "pk": self.credit.id}
        )
        self.login_url = reverse("login") + "?next=" + self.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = CreditUpdateView()
        view.request = request
        view.company = self.company
        view.object = self.company
        view.hours_step = 8
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual([8, 16, 24, 32, 40], list(context["hours_numbers"]))
        self.assertIn(self.c1, context["available_time_contracts"])
        self.assertIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_can_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_update_credit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(self.form_url, {"hours_number": 16, "contract": self.c2.pk}, follow=True)

        self.assertRedirects(
            response, reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        )
        credit = MaintenanceCredit.objects.get(pk=self.credit.pk)
        self.assertEqual(self.c2, credit.contract)
        self.assertEqual(16, credit.hours_number)

    def test_update_form_has_good_contract_ids(self):
        company, c1, c2, c3 = create_project(
            company={"name": "Aperture Science"},
            contract1={"total_type": AVAILABLE_TOTAL_TIME},
            contract2={"total_type": AVAILABLE_TOTAL_TIME},
            contract3={"total_type": CONSUMMED_TOTAL_TIME},
        )
        credit = MaintenanceCreditFactory(company=company, contract=c1)
        form_url = reverse("high_ui:project-update_credit", kwargs={"company_name": company.slug_name, "pk": credit.pk})

        factory = RequestFactory()
        request = factory.get(form_url)
        request.user = self.user
        view = CreditUpdateView()
        view.request = request
        view.company = company
        view.object = company
        view.hours_step = 8
        view.user = self.user

        context = view.get_context_data()
        self.assertIn(c1, context["available_time_contracts"])
        self.assertIn(c2, context["available_time_contracts"])
        self.assertNotIn(c3, context["available_time_contracts"])
        self.assertNotIn(self.c1, context["available_time_contracts"])
        self.assertNotIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])


class CreditDeleteViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(contract1={"total_type": AVAILABLE_TOTAL_TIME})

    def setUp(self):
        self.credit = MaintenanceCreditFactory(company=self.company, contract=self.c1, hours_number=8)
        self.form_url = reverse(
            "high_ui:project-delete_credit", kwargs={"company_name": self.company.slug_name, "pk": self.credit.id}
        )
        self.login_url = reverse("login") + "?next=" + self.form_url
        self.success_url = reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_delete_credit(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)
        self.assertEqual(self.credit, MaintenanceCredit.objects.get(pk=self.credit.pk))

    def test_operator_of_the_company_can_delete_credit(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.success_url, 301)
        self.assertEqual(0, MaintenanceCredit.objects.filter(pk=self.credit.pk).count())

    def test_operator_of_other_company_cannot_delete_credit(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)
        self.assertEqual(self.credit, MaintenanceCredit.objects.get(pk=self.credit.pk))

    def test_admin_can_delete_credit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.success_url, 301)
        self.assertEqual(0, MaintenanceCredit.objects.filter(pk=self.credit.pk).count())


class CreditChoicesUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.form_url = reverse("high_ui:admin-update_credits")
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        manager = ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_can_get_update_form(self):
        self.client.login(username=self.user.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_update_credit_choices_values(self):
        value1 = 10
        value2 = 20
        value3 = 30
        value4 = 40
        value5 = 50
        self.client.login(username=self.user.email, password="azerty")

        credit_choices = MaintenanceCreditChoices.objects.order_by("id")
        response = self.client.post(
            self.form_url,
            {
                "form-TOTAL_FORMS": "5",
                "form-INITIAL_FORMS": "5",
                "form-MAX_NUM_FORMS": "",
                "form-0-id": credit_choices[0].id,
                "form-0-value": value1,
                "form-1-id": credit_choices[1].id,
                "form-1-value": value2,
                "form-2-id": credit_choices[2].id,
                "form-2-value": value3,
                "form-3-id": credit_choices[3].id,
                "form-3-value": value4,
                "form-4-id": credit_choices[4].id,
                "form-4-value": value5,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("high_ui:admin"))

        credit_choices.all()
        self.assertEqual(value1, credit_choices[0].value)
        self.assertEqual(value2, credit_choices[1].value)
        self.assertEqual(value3, credit_choices[2].value)
        self.assertEqual(value4, credit_choices[3].value)
        self.assertEqual(value5, credit_choices[4].value)
