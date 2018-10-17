from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_url = reverse("high_ui:admin")
        cls.login_url = reverse("login") + "?next=" + cls.page_url

    def test_operator_cannot_see_the_admin_page(self):
        operator = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=operator.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

    def test_admin_user_can_see_the_admin_page(self):
        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=admin.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 200)
