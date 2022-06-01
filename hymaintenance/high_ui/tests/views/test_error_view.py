from customers.tests.factories import AdminUserFactory
from customers.tests.factories import ManagerUserFactory
from maintenance.tests.factories import create_project

from django.core.exceptions import PermissionDenied
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase
from django.test import override_settings
from django.urls import path
from django.utils.translation import ugettext_lazy as _

from hymaintenance.urls import urlpatterns as real_urlpatterns

from ...views.errors import internal_error_handler
from ...views.errors import not_found_handler


def permission_denied_view(request):
    raise PermissionDenied


def bad_request_view(request):
    raise SuspiciousOperation


urlpatterns = real_urlpatterns + [
    path('404/', not_found_handler),
    path('500/', internal_error_handler),
    path('403/', permission_denied_view),
    path('400/', bad_request_view),
]


handler403 = 'high_ui.views.errors.permission_denied_handler'
handler400 = 'high_ui.views.errors.bad_request_handler'


@override_settings(ROOT_URLCONF=__name__)
class ErrorViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = AdminUserFactory(email="gordon.freeman@blackmesa.com", password="azerty")
        cls.company, _, _, _ = create_project()
        cls.manager = ManagerUserFactory(company=cls.company)

    def test_404(self):
        response = self.client.get('/404/')

        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, _('Page not found'), status_code=404)

    def test_500(self):
        response = self.client.get('/500/')

        self.assertContains(response, '500', status_code=500)
        self.assertContains(response, _('Server Error'), status_code=500)

    def test_403(self):
        response = self.client.get('/403/')

        self.assertContains(response, '403', status_code=403)
        self.assertContains(response, _('Forbidden'), status_code=403)

    def test_400(self):
        response = self.client.get('/400/')

        self.assertContains(response, '400', status_code=400)
        self.assertContains(response, _('Bad Request'), status_code=400)

    def test_404__has_operator(self):
        self.client.force_login(self.user)
        response = self.client.get('/404/')

        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, _('Page not found'), status_code=404)
        self.assertContains(response, _('Administration'), status_code=404)

    def test_500__has_operator(self):
        self.client.force_login(self.user)
        response = self.client.get('/500/')

        self.assertContains(response, '500', status_code=500)
        self.assertContains(response, _('Server Error'), status_code=500)
        self.assertContains(response, _('Administration'), status_code=500)

    def test_403__has_operator(self):
        self.client.force_login(self.user)
        response = self.client.get('/403/')

        self.assertContains(response, '403', status_code=403)
        self.assertContains(response, _('Forbidden'), status_code=403)
        self.assertContains(response, _('Administration'), status_code=403)

    def test_400__has_operator(self):
        self.client.force_login(self.user)
        response = self.client.get('/400/')

        self.assertContains(response, '400', status_code=400)
        self.assertContains(response, _('Bad Request'), status_code=400)
        self.assertContains(response, _('Administration'), status_code=400)

    def test_404__has_manager(self):
        self.client.force_login(self.manager)
        response = self.client.get('/404/')

        self.assertContains(response, '404', status_code=404)
        self.assertContains(response, _('Page not found'), status_code=404)
        self.assertNotContains(response, _('Administration'), status_code=404)

    def test_500__has_manager(self):
        self.client.force_login(self.manager)
        response = self.client.get('/500/')

        self.assertContains(response, '500', status_code=500)
        self.assertContains(response, _('Server Error'), status_code=500)
        self.assertNotContains(response, _('Administration'), status_code=500)

    def test_403__has_manager(self):
        self.client.force_login(self.manager)
        response = self.client.get('/403/')

        self.assertContains(response, '403', status_code=403)
        self.assertContains(response, _('Forbidden'), status_code=403)
        self.assertNotContains(response, _('Administration'), status_code=403)

    def test_400__has_manager(self):
        self.client.force_login(self.manager)
        response = self.client.get('/400/')

        self.assertContains(response, '400', status_code=400)
        self.assertContains(response, _('Bad Request'), status_code=400)
        self.assertNotContains(response, _('Administration'), status_code=400)
