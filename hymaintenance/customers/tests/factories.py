
import factory

from ..models import Company
from ..models import MaintenanceUser


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = "Black Mesa"
    maintenance_contact = "G-Man"


class MaintenanceUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceUser

    password = factory.PostGenerationMethodCall("set_password", "password")
    email = factory.Sequence(lambda n: "robot{0}@example.com".format(n))


class AdminUserFactory(MaintenanceUserFactory):
    is_staff = True
    is_superuser = True
    is_active = True


class OperatorUserFactory(MaintenanceUserFactory):
    is_staff = True


class ManagerUserFactory(MaintenanceUserFactory):
    is_staff = False
