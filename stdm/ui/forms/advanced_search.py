"""
/***************************************************************************
Name                 : Advanced Search
Description          : Advanced Search form.
Date                 : 10/June/2018
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
    Qt,
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QApplication,
    QPushButton)

from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from stdm.data.pg_utils import table_column_names
from stdm.ui.forms.editor_dialog import EntityEditorDialog
from stdm.utils.util import entity_display_columns, format_name


class AdvancedSearch(EntityEditorDialog):
    search_triggered = pyqtSignal(dict)

    def __init__(self, entity, parent, initial_values: dict = None):
        super().__init__(entity, parent=parent)
        self.parent = parent

        self.initial_values = initial_values or {}

        for k, v in self.initial_values.items():
            for mapper in self._attrMappers:
                if mapper.attributeName() == k:
                    mapper.valueHandler().setValue(v)

    def _init_gui(self, show_str_tab: bool, is_party_unit: bool=False):
        # Setup base elements
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName('glMain')
        self.gridLayout.addLayout(
            self.vlNotification, 0, 0, 1, 1
        )

        column_widget_area = self._setup_columns_content_area()

        self.gridLayout.addWidget(
            column_widget_area, 1, 0, 1, 1
        )
        # Add notification for mandatory columns if applicable
        next_row = 2
        # Set title
        search_trans = self.tr('Advanced Search')
        if self._entity.label is not None:
            if self._entity.label != '':
                title_str = self._entity.label
            else:
                title_str = format_name(self._entity.short_name)
        else:
            title_str = format_name(self._entity.short_name)

        title = '{0} {1}'.format(title_str, search_trans)
        self.do_not_check_dirty = True
        self.setWindowTitle(title)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setObjectName('buttonBox')
        self.gridLayout.addWidget(
            self.buttonBox, next_row, 0, 1, 1
        )

        self.buttonBox.setOrientation(Qt.Horizontal)

        self.search = QPushButton(
            QApplication.translate(
                'EntityEditorDialog', 'Search'
            )
        )
        self.buttonBox.addButton(
            self.search, QDialogButtonBox.ActionRole
        )
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Close | QDialogButtonBox.Reset
        )
        self.search.clicked.connect(self.on_search)
        self.buttonBox.button(QDialogButtonBox.Close).clicked.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.reset)

    def reset(self):
        """
        Resets the dialog back to an empty/no filter status
        """
        for column in self._entity.columns.values():
            if column.name in entity_display_columns(self._entity):

                if column.name == 'id':
                    continue

                if not column.name in self.attribute_mappers:
                    continue

                handler = self.attribute_mappers[
                    column.name].valueHandler()

                handler.setValue(handler.default())

    def on_search(self):
        """
        Builds a dictionary of the desired search values and emits the search_triggered signal
        """
        self.search_triggered.emit(self.current_search_data())

    def current_search_data(self) -> dict:
        """
        Returns a dictionary representing the current search data
        """
        search_data = {}
        for column in self._entity.columns.values():
            if column.name in entity_display_columns(self._entity):

                if column.name == 'id':
                    continue

                if not column.name in self.attribute_mappers:
                    continue

                handler = self.attribute_mappers[
                    column.name].valueHandler()

                value = handler.value()

                if value != handler.default() and bool(value):
                    search_data[column.name] = value

        return search_data

    def _setup_columns_content_area(self):
        # Only use this if entity supports documents
        # self.entity_tab_widget = None
        self.doc_widget = None

        self.entity_scroll_area = QScrollArea(self)
        self.entity_scroll_area.setFrameShape(QFrame.NoFrame)
        self.entity_scroll_area.setWidgetResizable(True)
        self.entity_scroll_area.setObjectName('scrollArea')

        # Grid layout for controls
        self.gl = QGridLayout(self.scroll_widget_contents)
        self.gl.setObjectName('gl_widget_contents')

        # Append column labels and widgets
        table_name = self._entity.name
        columns = table_column_names(table_name)

        # Iterate entity column and assert if they exist
        row_id = 0
        for column_name, column_widget in self.column_widgets.items():
            c = self.columns[column_name]

            if c.name in self.exclude_columns:
                continue

            if isinstance(c, MultipleSelectColumn):
                continue

            if c.name not in columns and not isinstance(c, VirtualColumn):
                continue

            if column_widget is not None:
                header = c.ui_display()
                self.c_label = QLabel(self.scroll_widget_contents)

                self.c_label.setText(header)
                self.gl.addWidget(self.c_label, row_id, 0, 1, 1)

                if c.TYPE_INFO == 'AUTO_GENERATED':
                    column_widget.setReadOnly(False)
                    column_widget.btn_load.hide()

                self.gl.addWidget(column_widget, row_id, 1, 1, 1)

                col_name = c.name

                # Add widget to MapperMixin collection
                self.addMapping(
                    col_name,
                    column_widget,
                    c.mandatory,
                    pseudoname=c.ui_display()
                )

                # Bump up row_id
                row_id += 1


        self.entity_scroll_area.setWidget(self.scroll_widget_contents)

        if self.entity_tab_widget is None:
            self.entity_tab_widget = QTabWidget(self)

        # Check if there are children and add foreign key browsers

        # Add primary tab if necessary
        self._add_primary_attr_widget()

        # self.entity_tab_widget.setTabEnabled(0, False)  # enable/disable the tab
        # set the style sheet
        self.setStyleSheet(
            "QTabBar::tab::selected {width: 0; height: 0; margin: 0; "
            "padding: 0; border: none;} ")

        # Return the correct widget
        if self.entity_tab_widget is not None:
            return self.entity_tab_widget

        return self.entity_scroll_area
