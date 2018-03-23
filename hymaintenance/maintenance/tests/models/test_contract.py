from django.test import TestCase
from django.utils.timezone import datetime, now

from customers.tests.factories import CompanyFactory

from ...models import MaintenanceContract, MaintenanceType
from ..factories import IncomingChannelFactory, MaintenanceContractFactory, MaintenanceCreditFactory, MaintenanceIssueFactory


class MaintenanceContractTestCase(TestCase):

    def test_i_can_create_a_maintenance_contract(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        MaintenanceContract.objects.create(company=company,
                                           start=now().date(),
                                           maintenance_type=maintenance_type,
                                           number_hours=40)
        self.assertEqual(1, MaintenanceContract.objects.count())

    def test_str_is_good_for_contract(self):
        company = CompanyFactory(name="Reynholm Industries")
        maintenance_type = MaintenanceType.objects.get(id=1)
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2)
        self.assertEqual("Reynholm Industries , Maintenance", str(contract))

    def test_get_number_contract_hours(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=5)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=15)

        self.assertEqual(22, contract.get_number_contract_hours())

    def test_get_number_contract_minutes(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=5)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=15)

        self.assertEqual(1320, contract.get_number_contract_minutes())

    def test_get_number_consumed_minutes_in_month(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=42)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=10)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                date=datetime(day=1, month=today.month,
                                              year=today.year - 1),
                                number_minutes=20)

        self.assertEqual(40, contract.get_number_consumed_minutes_in_month(today))

    def test_get_number_consumed_hours_in_month(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=42)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                date=datetime(day=1, month=today.month,
                                              year=today.year - 1),
                                number_minutes=20)

        self.assertEqual(1, contract.get_number_consumed_hours_in_month(today))

    def test_get_number_consumed_hours(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=42)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                date=datetime(day=1, month=today.month,
                                              year=today.year - 1),
                                number_minutes=60)

        self.assertEqual(2, contract.get_number_consumed_hours())

    def test_get_number_consumed_minutes(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        channel = IncomingChannelFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=42)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=10)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                number_minutes=30)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                incoming_channel=channel,
                                date=datetime(day=1, month=today.month,
                                              year=today.year - 1),
                                number_minutes=20)

        self.assertEqual(60, contract.get_number_consumed_minutes())

    def test_get_number_remaining_minutes(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=1)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=1)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                number_minutes=10)
        self.assertEqual(110, contract.get_number_remaining_minutes())

    def test_get_number_remaining_hours(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=2)

        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                number_minutes=60)
        self.assertEqual(3, contract.get_number_remaining_hours())

    def test_get_number_credited_hours_in_month_with_start_date_in_month(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2,
                                              start=today)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=5)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=15)

        self.assertEqual(22, contract.get_number_credited_hours_in_month(today))

    def test_get_number_credited_hours_in_month_with_start_date_not_in_month(self):
        company = CompanyFactory()
        maintenance_type = MaintenanceType.objects.get(id=1)
        today = now()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2,
                                              start=datetime(day=1,
                                                             month=today.month,
                                                             year=today.year - 1))

        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=5)
        MaintenanceCreditFactory(company=company,
                                 maintenance_type=maintenance_type,
                                 hours_number=15)

        self.assertEqual(20, contract.get_number_credited_hours_in_month(today))
