from django.test import TestCase

from ...models import IncomingChannel, MaintenanceType
from ..factories import IncomingChannelFactory, MaintenanceTypeFactory


class MaintenanceTypeTestCase(TestCase):

    def test_i_can_create_a_maintenance_type(self):
        MaintenanceType.objects.all().delete()
        MaintenanceType.objects.create(name="Support",
                                       css_class="type-support",
                                       label_for_company_detailview="Support Label")
        self.assertEqual(1, MaintenanceType.objects.count())

    def test_str_is_good_for_maintenance_typ(self):
        MaintenanceTypeFactory(name="Support")
        self.assertEqual("Support", str(MaintenanceType.objects.first()))


class IncomingChannelTestCase(TestCase):

    def test_i_can_create_an_incoming_channel(self):
        IncomingChannel.objects.create(name="Phone")
        self.assertEqual(1, IncomingChannel.objects.count())

    def test_str_is_good_for_incoming_channel(self):
        IncomingChannelFactory(name="Phone")
        self.assertEqual("Phone", str(IncomingChannel.objects.first()))
