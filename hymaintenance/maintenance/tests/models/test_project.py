from django.test import TestCase

from customers.models import Company

from ...models import MaintenanceContract
from ..factories import create_project


class CreateProjectTestCase(TestCase):

    def test_i_can_create_a_project_with_some_parameters(self):
        company, contract1, _contract2, _contract3 = create_project(
            company={"name": "aperture Science"},
            contract1={"counter_name": "experiment"},
            contract2={"visible": False},
            contract3={"disabled": True})
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(3, MaintenanceContract.objects.all().count())

    def test_i_can_create_a_project_without_parameter(self):
        company, contract1, _contract2, _contract3 = create_project()
        self.assertEqual(1, Company.objects.all().count())
        self.assertEqual(3, MaintenanceContract.objects.all().count())
