from stdm.ui.forms.editor_extension import (
    AbstractEditorExtension,
    data_context
)


@data_context('SALaR Bukidnon', 'Enumerator')
class EnumeratorEditorExtension(AbstractEditorExtension):
    def post_init(self):
        # Print some message
        self.last_name = self.widget('last_name')
        self.last_name.setEnabled(False)

        first_name = self.widget('other_names')
        first_name.textChanged.connect(self.on_name_changed)

    def on_name_changed(self, txt):
        if txt == 'John':
            self.last_name.setEnabled(True)
        else:
            self.last_name.setEnabled(False)

    def validate(self):
        self.insert_warning_notification('Not valid!!')
        return False

