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
from collections import OrderedDict
import uuid
from PyQt4.QtCore import (
    Qt,
    pyqtSignal
)

from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QApplication,
    QPushButton,
    QLineEdit, QMessageBox)

from stdm.ui.admin_unit_manager import VIEW,MANAGE,SELECT

from stdm.data.configuration import entity_model
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from sqlalchemy.sql.expression import text
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import (
        table_column_names, 
        fetch_with_filter,
        pg_table_count
        )
from stdm.utils.util import (
        entity_display_columns, 
        format_name, simple_dialog
        )
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    UserTipLabel
)

from stdm.ui.forms.documents import SupportingDocumentsWidget
from stdm.ui.notification import NotificationBar

from editor_dialog import EntityEditorDialog

from stdm.settings import get_entity_browser_record_limit

class AdvancedSearch(EntityEditorDialog):
    def __init__(self, entity, parent):

        EntityEditorDialog.__init__(self, entity, parent=parent)
        self.parent = parent
        self.record_limit = self.get_records_limit() 

    def _init_gui(self):
        # Setup base elements
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName('glMain')
        self.gridLayout.addLayout(
            self.vlNotification, 0, 0, 1, 1
        )
        QApplication.processEvents()

        column_widget_area = self._setup_columns_content_area()
        self.gridLayout.addWidget(
            column_widget_area, 1, 0, 1, 1
        )
        QApplication.processEvents()
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

        title = u'{0} {1}'.format(title_str, search_trans)
        self.do_not_check_dirty = True
        self.setWindowTitle(title)
        # if self.has_mandatory:
        #     self.required_fields_lbl = QLabel(self)
        #     msg = self.tr(
        #         'Please fill out all required (*) fields.'
        #     )
        #     msg = self._highlight_asterisk(msg)
        #     self.required_fields_lbl.setText(msg)
        #     self.gridLayout.addWidget(
        #         self.required_fields_lbl, next_row, 0, 1, 2
        #     )
        #     # Bump up row reference
        #     next_row += 1

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
            QDialogButtonBox.Close)

        self.search.clicked.connect(self.on_search)

        #
        #
        # # edit model, collect model
        # # adding new record for child
        #
        # # Saving in parent editor
        # if not isinstance(self._parent._parent, EntityEditorDialog):
        #     # adding a new record
        #     if self.edit_model is None:
        #         # saving when digitizing.
        #         if self.collect_model:
        #             self.buttonBox.accepted.connect(self.on_model_added)
        #         # saving parent editor
        #         else:
        #             self.buttonBox.accepted.connect(self.save_parent_editor)
        #             self.save_new_button.clicked.connect(self.save_and_new)
        #     # updating existing record
        #     else:
        #         if not self.collect_model:
        #             # updating existing record of the parent editor
        #             self.buttonBox.accepted.connect(self.save_parent_editor)
        #         else:
        #             self.buttonBox.accepted.connect(self.on_model_added)
        # # Saving in child editor
        # else:
        #     # save and new record
        #     if self.edit_model is None:
        #         self.buttonBox.accepted.connect(self.on_child_saved)
        #         self.save_new_button.clicked.connect(
        #             lambda: self.on_child_saved(True)
        #         )
        #
        #     else:
        #         # When updating an existing child editor save to the db
        #         self.buttonBox.accepted.connect(
        #             self.on_child_saved
        #         )
        #         #self.buttonBox.accepted.connect(self.submit)
        #
        self.buttonBox.rejected.connect(self.cancel)

    def get_search_filter(self):
        '''
        rtype: dict
        '''
        search_data = {}
        for column in self._entity.columns.values():
            if column.name == 'id': continue
            if column.name in entity_display_columns(self._entity):
                handler = self.attribute_mappers[
                    column.name].valueHandler()
                value = handler.value()
                if value != handler.default() and bool(value):
                    search_data[column.name] = value

        return search_data

    
    def make_search_params(self, search_filter):
        params = []
        for attr, value in search_filter.iteritems():
            if isinstance(value, (int, float)):
                params.append(u'{} = {}'.format(unicode(attr), unicode(value)))
            if isinstance(value, (unicode, str)):
                params.append(u"{} = '{}'".format(unicode(attr), unicode(value)))
        return params

    def make_search_sql(self, search_filter):
        params = self.make_search_params(search_filter)
        sql = u'{}'.format(' AND '.join(params))
        return sql

    def on_search(self):
        self.parent.reset_browse_window()
        #self.parent._tableModel.removeRows(0, self.parent._tableModel.rowCount())

        search_filter = self.get_search_filter()

        # cache forl later use
        self.parent.plugin.current_parcel_filter = self.make_search_sql(search_filter)

        if len(search_filter) == 0: return
        results = self.search_db_raw(search_filter)

        if results.rowcount > 0: #is not None:
            found = QApplication.translate('AdvancedSearch', 'records found')
            new_title = '{} - {} {}'.format(self.title, results.rowcount, found)

            if results.rowcount > self.record_limit: # results will always be within the record limit
                title = QApplication.translate(
                        'AdvancedSearch',
                        'Advanced Search'
                )
                message = QApplication.translate(
                    'AdvancedSearch',
                    'The search results returned {0} records, which is above the '
                    'search results limit. <br>Would you like to see the first 3000 '
                    'records?'.format("{:,}".format(results.rowcount ))
                )

                res, chk_result = simple_dialog(self, title, message)
                if res:
                    self.setWindowTitle(new_title)
                    self.parent.show_entity_records(results)
            else:
                self.setWindowTitle(new_title)
                self.parent.show_entity_records(results)

    def search_db(self, search_data):
        ent_model_obj = self.ent_model()
        # query = ent_model_obj.queryObject()
        for attr, value in search_data.iteritems():
            ent_model_obj.queryObject().filter(
                getattr(self.ent_model(), attr) == value)

        # now we can run the query
        # print ent_model_obj.queryObject(), vars(ent_model_obj.queryObject())
        # print str(ent_model_obj.queryObject())
        results = ent_model_obj.queryObject().all()

    def search_db_raw(self, search_data):
        sql = u"SELECT * FROM {} WHERE ".format(self._entity.name)
        # query = ent_model_obj.queryObject()
        param = []
        for attr, value in search_data.iteritems():
            if isinstance(value, (int, float)):
                param.append(u'{} = {}'.format(unicode(attr), unicode(value)))
            if isinstance(value, (unicode, str)):
                param.append(u"{} = '{}'".format(unicode(attr), unicode(value)))

        final_sql = u'{} {}'.format(sql, ' AND '.join(param)) + ' LIMIT '+str(self.record_limit)
        # sql_text = text(final_sql)
        results = fetch_with_filter(final_sql)
        # now we can run the query

        return results

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
        for c, column_widget in self.column_widgets.iteritems():
            if c.name in self.exclude_columns:
                continue
            if isinstance(c, MultipleSelectColumn):
                continue
            if not c.name in columns and not isinstance(c, VirtualColumn):
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

    def closeEvent(self, event):
        '''
        Raised when a request to close the window is received.
        Check the dirty state of input controls and prompt user to
        save if dirty.
        '''
        event.accept()

    def cancel(self):
        '''
        Slot for closing the dialog.
        Checks the dirty state first before closing.
        '''
        self.reject()

    def get_records_limit(self):
        records = get_entity_browser_record_limit()
        if records == 0:
            records = pg_table_count(self.entity.name)
        return records

    
