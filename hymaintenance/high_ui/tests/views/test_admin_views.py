from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project


class AdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_url = reverse("high_ui:admin")
        cls.login_url = reverse("login") + "?next=" + cls.page_url

    def test_unlogged_user_cannot_see_the_admin_page(self):
        response = self.client.get(self.page_url)

        self.assertRedirects(response, self.login_url)

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

    def test_link_to_unarchive_archived_project_issues(self):
        company, contract, _, _ = create_project(company={"name": "Black Mesa"})
        MaintenanceIssueFactory(contract=contract, company=company, is_deleted=True)
        company, contract, _, _ = create_project(company={"name": "Aperture Science"})

        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        self.client.login(username=admin.email, password="azerty")
        response = self.client.get(self.page_url)

        print(str(response.content).replace("\\n", "\n"))

        self.assertContains(response, "<a href='/high_ui/admin/projects/black-mesa/issues/'>Black Mesa</a>")
        self.assertNotContains(
            response, "<a href='/high_ui/admin/projects/aperture-science/issues/'>Aperture Science</a>"
        )
