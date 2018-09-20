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
