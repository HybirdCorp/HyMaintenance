

from django.urls import path

from .views.admin import AdminView
from .views.credit import CreditCreateView
from .views.dashboard import DashboardView
from .views.general_information import GeneralInformationUpdateView
from .views.issue import IssueCreateView
from .views.issue import IssueDetailView
from .views.issue import IssueUpdateView
from .views.maintenance_type import MaintenanceTypeUpdateView
from .views.project import ProjectCreateView
from .views.project import ProjectDetailsView
from .views.project import ProjectUpdateView
from .views.users import AdminUserCreateView
from .views.users import AdminUserUpdateView
from .views.users import ConsumerCreateView
from .views.users import ConsumersUpdateView
from .views.users import ConsumerUpdateView
from .views.users import ManagerUserCreateView
from .views.users import ManagerUsersUpdateView
from .views.users import ManagerUserUpdateView
from .views.users import OperatorUserCreateView
from .views.users import OperatorUserCreateViewWithCompany
from .views.users import OperatorUsersArchiveView
from .views.users import OperatorUsersUnarchiveView
from .views.users import OperatorUsersUpdateView
from .views.users import OperatorUsersUpdateViewWithCompany
from .views.users import OperatorUserUpdateView
from .views.users import OperatorUserUpdateViewWithCompany
from .views.users import UserUpdateView


app_name = "high_ui"

urlpatterns = [
    path(r"", DashboardView.as_view(), name="dashboard"),
    path(r"admin/", AdminView.as_view(), name="admin"),
    path(r"infos/update/", GeneralInformationUpdateView.as_view(), name="update_infos"),
    path(r"counters/", MaintenanceTypeUpdateView.as_view(), name="update_maintenance_types"),
    path(r"projects/<slug:company_name>/", ProjectDetailsView.as_view(), name="project_details"),
    path(r"projects/", ProjectCreateView.as_view(), name="create_project"),
    path(r"projects/<slug:company_name>/update/", ProjectUpdateView.as_view(), name="update_project"),
    path(r"projects/<slug:company_name>/issues/", IssueCreateView.as_view(), name="project-create_issue"),
    path(
        r"projects/<slug:company_name>/issues/<int:company_issue_number>/",
        IssueDetailView.as_view(),
        name="project-issue_details",
    ),
    path(
        r"projects/<slug:company_name>/issues/<int:company_issue_number>/update/",
        IssueUpdateView.as_view(),
        name="project-update_issue",
    ),
    path(r"projects/<slug:company_name>/consumers/", ConsumerCreateView.as_view(), name="project-create_consumer"),
    path(
        r"projects/<slug:company_name>/consumers/<int:pk>/update/",
        ConsumerUpdateView.as_view(),
        name="project-update_consumer",
    ),
    path(
        r"projects/<slug:company_name>/consumers/update/",
        ConsumersUpdateView.as_view(),
        name="project-update_consumers",
    ),
    path(r"projects/<slug:company_name>/managers/", ManagerUserCreateView.as_view(), name="project-create_manager"),
    path(
        r"projects/<slug:company_name>/managers/<int:pk>/update/",
        ManagerUserUpdateView.as_view(),
        name="project-update_manager",
    ),
    path(
        r"projects/<slug:company_name>/managers/update/",
        ManagerUsersUpdateView.as_view(),
        name="project-update_managers",
    ),
    path(r"operators/", OperatorUserCreateView.as_view(), name="create_operator"),
    path(
        r"projects/<slug:company_name>/operators/",
        OperatorUserCreateViewWithCompany.as_view(),
        name="project-create_operator",
    ),
    path(r"operators/<int:pk>/update/", OperatorUserUpdateView.as_view(), name="update_operator"),
    path(
        r"projects/<slug:company_name>/operators/<int:pk>/update/",
        OperatorUserUpdateViewWithCompany.as_view(),
        name="project-update_operator",
    ),
    path(
        r"projects/<slug:company_name>/operators/update/",
        OperatorUsersUpdateViewWithCompany.as_view(),
        name="project-update_operators",
    ),
    path(r"operators/update/", OperatorUsersUpdateView.as_view(), name="update_operators"),
    path(r"operators/archive/", OperatorUsersArchiveView.as_view(), name="archive_operators"),
    path(r"operators/unarchive/", OperatorUsersUnarchiveView.as_view(), name="unarchive_operators"),
    path(r"account/update/", UserUpdateView.as_view(), name="update_user"),
    path(r"projects/<slug:company_name>/credits/", CreditCreateView.as_view(), name="project-create_credit"),
    path(r"admins/", AdminUserCreateView.as_view(), name="create_admin"),
    path(r"admins/<int:pk>/update/", AdminUserUpdateView.as_view(), name="update_admin"),
    path(r"operators/archive/", OperatorUsersArchiveView.as_view(), name="archive_operators"),
]
