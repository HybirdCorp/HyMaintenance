from django.test import TestCase
from django.utils.timezone import datetime
from django.utils.timezone import now

from customers.tests.factories import CompanyFactory

from ...models import MaintenanceContract
from ..factories import IncomingChannelFactory
from ..factories import MaintenanceContractFactory
from ..factories import MaintenanceCreditFactory
from ..factories import MaintenanceIssueFactory
from ..factories import create_project
from ..factories import get_default_maintenance_type


class MaintenanceContractTestCase(TestCase):
    def test_get_all_maintenance_contract(self):
        _, _, _, _ = create_project()
        self.assertEqual(3, MaintenanceContract.objects.all().count())

    def test_get_active_maintenance_contract_only(self):
        _, _, _, _ = create_project(contract1={"disabled": True})
        self.assertEqual(2, MaintenanceContract.objects.filter_enabled().count())

    def test_i_can_create_a_maintenance_contract(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        MaintenanceContract.objects.create(
            company=company, start=now().date(), maintenance_type=maintenance_type, credited_hours=40
        )
        self.assertEqual(1, MaintenanceContract.objects.count())

    def test_str_is_good_for_contract(self):
        company = CompanyFactory(name="Reynholm Industries")
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(company=company, maintenance_type=maintenance_type, credited_hours=2)
        self.assertEqual("Reynholm Industries , Maintenance", str(contract))

    def test_get_number_contract_hours(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=2
        )
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=5)
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=15)

        self.assertEqual(22, contract.get_number_contract_hours())

    def test_get_number_contract_hours_on_wrong_type_of_contract(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(company=company, maintenance_type=maintenance_type)

        self.assertEqual(0, contract.get_number_contract_hours())

    def test_get_number_contract_minutes(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=2
        )
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=5)
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=15)

        self.assertEqual(1320, contract.get_number_contract_minutes())

    def test_get_number_consumed_minutes_in_month(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=42
        )
        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=10)

        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(
            company=company,
            contract=contract,
            incoming_channel=channel,
            date=datetime(day=1, month=today.month, year=today.year - 1),
            number_minutes=20,
        )

        self.assertEqual(40, contract.get_number_consumed_minutes_in_month(today))

    def test_get_number_consumed_hours_in_month(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=42
        )
        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(
            company=company,
            contract=contract,
            incoming_channel=channel,
            date=datetime(day=1, month=today.month, year=today.year - 1),
            number_minutes=20,
        )

        self.assertEqual(1, contract.get_number_consumed_hours_in_month(today))

    def test_get_number_consumed_hours(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company, maintenance_type=maintenance_type, credited_hours=42)
        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(
            company=company,
            contract=contract,
            incoming_channel=channel,
            date=datetime(day=1, month=today.month, year=today.year - 1),
            number_minutes=60,
        )

        self.assertEqual(2, contract.get_number_consumed_hours())

    def test_get_number_consumed_minutes(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company, maintenance_type=maintenance_type, credited_hours=42)
        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=10)

        MaintenanceIssueFactory(company=company, contract=contract, incoming_channel=channel, number_minutes=30)

        MaintenanceIssueFactory(
            company=company,
            contract=contract,
            incoming_channel=channel,
            date=datetime(day=1, month=today.month, year=today.year - 1),
            number_minutes=20,
        )

        self.assertEqual(60, contract.get_number_consumed_minutes())

    def test_get_number_remaining_minutes(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=1
        )
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=1)

        MaintenanceIssueFactory(company=company, contract=contract, number_minutes=10)
        self.assertEqual(110, contract.get_number_remaining_minutes())

    def test_get_number_remaining_hours(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=2
        )
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=2)

        MaintenanceIssueFactory(company=company, contract=contract, number_minutes=60)
        self.assertEqual(3, contract.get_number_remaining_hours())

    def test_get_number_credited_hours_in_month_with_start_date_in_month(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        contract = MaintenanceContractFactory(
            company=company, maintenance_type=maintenance_type, credit_counter=True, credited_hours=2, start=today
        )
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=5)
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=15)

        self.assertEqual(22, contract.get_number_credited_hours_in_month(today))

    def test_get_number_credited_hours_in_month_with_start_date_not_in_month(self):
        company = CompanyFactory()
        maintenance_type = get_default_maintenance_type()
        today = now()
        contract = MaintenanceContractFactory(
            company=company,
            maintenance_type=maintenance_type,
            credited_hours=2,
            credit_counter=True,
            start=datetime(day=1, month=today.month, year=today.year - 1),
        )

        MaintenanceCreditFactory(company=company, contract=contract, hours_number=5)
        MaintenanceCreditFactory(company=company, contract=contract, hours_number=15)

        self.assertEqual(20, contract.get_number_credited_hours_in_month(today))

    def test_get_current_issues(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)
        company, contract, _, _ = create_project(contract1={"reset_date": time1})
        issue = MaintenanceIssueFactory(contract=contract, date=time1)
        MaintenanceIssueFactory(contract=contract, is_deleted=True, date=time1)
        MaintenanceIssueFactory(date=time2)
        self.assertEqual([issue], list(contract.get_current_issues()))

    def test_update_times_in_save_contract(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)

        company, contract, _, _ = create_project(contract1={"credited_hours": 10})
        self.assertEqual(10, contract.credited_hours)
        self.assertEqual(0, contract.consumed_minutes)

        MaintenanceIssueFactory(contract=contract, date=time2, number_minutes=60)
        contract.refresh_from_db()
        self.assertEqual(60, contract.consumed_minutes)

        contract.reset_date = time1
        contract.save()
        contract.refresh_from_db()
        self.assertEqual(0, contract.consumed_minutes)
        self.assertEqual(10, contract.credited_hours)
