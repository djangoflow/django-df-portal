from functools import cached_property

from django.urls import path

from df_portal.sidebar import SidebarSettings, SidebarItemSettings
from df_portal.views import login_view, logout_view


class PortalSite:
    brand_image = ""
    brand_url = ""
    brand_title = "Portal"
    name = "portal"
    theme = "datta-able"
    sidebar_items = []

    def __init__(self, **kwargs):
        self._registry = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def register(self, viewset_class):
        self._registry[viewset_class] = viewset_class(self, )

    def get_urls(self):
        urls = [
            path("login", login_view, name="login"),
            path("logout", logout_view, name="logout"),
        ]

        return urls + [
            url
            for viewset in self._registry.values()
            for url in viewset.get_urls()
        ]

    @property
    def urls(self):
        return self.get_urls(), "portal", self.name

    def sidebar(self, request):
        return SidebarSettings(
            title=self.brand_title,
            image=self.brand_image,
            url=self.brand_url,
            items=self.sidebar_items,
        ).build_sidebar(request)

    def viewset(self, viewset_class):
        return self._registry[viewset_class]


site = PortalSite()
