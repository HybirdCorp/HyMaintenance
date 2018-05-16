from django.test import TestCase

from customers.tests.factories import CompanyFactory

from ...forms.consumer import MaintenanceConsumersUpdateForm
from ...models import MaintenanceConsumer
from ..factories import MaintenanceConsumerFactory


class MaintenanceConsumersUpdateFormTestCase(TestCase):

    def setUp(self):
        self.company = CompanyFactory()
        self.c2 = MaintenanceConsumerFactory(name="Chell", is_used=False,
                                             company=self.company)
        self.c1 = MaintenanceConsumerFactory(name="Glados",
                                             company=self.company)
        self.c3 = MaintenanceConsumerFactory(name="Gordon Freeman",
                                             company=self.company)
        MaintenanceConsumerFactory(name="Wheatley", is_used=False,
                                   company=self.company)

    def test_update_form_initial_values(self):
        form = MaintenanceConsumersUpdateForm(company=self.company)
        self.assertEqual(list(form.fields['consumers'].initial), [self.c1, self.c3])

    def test_update_form(self):
        form = MaintenanceConsumersUpdateForm(company=self.company,
                                              data={"consumers": [self.c1, self.c2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceConsumer.objects.get(name="Chell").is_used)
        self.assertTrue(MaintenanceConsumer.objects.get(name="Glados").is_used)
        self.assertFalse(MaintenanceConsumer.objects.get(name="Gordon Freeman").is_used)
        self.assertFalse(MaintenanceConsumer.objects.get(name="Wheatley").is_used)
