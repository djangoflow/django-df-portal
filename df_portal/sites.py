from dataclasses import dataclass
from df_portal.sidebar import SidebarSettings
from df_portal.views import home_view
from df_portal.views import login_view
from df_portal.views import logout_view
from django.urls import path


@dataclass
class SiteViewInfo:
    login_name: str
    logout_name: str
    home_name: str


class PortalSite:
    brand_image = ""
    brand_url = ""
    brand_title = "Portal"

    name = "portal"
    theme = "datta-able"
    sidebar_items = []

    search_label = "Search"
    search_attrs = {
        "class": "form-control",
        "placeholder": "Search . . .",
        "style": "width: 90px;",
    }

    def __init__(self, **kwargs):
        self._registry = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def register(self, viewset_class):
        self._registry[viewset_class] = viewset_class(
            self,
        )

    def get_urls(self):
        kwargs = {"site": self}

        urls = [
            path("", home_view, name="home", kwargs=kwargs),
            path("login", login_view, name="login", kwargs=kwargs),
            path("logout", logout_view, name="logout", kwargs=kwargs),
        ]

        return urls + [
            url for viewset in self._registry.values() for url in viewset.get_urls()
        ]

    @property
    def views(self):
        return SiteViewInfo(
            login_name=f"{self.name}:login",
            logout_name=f"{self.name}:logout",
            home_name=f"{self.name}:home",
        )

    @property
    def urls(self):
        return self.get_urls(), "portal", self.name

    def sidebar(self, request):
        return SidebarSettings(
            title=self.brand_title,
            image=self.brand_image,
            url=self.brand_url or self.views.home_name,
            items=self.sidebar_items,
        ).build_sidebar(request)

    def viewset(self, klass):
        for viewset_class in self._registry.keys():
            if viewset_class is klass or viewset_class.model is klass:
                return self._registry[viewset_class]

        raise ValueError(f"Viewset {klass} is not registered")


site = PortalSite()


def register(viewset_class=None, *, portal_site=None):
    if portal_site:

        def wrapper(viewset_class_):
            portal_site.register(viewset_class_)
            return viewset_class_

        return wrapper
    else:
        site.register(viewset_class)
        return viewset_class
