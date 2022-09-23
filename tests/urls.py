from django.urls import path
from df_portal import site
from df_portal.sidebar import SidebarItemSettings
from tests.test_app.portal.viewsets import ProductViewSet

site.brand_url = "portal:product/index"
site.brand_image = "test_app/logo.png"
site.sidebar_items = [
    SidebarItemSettings(site.viewset(ProductViewSet), "shopping-bag"),
    SidebarItemSettings(icon="shopping-bag", title="Orders", children=[
        SidebarItemSettings(site.viewset(ProductViewSet), "shopping-bag"),
        SidebarItemSettings(site.viewset(ProductViewSet), "shopping-bag"),
    ]),
]

urlpatterns = [
    path("portal/", site.urls),
]