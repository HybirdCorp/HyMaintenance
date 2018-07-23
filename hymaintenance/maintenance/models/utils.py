def get_counter_name(event):
    counter_name = event.company.contracts.filter(maintenance_type=event.maintenance_type).first().counter_name
    return counter_name if counter_name != "" else event.maintenance_type.name
