

from django.urls import path

from .views import (
    CompanyDetailView, ConsumerCreateView, HomeView, IssueCreateView, IssueDetailView, IssueUpdateView, ManagerUserCreateView, OperatorUserCreateView,
    ProjectCreateView, ProjectUpdateView
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),
    path(r'company/<int:pk>/', CompanyDetailView.as_view(),
         name='company-details'),

    path(r'project/add/', ProjectCreateView.as_view(),
         name='add_project'),

    path(r'project/<slug:company_name>/change/', ProjectUpdateView.as_view(),
         name='change_project'),

    path(r'issue/<slug:company_name>/add/', IssueCreateView.as_view(),
         name='company-add_issue'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/', IssueDetailView.as_view(),
         name='issue-details'),

    path(r'issue/<slug:company_name>/<int:company_issue_number>/change/', IssueUpdateView.as_view(),
         name='change_issue'),

    path(r'consumer/add/<slug:company_name>/', ConsumerCreateView.as_view(),
         name='company-add_consumer'),

    path(r'manager/add/<slug:company_name>/', ManagerUserCreateView.as_view(),
         name='company-add_manager'),

    path(r'maintainer/add/<slug:company_name>/', OperatorUserCreateView.as_view(),
         name='company-add_operator'),

]
