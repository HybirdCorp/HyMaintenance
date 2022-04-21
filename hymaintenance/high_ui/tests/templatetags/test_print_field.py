from customers.tests.factories import CompanyFactory
from customers.tests.factories import OperatorUserFactory
from maintenance.tests.factories import MaintenanceConsumerFactory
from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from django.test import SimpleTestCase
from django.test import TestCase
from django.utils.translation import ugettext as _

from ...templatetags.print_fields import extra_credit_subject
from ...templatetags.print_fields import hide_disabled_consumer
from ...templatetags.print_fields import hide_disabled_operator
from ...templatetags.print_fields import pretty_print_contract_counter
from ...templatetags.print_fields import pretty_print_minutes
from ...templatetags.print_fields import pretty_print_name
from ...templatetags.print_fields import print_operator_projects
from ..utils import SetDjangoLanguage


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
        self.assertEqual("40 mins", pretty_print_minutes(40, use_long_minute_format=True))

    def test_negative_pretty_print_minutes_with_hours_and_no_minutes(self):
        self.assertEqual("-3h", pretty_print_minutes(-180))

    def test_negative_pretty_print_minutes_with_hours_and_minutes(self):
        self.assertEqual("-3h10", pretty_print_minutes(-190))

    def test_negative_pretty_print_minutes_with_only_minutes(self):
        self.assertEqual("-40m", pretty_print_minutes(-40))

    def test_negative_pretty_print_minutes_with_only_minutes_and_long_format(self):
        self.assertEqual("-40 mins", pretty_print_minutes(-40, use_long_minute_format=True))


class PrettyPrintContractCounterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company, cls.available_contract, cls.consumed_contract, _ = create_project(
            contract1={"credited_hours": 1, "credit_counter": True}, contract2={"credit_counter": False}
        )

    def test_print_available_time(self):
        MaintenanceIssueFactory(company=self.company, contract=self.available_contract, number_minutes=10)
        self.assertEqual("50m /&nbsp;1h", pretty_print_contract_counter(self.available_contract))

    def test_print_comsumed_time(self):
        MaintenanceIssueFactory(company=self.company, contract=self.consumed_contract, number_minutes=10)
        self.assertEqual("10m", pretty_print_contract_counter(self.consumed_contract))

    def test_print_fancy_time(self):
        MaintenanceIssueFactory(company=self.company, contract=self.consumed_contract, number_minutes=10)
        self.consumed_contract.total_type = 42
        self.assertEqual("", pretty_print_contract_counter(self.consumed_contract))

    def test_deleted_issue_not_counted(self):
        MaintenanceIssueFactory(
            company=self.company, contract=self.consumed_contract, number_minutes=10, is_deleted=True
        )
        self.assertEqual("0h", pretty_print_contract_counter(self.consumed_contract))
        MaintenanceIssueFactory(
            company=self.company, contract=self.available_contract, number_minutes=10, is_deleted=True
        )
        self.assertEqual("1h /&nbsp;1h", pretty_print_contract_counter(self.available_contract))


class PrintOperatorProjectsTestCase(TestCase):
    def setUp(self):
        self.op_id = 1
        self.user = OperatorUserFactory(id=self.op_id)

    def test_print_when_operator_has_no_project(self):
        self.assertEqual(_("project:") + " " + _("none"), print_operator_projects(self.op_id))

    def test_print_when_operator_has_one_project(self):
        company = CompanyFactory()
        self.user.operator_for.add(company)
        self.assertEqual(_("project:") + " " + "{}".format(company.name), print_operator_projects(self.op_id))

    def test_print_when_operator_has_projects(self):
        company1 = CompanyFactory()
        self.user.operator_for.add(company1)
        company2 = CompanyFactory()
        self.user.operator_for.add(company2)
        company3 = CompanyFactory()
        self.user.operator_for.add(company3)
        self.assertEqual(
            _("projects:") + " " + "{}, {}, {}".format(company1.name, company2.name, company3.name),
            print_operator_projects(self.op_id),
        )


class HideDisabledUsersTestCase(TestCase):
    def test_hide_disabled_consumers(self):
        consumer1 = MaintenanceConsumerFactory(is_used=True)
        consumer2 = MaintenanceConsumerFactory(is_used=False)

        self.assertEqual("", hide_disabled_consumer(consumer1.id))
        self.assertEqual('class="disabled_consumer"', hide_disabled_consumer(consumer2.id))

    def test_hide_disabled_operators(self):
        operator1 = OperatorUserFactory(is_active=True)
        operator2 = OperatorUserFactory(is_active=False)

        self.assertEqual("", hide_disabled_operator(operator1.id))
        self.assertEqual('class="disabled_operator"', hide_disabled_operator(operator2.id))


class ExtraCreditSubjectTestCase(TestCase):
    def test(self):
        with SetDjangoLanguage("en"):
            self.assertEqual('Add extra <span class="duration">12h</span>', extra_credit_subject(12))


class PrettyPrintNameTestCase(TestCase):
    def test_first_letter_upper_case(self):
        self.assertEqual("Gordon F.", pretty_print_name("Gordon", "Freeman"))

    def test_all_letter_lower_case(self):
        self.assertEqual("Gordon F.", pretty_print_name("gordon", "freeman"))

    def test_all_letter_upper_case(self):
        self.assertEqual("Gordon F.", pretty_print_name("GORDON", "FREEMAN"))

    def test_no_last_name(self):
        self.assertEqual("Gordon", pretty_print_name("gordon", None))

    def test_no_first_name(self):
        self.assertEqual(" F.", pretty_print_name(None, "freeman"))

    def test_no_name(self):
        self.assertEqual("", pretty_print_name(None, None))

    def test_no_name_empty_string(self):
        self.assertEqual("", pretty_print_name("", ""))
