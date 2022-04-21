from customers.tests.factories import CompanyFactory
from freezegun import freeze_time
from maintenance.models import MaintenanceCredit

from django.test import TestCase
from django.utils.timezone import datetime
from django.utils.timezone import now

from ...models import MaintenanceContract
from ...models.contract import get_next_month_date
from ...models.contract import get_next_year_date
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
        MaintenanceIssueFactory(contract=contract, date=time2)
        self.assertEqual([issue], list(contract.get_current_issues()))

    def test_get_old_issues(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)
        company, contract, _, _ = create_project()
        self.assertEqual([], list(contract.get_old_issues()))

        contract.reset_date = time1
        contract.save()
        self.assertEqual([], list(contract.get_old_issues()))

        MaintenanceIssueFactory(contract=contract, date=time1)
        MaintenanceIssueFactory(contract=contract, is_deleted=True, date=time2)
        issue = MaintenanceIssueFactory(contract=contract, date=time2)
        self.assertEqual([issue], list(contract.get_old_issues()))

    def test_get_current_credits(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)
        company, contract, _, _ = create_project(contract1={"reset_date": time1})
        credit = MaintenanceCreditFactory(contract=contract, date=time1)
        MaintenanceCreditFactory(contract=contract, date=time2)
        self.assertEqual([credit], list(contract.get_current_credits()))

    def test_get_old_credits(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)
        company, contract, _, _ = create_project()
        self.assertEqual([], list(contract.get_old_credits()))

        contract.reset_date = time1
        contract.save()
        self.assertEqual([], list(contract.get_old_credits()))

        MaintenanceCreditFactory(contract=contract, date=time1)
        credit = MaintenanceCreditFactory(contract=contract, date=time2)
        self.assertEqual([credit], list(contract.get_old_credits()))

    def test_update_times_in_save_contract(self):
        time1 = datetime(day=1, month=2, year=2021)
        time2 = datetime(day=1, month=1, year=2021)
        time3 = datetime(day=1, month=12, year=2020)

        company, contract, _, _ = create_project(contract1={"credited_hours": 10, "start": time3})
        self.assertEqual(10, contract.credited_hours)
        self.assertEqual(0, contract.consumed_minutes)

        MaintenanceIssueFactory(contract=contract, date=time1, number_minutes=70)
        MaintenanceIssueFactory(contract=contract, date=time3, number_minutes=60)
        contract.refresh_from_db()
        self.assertEqual(10, contract.credited_hours)
        self.assertEqual(130, contract.consumed_minutes)

        contract.reset_date = time2
        contract.save()
        contract.refresh_from_db()
        self.assertEqual(9, contract.credited_hours)
        self.assertEqual(70, contract.consumed_minutes)

    def test_is_available_time_counter(self):
        company, contract1, contract2, _ = create_project(
            contract1={"credit_counter": True}, contract2={"credit_counter": False}
        )
        self.assertFalse(contract2.is_available_time_counter())
        self.assertTrue(contract1.is_available_time_counter())

    def test_is_consumed_time_counter(self):
        company, contract1, contract2, _ = create_project(
            contract1={"credit_counter": True}, contract2={"credit_counter": False}
        )
        self.assertFalse(contract1.is_consumed_time_counter())
        self.assertTrue(contract2.is_consumed_time_counter())

    def test_has_annual_credit_recurrence(self):
        company, contract1, contract2, _ = create_project(
            contract1={"annual_recurrence": True}, contract2={"monthly_recurrence": False}
        )
        self.assertTrue(contract1.has_annual_credit_recurrence())
        self.assertFalse(contract2.has_annual_credit_recurrence())

    def test_get_monthly_recurrence_recurrence_next_date(self):
        time = datetime(day=2, month=12, year=2021)
        company, contract1, _, _ = create_project(
            contract1={"monthly_recurrence": True, "recurrence_start_date": time.date()}
        )
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(2, next_time.day)
        self.assertEqual(1, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_monthly_recurrence_recurrence_next_date_end_of_the_month(self):
        time = datetime(day=31, month=12, year=2021)
        company, contract1, _, _ = create_project(
            contract1={"monthly_recurrence": True, "recurrence_start_date": time.date()}
        )
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(31, next_time.day)
        self.assertEqual(1, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_monthly_recurrence_recurrence_next_date_day_not_exists(self):
        time = datetime(day=31, month=1, year=2021)
        company, contract1, _, _ = create_project(
            contract1={"monthly_recurrence": True, "recurrence_start_date": time.date()}
        )
        contract1.recurrence_next_date = contract1.get_recurrence_next_date()
        contract1.save()
        contract1.refresh_from_db()
        self.assertEqual(28, contract1.recurrence_next_date.day)
        self.assertEqual(2, contract1.recurrence_next_date.month)
        self.assertEqual(2021, contract1.recurrence_next_date.year)
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(31, next_time.day)
        self.assertEqual(3, next_time.month)
        self.assertEqual(2021, next_time.year)

    def test_get_annual_recurrence_recurrence_next_date(self):
        time = datetime(day=2, month=12, year=2021)
        company, contract1, _, _ = create_project(
            contract1={"annual_recurrence": True, "recurrence_start_date": time.date()}
        )
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(2, next_time.day)
        self.assertEqual(12, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_annual_recurrence_recurrence_next_date_end_of_the_month(self):
        time = datetime(day=31, month=12, year=2021)
        company, contract1, _, _ = create_project(
            contract1={"annual_recurrence": True, "recurrence_start_date": time.date()}
        )
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(31, next_time.day)
        self.assertEqual(12, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_annual_recurrence_recurrence_next_date_day_not_exists(self):
        time = datetime(day=29, month=2, year=2024)
        company, contract1, _, _ = create_project(
            contract1={"annual_recurrence": True, "recurrence_start_date": time.date()}
        )
        next_time = contract1.get_recurrence_next_date()
        self.assertEqual(28, next_time.day)
        self.assertEqual(2, next_time.month)
        self.assertEqual(2025, next_time.year)

    @freeze_time("2019-04-04")
    def test_get_recurrence_next_date(self):
        start_date = datetime(day=2, month=12, year=2021).date()
        company, contract, _, _ = create_project()
        next_time = contract.get_recurrence_next_date()
        self.assertIsNone(next_time)

        contract.recurrence_start_date = start_date
        contract.save()
        contract.set_annual_recurrence()
        next_time = contract.get_recurrence_next_date()
        self.assertEqual(2, next_time.day)
        self.assertEqual(12, next_time.month)
        self.assertEqual(2022, next_time.year)

        contract.set_monthly_recurrence()
        next_time = contract.get_recurrence_next_date()
        self.assertEqual(2, next_time.day)
        self.assertEqual(1, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_remove_recurrence(self):
        time = datetime(day=2, month=12, year=2021).date()
        company, contract, _, _ = create_project(contract1={"annual_recurrence": True, "recurrence_start_date": time})
        contract.remove_recurrence()
        contract.refresh_from_db()

        self.assertFalse(contract.has_credit_recurrence)

    def test_get_delta_credits_minutes_when_no_reset_date(self):
        company, contract, _, _ = create_project()

        self.assertEqual(0, contract.get_delta_credits_minutes())

    def test_get_delta_credits_minutes_when_only_issues(self):
        time1 = datetime(day=1, month=6, year=2021).date()
        time2 = datetime(day=1, month=5, year=2021).date()
        company, contract, _, _ = create_project(contract1={"reset_date": time1})
        MaintenanceIssueFactory(contract=contract, company=company, number_minutes=60, date=time2)

        self.assertEqual(-60, contract.get_delta_credits_minutes())

    def test_get_delta_credits_minutes_when_only_credits(self):
        time1 = datetime(day=1, month=6, year=2021).date()
        time2 = datetime(day=1, month=5, year=2021).date()
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": time2, "reset_date": time1}
        )

        self.assertEqual(20 * 60, contract.get_delta_credits_minutes())

    def test_get_delta_credits_minutes_credits_and_issues(self):
        time1 = datetime(day=1, month=6, year=2021).date()
        time2 = datetime(day=1, month=5, year=2021).date()
        company, contract, _, _ = create_project(
            contract1={"credit_counter": True, "start": time2, "reset_date": time1}
        )
        MaintenanceCreditFactory(contract=contract, company=company, hours_number=20, date=time1)

        MaintenanceIssueFactory(contract=contract, company=company, number_minutes=60, date=time2)
        MaintenanceIssueFactory(contract=contract, company=company, number_minutes=60, date=time1)

        self.assertEqual(20 * 60 - 60, contract.get_delta_credits_minutes())

    def test_set_recurrence_dates_and_create_all_old_credit_occurrences(self):
        time1 = datetime(day=1, month=5, year=2021).date()
        time2 = datetime(day=1, month=10, year=2021).date()
        company, contract, _, _ = create_project(contract1={"monthly_recurrence": True, "recurrence_start_date": time1})
        self.assertEqual(1, MaintenanceCredit.objects.filter(contract=contract).count())
        contract.recurrence_next_date = None
        contract.save()
        contract.set_recurrence_dates_and_create_all_old_credit_occurrences(now_date=time2)
        self.assertEqual(7, MaintenanceCredit.objects.filter(contract=contract).count())
        self.assertEqual(1, contract.recurrence_next_date.day)
        self.assertEqual(11, contract.recurrence_next_date.month)
        self.assertEqual(2021, contract.recurrence_next_date.year)


class NextDateTestCase(TestCase):
    def test_get_next_month_date(self):
        time = datetime(day=2, month=1, year=2021)
        next_time = get_next_month_date(time, time)
        self.assertEqual(2, next_time.day)
        self.assertEqual(2, next_time.month)
        self.assertEqual(2021, next_time.year)

    def test_get_next_month_date_end_of_year(self):
        time = datetime(day=2, month=12, year=2021)
        next_time = get_next_month_date(time, time)
        self.assertEqual(2, next_time.day)
        self.assertEqual(1, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_next_month_date_end_of_month(self):
        time = datetime(day=31, month=1, year=2022)
        next_time = get_next_month_date(time, time)
        self.assertEqual(28, next_time.day)
        self.assertEqual(2, next_time.month)
        self.assertEqual(2022, next_time.year)
        next_time = get_next_month_date(time, next_time)
        self.assertEqual(31, next_time.day)
        self.assertEqual(3, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_next_year_date(self):
        time = datetime(day=2, month=3, year=2021)
        next_time = get_next_year_date(time, time)
        self.assertEqual(2, next_time.day)
        self.assertEqual(3, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_next_year_date_end_of_year(self):
        time = datetime(day=2, month=12, year=2021)
        next_time = get_next_year_date(time, time)
        self.assertEqual(2, next_time.day)
        self.assertEqual(12, next_time.month)
        self.assertEqual(2022, next_time.year)

    def test_get_next_year_date_end_of_month(self):
        time = datetime(day=29, month=2, year=2024)
        next_time = get_next_year_date(time, time)
        self.assertEqual(28, next_time.day)
        self.assertEqual(2, next_time.month)
        self.assertEqual(2025, next_time.year)
        while next_time.year < 2028:
            next_time = get_next_year_date(time, next_time)
        self.assertEqual(29, next_time.day)
        self.assertEqual(2, next_time.month)
        self.assertEqual(2028, next_time.year)
