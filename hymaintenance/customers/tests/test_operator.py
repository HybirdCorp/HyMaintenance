from django.test import TestCase

from ..models.user import get_active_companies_of_operator
from ..models.user import get_companies_of_operator
from .factories import CompanyFactory
from .factories import OperatorUserFactory


class MaintenanceUserTestCase(TestCase):
    def test_get_companies_for_an_operator_all_companies_are_ok(self):
        c1 = CompanyFactory(name="Company1")
        c2 = CompanyFactory(name="Company2")
        c3 = CompanyFactory(name="Company3")
        operator = OperatorUserFactory()
        operator.operator_for.add(c1)
        operator.operator_for.add(c2)
        operator.operator_for.add(c3)
        self.assertEqual(3, get_companies_of_operator(operator).count())

    def test_get_companies_for_an_operator_exclude_not_managed_companies(self):
        c1 = CompanyFactory(name="Company1")
        CompanyFactory(name="Company2")
        c3 = CompanyFactory(name="Company3")
        operator = OperatorUserFactory()
        operator.operator_for.add(c1)
        operator.operator_for.add(c3)
        self.assertEqual([c1, c3], list(get_companies_of_operator(operator)))

    def test_get_active_companies_for_an_operator_all_companies_are_ok(self):
        c1 = CompanyFactory(name="Company1")
        c2 = CompanyFactory(name="Company2")
        c3 = CompanyFactory(name="Company3", is_archived=True)
        operator = OperatorUserFactory()
        operator.operator_for.add(c1)
        operator.operator_for.add(c2)
        operator.operator_for.add(c3)

        companies = get_active_companies_of_operator(operator)
        self.assertEqual(2, companies.count())
        self.assertIn(c1, companies)
        self.assertIn(c2, companies)

    def test_get_active_companies_for_an_operator_exclude_not_managed_companies(self):
        c1 = CompanyFactory(name="Company1")
        CompanyFactory(name="Company2")
        c3 = CompanyFactory(name="Company3", is_archived=True)
        operator = OperatorUserFactory()
        operator.operator_for.add(c1)
        operator.operator_for.add(c3)

        companies = get_active_companies_of_operator(operator)
        self.assertEqual(1, companies.count())
        self.assertIn(c1, companies)
