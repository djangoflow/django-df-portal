from df_portal.sites import site
from django.utils.module_loading import autodiscover_modules


def autodiscover():
    autodiscover_modules("portal", register_to=site)
