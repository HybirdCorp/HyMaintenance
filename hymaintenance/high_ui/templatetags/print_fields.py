
from django.template import Library
from django.utils.html import mark_safe


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
    if contract.total_type == 0:
        counter = pretty_print_minutes(contract.get_number_remaining_minutes())
        counter += " /&nbsp;" + str(contract.get_number_contract_hours()) + "h"
    elif contract.total_type == 1:
        counter = pretty_print_minutes(contract.get_number_consumed_minutes())
    return mark_safe(counter)
