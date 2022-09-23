import django_tables2 as tables


class ActionsColumn(tables.TemplateColumn):
    def __init__(self, **extra):
        extra.update(
            {
                "verbose_name": "",
                "template_name": "portal/common/table_actions.html",
                "orderable": False,
            }
        )
        super().__init__(**extra)

