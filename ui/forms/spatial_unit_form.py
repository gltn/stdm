import re
import time
from PyQt4.QtGui import (
    QLineEdit,
    QDateEdit,
    QTextEdit,
    QDateTimeEdit,
    QComboBox,
    QDoubleSpinBox,
    QApplication,
    QLabel
)
from PyQt4.QtCore import pyqtSlot
from qgis.gui import (
    QgsEditorWidgetWrapper,
    QgsEditorConfigWidget,
    QgsEditorWidgetFactory,
    QgsEditorWidgetRegistry
)
from qgis.core import (
    NULL,
    QgsFeatureRequest,
    QgsMessageLog
)
from stdm.ui.forms.widgets import ColumnWidgetRegistry
from stdm.settings import (
    current_profile
)
from stdm.utils.util import (
    setComboCurrentIndexWithItemData,
    format_name
)
from stdm.data.configuration import entity_model
from stdm.data.mapping import MapperMixin

from stdm.ui.customcontrols.relation_line_edit import (
    AdministrativeUnitLineEdit,
    RelatedEntityLineEdit,
    RelatedEntityLineEdit
)
from qgis.utils import (
    iface,
    QGis
)



class STDMFieldWidget():
    def __init__(self):
        self.layer = None
        self.data_source = None
        self.entity = None
        self.mapper = None

    def set_layer(self, layer=None):
        self.layer = layer

    def set_layer_source(self, source):
        curr_profile = current_profile()
        self.data_source = source
        self.entity = curr_profile.entity_by_name(
            source
        )

    def qgis_version(self):
        qgis_version = '.'.join(
            re.findall("[-+]?\d+[\.]?\d*", QGis.QGIS_VERSION[:4])
        )
        return float(qgis_version)

    def crete_widget(self, column, parent):
        # Get widget factory to be used in value formatter
        # Get widget factory

        column_obj = self.entity.columns[column]
        column_widget = ColumnWidgetRegistry.create(
            column_obj,
            parent
        )

        return column_widget

    def set_mapper(self):
        model = entity_model(self.entity)
        self.mapper = MapperMixin(model)

    def init_widget(self, column, widget):
        # Add widget to MapperMixin collection
        column_obj = self.entity.columns[column]
        self.mapper.addMapping(
            column,
            widget,
            column_obj.mandatory,
            pseudoname=column_obj.header()
        )

    def set_widget(self):
        for column, widget_type in self.widget_mapping().iteritems():
            idx = self.layer.fieldNameIndex(column)
            if self.qgis_version() < 2.14:
                self.layer.editFormConfig().setWidgetType(idx, widget_type)
            else:
                self.layer.setEditorWidgetV2(idx, widget_type)

    def widget_mapping(self):
        widget_mapping = {}
        for c in self.entity.columns.values():
            if c.TYPE_INFO == 'SERIAL':
                widget_mapping[c.name] = 'Hidden'
            else:
                widget_mapping[c.name] = 'stdm_widgets'
        return widget_mapping


def get_layer_source(layer):
    """
    Get the layer table name if the source is from the database.
    :param layer: The layer for which the source is checked
    :type QGIS vectorlayer
    :return: The table name of the layer
    :rtype: String or None
    """
    if layer is not None:
        source = layer.source()
        vals = dict(re.findall('(\S+)="?(.*?)"? ', source))
        try:
            table = vals['table'].split('.')
            tableName = table[1].strip('"')
            return tableName
        except KeyError:
            return None

STDM_WIDGET = STDMFieldWidget()

class WidgetWrapper(QgsEditorWidgetWrapper):

    def __init__(self, layer, fieldIdx, editor, parent):
        super(WidgetWrapper, self).__init__(
            layer, fieldIdx, editor, parent
        )
        self.layer = layer
        self.formatted_widget = None
        self.parent = parent

    def value(self):
        """ Return the current value of the widget"""
        if isinstance(self.widget(), QLineEdit):
            return self.widget().text()
        elif isinstance(self.widget(), QComboBox):
            return self.widget().itemData(self.widget().currentIndex())
        elif isinstance(self.widget(), AdministrativeUnitLineEdit):
            if not self.control.current_item is None:
                return self.widget().current_item.id
            return None
        elif isinstance(self.widget(), RelatedEntityLineEdit):
            if not self.control.current_item is None:
                return self.widget().current_item.id
            return None
        elif isinstance(self.widget(), QDateTimeEdit):
            return self.widget().dateTime().toPyDateTime()
        elif isinstance(self.widget(), QDateEdit):
            return self.widget().date().toPyDate()
        elif isinstance(self.widget(), QTextEdit):
            return self.widget().toPlainText()
        elif isinstance(self.widget(), QDoubleSpinBox):
            self.widget().value()
        else:
            return self.widget().value()

    def setValue(self, value):
        """ Set a value on the widget """
        if value == NULL:
            pass
        elif isinstance(value, QComboBox) and value != NULL:
            self.widget().setValue(value)
        elif isinstance(self.widget(), QLineEdit) and value != NULL:
            self.widget().setText(value)
        elif isinstance(self.widget(), QComboBox) and value != NULL:
            setComboCurrentIndexWithItemData(self.widget(), value)
        elif isinstance(self.widget(), AdministrativeUnitLineEdit) and value != NULL:
            self.widget().load_current_item_from_id(value)
        elif isinstance(self.widget(), RelatedEntityLineEdit) and value != NULL:
            self.widget().load_current_item_from_id(value)
        elif isinstance(self.widget(), QDateEdit) and value != NULL:
            self.widget().setDate(value)
        elif isinstance(self.widget(), QDateTimeEdit) and value != NULL:
            self.widget().setDateTime(value)
        elif isinstance(self.widget(), QTextEdit) and value != NULL:
            self.widget().setText(value)
        elif isinstance(self.widget(), QDoubleSpinBox) and value != NULL:
            self.widget().setValue(value)

    def createWidget(self, parent):
        """ Create a new empty widget """
        self.formatted_widget = STDM_WIDGET.crete_widget(
            self.field().name(), parent
        )
        return self.formatted_widget

    def valid(self):
        return True

    def initWidget(self, widget):
        """
        Style the widget with a yellow background by default
        and compile the rule
        """
        STDM_WIDGET.init_widget(
            self.field().name(), self.formatted_widget
        )
        title = format_name(STDM_WIDGET.entity.short_name)
        title = QApplication.translate(
            'STDMFieldWidget',
            '{} Records'.format(title)
        )
        # Set title and format labels for qgis form
        if self.parent.parent() is not None:
            self.parent.parent().setWindowTitle(title)
            for label in self.parent.parent().findChildren(QLabel):
                text = label.text()
                formatted_text = format_name(text)
                label.setText(formatted_text)

    @pyqtSlot(unicode)
    def onTextChanged(self, newText):
        """ Will be exectued, every time the text is edited """
        pass

class QGISFieldWidgetConfig(QgsEditorConfigWidget):
    def __init__(self, layer, idx, parent):
        QgsEditorConfigWidget.__init__(
            self, layer, idx, parent
        )


class QGISFieldWidgetFactory(QgsEditorWidgetFactory):
    def __init__(self, name):
        QgsEditorWidgetFactory.__init__(self, name)

    def create(self, layer, fieldIdx, editor, parent):
        widget_wrapper = WidgetWrapper(
            layer, fieldIdx, editor, parent
        )
        return widget_wrapper

    def configWidget(self, layer, idx, parent):
        return QGISFieldWidgetConfig(layer, idx, parent)

WIDGET_NAME = QApplication.translate(
    'STDMFieldWidget', 'STDM Widgets'
)
WIDGET_FACTORY = QGISFieldWidgetFactory(WIDGET_NAME)
QgsEditorWidgetRegistry.instance().registerWidget(
    "stdm_widgets", WIDGET_FACTORY
)