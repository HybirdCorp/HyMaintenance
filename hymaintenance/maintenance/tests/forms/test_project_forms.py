from django.test import TestCase

from customers.tests.factories import MaintenanceUserFactory
from maintenance.tests.factories import MaintenanceTypeFactory


class ProjectCreateFormTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = MaintenanceUserFactory(email="gordon.freeman@blackmesa.com",
                                          password="azerty")
        # TO CHANGE : Refs #51
        MaintenanceTypeFactory(name="support",
                               css_class="type-support",
                               label_for_company_detailview="support")
        MaintenanceTypeFactory(name="maintenance",
                               css_class="type-maintenance",
                               label_for_company_detailview="maintenance")
        MaintenanceTypeFactory(name="correction",
                               css_class="type-correction",
                               label_for_company_detailview="correction")
