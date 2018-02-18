
import factory

from ..models import Company, MaintenanceUser


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = "Black Mesa"
    name_for_site = "The Great Black MEsa"
    maintenance_contact = "G-Man"


class MaintenanceUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MaintenanceUser

    password = factory.PostGenerationMethodCall('set_password', 'password')
    email = factory.Sequence(lambda n: 'robot{0}@example.com'.format(n))


class MaintenanceSuperUserFactory(MaintenanceUserFactory):
    is_staff = True
    is_superuser = True
    is_active = True
