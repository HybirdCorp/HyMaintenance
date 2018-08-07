
from django import forms

from ..models.other_models import MaintenanceType


class MaintenanceTypeUpdateForm(forms.Form):
    maintenance_type1_name = forms.CharField(max_length=255, required=True)
    maintenance_type2_name = forms.CharField(max_length=255, required=True)
    maintenance_type3_name = forms.CharField(max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        maintenance_types = MaintenanceType.objects.order_by("id")
        if not kwargs.get("initial"):
            kwargs["initial"] = {}
        kwargs["initial"].update(
            {
                "maintenance_type1_name": maintenance_types[0].name,
                "maintenance_type2_name": maintenance_types[1].name,
                "maintenance_type3_name": maintenance_types[2].name,
            }
        )
        super().__init__(*args, **kwargs)

    def update_maintenance_types_names(self, operator=None):
        maintenance_types = MaintenanceType.objects.all().order_by("id")
        maintenance_types_names = (
            self.cleaned_data["maintenance_type1_name"],
            self.cleaned_data["maintenance_type2_name"],
            self.cleaned_data["maintenance_type3_name"],
        )

        for i, maintenance_type in enumerate(maintenance_types):
            if maintenance_type.name != maintenance_types_names[i]:
                maintenance_type.name = maintenance_types_names[i]
                maintenance_type.save()
