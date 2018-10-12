from .models import GeneralInformation


def context_data_footer(request):
    return {"general_info": GeneralInformation.objects.all().first()}
