
from django.test import TestCase

from maintenance.tests.factories import MaintenanceContractFactory, MaintenanceIssueFactory, get_default_maintenance_type

from ...models import Company


class CompanyTestCase(TestCase):

    def test_i_can_create_a_company(self):
        Company.objects.create(name="Hybird",
                               maintenance_contact="One Men in Company")
        self.assertEqual(1, Company.objects.count())

    def test_i_cant_save_again_issue_number(self):
        company = Company.objects.create(name="Hybird",
                                         maintenance_contact="One Men in Company")
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
        MaintenanceContractFactory(company=company)
        MaintenanceIssueFactory(company=company, maintenance_type=get_default_maintenance_type())
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
