

from django.urls import path

from .views import (
    CompanyDetailView, CreateConsumerView, CreateMaintainerView, CreateManagerView, CreateProjectView, HomeView, IssueCreateView, IssueDetailView,
    UpdateIssueView, UpdateProjectView
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),
    path(r'company/<int:pk>/', CompanyDetailView.as_view(),
         name='company-details'),

    path(r'project/add/', CreateProjectView.as_view(),
         name='add_project'),

    path(r'project/<int:company_id>/change/', UpdateProjectView.as_view(),
         name='change_project'),

    path(r'issue/<slug:company_name>/add/', IssueCreateView.as_view(),
         name='company-add_issue'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/', IssueDetailView.as_view(),
         name='issue-details'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/change/', UpdateIssueView.as_view(),
         name='change_issue'),

    path(r'consumer/add/<int:company_id>/', CreateConsumerView.as_view(),
         name='company-add_consumer'),

    path(r'manager/add/<int:company_id>/', CreateManagerView.as_view(),
         name='company-add_manager'),

    path(r'maintainer/add/<int:company_id>/', CreateMaintainerView.as_view(),
         name='company-add_maintainer'),

]
