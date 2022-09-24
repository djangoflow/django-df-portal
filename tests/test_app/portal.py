from df_portal.sites import register
from df_portal.viewsets import PortalViewSet
from django_select2 import forms as s2forms
from tests.test_app.models import Order
from tests.test_app.models import OrderItem
from tests.test_app.models import Product
from tests.test_app.models import Tag


@register
class ProductViewSet(PortalViewSet):
    model = Product
    table_columns = ["title", "price"]
    filterset_search_fields = ["title__icontains", "description__icontains"]


@register
class TagViewSet(PortalViewSet):
    model = Tag
    table_columns = ["title"]
    filterset_search_fields = ["title__icontains"]


@register
class OrderViewSet(PortalViewSet):
    model = Order
    table_columns = ["user", "total_amount", "created_at"]
    filterset_search_fields = ["user__email__icontains"]


@register
class OrderItemViewSet(PortalViewSet):
    model = OrderItem
    table_columns = ["product", "count", "price", "order"]
    filterset_fields = ["order"]
    filterset_search_fields = ["user__email__icontains"]
    default_form_widgets = {
        "product": s2forms.ModelSelect2Widget(
            search_fields=ProductViewSet.filterset_search_fields
        )
    }
