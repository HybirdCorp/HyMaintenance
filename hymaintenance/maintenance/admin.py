from django.contrib import admin

from .models import IncomingChannel, MaintenanceConsumer, MaintenanceContract, MaintenanceCredit, MaintenanceIssue, MaintenanceType


class MaintenanceIssueAdmin(admin.ModelAdmin):
    model = MaintenanceIssue
    list_display = ('subject', 'company', 'consumer_who_ask', 'date', 'maintenance_type')

    list_filter = ('consumer_who_ask', 'company', 'maintenance_type')
    search_fields = ('subject', 'company__name')


class MaintenanceContractAdmin(admin.ModelAdmin):
    model = MaintenanceContract
    list_display = ('company', 'start', 'number_hours', 'maintenance_type',
                    'get_number_contract_hours', 'get_number_consumed_hours',
                    'get_number_remaining_hours')

    list_filter = ('company', 'maintenance_type')
    search_fields = ('company__name', )


admin.site.register(MaintenanceType)
admin.site.register(MaintenanceConsumer)
admin.site.register(IncomingChannel)
admin.site.register(MaintenanceContract, MaintenanceContractAdmin)
admin.site.register(MaintenanceIssue, MaintenanceIssueAdmin)
admin.site.register(MaintenanceCredit)
# admin.site.register(MaintenanceAnswer)
