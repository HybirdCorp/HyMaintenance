from datetime import datetime

from django.db import models
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce


def get_counter_name(event):
    counter_name = event.company.contracts.filter(maintenance_type=event.contract.maintenance_type).first().counter_name
    return counter_name if counter_name != "" else event.contract.maintenance_type.name


class MaintenanceEventManager(models.Manager):
    HOME_VALUES = (
        "type",
        "css_class",
        "date",
        "counter_name",
        "company__slug_name",
        "subject",
        "contract"
    )

    SPECIFIC_FILTERS = {}

    TYPE_VALUE = "event"

    def get_queryset(self):
        return super().get_queryset()\
            .select_related("contract", "contract__maintenance_type") \
            .annotate(
            counter_name=Coalesce(
                Case(
                    When(contract__counter_name__exact='', then=None),
                    When(contract__counter_name__isnull=False, then='contract__counter_name'),
                    default=None,
                    output_field=CharField()
                ),
                "contract__maintenance_type__name"
            ),
            css_class=Case(
                When(contract__maintenance_type__id__exact=1, then=Value("type-maintenance", CharField())),
                When(contract__maintenance_type__id__exact=2, then=Value("type-support", CharField())),
                When(contract__maintenance_type__id__exact=3, then=Value("type-correction", CharField())),
                default=Value("type-maintenance", CharField()),
                output_field=CharField()
            ),
        )

    def home_history_values(self, company, contracts, last_month):
        return self.get_queryset()\
            .filter(
                contract__in=contracts,
                company_id=company,
                date__lte=datetime.now(),
                date__gte=last_month,
                **self.SPECIFIC_FILTERS,)\
            .annotate(type=Value(self.TYPE_VALUE, CharField()),)\
            .values(*self.HOME_VALUES)

    def home_forecast_values(self, company, contracts):
        return self.get_queryset() \
            .filter(
                contract__in=contracts,
                company_id=company,
                date__gt=datetime.now(),
                **self.SPECIFIC_FILTERS,)\
            .annotate(type=Value(self.TYPE_VALUE, CharField()),)\
            .values(*self.HOME_VALUES)
