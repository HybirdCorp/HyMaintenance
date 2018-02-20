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
from django.urls import include, path, reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView


urlpatterns = [
    path('hymaintadmin/', admin.site.urls),
    path('high_ui/', include('high_ui.urls', namespace='high_ui')),
    path('login', auth_views.login, {'template_name': 'high_ui/login.html'}, name="login"),
    path('logout', auth_views.logout_then_login, name="logout"),

    path('', RedirectView.as_view(url=reverse_lazy('high_ui:home'), permanent=False)),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
