import re

from PyQt4.QtGui import (
    QLineEdit
, QHBoxLayout
)
from PyQt4.QtCore import pyqtSlot
from qgis.gui import (
    QgsEditorWidgetWrapper,
    QgsEditorConfigWidget,
    QgsEditorWidgetFactory,
    QgsEditorWidgetRegistry
)
from qgis.core import NULL



class QGISFieldWidget(QgsEditorWidgetWrapper):
    def value(self):
        """ Return the current value of the widget"""
        if (self.widget().text() == u"NULL"):
            return NULL
        else:
            return self.widget().text()

    def setValue(self, value):
        """ Set a value on the widget """
        if value == NULL:
            self.widget().setText('NULL')
        else:
            self.widget().setText(value)

    def createWidget(self, parent):
        """ Create a new empty widget """
        return QLineEdit(parent)

    def initWidget(self, widget):
        """
        Style the widget with a yellow background by default
        and compile the rule
        """
        rule = self.config('rule')
        self.regex = re.compile(rule)
        widget.setStyleSheet("QLineEdit { background: yellow }")
        # Connect the textChanged signal of the widget to our onTextChanged slot
        widget.textChanged.connect(self.onTextChanged)

    @pyqtSlot(unicode)
    def onTextChanged(self, newText):
        """ Will be exectued, every time the text is edited """
        # Check if the new text matches our regex and change the background
        # according to this
        if self.regex.match(newText):
            self.widget().setStyleSheet("QLineEdit { background: green }")
        else:
            self.widget().setStyleSheet("QLineEdit { background: red }")

        # Always send this signal, when the value changes, so the form knows
        # that there are changes to save. You should adapt this to your widget
        # as well!!!
        self.valueChanged.emit(newText)


class QGISFieldWidgetConfig(QgsEditorConfigWidget):
    def __init__(self, layer, idx, parent):
        QgsEditorConfigWidget.__init__(self, layer, idx, parent)
        self.setLayout(QHBoxLayout())
        self.ruleEdit = QLineEdit(self)
        # self.ruleEdit.setPlaceholderText("Write your rule here")
        # self.layout().addWidget(self.ruleEdit)

    def config(self):
        """ read the config from the QLineEdit to a dict """
        return {'rule': '[A-Z]'}

    def setConfig(self, config):
        """ Write the config from a dict to a QLineEdit """
        try:
            self.ruleEdit.setText(config['rule'])
        except KeyError:
            self.ruleEdit.setText("")


class QGISFieldWidgetFactory(QgsEditorWidgetFactory):
    def __init__(self):
        QgsEditorWidgetFactory.__init__(self, "My Widget Rules")

    def create(self, layer, fieldIdx, editor, parent):
        return QGISFieldWidget(layer, fieldIdx, editor, parent)

    def configWidget(self, layer, idx, parent):
        return QGISFieldWidgetConfig(layer, idx, parent)

    def writeConfig(self, config, elem, doc, layer, idx):
        """ Write the config to an XML element """
        elem.setAttribute('rule', config['rule'])

    def readConfig(self, elem, layer, idx):
        """ Read a config object from an XML element """
        config = dict()
        config['rule'] = elem.attribute('rule')
        return config


myFactory = QGISFieldWidgetFactory()
QgsEditorWidgetRegistry.instance().registerWidget("MyRuleWidget", myFactory)