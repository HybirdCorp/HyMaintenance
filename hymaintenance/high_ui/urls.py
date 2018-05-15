

from django.urls import path

from .views.company import CompanyDetailView
from .views.dashboard import HomeView
from .views.issue import IssueCreateView, IssueDetailView, IssueUpdateView
from .views.project import ProjectCreateView, ProjectUpdateView
from .views.users import (
    ConsumerCreateView, ManagerUserCreateView, OperatorUserCreateView, OperatorUsersArchiveView, OperatorUsersUnarchiveView, OperatorUsersUpdateView
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),
    path(r'company/<slug:company_name>/', CompanyDetailView.as_view(),
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

    path(r'operator/add/<slug:company_name>/', OperatorUserCreateView.as_view(),
         name='company-add_operator'),

    path(r'operators/change/', OperatorUsersUpdateView.as_view(),
         name='change_operators'),

    path(r'operators/archive/', OperatorUsersArchiveView.as_view(),
         name='archive_operators'),

    path(r'operators/unarchive/', OperatorUsersUnarchiveView.as_view(),
         name='unarchive_operators'),

]
