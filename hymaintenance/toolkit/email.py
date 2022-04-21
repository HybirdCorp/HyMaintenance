from high_ui.models import GeneralInformation
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from toolkit.pretty_print import pretty_print_minutes

from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _


email_content = """Hello {recipient},

There are {hours} hours left on you {counter} contract.
Please contact {sender} to add credits on your contract.

{name} team"""


def is_credited_hours_min_exceeded(contract):
    if contract.total_type == AVAILABLE_TOTAL_TIME and contract.email_alert:
        return contract.get_number_remaining_hours() <= contract.credited_hours_min
    return False


def create_email_alert(contract):
    general_info = GeneralInformation.objects.all().order_by("id").first()
    hours = pretty_print_minutes(contract.get_number_remaining_minutes())
    counter = contract.get_counter_name()
    name = general_info.name
    subject = _(
        "{name} HyMaintenance, there are {hours} left on your {counter} contract".format(
            name=name, hours=hours, counter=counter
        )
    )
    sender = contract.company.contact.email if contract.company.contact else general_info.email
    recipient_email = contract.recipient.email
    recipient_name = "{} {}".format(contract.recipient.first_name, contract.recipient.last_name)
    content = _(email_content.format(recipient=recipient_name, hours=hours, counter=counter, sender=sender, name=name))

    email = EmailMessage(subject, content, sender, [recipient_email])
    return email


def send_email_alert(contract):
    email = create_email_alert(contract)
    email.send()
