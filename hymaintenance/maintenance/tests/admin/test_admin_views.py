

from django.test import Client, TestCase

from customers.tests.factories import CompanyFactory, MaintenanceSuperUserFactory

from ..factories import (
    IncomingChannelFactory, MaintenanceConsumerFactory, MaintenanceContractFactory, MaintenanceCreditFactory, MaintenanceIssueFactory,
    MaintenanceTypeFactory
)


class AdminMaintenanceViewTestCase(TestCase):

    def test_listview_admin_pages(self):
        user = MaintenanceSuperUserFactory()
        client = Client()
        client.login(username=user.email, password='password')

        admin_pages = [
            "/hymaintadmin/maintenance/maintenanceconsumer/",
            "/hymaintadmin/maintenance/maintenancecontract/",
            "/hymaintadmin/maintenance/maintenanceissue/",
            "/hymaintadmin/maintenance/maintenancecredit/",
            "/hymaintadmin/maintenance/maintenancetype/",
            "/hymaintadmin/maintenance/incomingchannel/",
        ]
        for page in admin_pages:
            resp = client.get(page, follow=True)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, "<!DOCTYPE html")

    def test_detailview_admin_pages(self):
        user = MaintenanceSuperUserFactory()
        client = Client()
        client.login(username=user.email, password='password')

        company = CompanyFactory()
        maintenance_type = MaintenanceTypeFactory()
        contract = MaintenanceContractFactory(company=company,
                                              maintenance_type=maintenance_type,
                                              number_hours=2)
        credit = MaintenanceCreditFactory(company=company,
                                          maintenance_type=maintenance_type,
                                          hours_number=5)
        channel = IncomingChannelFactory()
        consumer = MaintenanceConsumerFactory()
        issue = MaintenanceIssueFactory()

        admin_pages = [
            "/hymaintadmin/maintenance/maintenanceconsumer/%s/change" % consumer.pk,
            "/hymaintadmin/maintenance/maintenancecontract/%s/change" % contract.pk,
            "/hymaintadmin/maintenance/maintenanceissue/%s/change" % issue.pk,
            "/hymaintadmin/maintenance/maintenancecredit/%s/change" % credit.pk,
            "/hymaintadmin/maintenance/maintenancetype/%s/change" % maintenance_type.pk,
            "/hymaintadmin/maintenance/incomingchannel/%s/change" % channel.pk,
        ]
        for page in admin_pages:
            resp = client.get(page, follow=True)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, "<!DOCTYPE html")
