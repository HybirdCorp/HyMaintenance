from django.contrib import admin

from .models import IncomingChannel
from .models import MaintenanceConsumer
from .models import MaintenanceContract
from .models import MaintenanceCredit
from .models import MaintenanceIssue
from .models import MaintenanceType


class MaintenanceIssueAdmin(admin.ModelAdmin):
    model = MaintenanceIssue
    list_display = ("subject", "company", "consumer_who_ask", "date", "contract")

    list_filter = ("consumer_who_ask", "company", "contract")
    search_fields = ("subject", "company__name")


class MaintenanceContractAdmin(admin.ModelAdmin):
    model = MaintenanceContract
    list_display = (
        "company",
        "start",
        "credited_hours",
        "maintenance_type",
        "get_number_contract_hours",
        "get_number_consumed_hours",
        "get_number_remaining_hours",
    )

    list_filter = ("company", "maintenance_type")
    search_fields = ("company__name",)


admin.site.register(MaintenanceType)
admin.site.register(MaintenanceConsumer)
admin.site.register(IncomingChannel)
admin.site.register(MaintenanceContract, MaintenanceContractAdmin)
admin.site.register(MaintenanceIssue, MaintenanceIssueAdmin)
admin.site.register(MaintenanceCredit)
# admin.site.register(MaintenanceAnswer)
