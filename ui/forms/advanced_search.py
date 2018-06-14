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
    QPushButton
)

from stdm.ui.admin_unit_manager import VIEW,MANAGE,SELECT

from stdm.data.configuration import entity_model
from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn
)
from sqlalchemy.sql.expression import text
from stdm.data.mapping import MapperMixin
from stdm.data.pg_utils import table_column_names, fetch_with_filter
from stdm.utils.util import entity_display_columns
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    UserTipLabel
)

from stdm.ui.forms.documents import SupportingDocumentsWidget
from stdm.ui.notification import NotificationBar

from editor_dialog import EntityEditorDialog

class AdvancedSearch(EntityEditorDialog):
    def __init__(self, entity, parent):

        EntityEditorDialog.__init__(self, entity, parent=parent)
        self.parent = parent

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
            QDialogButtonBox.Cancel
        )
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

    def on_search(self):
        search_data = {}
        for column in self._entity.columns.values():
            if column.name in entity_display_columns(self._entity):
                if column.name == 'id':
                    continue
                handler = self.attribute_mappers[
                    column.name].valueHandler()
                value = handler.value()
                if value != handler.default() and bool(value):
                    search_data[column.name] = value
        # self.search_db(search_data)
        result = self.search_db_raw(search_data)
        self.parent._tableModel.removeRows(0, self.parent._tableModel.rowCount())

        self.parent._initializeData(result)

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
        print results

    def search_db_raw(self, search_data):
        sql = u"SELECT * FROM {} WHERE ".format(self._entity.name)
        # query = ent_model_obj.queryObject()
        param = []
        for attr, value in search_data.iteritems():
            param.append(u'{} = {}'.format(unicode(attr), unicode(value)))
        final_sql = u'{} {}'.format(sql, ' AND '.join(param))
        # sql_text = text(final_sql)
        results = fetch_with_filter(final_sql)
        # now we can run the query

        return results