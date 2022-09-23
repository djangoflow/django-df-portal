from df_portal.sites import register
from df_portal.viewsets import PortalViewSet
from tests.test_app.models import Product, Tag, Order, OrderItem


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
