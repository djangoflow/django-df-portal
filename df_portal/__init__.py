from django.utils.module_loading import autodiscover_modules

from df_portal.sites import site


def autodiscover():
    autodiscover_modules('portal', register_to=site)
