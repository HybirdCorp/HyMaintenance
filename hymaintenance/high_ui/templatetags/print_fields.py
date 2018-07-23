
from django.template import Library
from django.utils.html import format_html
from django.utils.html import mark_safe
from django.utils.translation import ugettext as _

from customers.models.user import MaintenanceUser
from customers.models.user import get_companies_of_operator
from maintenance.models.consumer import MaintenanceConsumer
from maintenance.models.contract import AVAILABLE_TOTAL_TIME
from maintenance.models.contract import CONSUMMED_TOTAL_TIME


register = Library()


@register.simple_tag
def pretty_print_minutes(value, use_long_minute_format=False):
    negative_op = ""
    if value == "":
        return ""
    if value < 0:
        value = abs(value)
        negative_op = "-"

    value = int(value)
    minutes = value % 60
    hours = value // 60
    if minutes != 0:
        if hours != 0:
            return "%s%sh%02d" % (negative_op, hours, minutes)
        if use_long_minute_format:
            return "%s%s mins" % (negative_op, minutes)
        return "%s%sm" % (negative_op, minutes)
    return "%s%sh" % (negative_op, value // 60)


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
            return _("project:") + " " + projects_names[0]
        else:
            return _("projects:") + " " + ", ".join(projects_names)
    return _("project:") + " " + _("none")


@register.filter
def hide_disabled_consumer(consumer_id):
    if consumer_id == "" or MaintenanceConsumer.objects.get(id=consumer_id).is_used:
        return ""
    else:
        return mark_safe('class="disabled_consumer"')


@register.filter
def hide_disabled_operator(operator_id):
    if operator_id == "" or MaintenanceUser.objects.get(id=operator_id).is_active:
        return ""
    else:
        return mark_safe('class="disabled_operator"')


@register.simple_tag
def extra_credit_subject(value):
    return format_html(_("Add extra {duration}"), duration=format_html('<span class="duration">{}h</span>', value))
