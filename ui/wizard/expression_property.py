from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QApplication, QDialogButtonBox, QMessageBox, \
    QTabWidget, QLabel
from qgis.core import (
    QgsExpression,
    QgsVectorLayer,
    QGis
)
from qgis.utils import (
    iface
)
from qgis.gui import QgsExpressionBuilderDialog

class ExpressionProperty(QgsExpressionBuilderDialog):
    """
    Enables the QGIS expression builder dialog to add expression in columns.
    """
    recordSelected = pyqtSignal(int)

    def __init__(
            self, layer, form_fields, parent=None,
            context=QApplication.translate("ExpressionProperty", "Configuration")
    ):

        QgsExpressionBuilderDialog.__init__(
            self, layer, form_fields['expression'], parent, context
        )
        self.expression = form_fields['expression']
        self.output_data_type = form_fields['output_data_type']
        self._ref_layer = layer

        btn_box = self.findChild(QDialogButtonBox)

        if not btn_box is None:
            btn_ok = btn_box.button(QDialogButtonBox.Ok)
            if not btn_ok is None:
                btn_ok.setText(QApplication.translate("ExpressionProperty",
                                                  "Select"))


    def _features_select(self):
        """
        Generator function that returns features based on user-defined
        expression.
        """
        exp = QgsExpression(self.expressionText())
        print exp.quotedValue(), ' test ', exp.quotedString()
        if exp.hasParserError():
            raise Exception(exp.parserErrorString())

        exp.prepare(self._ref_layer.pendingFields())

        for f in self._ref_layer.getFeatures():
            value = exp.evaluate(f)
            print value, f.id()
            break
            if bool(value):
                yield f

    def layer(self):
        return self._ref_layer

    def expression_text(self):
        return self.expressionText()

    def get_output_data_type(self):
        tab_widget = [
            w for w in self.expressionBuilder().children()
            if isinstance(w, QTabWidget)
        ]
        text = None
        data_type = None
        exp_tab = tab_widget[0].widget(0)
        for label in exp_tab.findChildren(QLabel):
            if label.objectName() == 'lblPreview':
                text = label.text()
        try:
            text = float(text)
        except Exception:
            try:
                text = int(text)
            except Exception:
                pass
        if isinstance(text, float):
            return 'float'
        elif isinstance(text, int):
            return 'int'
        else:
            return 'str'

    def accept(self):
        """
        Override so that we can capture features matching the specified
        expression and raise record selected event for the mapper to
        capture.
        """
        self.get_output_data_type()
        self.expressionText()
        self.done(1)
        # features = self._features_select()
        # #
        # # count = 0
        # for f in features:
        #     fid = -1
        #     try:
        #         fid = f.attribute("id")
        #     except KeyError:
        #         pass
        #
        #     if fid != -1:
        #         self.recordSelected.emit(fid)

