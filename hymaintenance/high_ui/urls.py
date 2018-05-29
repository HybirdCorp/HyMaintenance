

from django.urls import path

from .views.company import CompanyDetailView
from .views.dashboard import HomeView
from .views.issue import IssueCreateView, IssueDetailView, IssueUpdateView
from .views.project import ProjectCreateView, ProjectUpdateView
from .views.users import (
    ConsumerCreateView, ConsumersUpdateView, ManagerUserCreateView, ManagerUsersUpdateView, OperatorUserCreateView, OperatorUsersArchiveView,
    OperatorUsersUnarchiveView, OperatorUsersUpdateView, OperatorUsersUpdateViewWithCompany
)


app_name = 'high_ui'

urlpatterns = [
    path(r'', HomeView.as_view(), name='home'),

    path(r'projects/<slug:company_name>/', CompanyDetailView.as_view(),
         name='project_details'),

    path(r'projects/add/', ProjectCreateView.as_view(),
         name='add_project'),

    path(r'projects/<slug:company_name>/update/', ProjectUpdateView.as_view(),
         name='update_project'),

    path(r'projects/<slug:company_name>/issues/add/', IssueCreateView.as_view(),
         name='project-add_issue'),

    path(r'projects/<slug:company_name>/issues/<int:company_issue_number>/', IssueDetailView.as_view(),
         name='project-issue_details'),

    path(r'projects/<slug:company_name>/issues/<int:company_issue_number>/update/', IssueUpdateView.as_view(),
         name='project-update_issue'),

    path(r'projects/<slug:company_name>/consumers/add/', ConsumerCreateView.as_view(),
         name='project-add_consumer'),

    path(r'projects/<slug:company_name>/consumers/update/', ConsumersUpdateView.as_view(),
         name='project-update_consumers'),

    path(r'projects/<slug:company_name>/managers/add/', ManagerUserCreateView.as_view(),
         name='project-add_manager'),

    path(r'projects/<slug:company_name>/managers/update/', ManagerUsersUpdateView.as_view(),
         name='project-update_managers'),

    path(r'projects/<slug:company_name>/operators/add/', OperatorUserCreateView.as_view(),
         name='project-add_operator'),

    path(r'projects/<slug:company_name>/operators/update/', OperatorUsersUpdateViewWithCompany.as_view(),
         name='project-update_operators'),

    path(r'operators/update/', OperatorUsersUpdateView.as_view(),
         name='update_operators'),

    path(r'operators/archive/', OperatorUsersArchiveView.as_view(),
         name='archive_operators'),

    path(r'operators/unarchive/', OperatorUsersUnarchiveView.as_view(),
         name='unarchive_operators'),

]

#   path(r'projects/<slug:company_name>/consumers/<int:pk>/update/', ConsumerUpdateView.as_view(),
#        name='project-update_consumer'),
#   path(r'projects/<slug:company_name>/managers/<int:pk>/update/', ManagerUserUpdateView.as_view(),
#        name='project-update_manager'),
#   path(r'operators/<int:pk>/update/', OperatorUserUpdateView.as_view(),
#        name='update_operator'),
