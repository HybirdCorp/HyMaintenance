from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from django.test import TestCase
from django.urls import reverse


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

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_see_the_admin_page(self):
        manager = ManagerUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")

        self.client.login(username=manager.email, password="azerty")

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, 403)

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

        self.assertContains(response, "<a href='/high_ui/admin/projects/black-mesa/issues/'>Black Mesa</a>")
        self.assertNotContains(
            response, "<a href='/high_ui/admin/projects/aperture-science/issues/'>Aperture Science</a>"
        )

    def test_user_and_project_numbers_are_well_displayed(self):
        company, contract, _, _ = create_project()
        company, contract, _, _ = create_project(company={"is_archived": True})

        admin = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        OperatorUserFactory()
        self.client.login(username=admin.email, password="azerty")
        response = self.client.get(self.page_url)

        op_span = '<span class="dashboard-value" id="operators_number">1</span>'
        admin_span = '<span class="dashboard-value" id="admins_number">1</span>'
        active_span = '<span class="dashboard-value" id="active_projects_number">1</span>'
        archived_span = '<span class="dashboard-value" id="archived_projects_number">1</span>'

        self.assertContains(response, op_span)
        self.assertContains(response, admin_span)
        self.assertContains(response, active_span)
        self.assertContains(response, archived_span)
