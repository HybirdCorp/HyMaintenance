

from django.urls import path

from .views import (
    CompanyDetailView, CreateConsumerView, CreateManagerUserView, CreateOperatorUserView, CreateProjectView, HomeView, IssueCreateView,
    IssueDetailView, UpdateIssueView, UpdateProjectView
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),
    path(r'company/<int:pk>/', CompanyDetailView.as_view(),
         name='company-details'),

    path(r'project/add/', CreateProjectView.as_view(),
         name='add_project'),

    path(r'project/<slug:company_name>/change/', UpdateProjectView.as_view(),
         name='change_project'),

    path(r'issue/<slug:company_name>/add/', IssueCreateView.as_view(),
         name='company-add_issue'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/', IssueDetailView.as_view(),
         name='issue-details'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/change/', UpdateIssueView.as_view(),
         name='change_issue'),

    path(r'consumer/add/<slug:company_name>/', CreateConsumerView.as_view(),
         name='company-add_consumer'),

    path(r'manager/add/<slug:company_name>/', CreateManagerUserView.as_view(),
         name='company-add_manager'),

    path(r'maintainer/add/<slug:company_name>/', CreateOperatorUserView.as_view(),
         name='company-add_operator'),

]
