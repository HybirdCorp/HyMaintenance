from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from ...models.user import MaintenanceUser


email = "admin@mail.com"
password = "adminadmin"


class Command(BaseCommand):
    help = _(
        """Create a admin user if it does not exist. The default login are:
           * email: "{}"
           * password: "{}"
           Please do not forget to change this information."""
    ).format(email, password)

    def handle(self, *args, **options):
        admins = MaintenanceUser.objects.filter(is_superuser=True)
        if not admins:
            admin = MaintenanceUser.objects.create(is_superuser=True, is_staff=True, is_active=True, email=email)
            admin.set_password(password)
            admin.save()

            self.stdout.write(
                self.style.SUCCESS(
                    _(
                        """Successfully create an admin user. the login are:
                       * email: "{}"
                       * password: "{}"
                       Please do not forget to change this information."""
                    ).format(email, password)
                )
            )
        if admins == 1:
            self.stdout.write(self.style.ERROR(_("There is already one admin user.")))
        else:
            self.stdout.write(self.style.ERROR(_("There are already {} admin users.").format(admins.count())))
