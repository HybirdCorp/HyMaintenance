from django.test import SimpleTestCase, TestCase

from customers.tests.factories import CompanyFactory
from maintenance.tests.factories import MaintenanceContractFactory, MaintenanceIssueFactory, MaintenanceTypeFactory

from ...templatetags.print_fields import pretty_print_contract_counter, pretty_print_minutes


class PrettyPrintMinutesTestCase(SimpleTestCase):

    def test_pretty_print_minutes_if_value_is_blank(self):
        self.assertEqual("", pretty_print_minutes(""))

    def test_pretty_print_minutes_with_hours_and_no_minutes(self):
        self.assertEqual("3h", pretty_print_minutes(180))

    def test_pretty_print_minutes_with_hours_and_minutes(self):
        self.assertEqual("3h10", pretty_print_minutes(190))

    def test_pretty_print_minutes_with_only_minutes(self):
        self.assertEqual("40m", pretty_print_minutes(40))

    def test_pretty_print_minutes_with_only_minutes_and_long_format(self):
        self.assertEqual("40 mins", pretty_print_minutes(40,
                                                         use_long_minute_format=True))

    def test_negative_pretty_print_minutes_with_hours_and_no_minutes(self):
        self.assertEqual("-3h", pretty_print_minutes(-180))

    def test_negative_pretty_print_minutes_with_hours_and_minutes(self):
        self.assertEqual("-3h10", pretty_print_minutes(-190))

    def test_negative_pretty_print_minutes_with_only_minutes(self):
        self.assertEqual("-40m", pretty_print_minutes(-40))

    def test_negative_pretty_print_minutes_with_only_minutes_and_long_format(self):
        self.assertEqual("-40 mins", pretty_print_minutes(-40,
                                                          use_long_minute_format=True))


class PrettyPrintContractCounterTestCase(TestCase):
    def create_company_mtype_contract_and_issue(self, total_type):
        company = CompanyFactory()
        maintenance_type = MaintenanceTypeFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=1,
                                              total_type=total_type)
        MaintenanceIssueFactory(company=company,
                                maintenance_type=maintenance_type,
                                number_minutes=10)
        return contract

    def test_print_comsummed_time(self):
        contract = self.create_company_mtype_contract_and_issue(0)
        self.assertEqual("50m /&nbsp;1h", pretty_print_contract_counter(contract))

    def test_print_available_time(self):
        contract = self.create_company_mtype_contract_and_issue(1)
        self.assertEqual("10m", pretty_print_contract_counter(contract))

    def test_print_fancy_time(self):
        contract = self.create_company_mtype_contract_and_issue(1)
        contract.total_type = 42
        self.assertEqual("", pretty_print_contract_counter(contract))
