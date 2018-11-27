from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..fields import LowerCaseEmailField
from .company import Company


class MaintenanceUserManager(BaseUserManager):
    """Custom MaintenanceUser Manager"""

    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """Returns email in lower case

        Args:
            email
        Returns:
            the email in lower case.
        """
        return email.lower().replace(" ", "")

    def get_by_natural_key(self, username):
        """Returns MaintenanceUser by email

        Args:
            username : str the email of the user
        Returns:
            the MaintenanceUser with the current email
        """
        return self.get(email=self.normalize_email(username))

    def get_by_primary_key(self, primary_key):
        """Returns MaintenanceUser by primary key

        Args:
            primary_key : int the id
        Returns:
            the MaintenanceUser with the current primary_key
        """
        return self.get(pk=primary_key)

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves a MaintenanceUser with the given email and password.

        Args:
            email: str the email and identifier of the user
            password: str the password
            is_staff: true if operator, false else
            is_superuser: true if superuser, false else
            extra_fields: other non requiered fields like first and last name
        Returns:
            the created MaintenanceUser
        """
        if not email:
            raise ValueError(_("The given email must be set."))
        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_manager_user(self, email, password, **extra_fields):
        """Creates and saves a ManagerUser with the given email and password.

        Args:
            email: str the email and identifier of the manager
            password: str the password
            extra_fields: other non requiered fields like first and last name
        Returns:
            the created ManagerUser
        """
        return self._create_user(email, password, False, False, **extra_fields)

    def create_operator_user(self, email, password, **extra_fields):
        """Creates and saves a OperatorUser with the given email and password.

        Args:
            email: str the email and identifier of the operator
            password: str the password
            extra_fields: other non requiered fields like first and last name
        Returns:
            the created OperatorUser
        """
        return self._create_user(email, password, True, False, **extra_fields)

    def create_admin_user(self, email, password, **extra_fields):
        """Creates and saves a AdminUser with the given email and password.

        Args:
            email: str the email and identifier of the admin
            password: str the password
            extra_fields: other non requiered fields like first and last name
        Returns:
            the created AdminUser
        """
        return self._create_user(email, password, False, True, **extra_fields)

    def create_admin_operator_user(self, email, password, **extra_fields):
        """Creates and saves a AdminUseri who is an operator too with the given email and password.

        Args:
            email: str the email and identifier of the admin
            password: str the password
            extra_fields: other non requiered fields like first and last name
        Returns:
            the created AdminUser
        """
        return self._create_user(email, password, True, True, **extra_fields)

    def get_admin_users_queryset(self):
        """Gets all AdminUsers in a queryset

        Returns:
            a queryset with all the AdminUsers
        """
        return self.get_queryset().filter(is_superuser=True).order_by("first_name")

    def get_active_admin_users_queryset(self):
        """Gets all active AdminUsers in a queryset

        Returns:
            a queryset with all the active AdminUsers
        """
        return self.get_queryset().filter(is_superuser=True, is_active=True).order_by("first_name")

    def get_operator_users_queryset(self):
        """Gets all OperatorUsers in a queryset

        Returns:
            a queryset with all the OperatorUsers
        """
        return self.get_queryset().filter(is_superuser=False, is_staff=True).order_by("first_name")

    def get_active_operator_users_queryset(self):
        """Gets all active OperatorUsers in a queryset

        Returns:
            a queryset with all the active OperatorUsers
        """
        return self.get_queryset().filter(is_superuser=False, is_staff=True, is_active=True).order_by("first_name")

    def get_all_types_operator_users_queryset(self):
        """Gets all OperatorUsers and AdminUsers with are operators in a queryset

        Returns:
            a queryset with all the OperatorUsers and AdminUsers which are operators for at least one company
        """
        return self.get_queryset().filter(is_staff=True).order_by("first_name")

    def get_active_all_types_operator_users_queryset(self):
        """Gets all active OperatorUsers and AdminUsers with are operators in a queryset

        Returns:
            a queryset with all the active OperatorUsers and AdminUsers which are operators for at least one company
        """
        return self.get_queryset().filter(is_staff=True, is_active=True).order_by("first_name")

    def get_manager_users_queryset(self):
        """Gets all ManagerUsers in a queryset

        Returns:
            a queryset with all the ManagerUsers
        """
        return self.get_queryset().filter(is_staff=False, is_superuser=False).order_by("first_name")

    def get_active_manager_users_queryset(self):
        """Gets all active ManagerUsers in a queryset

        Returns:
            a queryset with all the active ManagerUsers
        """
        return (
            self.get_queryset().filter(is_staff=False, is_superuser=False).filter(is_active=True).order_by("first_name")
        )


class MaintenanceUser(AbstractBaseUser, PermissionsMixin):
    """All the users of HyMaintenance

    General:
    This class represents all the users of HyMaintenance.
    There are three types of users with differents permissions :
        * manager
        * operator
        * administrator

    Manager:
    The user is an manager when is_staff=False and is_superuser=False.

    Operator:
    The user is an operator when is_staff=True and is_superuser=False.

    Administrator:
    The user is an administrator when is_superuser=True.
    An administrator can be an operator.
    If he operates at least one company is_staff=True
    else is_staff=False

    Attributes:
        created: date of creation
        modified: date of the last modification
        first_name: string of the first name
        last_name: string of the last name
        email: string of the email, identifier to log in HyMaintenance
        phone: string of the phone nuumber
        is_staff: True if operator or administrator, False if manager
        is_active: True if active, False if archived. When archived the user can't be log
        company: company of the manager, not used for operator and administrator
        operator_for: companies operated by the operator or administrator, not used for manager
        objects: overwrite of the default object manager
    """

    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    modified = models.DateTimeField(_("Last modification date"), auto_now=True)

    first_name = models.CharField(_("First name"), max_length=50, blank=True)
    last_name = models.CharField(_("Last name"), max_length=50, blank=True)
    email = LowerCaseEmailField(
        _("Email address"),
        unique=True,
        db_index=True,
        error_messages={"unique": _("A user with that email already exists.")},
    )
    phone = models.CharField(_("phone number"), max_length=20, blank=True, null=True)

    is_staff = models.BooleanField(
        _("Staff"), default=False, help_text=_("Designates whether the user can log into this admin site.")
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )

    company = models.ForeignKey(
        Company, verbose_name=_("User's company"), null=True, blank=True, on_delete=models.PROTECT
    )

    operator_for = models.ManyToManyField(
        Company, blank=True, verbose_name=_("Managed Companies"), related_name="managed_by"
    )

    objects = MaintenanceUserManager()

    USERNAME_FIELD = "email"
    PASSWORD_MIN_LENGTH = 5
    REQUIRED_FIELDS = []

    def get_full_name(self):
        """Returns the full name of the user."""
        return get_full_name(first_name=self.first_name, last_name=self.last_name)

    def __str__(self):
        """See get_full_name method"""
        return self.get_full_name()

    def has_admin_permissions(self):
        """Returns True if the user is an AdminUser, else False"""
        return self.is_superuser

    def has_operator_permissions(self):
        """Returns True if the user is an OperatorUser, else False"""
        return self.is_staff

    def has_operator_or_admin_permissions(self):
        """Returns True if the user is an OperatorUser or an AdminUser, else False"""
        return self.is_staff or self.is_superuser


def get_full_name(*, first_name: str, last_name: str) -> str:
    """Formates the full name from the first and last names

    Formates the full name from the first and last names.
    The format is the first_name then the last_name with a space between.
    Note that you must name your parameters.

    Args:
        first_name: str a first_name
        last_name: str a last_name
    Returns:
        A string with the first_name then the last_name with a space between.
    """
    full_name = "%s %s" % (first_name, last_name)
    return full_name.strip()


def get_companies_of_operator(operator):
    """Returns a queryset of companies operated by the given operator.

    Returns a queryset of companies operated by the given operator order by id

    Args:
        operator: MaintenanceUser instance which is an operator
    Returns:
        A Company queryset with all the companies operated by the given operator order by id.
    """
    return operator.operator_for.order_by("id").prefetch_related("maintenanceuser_set")


def get_active_companies_of_operator(operator):
    """Returns a queryset of active companies operated by the given operator.

    Returns a queryset of active companies operated by the given operator order by id

    Args:
        operator: MaintenanceUser instance which is an operator
    Returns:
        A Company queryset with all the active companies operated by the given operator order by id.
    """
    return operator.operator_for.filter(is_archived=False).order_by("id").prefetch_related("maintenanceuser_set")
