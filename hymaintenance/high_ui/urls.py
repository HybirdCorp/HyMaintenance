

from django.urls import path

from .views.admin import AdminView
from .views.contact import ContactView
from .views.credit import CreditCreateView
from .views.credit import CreditDeleteView
from .views.credit import CreditUpdateView
from .views.dashboard import DashboardView
from .views.general_information import GeneralInformationUpdateView
from .views.issue import IssueArchiveView
from .views.issue import IssueCreateView
from .views.issue import IssueDetailView
from .views.issue import IssueUpdateView
from .views.maintenance_type import MaintenanceTypeUpdateView
from .views.project import EmailAlertUpdateView
from .views.project import ProjectCreateView
from .views.project import ProjectCustomizeView
from .views.project import ProjectDetailsView
from .views.project import ProjectListArchiveView
from .views.project import ProjectListUnarchiveView
from .views.project import ProjectUpdateView
from .views.users.create_user import AdminUserCreateView
from .views.users.create_user import ConsumerCreateView
from .views.users.create_user import ManagerUserCreateView
from .views.users.create_user import OperatorUserCreateView
from .views.users.create_user import OperatorUserCreateViewWithCompany
from .views.users.update_profile import UserUpdateView
from .views.users.update_user import AdminUserUpdateView
from .views.users.update_user import ConsumerUpdateView
from .views.users.update_user import ManagerUserUpdateView
from .views.users.update_user import OperatorUserUpdateView
from .views.users.update_user import OperatorUserUpdateViewWithCompany
from .views.users_list.update_users_list import AdminUsersListArchiveView
from .views.users_list.update_users_list import AdminUsersListUnarchiveView
from .views.users_list.update_users_list import AdminUsersListUpdateView
from .views.users_list.update_users_list import ConsumersListUpdateView
from .views.users_list.update_users_list import ManagerUsersListUpdateView
from .views.users_list.update_users_list import OperatorUsersListArchiveView
from .views.users_list.update_users_list import OperatorUsersListUnarchiveView
from .views.users_list.update_users_list import OperatorUsersListUpdateView
from .views.users_list.update_users_list import OperatorUsersListUpdateViewWithCompany


app_name = "high_ui"

urlpatterns = [
    path(r"", DashboardView.as_view(), name="dashboard"),
    path(r"admin/", AdminView.as_view(), name="admin"),
    path(r"infos/update/", GeneralInformationUpdateView.as_view(), name="update_infos"),
    path(r"projects/<slug:company_name>/contact", ContactView.as_view(), name="project-contact"),
    path(r"counters/", MaintenanceTypeUpdateView.as_view(), name="update_maintenance_types"),
    path(r"projects/<slug:company_name>/", ProjectDetailsView.as_view(), name="project_details"),
    path(r"projects/", ProjectCreateView.as_view(), name="create_project"),
    path(r"admin/projects/archive/", ProjectListArchiveView.as_view(), name="archive_projects"),
    path(r"admin/projects/unarchive/", ProjectListUnarchiveView.as_view(), name="unarchive_projects"),
    path(r"projects/<slug:company_name>/update/", ProjectUpdateView.as_view(), name="update_project"),
    path(r"projects/<slug:company_name>/customize/", ProjectCustomizeView.as_view(), name="customize_project"),
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
    path(
        r"projects/<slug:company_name>/issues/<int:company_issue_number>/archive/",
        IssueArchiveView.as_view(),
        name="project-archive_issue",
    ),
    path(r"projects/<slug:company_name>/consumers/", ConsumerCreateView.as_view(), name="project-create_consumer"),
    path(
        r"projects/<slug:company_name>/consumers/<int:pk>/update/",
        ConsumerUpdateView.as_view(),
        name="project-update_consumer",
    ),
    path(
        r"projects/<slug:company_name>/consumers/update/",
        ConsumersListUpdateView.as_view(),
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
        ManagerUsersListUpdateView.as_view(),
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
        OperatorUsersListUpdateViewWithCompany.as_view(),
        name="project-update_operators",
    ),
    path(r"operators/update/", OperatorUsersListUpdateView.as_view(), name="update_operators"),
    path(r"operators/archive/", OperatorUsersListArchiveView.as_view(), name="archive_operators"),
    path(r"operators/unarchive/", OperatorUsersListUnarchiveView.as_view(), name="unarchive_operators"),
    path(r"account/update/", UserUpdateView.as_view(), name="update_user"),
    path(r"projects/<slug:company_name>/credits/", CreditCreateView.as_view(), name="project-create_credit"),
    path(
        r"projects/<slug:company_name>/credits/<int:pk>/update/",
        CreditUpdateView.as_view(),
        name="project-update_credit",
    ),
    path(
        r"projects/<slug:company_name>/credits/<int:pk>/delete/",
        CreditDeleteView.as_view(),
        name="project-delete_credit",
    ),
    path(r"admins/", AdminUserCreateView.as_view(), name="create_admin"),
    path(r"admins/<int:pk>/update/", AdminUserUpdateView.as_view(), name="update_admin"),
    path(r"admins/update/", AdminUsersListUpdateView.as_view(), name="update_admins"),
    path(r"admins/archive/", AdminUsersListArchiveView.as_view(), name="archive_admins"),
    path(r"admins/unarchive/", AdminUsersListUnarchiveView.as_view(), name="unarchive_admins"),
    path(
        r"projects/<slug:company_name>/email-alert/", EmailAlertUpdateView.as_view(), name="project-update_email_alert"
    ),
]
