
from django.template import Library
from django.utils.html import format_html
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from customers.models.user import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models.consumer import MaintenanceConsumer
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME
from toolkit.pretty_print import pretty_print_minutes


register = Library()


@register.simple_tag
def pretty_print_minutes_tag(value, use_long_minute_format=False):
    return pretty_print_minutes(value, use_long_minute_format)


@register.simple_tag
def pretty_print_contract_counter(contract):
    counter = ""
    if contract.total_type == AVAILABLE_TOTAL_TIME:
        counter = pretty_print_minutes(contract.get_number_remaining_minutes())
        counter += " /&nbsp;" + str(contract.get_number_contract_hours()) + "h"
    elif contract.total_type == CONSUMMED_TOTAL_TIME:
        counter = pretty_print_minutes(contract.get_number_consumed_minutes())
    return mark_safe(counter)


@register.filter
def print_operator_projects(operator_id):
    operator = MaintenanceUser.objects.get(id=operator_id)
    projects = get_companies_of_operator(operator)
    if projects:
        projects_names = [project.name for project in projects]
        if len(projects_names) == 1:
            return format_html(_("project: {}"), projects_names[0])
        else:
            return format_html(_("projects: {}"), ", ".join(projects_names))
    return format_html(_("project: none"))


@register.simple_tag
def hide_disabled_consumer(consumer_id, unused_consumers_ids):
    if consumer_id == "" or consumer_id not in unused_consumers_ids:
        return ""
    else:
        return mark_safe("disabled_consumer")


@register.simple_tag
def hide_disabled_operator(operator_id, unused_operators_ids):
    if operator_id == "" or operator_id not in unused_operators_ids:
        return ""
    else:
        return mark_safe("disabled_operator")


@register.simple_tag
def extra_credit_subject(value):
    return format_html(_("Add extra {duration}"), duration=format_html('<span class="duration">{}h</span>', value))


@register.simple_tag
def pretty_print_name(first_name, last_name):
    name = ""
    if first_name:
        name += format_html("{}", first_name.title())
    if last_name:
        name += format_html(" {}.", last_name[0].upper())
    return name
