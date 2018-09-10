"""hymaintenance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView

from high_ui.views.base import get_context_data_footer


urlpatterns = [
    path("hymaintadmin/", admin.site.urls),
    path("high_ui/", include("high_ui.urls", namespace="high_ui")),
    path(
        "login",
        auth_views.LoginView.as_view(template_name="auth/login.html", extra_context=get_context_data_footer()),
        name="login",
    ),
    path("logout", auth_views.logout_then_login, name="logout"),
    path(
        "password_reset",
        auth_views.PasswordResetView.as_view(
            template_name="auth/password_reset_form.html", extra_context=get_context_data_footer()
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html", extra_context=get_context_data_footer()
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html", extra_context=get_context_data_footer()
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complet.html", extra_context=get_context_data_footer()
        ),
        name="password_reset_complete",
    ),
    path("", RedirectView.as_view(url=reverse_lazy("high_ui:dashboard"), permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))] + staticfiles_urlpatterns()
