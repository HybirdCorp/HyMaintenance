
from django.db import models
from django.urls import reverse


# TODO: clean up the semantics of the 2 "names"
class Company(models.Model):
    name = models.CharField("name", max_length=255)
    maintenance_contact = models.CharField("name of internal contact", default="", max_length=500)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('high_ui:company-details', args=[self.pk])
