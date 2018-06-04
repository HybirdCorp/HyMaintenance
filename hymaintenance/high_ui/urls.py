

from django.urls import path

from .views.dashboard import DashboardView
from .views.issue import IssueCreateView, IssueDetailView, IssueUpdateView
from .views.project import ProjectCreateView, ProjectDetailsView, ProjectUpdateView
from .views.users import (
    ConsumerCreateView, ConsumersUpdateView, ConsumerUpdateView, ManagerUserCreateView, ManagerUsersUpdateView, ManagerUserUpdateView,
    OperatorUserCreateViewWithCompany, OperatorUsersArchiveView, OperatorUsersUnarchiveView, OperatorUsersUpdateView,
    OperatorUsersUpdateViewWithCompany, OperatorUserUpdateView, OperatorUserUpdateViewWithCompany
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', DashboardView.as_view(), name='dashboard'),

    path(r'projects/<slug:company_name>/', ProjectDetailsView.as_view(),
         name='project_details'),

    path(r'projects/', ProjectCreateView.as_view(),
         name='create_project'),

    path(r'projects/<slug:company_name>/update/', ProjectUpdateView.as_view(),
         name='update_project'),

    path(r'projects/<slug:company_name>/issues/', IssueCreateView.as_view(),
         name='project-create_issue'),

    path(r'projects/<slug:company_name>/issues/<int:company_issue_number>/', IssueDetailView.as_view(),
         name='project-issue_details'),

    path(r'projects/<slug:company_name>/issues/<int:company_issue_number>/update/', IssueUpdateView.as_view(),
         name='project-update_issue'),

    path(r'projects/<slug:company_name>/consumers/', ConsumerCreateView.as_view(),
         name='project-create_consumer'),

    path(r'projects/<slug:company_name>/consumers/<int:pk>/update/', ConsumerUpdateView.as_view(),
         name='project-update_consumer'),

    path(r'projects/<slug:company_name>/consumers/update/', ConsumersUpdateView.as_view(),
         name='project-update_consumers'),

    path(r'projects/<slug:company_name>/managers/', ManagerUserCreateView.as_view(),
         name='project-create_manager'),

    path(r'projects/<slug:company_name>/managers/<int:pk>/update/', ManagerUserUpdateView.as_view(),
         name='project-update_manager'),

    path(r'projects/<slug:company_name>/managers/update/', ManagerUsersUpdateView.as_view(),
         name='project-update_managers'),

    path(r'projects/<slug:company_name>/operators/', OperatorUserCreateViewWithCompany.as_view(),
         name='project-create_operator'),

    path(r'operators/<int:pk>/update/', OperatorUserUpdateView.as_view(),
         name='update_operator'),

    path(r'projects/<slug:company_name>/operators/<int:pk>/update/', OperatorUserUpdateViewWithCompany.as_view(),
         name='project-update_operator'),

    path(r'projects/<slug:company_name>/operators/update/', OperatorUsersUpdateViewWithCompany.as_view(),
         name='project-update_operators'),

    path(r'operators/update/', OperatorUsersUpdateView.as_view(),
         name='update_operators'),

    path(r'operators/archive/', OperatorUsersArchiveView.as_view(),
         name='archive_operators'),

    path(r'operators/unarchive/', OperatorUsersUnarchiveView.as_view(),
         name='unarchive_operators'),

]
