

from django.conf.urls import url

from .views import (
    CompanyDetailView, CreateCompanyView, CreateConsumerView, CreateMaintainerView, CreateManagerView, HomeView, IssueCreateView, IssueDetailView
)


urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^company/(?P<pk>\d+)/$', CompanyDetailView.as_view(),
        name='company-details'),

    url(r'^company/add/$', CreateCompanyView.as_view(),
        name='add_company'),

    url(r'^issue/(?P<pk>\d+)/$', IssueDetailView.as_view(),
        name='issue-details'),

    url(r'^issue/add/(?P<company_id>\d+)/$', IssueCreateView.as_view(),
        name='company-add_issue'),

    url(r'^consumer/add/(?P<company_id>\d+)/$', CreateConsumerView.as_view(),
        name='company-add_consumer'),

    url(r'^manager/add/(?P<company_id>\d+)/$', CreateManagerView.as_view(),
        name='company-add_manager'),

    url(r'^maintainer/add/(?P<company_id>\d+)/$', CreateMaintainerView.as_view(),
        name='company-add_maintainer'),

]
