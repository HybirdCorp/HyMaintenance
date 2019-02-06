from django.test import TestCase

from ..models import MaintenanceContract
from ..models import MaintenanceCredit
from ..models.contract import AVAILABLE_TOTAL_TIME
from ..models.contract import CONSUMMED_TOTAL_TIME
from .factories import MaintenanceContractFactory


class MaintenanceContractFactoryTestCase(TestCase):
    def test_default_values(self):
        contract = MaintenanceContractFactory()
        self.assertEqual(1, MaintenanceContract.objects.all().count())
        self.assertEqual(1, MaintenanceContract.objects.filter(total_type=CONSUMMED_TOTAL_TIME).count())
        self.assertEqual(0, MaintenanceCredit.objects.filter(contract=contract, hours_number=20).count())

    def test_when_no_contract_created(self):
        MaintenanceContractFactory.build()
        self.assertEqual(0, MaintenanceContract.objects.all().count())
        self.assertEqual(0, MaintenanceCredit.objects.all().count())

    def test_create_available_contract_and_credit(self):
        contract = MaintenanceContractFactory(number_hours=20)
        self.assertEqual(1, MaintenanceContract.objects.filter(total_type=AVAILABLE_TOTAL_TIME).count())
        self.assertEqual(1, MaintenanceCredit.objects.filter(contract=contract, hours_number=20).count())
