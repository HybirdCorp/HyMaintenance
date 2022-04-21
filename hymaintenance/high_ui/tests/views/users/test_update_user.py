from customers.models.user import MaintenanceUser
from customers.tests.factories import AdminUserFactory
from customers.tests.factories import CompanyFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceConsumer
from maintenance.tests.factories import MaintenanceConsumerFactory

from django.test import RequestFactory
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from ....views.users.update_user import AdminUserUpdateView
from ....views.users.update_user import ConsumerUpdateView
from ....views.users.update_user import ManagerUserUpdateView
from ....views.users.update_user import OperatorUserUpdateView
from ....views.users.update_user import OperatorUserUpdateViewWithCompany
from ...utils import SetDjangoLanguage


class ConsumerUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.consumer = MaintenanceConsumerFactory(name="Chell", company=cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_consumer", kwargs={"company_name": cls.company.slug_name, "pk": cls.consumer.pk}
        )
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ConsumerUpdateView()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = self.consumer

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty", company=self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_can_get_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_operator_of_other_company_cannot_get_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.get(self.form_url)
        self.assertEqual(response.status_code, 200)

    def test_get_form_when_company_does_not_exist(self):
        not_used_name = "not_used_company_slug_name"
        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        test_url = reverse(
            "high_ui:project-update_consumer", kwargs={"company_name": not_used_name, "pk": self.consumer.pk}
        )
        response = self.client.get(test_url)

        self.assertEqual(response.status_code, 404)

    def test_update_maintenance_consumer_with_form(self):
        name = "Wheatley"

        self.client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = self.client.post(self.form_url, {"name": name}, follow=True)

        success_url = reverse("high_ui:project-update_consumers", kwargs={"company_name": self.company.slug_name})
        self.assertRedirects(response, success_url)
        consumers = MaintenanceConsumer.objects.filter(pk=self.consumer.pk, name=name)
        self.assertEqual(1, consumers.count())


class ManagerUserUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.manager = ManagerUserFactory(company=cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_manager", kwargs={"company_name": cls.company.slug_name, "pk": cls.manager.pk}
        )
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = ManagerUserUpdateView()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = self.manager

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_other_company_cannot_get_update_form(self):
        OperatorUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_update_manager_profile_with_form(self):
        with SetDjangoLanguage("en"):
            first_name = "Barney"
            last_name = "Calhoun"
            email = "barney.calhoun@blackmesa.com"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            managers = MaintenanceUser.objects.filter(
                email=email, first_name=first_name, last_name=last_name, company=self.company, pk=self.manager.pk
            )
            self.assertEqual(1, managers.count())

    def test_errors_on_update_manager_profile(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(self.form_url, {"first_name": "Chell", "form-mod": "profile"}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_update_manager_password_with_form(self):
        with SetDjangoLanguage("en"):
            password = "my safe password"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"new_password1": password, "new_password2": password, "form-mod": "password"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            self.assertTrue(MaintenanceUser.objects.get(pk=self.manager.pk).check_password(password))

    def test_errors_on_update_manager_password(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"new_password1": "my safe password", "new_password2": "my password", "form-mod": "password"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")

    def test_update_wrong_keyword_form(self):
        password = "qwertyuiop"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url, {"new_password1": password, "new_password2": password, "form-mod": "wrong"}, follow=True
        )

        self.assertEqual(response.status_code, 400)


class OperatorUserUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse("high_ui:update_operator", kwargs={"pk": cls.operator.pk})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUserUpdateView()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = self.operator

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_update_operator_profile_with_form(self):
        with SetDjangoLanguage("en"):
            first_name = "Barney"
            last_name = "Calhoun"
            email = "barney.calhoun@blackmesa.com"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            operators = MaintenanceUser.objects.filter(
                email=email, first_name=first_name, last_name=last_name, pk=self.operator.pk
            )
            self.assertEqual(1, operators.count())

    def test_update_operator_password_with_form(self):
        with SetDjangoLanguage("en"):
            password = "my safe password"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"new_password1": password, "new_password2": password, "form-mod": "password"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            self.assertTrue(MaintenanceUser.objects.get(pk=self.operator.pk).check_password(password))


class OperatorUserUpdateViewWithCompanyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        cls.company = CompanyFactory()
        cls.operator = OperatorUserFactory()
        cls.operator.operator_for.add(cls.company)
        cls.form_url = reverse(
            "high_ui:project-update_operator", kwargs={"company_name": cls.company.slug_name, "pk": cls.operator.pk}
        )
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = OperatorUserUpdateViewWithCompany()
        view.request = request
        view.user = self.admin
        view.company = self.company
        view.object = self.operator

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_manager_cannot_get_update_form(self):
        ManagerUserFactory(email="chell@aperture-science.com", password="azerty")

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_operator_of_the_company_cannot_get_update_form(self):
        operator = OperatorUserFactory(email="chell@aperture-science.com", password="azerty")
        operator.operator_for.add(self.company)

        self.client.login(username="chell@aperture-science.com", password="azerty")
        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_update_operator_form(self):
        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.get(self.form_url, follow=True)

        self.assertEqual(response.status_code, 200)

    def test_update_operator_profile_with_form(self):
        with SetDjangoLanguage("en"):
            first_name = "Barney"
            last_name = "Calhoun"
            email = "barney.calhoun@blackmesa.com"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            operators = MaintenanceUser.objects.filter(
                email=email, first_name=first_name, last_name=last_name, pk=self.operator.pk
            )
            self.assertEqual(1, operators.count())

    def test_update_operator_password_with_form(self):
        with SetDjangoLanguage("en"):
            password = "my safe password"

            self.client.login(username=self.admin.email, password="azerty")
            response = self.client.post(
                self.form_url,
                {"new_password1": password, "new_password2": password, "form-mod": "password"},
                follow=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, _("Modifications have been registered!"))
            self.assertTrue(MaintenanceUser.objects.get(pk=self.operator.pk).check_password(password))


class AdminUserUpdateViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = AdminUserFactory(email="barney.calhoun@blackmesa.com", password="azerty")
        cls.modified_admin = AdminUserFactory(email="chell@aperture-science.com")
        cls.form_url = reverse("high_ui:update_admin", kwargs={"pk": cls.modified_admin.pk})
        cls.login_url = reverse("login") + "?next=" + cls.form_url

    def test_get_context_data(self):
        factory = RequestFactory()
        request = factory.get(self.form_url)
        request.user = self.admin
        view = AdminUserUpdateView()
        view.request = request
        view.user = self.admin
        view.object = self.modified_admin

        context = view.get_context_data()
        self.assertEqual(reverse("high_ui:dashboard"), context["previous_page"])

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_see_the_admin_page(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.form_url)

        self.assertEqual(response.status_code, 200)

    def test_create_admin_with_form(self):
        first_name = "Gordon"
        last_name = "Freeman"
        email = "gordon.freeman@blackmesa.com"

        self.client.login(username=self.admin.email, password="azerty")
        response = self.client.post(
            self.form_url,
            {"first_name": first_name, "last_name": last_name, "email": email, "form-mod": "profile"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Les modifications ont bien été prises en compte!"))
        self.assertEqual(email, MaintenanceUser.objects.get(pk=self.modified_admin.pk).email)
