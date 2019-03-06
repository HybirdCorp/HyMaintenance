from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from maintenance.models.contract import MaintenanceContract
from toolkit.email import is_credited_hours_min_exceeded
from toolkit.email import send_email_alert


class Command(BaseCommand):
    help = _(
        """This command do for each contracts :
           * check if remaining minutes reach the minutes minimum
           * if yes, send an alert email to the client"""
    )

    def handle(self, *args, **options):
        contracts = MaintenanceContract.objects.all()
        for contract in contracts:
            if contract.recipient and contract.credited_hours_min and is_credited_hours_min_exceeded(contract):
                send_email_alert(contract)
