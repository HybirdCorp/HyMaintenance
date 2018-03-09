

from django.urls import path

from .views import (
    CompanyDetailView, CreateCompanyView, CreateConsumerView, CreateMaintainerView, CreateManagerView, CreateProjectView, HomeView, IssueCreateView,
    IssueDetailView
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),
    path(r'company/<int:pk>/', CompanyDetailView.as_view(),
         name='company-details'),

    # DEPRECATED use CreateProject instead
    path(r'company/add/', CreateCompanyView.as_view(),
         name='add_company'),

    path(r'project/add/', CreateProjectView.as_view(),
         name='add_project'),

    path(r'issue/<int:pk>/', IssueDetailView.as_view(),
         name='issue-details'),

    path(r'issue/add/<int:company_id>/', IssueCreateView.as_view(),
         name='company-add_issue'),

    path(r'consumer/add/<int:company_id>/', CreateConsumerView.as_view(),
         name='company-add_consumer'),

    path(r'manager/add/<int:company_id>/', CreateManagerView.as_view(),
         name='company-add_manager'),

    path(r'maintainer/add/<int:company_id>/', CreateMaintainerView.as_view(),
         name='company-add_maintainer'),

]
