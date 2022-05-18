import os
from shutil import rmtree
from tempfile import TemporaryDirectory

from customers.tests.factories import CompanyFactory
from customers.tests.factories import OperatorUserFactory
from PIL import Image
from toolkit.tests import create_temporary_image

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.translation import gettext as _

from ...forms.company import ProjectCustomizeForm
from ...forms.project import ProjectListArchiveForm
from ...forms.project import ProjectListUnarchiveForm
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
        return {
            "name": self.company.name,
            "has_custom_color": True,
            "contact": self.user.pk,
            "dark_font_color": False,
            "color": "#000",
            "logo": None,
        }

    def test_all_required_fields_by_sending_a_empty_update_form(self):
        form = ProjectCustomizeForm(instance=self.company, data={})
        self.assertFalse(form.is_valid())
        expected = _("This field is required.")
        self.assertDictEqual(form.errors, {"name": [expected]})

    def test_contact_queryset(self):
        form = ProjectCustomizeForm(instance=self.company, data={})
        self.assertEqual([self.user], list(form.fields["contact"]._queryset))

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

    def test_when_user_sends_with_default_color(self):
        dict_for_post = self.__get_dict_for_post()
        dict_for_post["has_custom_color"] = False
        form = ProjectCustomizeForm(instance=self.company, data=dict_for_post)
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())
        company = Company.objects.get(pk=self.company.pk)
        self.assertEqual(None, company.color)

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

    def test_when_user_sends_an_invalid_string_for_color(self):
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


class ProjectArchiveFormTestCase(TestCase):
    def setUp(self):
        self.c1 = CompanyFactory(name="Black Mesa", is_archived=True)
        self.c2 = CompanyFactory(name="Aperture Science")

    def test_archive_form_queryset(self):
        form = ProjectListArchiveForm(data={"projects": []})
        project_choices = [project[0] for project in form.fields["projects"].choices if len(project) > 0]
        self.assertIn(self.c2.pk, project_choices)
        self.assertNotIn(self.c1.pk, project_choices)

    def test_archive_form_update_new_status(self):
        form = ProjectListArchiveForm(data={"projects": [self.c2]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(Company.objects.get(pk=self.c1.pk).is_archived)
        self.assertTrue(Company.objects.get(pk=self.c2.pk).is_archived)

    def test_archive_form_dont_update_when_no_new_status(self):
        form = ProjectListArchiveForm(data={"projects": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(Company.objects.get(pk=self.c1.pk).is_archived)
        self.assertFalse(Company.objects.get(pk=self.c2.pk).is_archived)

    def test_unarchive_form_queryset(self):
        form = ProjectListUnarchiveForm(data={"projects": []})
        project_choices = [project[0] for project in form.fields["projects"].choices if len(project) > 0]
        self.assertNotIn(self.c2.pk, project_choices)
        self.assertIn(self.c1.pk, project_choices)

    def test_unarchive_form_update_new_status(self):
        form = ProjectListUnarchiveForm(data={"projects": [self.c1]})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertFalse(Company.objects.get(pk=self.c1.pk).is_archived)
        self.assertFalse(Company.objects.get(pk=self.c2.pk).is_archived)

    def test_unarchive_form_dont_update_when_no_new_status(self):
        form = ProjectListUnarchiveForm(data={"projects": []})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(Company.objects.get(pk=self.c1.pk).is_archived)
        self.assertFalse(Company.objects.get(pk=self.c2.pk).is_archived)
