from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DFPortalConfig(AppConfig):
    name = "df_portal"
    verbose_name = _("DjangoFlow Portal")

    def ready(self):
        super().ready()
        self.module.autodiscover()
