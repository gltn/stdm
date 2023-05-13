"""
/***************************************************************************
Name                 : Composer Data Field Selector
Description          : Widget for selecting a data field based on the
                       specified composition data source.
Date                 : 14/May/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal

from qgis.core import (
    QgsLayoutItem
)

from stdm.composer.layout_utils import LayoutUtils
from stdm.data.pg_utils import table_column_names
from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('composer/ui_composer_data_field.ui'))


class BaseComposerFieldSelector(WIDGET, BASE):
    """
    Base widget for enabling the selection of a field from a database table
    or view.
    """

    changed = pyqtSignal()

    def __init__(self, item: QgsLayoutItem, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._layout = item.layout()
        self._item = item

        # Load fields if the data source has been specified
        ds_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        if ds_name is not None:
            self._loadFields(ds_name)

        # Connect signals
        self._layout.variablesChanged.connect(self.layout_variables_changed)
        self.cboDataField.currentIndexChanged[str].connect(self.onFieldNameChanged)
        self.cboDataField.currentIndexChanged[str].connect(self.changed)

    def layout_variables_changed(self):
        """
        When the user changes the data source then update the fields.
        """
        data_source_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self._loadFields(data_source_name)

    def onFieldNameChanged(self, fieldName):
        """
        Slot raised when the field selection changes. To be overridden by
        sub-classes.
        """
        pass

    def fieldName(self):
        """
        Return the name of the selected field.
        """
        return self.cboDataField.currentText()

    def selectFieldName(self, fieldName):
        """
        Select the specified field name from the items in the combobox.
        """
        fieldIndex = self.cboDataField.findText(fieldName)

        if fieldIndex != -1:
            self.cboDataField.setCurrentIndex(fieldIndex)

    def _loadFields(self, dataSourceName):
        """
        Load fields/columns of the given data source.
        """
        if dataSourceName == "":
            self.cboDataField.clear()
            return

        columnsNames = table_column_names(dataSourceName)
        if len(columnsNames) == 0:
            return

        self.cboDataField.clear()
        self.cboDataField.addItem("")

        self.cboDataField.addItems(columnsNames)


class ComposerFieldSelector(BaseComposerFieldSelector):
    """
    Widget for selecting the field from a database table or view.
    """

    def onFieldNameChanged(self, fieldName):
        """
        Slot raised when the field selection changes.
        """
        data_source = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        if fieldName == "" or data_source is None:
            self._item.setText("[STDM Data Field]")
            self._item.set_linked_field(None)

        else:
            label_text = self._item.text()
            data_text = label_text[
                        label_text.find('[') + 1:label_text.find(']')]
            data_source = data_source + "." + self.fieldName()

            self._item.setText(
                self._item.text().replace(data_text, data_source)
            )
            self._item.set_linked_field(self.fieldName())

        self._item.refresh()
