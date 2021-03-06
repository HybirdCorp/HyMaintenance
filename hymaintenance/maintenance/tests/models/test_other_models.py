from django.test import TestCase

from ...models import IncomingChannel
from ...models import MaintenanceType
from ..factories import IncomingChannelFactory


class MaintenanceTypeTestCase(TestCase):
    def test_i_can_create_a_maintenance_type(self):
        MaintenanceType.objects.all().delete()
        MaintenanceType.objects.create(name="Support")
        self.assertEqual(1, MaintenanceType.objects.count())

    def test_str_is_good_for_maintenance_typ(self):
        self.assertEqual("Maintenance", str(MaintenanceType.objects.order_by("id").first()))


class IncomingChannelTestCase(TestCase):
    def test_i_can_create_an_incoming_channel(self):
        IncomingChannel.objects.create(name="Phone")
        self.assertEqual(1, IncomingChannel.objects.count())

    def test_str_is_good_for_incoming_channel(self):
        IncomingChannelFactory(name="Phone")
        self.assertEqual("Phone", str(IncomingChannel.objects.first()))
