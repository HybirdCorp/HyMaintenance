from django.test import TestCase
from django.urls import reverse

from customers.tests.factories import CompanyFactory, OperatorUserFactory


class HomeViewTestCase(TestCase):
    def test_customer_user_can_seen_this_company(self):
        company = CompanyFactory(name="First Company")
        OperatorUserFactory(email="other.man@blackmesa.com", password="azerty", first_name="Op1",
                            last_name="Op1")
        op2 = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty", first_name="Op2",
                                  last_name="Op2")
        op2.operator_for.add(company)
        client = self.client
        client.login(username="gordon.freeman@blackmesa.com", password="azerty")
        response = client.get(reverse('high_ui:home'))

        self.assertEqual(1, company.managed_by.count())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Op2 Op2")
        self.assertNotContains(response, "Op1 Op1")
