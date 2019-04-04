
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from django.utils.translation import gettext as _

from ...models import MaintenanceContract
from ...models import MaintenanceCredit


class Command(BaseCommand):
    help = _(
        """This command do for each contracts :
           * check if remaining minutes reach the minutes minimum
           * if yes, send an alert email to the client"""
    )

    def handle(self, *args, **options):
        check_and_apply_credit_recurrence()


def check_and_apply_credit_recurrence(now_date=now().date()):
    contracts = MaintenanceContract.objects.all()
    for contract in contracts:
        if contract.has_credit_recurrence() and now_date >= contract.recurrence_next_date:
            MaintenanceCredit.objects.create(
                contract=contract,
                company=contract.company,
                date=now_date,
                hours_number=contract.hours_to_credit,
                subject=_("{}'s credit recurrence".format(now_date.strftime("%B"))),
            )
            contract.recurrence_last_date = contract.recurrence_next_date
            contract.recurrence_next_date = contract.get_recurrence_next_date()
            contract.save()
