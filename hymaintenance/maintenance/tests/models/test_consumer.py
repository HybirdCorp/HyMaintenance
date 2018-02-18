from django.test import TestCase

from customers.tests.factories import CompanyFactory

from ...models import MaintenanceConsumer
from ..factories import MaintenanceConsumerFactory


class MaintenanceConsumerTestCase(TestCase):

    def test_i_can_create_a_maintenance_consumer(self):
        company = CompanyFactory()
        MaintenanceConsumer.objects.create(name="Isaac Kleiner",
                                           company=company)
        self.assertEqual(1, MaintenanceConsumer.objects.count())

    def test_str_is_good_for_maintenance_consumer(self):
        MaintenanceConsumerFactory(name="Scrooge McDuck")
        self.assertEqual("Scrooge McDuck", str(MaintenanceConsumer.objects.first()))
