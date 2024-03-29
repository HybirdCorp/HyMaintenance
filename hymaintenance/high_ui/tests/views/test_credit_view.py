from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceCredit
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from maintenance.models.credit import MaintenanceCreditChoices
from maintenance.tests.factories import MaintenanceCreditFactory
from maintenance.tests.factories import create_project

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from ...views.credit import CreditChoicesUpdateView
from ...views.credit import CreditCreateView
from ...views.credit import CreditUpdateView


class CreditCreateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(
            contract1={"credit_counter": True}, contract2={"credit_counter": True}, contract3={"credit_counter": False}
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
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual([8, 16, 24, 32, 40], list(context["hours_numbers"]))
        self.assertIn(self.c1, context["available_time_contracts"])
        self.assertIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_create_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(1, MaintenanceCredit.objects.filter(contract=self.c1.pk, company=self.company).count())
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url, {"hours_number": 16, "contract": self.c1.pk, "date": now().date()}, follow=True
        )

        self.assertRedirects(
            response, reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        )

        self.assertEqual(2, MaintenanceCredit.objects.filter(contract=self.c1.pk, company=self.company).count())

    def test_create_form_has_good_contract_ids(self):
        company, c1, c2, c3 = create_project(
            company={"name": "Aperture Science"},
            contract1={"credit_counter": True},
            contract2={"credit_counter": True},
            contract3={"credit_counter": False},
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
            contract1={"credit_counter": True}, contract2={"credit_counter": True}, contract3={"credit_counter": False}
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
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual([8, 16, 24, 32, 40], list(context["hours_numbers"]))
        self.assertIn(self.c1, context["available_time_contracts"])
        self.assertIn(self.c2, context["available_time_contracts"])
        self.assertNotIn(self.c3, context["available_time_contracts"])
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

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

    def test_get_update_form__error_when_contract_debit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        self.c1.total_type = CONSUMMED_TOTAL_TIME
        self.c1.save()
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 404)
        self.c1.total_type = AVAILABLE_TOTAL_TIME
        self.c1.save()

    def test_admin_can_post_form_to_update_credit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")

        response = self.client.post(
            self.form_url, {"hours_number": 16, "contract": self.c2.pk, "date": now().date()}, follow=True
        )

        self.assertRedirects(
            response, reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        )
        credit = MaintenanceCredit.objects.get(pk=self.credit.pk)
        self.assertEqual(self.c2, credit.contract)
        self.assertEqual(16, credit.hours_number)

    def test_update_credit__error_when_contract_debit(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        self.c1.total_type = CONSUMMED_TOTAL_TIME
        self.c1.save()

        response = self.client.post(
            self.form_url, {"hours_number": 16, "contract": self.c2.pk, "date": now().date()}, follow=True
        )
        self.assertEqual(response.status_code, 404)

        self.c1.total_type = AVAILABLE_TOTAL_TIME
        self.c1.save()

    def test_update_form_has_good_contract_ids(self):
        company, c1, c2, c3 = create_project(
            company={"name": "Aperture Science"},
            contract1={"credit_counter": True},
            contract2={"credit_counter": True},
            contract3={"credit_counter": False},
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
        cls.company, cls.c1, cls.c2, cls.c3 = create_project(contract1={"credit_counter": True})

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

        self.assertEqual(response.status_code, 403)
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

        self.assertEqual(response.status_code, 403)
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

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.user
        view = CreditChoicesUpdateView()
        view.request = request
        view.user = self.user

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_unlogged_user_cannot_see_the_page(self):
        response = self.client.get(self.form_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_get_update_form(self):
        manager = ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username=self.user.email, password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_post_form_to_update_credit_choices_values(self):
        self.client.login(username=self.user.email, password="azerty")

        credit_choices = MaintenanceCreditChoices.objects.order_by("id")
        credit_choices_number = len(credit_choices)
        dict_to_post = {
            "form-TOTAL_FORMS": credit_choices_number,
            "form-INITIAL_FORMS": credit_choices_number,
            "form-MAX_NUM_FORMS": "",
        }
        values = []
        for count, credit_choice in enumerate(credit_choices):
            value = (count + 1) * 10
            dict_to_post[f"form-{count}-id"] = credit_choice.id
            dict_to_post[f"form-{count}-value"] = value
            values.append(value)

        response = self.client.post(self.form_url, dict_to_post, follow=True)

        self.assertRedirects(response, reverse("high_ui:admin"))

        credit_choices = MaintenanceCreditChoices.objects.order_by("id")
        for count, credit_choice in enumerate(credit_choices):
            self.assertEqual(values[count], credit_choice.value)
