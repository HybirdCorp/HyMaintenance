
from django.test import TestCase

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
