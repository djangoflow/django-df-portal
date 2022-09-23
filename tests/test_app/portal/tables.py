import django_tables2 as tables

from tests.test_app.models import Product


class ProductTable(tables.Table):
    class Meta:
        model = Product
        fields = ["title", "price"]
        attrs = {"class": "table table-hover"}
        template_name = "django_tables2/bootstrap4.html"
