from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from django.http import HttpRequest
from typing import Any
from typing import List
from typing import Optional


@dataclass
class SidebarItem:
    title: str
    icon: str = ""
    url: str = ""
    is_active: bool = False
    children: List[SidebarItem] = field(default_factory=list)


@dataclass
class SidebarItemSettings:
    viewset: Optional[Any] = None
    icon: str = ""
    children: List[SidebarItemSettings] = field(default_factory=list)
    title: str = ""
    permission: str = ""
    url: str = ""

    def get_title(self):
        return self.title or self.viewset.get_model_verbose_name_plural()

    def has_permission(self, request):
        if self.children:
            return any((item.has_permission(request) for item in self.children))
        else:
            permission = self.permission or self.viewset.views.index_permission
            return request.user.has_perm(permission)

    def get_url(self):
        if self.url:
            return self.url

        if self.viewset is not None:
            return self.viewset.views.index_name

        return ""

    def is_active(self, request: HttpRequest):
        if self.children:
            return any((item.is_active(request) for item in self.children))
        else:
            return f"/{self.viewset.model_meta.model_name}/" in request.path

    def build_item(self, request):
        return SidebarItem(
            title=self.get_title(),
            icon=self.icon,
            is_active=self.is_active(request),
            url=self.get_url(),
            children=[
                item.build_item(request)
                for item in self.children
                if item.has_permission(request)
            ],
        )


@dataclass
class Sidebar:
    title: str
    image: str
    url: str
    items: List[SidebarItem]


@dataclass
class SidebarSettings:
    title: str
    image: str
    url: str
    items: List[SidebarItemSettings]

    def build_sidebar(self, request):
        return Sidebar(
            title=self.title,
            image=self.image,
            url=self.url,
            items=[
                item.build_item(request)
                for item in self.items
                if item.has_permission(request)
            ],
        )
