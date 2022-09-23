from django.urls import path, include
from df_portal import site
from df_portal.sidebar import SidebarItemSettings
from tests.test_app.portal import ProductViewSet, OrderViewSet, TagViewSet, OrderItemViewSet

site.name = "portal2"
site.brand_image = "test_app/logo.png"
site.sidebar_items = [
    SidebarItemSettings(site.viewset(ProductViewSet), "book"),
    SidebarItemSettings(site.viewset(OrderViewSet), "shopping-cart"),
    SidebarItemSettings(site.viewset(OrderItemViewSet), "shopping-cart"),
    SidebarItemSettings(icon="settings", title="Settings", children=[
        SidebarItemSettings(site.viewset(TagViewSet), "tag"),
    ]),
]

urlpatterns = [
    path("select2/", include("django_select2.urls")),
    path("portal/", site.urls),
]