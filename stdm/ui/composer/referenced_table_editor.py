"""
/***************************************************************************
Name                 : ReferencedTableEditor
Description          : Widget for specifying table and column properties for
                       composer items which reference data from tables or
                       views that are linked to the primary data source
                       through a common (linked) field.
Date                 : 2/January/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from qgis.PyQt.QtCore import (
    QMetaObject,
    QSize,
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QLabel,
    QWidget
)

from stdm.composer.layout_utils import LayoutUtils
from stdm.data.pg_utils import (
    table_column_names,
    pg_tables,
    TABLES,
    VIEWS
)
from stdm.settings import (
    current_profile
)
from stdm.utils.util import (
    profile_and_user_views
)
from stdm.ui.gui_utils import GuiUtils


class LinkedTableProps(object):
    """
    Container for user selections in the ReferencedTableEditor widget.
    """

    def __init__(self, **kwargs):
        self._linked_table = kwargs.pop("linked_table", "")
        self._source_field = kwargs.pop("source_field", "")
        self._linked_field = kwargs.pop("linked_field", "")

    @property
    def linked_table(self):
        return self._linked_table

    @linked_table.setter
    def set_linked_table(self, table):
        self._linked_table = table

    @property
    def source_field(self):
        return self._source_field

    @source_field.setter
    def set_source_field(self, field):
        self._source_field = field

    @property
    def linked_field(self):
        return self._linked_field

    @linked_field.setter
    def set_linked_field(self, field):
        self._linked_field = field


class ReferencedTableEditor(QWidget):
    referenced_table_changed = pyqtSignal(str)

    changed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi()

        self._block_changed = False

        #self.cbo_ref_table.setInsertPolicy(QComboBox.InsertAlphabetically)

        self.cbo_ref_table.currentIndexChanged[str].connect(self._on_ref_table_changed)
        self.cbo_source_field.currentTextChanged.connect(self._on_changed)
        self.cbo_source_field.currentIndexChanged.connect(self._on_source_field_changed)

        self.cbo_ref_table.currentIndexChanged[str].connect(self._on_changed)
        self.cbo_referencing_col.currentTextChanged.connect(self._on_changed)

        # Tables that will be omitted from the referenced table list
        self._omit_ref_tables = []

        self._layout = None

        self.prev_source_field_index = -1


    def _on_changed(self):
        if not self._block_changed:
            self.changed.emit()

    def _on_source_field_changed(self, index: int):
        self.prev_source_field_index = index

    def add_omit_table(self, table):
        """
        Add a table name that will be omitted from the list of referenced
        tables.
        :param table: Table name that will be omitted
        :type table: str
        """
        if not table in self._omit_ref_tables:
            self._omit_ref_tables.append(table)

    def add_omit_tables(self, tables):
        """
        Add a list of tables that will be omitted from the list of referenced
        tables.
        :param tables: Table names to be omitted.
        :type tables: list
        """
        for t in tables:
            self.add_omit_table(t)

    @property
    def omit_tables(self):
        """
        :return: Returns a list of tables that are to be omitted from the
        list of referenced tables.
        """
        return self._omit_ref_tables

    def setupUi(self):
        self.setObjectName("ReferencedTableEditor")
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QLabel(self)
        self.label_2.setMaximumSize(QSize(100, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.cbo_source_field = QComboBox(self)
        self.cbo_source_field.setMinimumSize(QSize(0, 30))
        self.cbo_source_field.setObjectName("cbo_source_field")
        self.gridLayout.addWidget(self.cbo_source_field, 2, 1, 1, 1)
        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_3 = QLabel(self)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.cbo_referencing_col = QComboBox(self)
        self.cbo_referencing_col.setMinimumSize(QSize(0, 30))
        self.cbo_referencing_col.setObjectName("cbo_referencing_col")
        self.gridLayout.addWidget(self.cbo_referencing_col, 3, 1, 1, 1)
        self.cbo_ref_table = QComboBox(self)
        self.cbo_ref_table.setMinimumSize(QSize(0, 30))
        self.cbo_ref_table.setObjectName("cbo_ref_table")
        self.gridLayout.addWidget(self.cbo_ref_table, 1, 1, 1, 1)

        self.label_2.setText(QApplication.translate("ReferencedTableEditor",
                                                    "References"))
        self.label.setText(QApplication.translate("ReferencedTableEditor",
                                                  "Data source field"))
        self.label_3.setText(QApplication.translate("ReferencedTableEditor",
                                                    "Referencing"))

        self._current_profile = current_profile()
        self._current_profile_tables = []

        if self._current_profile is not None:
            self._current_profile_tables =self._current_profile.user_table_names()

        # Connect signals
        QMetaObject.connectSlotsByName(self)
        self.cbo_ref_table.currentIndexChanged[str].connect(self.load_referencing_fields)


    def set_layout(self, layout):
        self._layout = layout
        self._layout.variablesChanged.connect(self.layout_variables_changed)

    def layout_variables_changed(self):
        """
        When the user changes the data source then update the fields.
        """
        data_source_name = LayoutUtils.get_stdm_data_source_for_layout(self._layout)
        self.load_data_source_fields(data_source_name)

        # referenced_table_name = LayoutUtils.get_stdm_referenced_table_for_layout(self._layout)
        # self.load_referencing_fields(referenced_table_name)

    def on_data_source_changed(self, data_source_name):
        """
        Loads data source fields for the given data source name.
        """
        self.load_data_source_fields(data_source_name)

    def _on_ref_table_changed(self, table):
        """
        Raise signal when the referenced table changes.
        :param table: Selected table name.
        :type table: str
        """
        self.referenced_table_changed.emit(table)

    def properties(self):
        """
        :returns: Returns the user-defined mapping of linked table and column
        pairings.
        :rtype: LinkedTableProps
        """
        l_table = self.cbo_ref_table.currentText()
        s_field = self.cbo_source_field.currentText()
        l_field = self.cbo_referencing_col.currentText()

        return LinkedTableProps(linked_table=l_table,
                                source_field=s_field,
                                linked_field=l_field)

    def set_properties(self, table_props):
        """
        Sets the combo selection based on the text in the linked table
        object properties.
        :param table_props: Object containing the linked table information.
        :type table_props: LinkedTableProps
        """
        self._block_changed = True
        print('>> SET_PROPERTIES >> ', table_props.linked_table, '<<<< ')
        GuiUtils.set_combo_current_index_by_text(self.cbo_ref_table, table_props.linked_table)
        GuiUtils.set_combo_current_index_by_text(self.cbo_source_field, table_props.source_field)
        GuiUtils.set_combo_current_index_by_text(self.cbo_referencing_col, table_props.linked_field)
        self._block_changed = False

    def load_data_source_fields(self, data_source_name):
        """
        Load fields/columns of the given data source.
        """
        if data_source_name == "":
            self.clear()
            return

        current_text = self.cbo_source_field.currentText()

        columns_names = table_column_names(data_source_name)

        if len(columns_names) == 0:
            return

        self.cbo_source_field.blockSignals(True)

        self.cbo_source_field.clear()
        self.cbo_source_field.addItem("")
        self.cbo_source_field.addItems(columns_names)

        self.cbo_source_field.blockSignals(False)

        self._set_selected_text(self.cbo_source_field, current_text)

        # if self.prev_source_field_index != -1:
        #     self.cbo_source_field.setCurrentIndex(self.prev_source_field_index)

    def load_referencing_fields(self, ref_table_name: str):

        current_text = self.cbo_referencing_col.currentText()

        self.cbo_referencing_col.clear()

        #data_source_index = self.cbo_source_field.currentIndex()
        # self.on_data_source_changed(
        #     self.cbo_source_field.itemData(data_source_index)
        # )

        if not ref_table_name:
            return

        column_names = table_column_names(ref_table_name)

        self.cbo_referencing_col.clear()
        self.cbo_referencing_col.addItem("")
        self.cbo_referencing_col.addItems(column_names)

        if current_text:
            self._set_selected_text(self.cbo_referencing_col, current_text)

    def clear(self):
        """
        Resets combo box selections.
        """
        self._reset_combo_index(self.cbo_ref_table)
        self._reset_combo_index(self.cbo_referencing_col)
        self._reset_combo_index(self.cbo_source_field)

    def _reset_combo_index(self, combo):
        if combo.count > 0:
            combo.setCurrentIndex(0)

    def reset_referenced_table(self):
        self._reset_combo_index(self.cbo_ref_table)

    def load_link_tables(self, reg_exp=None, source=TABLES | VIEWS):
        self.cbo_ref_table.clear()
        self.cbo_ref_table.addItem("")

        ref_tables = []
        source_tables = []
        # Table source
        if (TABLES & source) == TABLES:
            ref_tables.extend(pg_tables(exclude_lookups=True))

            for t in ref_tables:
                # Ensure we are dealing with tables in the current profile
                # if not t in self._current_profile_tables:
                #     continue

                # Assert if the table is in the list of omitted tables
                if t in self._omit_ref_tables:
                    continue

                if not reg_exp is None:
                    if reg_exp.indexIn(t) >= 0:
                        source_tables.append(t)
                else:
                    source_tables.append(t)

        # View source
        if (VIEWS & source) == VIEWS:
            profile_user_views = profile_and_user_views(self._current_profile)
            source_tables = source_tables + profile_user_views

        self.cbo_ref_table.addItems(source_tables)


    def _set_selected_text(self, cbox: QComboBox, text:str):
        """
        Select the specified field name from the items in the combobox.
        """
        text_index = cbox.findText(text)

        if text_index != -1:
            cbox.setCurrentIndex(text_index)