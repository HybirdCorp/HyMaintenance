from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext as _

from ...models import MaintenanceContract
from ...models.credit import calcul_credited_hours
from ...models.issue import calcul_consumed_minutes


class Command(BaseCommand):
    help = _(
        """This command do for each contracts :
           * check if remaining minutes reach the minutes minimum
           * if yes, send an alert email to the client"""
    )

    def handle(self, *args, **options):
        compute_contracts_times()


def compute_contracts_times(now_date=now().date()):
    contracts = MaintenanceContract.objects.all()
    for contract in contracts:
        contract.consumed_minutes = calcul_consumed_minutes(contract=contract)
        contract.credited_hours = calcul_credited_hours(contract=contract)
        contract.save()
