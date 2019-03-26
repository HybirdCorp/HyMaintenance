
import factory

from django.utils.timezone import now

from customers.tests.factories import CompanyFactory
from customers.tests.factories import OperatorUserFactory

from ..models import IncomingChannel
from ..models import MaintenanceConsumer
from ..models import MaintenanceContract
from ..models import MaintenanceCredit
from ..models import MaintenanceIssue
from ..models import MaintenanceType
from ..models.contract import AVAILABLE_TOTAL_TIME
from ..models.contract import CONSUMMED_TOTAL_TIME


def create_project(**kwargs):
    if "company" in kwargs:
        company = CompanyFactory(**kwargs["company"])
    else:
        company = CompanyFactory()
    if "contract1" in kwargs:
        contract1 = MaintenanceContractFactory(
            company=company, maintenance_type=MaintenanceType.objects.get(id=1), **kwargs["contract1"]
        )
    else:
        contract1 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=1))
    if "contract2" in kwargs:
        contract2 = MaintenanceContractFactory(
            company=company, maintenance_type=MaintenanceType.objects.get(id=2), **kwargs["contract2"]
        )
    else:
        contract2 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=2))
    if "contract3" in kwargs:
        contract3 = MaintenanceContractFactory(
            company=company, maintenance_type=MaintenanceType.objects.get(id=3), **kwargs["contract3"]
        )
    else:
        contract3 = MaintenanceContractFactory(company=company, maintenance_type=MaintenanceType.objects.get(id=3))
    return company, contract1, contract2, contract3


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
    is_used = True


class MaintenanceContractFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceContract

    company = factory.SubFactory(CompanyFactory)
    maintenance_type = factory.LazyFunction(get_default_maintenance_type)
    start = now()

    class Params:
        credit_counter = False

    @factory.lazy_attribute
    def total_type(self):
        if self.credit_counter or self.credited_hours:
            return AVAILABLE_TOTAL_TIME
        else:
            return CONSUMMED_TOTAL_TIME

    @factory.lazy_attribute
    def credited_hours(self):
        if self.credit_counter:
            return 20
        else:
            return None

    @factory.post_generation
    def create_credit(self, create, extracted, **kwargs):
        if not create:
            return
        if self.total_type == AVAILABLE_TOTAL_TIME:
            MaintenanceCreditFactory(
                hours_number=self.credited_hours, contract=self, date=self.start, company=self.company
            )


class MaintenanceCreditFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceCredit

    company = factory.SubFactory(CompanyFactory)
    date = now()
    contract = factory.SubFactory(MaintenanceContractFactory, credit_counter=True)
    hours_number = 10


class MaintenanceIssueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceIssue

    company = factory.SubFactory(CompanyFactory)
    contract = factory.SubFactory(MaintenanceContractFactory)
    incoming_channel = factory.SubFactory(IncomingChannelFactory)
    user_who_fix = factory.SubFactory(OperatorUserFactory)
    consumer_who_ask = factory.SubFactory(MaintenanceConsumerFactory)
    subject = "It's not working"
    date = now().date()
    number_minutes = 12
    answer = "Have you tried turning it off and on again?"
