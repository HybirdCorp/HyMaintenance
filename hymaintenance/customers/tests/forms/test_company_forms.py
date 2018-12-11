import os
from shutil import rmtree
from tempfile import TemporaryDirectory

from PIL import Image

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.translation import gettext as _

from customers.tests.factories import CompanyFactory
from customers.tests.factories import OperatorUserFactory
from toolkit.tests import create_temporary_image

from ...forms.company import ProjectCustomizeForm
from ...models.company import Company


class ProjectCustomizeFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = OperatorUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.tmp_directory = TemporaryDirectory(
            prefix="customize-project-view-", dir=os.path.join(settings.MEDIA_ROOT, "upload/")
        )
        cls.company = CompanyFactory(name=os.path.basename(cls.tmp_directory.name))
        cls.user.operator_for.add(cls.company)

    def tearDown(self):
        rmtree(os.path.join(settings.MEDIA_ROOT, "upload/", self.company.slug_name, "logo"), ignore_errors=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp_directory.cleanup()
        super().tearDownClass()

    def __get_dict_for_post(self):
        return {"name": self.company.name, "contact": self.user.pk, "color": "#000", "logo": None}

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = ProjectCustomizeForm(instance=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"name": [expected]})

    def test_when_user_sends_valid_form(self):
        dict_for_post = self.__get_dict_for_post()

        with create_temporary_image() as tmp_file:
            dict_for_post["logo"] = tmp_file

            form = ProjectCustomizeForm(
                instance=self.company,
                data=dict_for_post,
                files={
                    "logo": SimpleUploadedFile(
                        name=os.path.basename(dict_for_post["logo"].name),
                        content=dict_for_post["logo"].read(),
                        content_type="image/jpeg",
                    )
                },
            )
            form.is_valid()
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            company = Company.objects.get(pk=self.company.pk)
            self.assertEqual(self.user, company.contact)
            self.assertEqual("#000", company.color)
            tmp_file.seek(0)
            self.assertTrue(os.path.basename(tmp_file.name), os.path.basename(company.logo.path))
            self.assertTrue(os.path.isfile(company.logo.path))
            self.assertTrue(Image.open(company.logo).width <= 125)
            self.assertTrue(Image.open(company.logo).height <= 75)
            self.company.logo.delete()
            self.company.save()

    def test_when_user_sends_an_six_characters_hexadecimal_color(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["color"] = "#f0f0f0"
        form = ProjectCustomizeForm(instance=self.company, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual("#f0f0f0", company.color)

    def test_when_user_sends_an_other_type_of_value_for_color(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["color"] = 42
        form = ProjectCustomizeForm(instance=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {"color": [_("Invalid hexadecimal color code: '42'")]})

    def test_when_user_sends_an_invalid_stringi_for_color(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["color"] = "000"
        form = ProjectCustomizeForm(instance=self.company, data=dict_for_post)
        self.assertFalse(form.is_valid())
        self.assertDictEqual(form.errors, {"color": [_("Invalid hexadecimal color code: '000'")]})

    def test_when_user_update_already_existing_logo(self):
        dict_for_post = self.__get_dict_for_post()

        with create_temporary_image() as tmp_file, create_temporary_image() as old_tmp_file:
            self.company.logo.save(os.path.basename(old_tmp_file.name), File(old_tmp_file))
            self.company.save()
            company = Company.objects.get(pk=self.company.pk)
            self.assertTrue(os.path.isfile(company.logo.path))

            dict_for_post["logo"] = tmp_file
            form = ProjectCustomizeForm(
                instance=self.company,
                data=dict_for_post,
                files={
                    "logo": SimpleUploadedFile(
                        name=os.path.basename(dict_for_post["logo"].name),
                        content=dict_for_post["logo"].read(),
                        content_type="image/jpeg",
                    )
                },
            )
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            self.assertFalse(os.path.isfile(company.logo.path))
            company = Company.objects.get(pk=self.company.pk)
            self.assertTrue(os.path.basename(tmp_file.name), os.path.basename(company.logo.path))
            self.assertTrue(os.path.isfile(company.logo.path))
            self.company.logo.delete()
            self.company.save()

    def test_when_user_dont_update_already_existing_logo(self):
        with create_temporary_image() as old_tmp_file:
            self.company.logo.save(os.path.basename(old_tmp_file.name), File(old_tmp_file))
            self.company.save()
            company = Company.objects.get(pk=self.company.pk)
            self.assertTrue(os.path.isfile(company.logo.path))

            form = ProjectCustomizeForm(instance=self.company, data=self.__get_dict_for_post())
            self.assertTrue(form.is_valid())
            self.assertTrue(form.save())
            self.assertTrue(os.path.isfile(company.logo.path))
            self.company.logo.delete()
            self.company.save()
