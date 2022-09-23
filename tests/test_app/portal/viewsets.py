from df_portal import site
from df_portal.viewsets import PortalViewSet
from tests.test_app.models import Product
from tests.test_app.portal.filters import ProductFilter
from tests.test_app.portal.tables import ProductTable


class ProductViewSet(PortalViewSet):
    model = Product
    table_class = ProductTable
    filterset_class = ProductFilter


site.register(ProductViewSet)
