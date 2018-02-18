
from django.test import TestCase

from ...models import Company


class CompanyTestCase(TestCase):

    def test_i_can_create_a_company(self):
        Company.objects.create(name="Hybird",
                               name_for_site="Great Hybird",
                               maintenance_contact="One Men in Company")
        self.assertEqual(1, Company.objects.count())
