import os
from tempfile import TemporaryDirectory

import factory

from django.conf import settings
from django.test import TestCase

from customers.tests.factories import CompanyFactory
from maintenance.tests.factories import MaintenanceIssueFactory

from ...templatetags.print_files import file_name


class PrintFileNameTestCase(TestCase):

    def test_print_file_name(self):
        temp_directory = TemporaryDirectory(dir=os.path.join(*[settings.MEDIA_ROOT, 'upload/']))
        company = CompanyFactory(name=os.path.basename(temp_directory.name))
        the_file = factory.django.FileField(filename='the_cake.lie')
        issue = MaintenanceIssueFactory(company=company, context_description_file=the_file)
        self.assertEqual('the_cake.lie', file_name(issue.context_description_file))
