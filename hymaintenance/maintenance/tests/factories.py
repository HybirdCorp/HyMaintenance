
import factory

from django.utils.timezone import now

from customers.tests.factories import CompanyFactory, MaintenanceUserFactory

from ..models import IncomingChannel, MaintenanceConsumer, MaintenanceContract, MaintenanceCredit, MaintenanceIssue, MaintenanceType


class IncomingChannelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncomingChannel

    name = "Phone"


def get_default_maintenance_type():
    return MaintenanceType.objects.get(id=1)


class MaintenanceConsumerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceConsumer

    company = factory.SubFactory(CompanyFactory)
    name = "Isaac Kleiner"


class MaintenanceContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceContract

    company = factory.SubFactory(CompanyFactory)
    maintenance_type = factory.LazyFunction(get_default_maintenance_type)
    start = now()
    number_hours = 20


class MaintenanceCreditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceCredit

    company = factory.SubFactory(CompanyFactory)
    date = now()
    maintenance_type = factory.LazyFunction(get_default_maintenance_type)
    hours_number = 10


class MaintenanceIssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceIssue

    company = factory.SubFactory(CompanyFactory)
    maintenance_type = factory.LazyFunction(get_default_maintenance_type)
    incoming_channel = factory.SubFactory(IncomingChannelFactory)
    user_who_fix = factory.SubFactory(MaintenanceUserFactory)
    consumer_who_ask = factory.SubFactory(MaintenanceConsumerFactory)
    subject = "It's not working"
    date = now().date()
    maintenance_type = maintenance_type
    number_minutes = 12
    answer = "Have you tried turning it off and on again?"


def create_project(**kwargs):
    if "company" in kwargs:
        company = CompanyFactory(**kwargs['company'])
    else:
        company = CompanyFactory()
    if "contract1" in kwargs:
        contract1 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=1), **kwargs['contract1'])
    else:
        contract1 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=1))
    if "contract2" in kwargs:
        contract2 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=2), **kwargs['contract2'])
    else:
        contract2 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=2))
    if "contract3" in kwargs:
        contract3 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=3), **kwargs['contract3'])
    else:
        contract3 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=3))
    return {company, contract1, contract2, contract3}
