
import factory

from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory

from ..models import IncomingChannel, MaintenanceConsumer, MaintenanceContract, MaintenanceCredit, MaintenanceIssue, MaintenanceType


class MaintenanceTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceType

    name = "Support"
    css_class = "type-support"


class IncomingChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncomingChannel

    name = "Phone"


class MaintenanceConsumerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceConsumer

    company = factory.SubFactory(CompanyFactory)
    name = "Isaac Kleiner"


class MaintenanceContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceContract

    company = factory.SubFactory(CompanyFactory)
    maintenance_type = factory.SubFactory(MaintenanceTypeFactory)
    start = now()
    number_hours = 20


class MaintenanceCreditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceCredit

    company = factory.SubFactory(CompanyFactory)
    date = now()
    maintenance_type = factory.SubFactory(MaintenanceTypeFactory)
    hours_number = 10


class MaintenanceIssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceIssue

    company = factory.SubFactory(CompanyFactory)
    maintenance_type = factory.SubFactory(MaintenanceTypeFactory)
    incoming_channel = factory.SubFactory(IncomingChannelFactory)
    user_who_fix = factory.SubFactory(MaintenanceUserFactory)
    consumer_who_ask = factory.SubFactory(MaintenanceConsumerFactory)
    subject = "It's not working"
    date = now().date()
    maintenance_type = maintenance_type
    number_minutes = 12
    answer = "Have you tried turning it off and on again?"
