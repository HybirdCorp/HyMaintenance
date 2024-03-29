import os
from tempfile import TemporaryDirectory
from tempfile import TemporaryFile

from maintenance.tests.factories import MaintenanceIssueFactory
from maintenance.tests.factories import create_project

from django.conf import settings
from django.core.files import File
from django.test import TestCase

from ...templatetags.print_files import file_name


class PrintFileNameTestCase(TestCase):
    def test_print_file_name(self):
        test_file_name = "the_cake.lie"
        tmp_directory = TemporaryDirectory(prefix="test-issue-", dir=os.path.join(settings.MEDIA_ROOT, "upload/"))
        company, contract, _, _ = create_project(company={"name": os.path.basename(tmp_directory.name)})

        issue = MaintenanceIssueFactory(company=company, contract=contract)
        with TemporaryFile() as tmp_file:
            issue.context_description_file.save(test_file_name, File(tmp_file), save=True)
            self.assertEqual(test_file_name, file_name(issue.context_description_file))
