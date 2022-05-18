from random import choice

from customers.models import Company
from customers.models import MaintenanceUser
from customers.tests.factories import AdminOperatorUserFactory
from customers.tests.factories import ManagerUserFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.models import MaintenanceConsumer
from maintenance.models import MaintenanceCredit
from maintenance.tests.factories import MaintenanceConsumerFactory
from maintenance.tests.factories import MaintenanceCreditFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from django.test import TestCase
from django.urls import reverse


class ViewsPerformancesTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = AdminOperatorUserFactory()
        operators = [cls.admin] + OperatorUserFactory.create_batch(size=5)
        for _ in range(5):

            company, contract1, contract2, contract3 = create_project()
            ManagerUserFactory.create_batch(company=company, size=10)
            contracts = (contract1, contract2, contract3)
            for operator in operators:
                operator.operator_for.add(company)
                operator.save()

            consumers = MaintenanceConsumerFactory.create_batch(company=company, size=20)
            MaintenanceIssueFactory.create_batch(
                company=company,
                contract=choice(contracts),
                consumer_who_ask=choice(consumers),
                user_who_fix=choice(operators),
                size=80,
            )
            MaintenanceIssueFactory.create_batch(
                company=company,
                contract=choice(contracts),
                consumer_who_ask=choice(consumers),
                user_who_fix=choice(operators),
                size=20,
                is_deleted=True,
            )
            MaintenanceCreditFactory.create_batch(company=company, size=30)
        cls.company = Company.objects.first()
        cls.consumer = MaintenanceConsumer.objects.filter(company=cls.company).first()
        cls.manager = MaintenanceUser.objects.filter(company=cls.company).first()
        cls.operator = MaintenanceUser.objects.filter(operator_for=cls.company, is_superuser=False).first()
        cls.credit = MaintenanceCredit.objects.filter(company=cls.company).first()

    def test_dashboard_view(self):
        url = reverse("high_ui:dashboard")
        self.client.force_login(self.admin)
        with self.assertNumQueries(1091):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_account_update_view(self):
        url = reverse("high_ui:update_user")
        self.client.force_login(self.admin)
        with self.assertNumQueries(3):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_update_info_view(self):
        url = reverse("high_ui:update_infos")
        self.client.force_login(self.admin)
        with self.assertNumQueries(6):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_maintenance_types_update_view(self):
        url = reverse("high_ui:update_maintenance_types")
        self.client.force_login(self.admin)
        with self.assertNumQueries(6):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_view(self):
        url = reverse("high_ui:admin")
        self.client.force_login(self.admin)
        with self.assertNumQueries(15):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_credit_name_update_view(self):
        url = reverse("high_ui:admin-update_credits")
        self.client.force_login(self.admin)
        with self.assertNumQueries(6):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_archive_projects_view(self):
        url = reverse("high_ui:archive_projects")
        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_unarchive_projects_view(self):
        url = reverse("high_ui:unarchive_projects")
        self.client.force_login(self.admin)
        with self.assertNumQueries(7):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_project_unarchive_issues_view(self):
        url = reverse("high_ui:admin-project-unarchive_issues", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(11):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_create_view(self):
        url = reverse("high_ui:create_admin")
        self.client.force_login(self.admin)
        with self.assertNumQueries(5):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_list_update_view(self):
        url = reverse("high_ui:update_admins")
        self.client.force_login(self.admin)
        with self.assertNumQueries(12):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_admin_update_view(self):
        url = reverse("high_ui:update_admin", kwargs={"pk": self.admin.pk})
        self.client.force_login(self.admin)
        with self.assertNumQueries(6):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_create_view(self):
        url = reverse("high_ui:create_project")
        self.client.force_login(self.admin)
        with self.assertNumQueries(16):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_detail_view(self):
        url = reverse("high_ui:project_details", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(415):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_contact_update_view(self):
        url = reverse("high_ui:project-contact", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(7):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_update_view(self):
        url = reverse("high_ui:update_project", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(30):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_customize_view(self):
        url = reverse("high_ui:customize_project", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(10):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_issue_create_view(self):
        url = reverse("high_ui:project-create_issue", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(35):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_issue_detail_view(self):
        url = reverse(
            "high_ui:project-issue_details", kwargs={"company_name": self.company.slug_name, "company_issue_number": 1}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(17):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_issue_update_view(self):
        url = reverse(
            "high_ui:project-update_issue", kwargs={"company_name": self.company.slug_name, "company_issue_number": 1}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(42):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_consumer_create_view(self):
        url = reverse("high_ui:project-create_consumer", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(7):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_consumer_list_update_view(self):
        url = reverse("high_ui:project-update_consumers", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(10):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_consumer_update_view(self):
        url = reverse(
            "high_ui:project-update_consumer", kwargs={"company_name": self.company.slug_name, "pk": self.consumer.pk}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(9):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_manager_create_view(self):
        url = reverse("high_ui:project-create_manager", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(7):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_manager_list_update_view(self):
        url = reverse("high_ui:project-update_managers", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(10):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_manager_update_view(self):
        url = reverse(
            "high_ui:project-update_manager", kwargs={"company_name": self.company.slug_name, "pk": self.manager.pk}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_operator_create_view(self):
        url = reverse("high_ui:project-create_operator", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(7):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_operator_list_update_view(self):
        url = reverse("high_ui:project-update_operators", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(10):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_operator_update_view(self):
        url = reverse(
            "high_ui:project-update_operator", kwargs={"company_name": self.company.slug_name, "pk": self.admin.pk}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_credit_create_view(self):
        url = reverse("high_ui:project-create_credit", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(11):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_credit_update_view(self):
        url = reverse(
            "high_ui:project-update_credit", kwargs={"company_name": self.company.slug_name, "pk": self.credit.pk}
        )
        self.client.force_login(self.admin)
        with self.assertNumQueries(12):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_email_alert_update_view(self):
        url = reverse("high_ui:project-update_email_alert", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(10):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_counter_reset_view(self):
        url = reverse("high_ui:project-reset_counters", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_project_credit_recurrence_update_view(self):
        url = reverse("high_ui:project-update_credit_recurrence", kwargs={"company_name": self.company.slug_name})
        self.client.force_login(self.admin)
        with self.assertNumQueries(8):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_operator_create_view(self):
        url = reverse("high_ui:create_operator")
        self.client.force_login(self.admin)
        with self.assertNumQueries(5):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_operator_list_update_view(self):
        url = reverse("high_ui:update_operators")
        self.client.force_login(self.admin)
        with self.assertNumQueries(24):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)

    def test_operator_update_view(self):
        url = reverse("high_ui:update_operator", kwargs={"pk": self.operator.pk})
        self.client.force_login(self.admin)
        with self.assertNumQueries(6):
            response = self.client.get(url)
            response.render()
            self.assertEqual(response.status_code, 200)
