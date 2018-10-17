from django.test import TestCase

from customers.tests.factories import CompanyFactory

from ...forms.consumer import MaintenanceConsumerModelForm
from ...forms.consumer import MaintenanceConsumersListUpdateForm
from ...models import MaintenanceConsumer
from ..factories import MaintenanceConsumerFactory


class MaintenanceConsumersListUpdateFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()
        self.c2 = MaintenanceConsumerFactory(name="Chell", is_used=False, company=self.company)
        self.c1 = MaintenanceConsumerFactory(name="Glados", company=self.company)
        self.c3 = MaintenanceConsumerFactory(name="Gordon Freeman", company=self.company)
        MaintenanceConsumerFactory(name="Wheatley", is_used=False, company=self.company)

    def test_update_form_initial_values(self):
        form = MaintenanceConsumersListUpdateForm(company=self.company)
        self.assertEqual(list(form.fields["users"].initial), [self.c1, self.c3])

    def test_update_form(self):
        form = MaintenanceConsumersListUpdateForm(company=self.company, data={"users": [self.c1, self.c2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(MaintenanceConsumer.objects.get(name="Chell").is_used)
        self.assertTrue(MaintenanceConsumer.objects.get(name="Glados").is_used)
        self.assertFalse(MaintenanceConsumer.objects.get(name="Gordon Freeman").is_used)
        self.assertFalse(MaintenanceConsumer.objects.get(name="Wheatley").is_used)


class MaintenanceConsumerModelFormTestCase(TestCase):
    def setUp(self):
        self.company = CompanyFactory()

    def test_create_consumer_with_model_form(self):
        form = MaintenanceConsumerModelForm(company=self.company, data={"name": "Chell"})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(1, MaintenanceConsumer.objects.filter(name="Chell").count())

    def test_update_consumer_with_model_form(self):
        self.consumer = MaintenanceConsumerFactory(name="Gordon", company=self.company)
        form = MaintenanceConsumerModelForm(company=self.company, instance=self.consumer, data={"name": "Chell"})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(1, MaintenanceConsumer.objects.filter(pk=self.consumer.pk, name="Chell").count())
