from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..fields import LowerCaseEmailField
from .company import Company


class MaintenanceUserManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        return email.lower().replace(' ', '')

    def get_by_natural_key(self, username):
        return self.get(email=self.normalize_email(username))

    def get_by_primary_key(self, primary_key):
        return self.get(pk=primary_key)

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The given email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_manager_user(self, email, password, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_operator_user(self, email, password, **extra_fields):
        return self._create_user(email, password, True, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def get_operator_users_queryset(self):
        return self.get_queryset().filter(company__isnull=True).order_by("first_name")


class MaintenanceUser(AbstractBaseUser, PermissionsMixin):
    created = models.DateTimeField(_("Creation date"), auto_now_add=True)
    modified = models.DateTimeField(_("Last modification date"), auto_now=True)

    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    email = LowerCaseEmailField(_('email address'), unique=True, db_index=True,
                                error_messages={'unique': _("A user with that username already exists.")})

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))

    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.PROTECT)

    operator_for = models.ManyToManyField(Company, blank=True, verbose_name=_("Managed Companies"),
                                          related_name="managed_by")

    objects = MaintenanceUserManager()

    USERNAME_FIELD = 'email'
    PASSWORD_MIN_LENGTH = 5
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return get_full_name(first_name=self.first_name,
                             last_name=self.last_name)

    def get_short_name(self):
        "Returns the short name for the user."
        return self.last_name


def get_full_name(*, first_name: str, last_name: str) -> str:
    full_name = '%s %s' % (first_name, last_name)
    return full_name.strip()


def get_companies_of_operator(operator):
    return operator.operator_for.order_by('id').prefetch_related("maintenanceuser_set")
