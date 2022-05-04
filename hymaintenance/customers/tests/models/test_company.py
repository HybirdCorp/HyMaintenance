
from maintenance.tests.factories import MaintenanceContractFactory
from maintenance.tests.factories import MaintenanceIssueFactory

from django.test import TestCase

from ...models import Company
from ..factories import CompanyFactory
from ..factories import OperatorUserFactory


class CompanyTestCase(TestCase):
    def test_i_can_create_a_company(self):
        Company.objects.create(name="Aperture Science")
        self.assertEqual(1, Company.objects.count())

    def test_i_cant_save_again_issue_number(self):
        company = Company.objects.create(name="Aperture Science")
        company.name = "Black Mesa"
        company.issues_counter += 10
        company.save()
        company = Company.objects.get(pk=company.pk)
        self.assertEqual(0, company.issues_counter)
        self.assertEqual("Black Mesa", company.name)

    def test_if_counter_is_inited(self):
        company = Company.objects.create(name="Black Mesa")
        self.assertEqual(0, company.issues_counter)

    def test_if_counter_is_updated_when_new_issue(self):
        company = Company.objects.create(name="Black Mesa")
        contract = MaintenanceContractFactory(company=company)
        MaintenanceIssueFactory(company=company, contract=contract)
        company = Company.objects.filter(name="Black Mesa").first()
        self.assertEqual(1, company.issues_counter)

    def test_if_slug_name_is_created(self):
        company = Company.objects.create(name="Black Mesa")
        self.assertEqual("black-mesa", company.slug_name)

    def test_if_slug_name_is_well_created_when_sakename_exist(self):
        Company.objects.create(name="Black Mesa")
        company = Company.objects.create(name="Black Mesa")
        self.assertEqual("black-mesa2", company.slug_name)
        company = Company.objects.create(name="Black Mesa")
        self.assertEqual("black-mesa3", company.slug_name)

    def test_if_slug_name_is_not_update_when_update_company_without_changing_name(self):
        company = Company.objects.create(name="Black Mesa")
        self.assertEqual("black-mesa", company.slug_name)
        operator = OperatorUserFactory()
        operator.operator_for.add(company)
        company.save()
        company = Company.objects.get(pk=company.pk)
        self.assertEqual("black-mesa", company.slug_name)

    def test_cannot_update_slug_name(self):
        company = Company.objects.create(name="Black Mesa")
        company.slug_name = "i-m-a-sluggy-name"
        company.save()
        company = Company.objects.filter(name="Black Mesa").first()
        self.assertEqual("black-mesa", company.slug_name)

    def test_cannot_update_issues_counter(self):
        company = Company.objects.create(name="Black Mesa")
        company.issues_counter += 10
        company.save()
        company = Company.objects.filter(name="Black Mesa").first()
        self.assertEqual(0, company.issues_counter)

    def test_can_update_name(self):
        company = Company.objects.create(name="Black Mesa")
        company.name = "Aperture Science"
        company.save()
        self.assertListEqual([company], list(Company.objects.filter(name=company.name)))
        company = Company.objects.filter(name=company.name).first()
        self.assertEqual("aperture-science", company.slug_name)

    def test_get_operators_choices(self):
        company = CompanyFactory()

        operator = OperatorUserFactory(first_name="Gordon", last_name="Freeman")
        operator.operator_for.add(company)
        operator.is_active = False
        operator.save()

        operator2 = OperatorUserFactory(first_name="Cave", last_name="Johnson")
        operator2.operator_for.add(company)

        operators_choices = company.get_operators_choices()
        self.assertListEqual([(operator2.pk, "Cave Johnson"), (operator.pk, "Gordon Freeman")], operators_choices)

    def test_get_active_operators_choices(self):
        company = CompanyFactory()

        operator = OperatorUserFactory(first_name="Gordon", last_name="Freeman")
        operator.operator_for.add(company)
        operator.is_active = False
        operator.save()

        operator2 = OperatorUserFactory(first_name="Cave", last_name="Johnson")
        operator2.operator_for.add(company)

        operators_choices = company.get_active_operators_choices()
        self.assertEqual([(operator2.pk, "Cave Johnson")], operators_choices)

    def test_archive(self):
        company = CompanyFactory(is_archived=False)
        company.archive()
        self.assertTrue(Company.objects.get(id=company.id).is_archived)
