from crispy_forms import helper, layout


class BaseFilterFormHelper(helper.FormHelper):
    form_method = "GET"

    def __init__(self, form=None):
        super().__init__(form)
        self.include_media = False
        self.form_id = "filter-form"

        self.layout = layout.Layout(
            layout.Row(
                *[layout.Column(field) for field in form.fields.keys()],
                layout.Div(
                    layout.Submit("submit", "Filter", css_class="btn-table-filter"),
                ),
            ),
        )
