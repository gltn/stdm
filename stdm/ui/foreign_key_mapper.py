"""
/***************************************************************************
Name                 : Foreign Key Mapper Widget
Description          : Widget that can be embedded in other widgets, dialogs,
                       or windows that displays and enables a user to select
                       related entities which are linked to the primary
                       data object through appropriate foreign key mappings.
Date                 : 18/February/2014
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
from collections import OrderedDict

from qgis.PyQt.QtCore import (
    pyqtSignal,
    QSortFilterProxyModel,
    QVariant
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QWidget,
    QAbstractItemView,
    QMessageBox,
    QToolButton,
    QTableView,
    QVBoxLayout,
    QHeaderView,
    QGridLayout
)
from qgis.core import (
    QgsExpression
)
from qgis.gui import QgsExpressionBuilderDialog

from stdm.data.configuration import entity_model
from stdm.data.configuration.columns import (
    MultipleSelectColumn,
    VirtualColumn,
    GeometryColumn
)
from stdm.data.pg_utils import table_column_names
from stdm.data.qtmodels import BaseSTDMTableModel
from stdm.settings import current_profile
from stdm.ui.admin_unit_manager import SELECT
from stdm.ui.forms.widgets import (
    ColumnWidgetRegistry,
    WidgetException
)
from stdm.ui.gui_utils import GuiUtils
from stdm.utils.util import getIndex

__all__ = ["ForeignKeyMapper", "ForeignKeyMapperExpressionDialog"]


class ForeignKeyMapperExpressionDialog(QgsExpressionBuilderDialog):
    """
    Enables the QGIS expression builder dialog to be used in
    cases where advanced filtering is required to select entities.
    It is important to note that formatting will not be applied to
    the table values and as such the user must be familiar with the
    table schema so that the appropriate values can be used
    when building expressions.
    """
    recordSelected = pyqtSignal(int)

    def __init__(self, layer, parent=None, start_text="",
                 context=QApplication.translate("ForeignKeyMapperExpressionDialog",
                                                "Reports")):
        QgsExpressionBuilderDialog.__init__(self, layer, start_text, parent,
                                            context)

        self._ref_layer = layer

        btn_box = self.findChild(QDialogButtonBox)

        if not btn_box is None:
            btn_ok = btn_box.button(QDialogButtonBox.Ok)
            if not btn_ok is None:
                btn_ok.setText(QApplication.translate("ForeignKeyMapperExpressionDialog",
                                                      "Select"))

    def _features_select(self):
        """
        Generator function that returns features based on user-defined
        expression.
        """
        exp = QgsExpression(self.expressionText())

        if exp.hasParserError():
            raise Exception(exp.parserErrorString())

        exp.prepare(self._ref_layer.fields())

        for f in self._ref_layer.getFeatures():
            value = exp.evaluate(f)
            if bool(value):
                yield f

    def layer(self):
        return self._ref_layer

    def accept(self):
        """
        Override so that we can capture features matching the specified
        expression and raise record selected event for the mapper to
        capture.
        """
        features = self._features_select()

        count = 0
        for f in features:
            fid = -1
            try:
                fid = f.attribute("id")
            except KeyError:
                pass

            if fid != -1:
                self.recordSelected.emit(fid)

            count += 1

        # Notify user if no results were returned
        if count == 0:
            QMessageBox.warning(self, QApplication.translate("ForeignKeyMapperExpressionDialog",
                                                             "Results"),
                                QApplication.translate("ForeignKeyMapperExpressionDialog",
                                                       "No features matched the expression.")
                                )

            return

        super(ForeignKeyMapperExpressionDialog, self).accept()


class ForeignKeyMapper(QWidget):
    """
    Widget for selecting database records through an entity browser or
    using an ExpressionBuilder for filtering records.
    """
    # Custom signals
    beforeEntityAdded = pyqtSignal("PyQt_PyObject")
    afterEntityAdded = pyqtSignal("PyQt_PyObject", int)
    entityRemoved = pyqtSignal("PyQt_PyObject")
    deletedRows = pyqtSignal(list)

    def __init__(self, entity, parent=None, notification_bar=None,
                 enable_list=True, can_filter=False, plugin=None):

        QWidget.__init__(self, parent)
        self.current_profile = current_profile()

        self._tbFKEntity = QTableView(self)
        self._tbFKEntity.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tbFKEntity.setAlternatingRowColors(True)
        self._tbFKEntity.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plugin = plugin
        self._add_entity_btn = QToolButton(self)
        self._add_entity_btn.setToolTip(
            QApplication.translate("ForeignKeyMapper", "Add"))
        self._add_entity_btn.setIcon(
            GuiUtils.get_icon("add.png"))
        self._add_entity_btn.clicked.connect(self.onAddEntity)

        self._edit_entity_btn = QToolButton(self)
        self._edit_entity_btn.setVisible(False)
        self._edit_entity_btn.setToolTip(
            QApplication.translate("ForeignKeyMapper", "Edit"))
        self._edit_entity_btn.setIcon(
            GuiUtils.get_icon("edit.png"))

        self._filter_entity_btn = QToolButton(self)
        self._filter_entity_btn.setVisible(False)
        self._filter_entity_btn.setToolTip(
            QApplication.translate("ForeignKeyMapper", "Select by expression"))
        self._filter_entity_btn.setIcon(
            GuiUtils.get_icon("filter.png"))
        self._filter_entity_btn.clicked.connect(self.onFilterEntity)

        self._delete_entity_btn = QToolButton(self)
        self._delete_entity_btn.setToolTip(
            QApplication.translate("ForeignKeyMapper", "Remove"))
        self._delete_entity_btn.setIcon(
            GuiUtils.get_icon("remove.png"))
        self._delete_entity_btn.clicked.connect(self.onRemoveEntity)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setMargin(5)

        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.addWidget(self._add_entity_btn, 0, 0, 1, 1)
        self.grid_layout.addWidget(self._filter_entity_btn, 0, 1, 1, 1)
        self.grid_layout.addWidget(self._edit_entity_btn, 0, 2, 1, 1)
        self.grid_layout.addWidget(self._delete_entity_btn, 0, 3, 1, 1)
        self.grid_layout.setColumnStretch(4, 5)

        layout.addLayout(self.grid_layout)
        layout.addWidget(self._tbFKEntity)
        self.social_tenure = self.current_profile.social_tenure

        self._tableModel = None
        self._notifBar = notification_bar
        self._headers = []
        self._entity_attrs = []
        self._cell_formatters = {}
        self._searchable_columns = OrderedDict()
        self._supportsLists = enable_list
        self._deleteOnRemove = False
        self._uniqueValueColIndices = OrderedDict()
        self.global_id = None
        self._deferred_objects = {}
        self._use_expression_builder = can_filter

        if self._use_expression_builder:
            self._filter_entity_btn.setVisible(True)
            self._edit_entity_btn.setVisible(False)
        self.set_entity(entity)

    def set_entity(self, entity):
        """
        Sets new entity and updates the ForeignKeyMapper with a new
        :param entity: The entity of the ForeignKeyMapper
        :type entity:Object
        """
        from stdm.ui.entity_browser import EntityBrowser

        self._entity = entity

        self._dbmodel = entity_model(entity)
        self._init_fk_columns()
        self._entitySelector = EntityBrowser(
            self._entity,
            parent=self,
            state=SELECT,
            plugin=self.plugin
        )

        # Connect signals
        self._entitySelector.recordSelected.connect(
            self._onRecordSelectedEntityBrowser
        )

    def test_close_selector(self):
        self._entitySelector.done(1)

    def _init_fk_columns(self):
        """
        Asserts if the entity columns actually do exist in the database. The
        method also initializes the table headers, entity column and cell
        formatters.
        """
        self._headers[:] = []
        self._entity_attrs[:] = []
        if self._dbmodel is None:
            msg = QApplication.translate(
                'ForeignKeyMapper', 'The data model for '
                                    'the entity could '
                                    'not be loaded, '
                                    'please contact '
                                    'your database '
                                    'administrator.'
            )
            QMessageBox.critical(
                self,
                QApplication.translate(
                    'EntityBrowser',
                    'Entity Browser'
                ),
                msg
            )

            return

        table_name = self._entity.name
        columns = table_column_names(table_name)
        missing_columns = []

        header_idx = 0

        # Iterate entity column and assert if they exist
        for c in self._entity.columns.values():

            # Hide geometry columns
            if isinstance(c, GeometryColumn):
                continue

            # Do not include virtual columns in list of missing columns
            if not c.name in columns and not isinstance(c, VirtualColumn):
                missing_columns.append(c.name)

            else:
                header = c.header()
                self._headers.append(header)
                '''
                If it is a virtual column then use column name as the header
                but fully qualified column name (created by SQLAlchemy
                relationship) as the entity attribute name.
                '''
                col_name = c.name

                if isinstance(c, MultipleSelectColumn):
                    col_name = c.model_attribute_name

                self._entity_attrs.append(col_name)

                # Get widget factory so that we can use the value formatter
                w_factory = ColumnWidgetRegistry.factory(c.TYPE_INFO)
                if not w_factory is None:
                    try:
                        formatter = w_factory(c)
                        self._cell_formatters[col_name] = formatter
                    except WidgetException as we:
                        msg = QApplication.translate(
                            'ForeignKeyMapper',
                            'Error in creating column:'
                        )
                        msg = '{0} {1}:{2}\n{3}'.format(
                            msg, self._entity.name, c.name, str(we)
                        )
                        QMessageBox.critical(
                            self,
                            QApplication.translate(
                                'ForeignKeyMapper',
                                'Widget Creation Error'
                            ),
                            msg
                        )

                # Set searchable columns
                if c.searchable:
                    self._searchable_columns[header] = {
                        'name': c.name,
                        'header_index': header_idx
                    }

                header_idx += 1

        if len(missing_columns) > 0:
            msg = QApplication.translate(
                'ForeignKeyMapper',
                'The following columns have been defined in the '
                'configuration but are missing in corresponding '
                'database table, please re-run the configuration wizard '
                'to create them.\n{0}'.format(
                    '\n'.join(missing_columns)
                )
            )

            QMessageBox.warning(
                self,
                QApplication.translate('ForeignKeyMapper', 'Entity Browser'),
                msg
            )

        self._tableModel = BaseSTDMTableModel([], self._headers, self)
        self._tbFKEntity.setModel(self._tableModel)
        # First (id) column will always be hidden
        self._tbFKEntity.hideColumn(0)

        self._tbFKEntity.horizontalHeader().setSectionResizeMode(
            QHeaderView.Interactive
        )
        self._tbFKEntity.horizontalHeader().setStretchLastSection(True)

        self._tbFKEntity.verticalHeader().setVisible(True)

    def databaseModel(self):
        '''
        Returns the database model that represents the foreign key entity.
        '''
        return self._dbmodel

    def setDatabaseModel(self, model):
        '''
        Set the database model that represents the foreign key entity.
        Model has to be a callable.
        '''
        self._dbmodel = model

    def cellFormatters(self):
        """
        Returns a dictionary of cell formatters used by the foreign key mapper.
        """
        return self._cell_formatters

    def cell_formatter(self, column):
        """
        :param column: Column name:
        :type column: str
        :return: Returns the corresponding formatter object based on the
        column name. None will be returned if there is no corresponding
        object.
        :rtype: object
        """
        return self._cell_formatters.get(column, None)

    def entitySelector(self):
        '''
        Returns the dialog for selecting the entity objects.
        '''
        return self._entitySelector

    def supportList(self):
        '''
        Returns whether the mapper supports only one item or multiple entities.
        Default is 'True'.
        '''
        return self._supportsLists

    def setSupportsList(self, supportsList):
        '''
        Sets whether the mapper supports only one item or multiple entities i.e.
        one-to-one (False) and one-to-many mapping (True).
        '''
        self._supportsLists = supportsList

    def setNotificationBar(self, notificationBar):
        '''
        Set the notification bar for displaying user messages.
        '''
        self._notifBar = notificationBar

    def viewModel(self):
        '''
        Return the view model used by the table view.
        '''
        return self._tableModel

    def set_expression_builder(self, state):
        """
        Set the mapper to use QGIS expression builder as the entity selector.
        """
        self._use_expression_builder = state

    def expression_builder_enabled(self):
        """
        Returns whether the mapper has been configured to use the expression builder
        """
        return self._use_expression_builder

    def deleteOnRemove(self):
        '''
        Returns the state whether a record should be deleted from the database when it
        is removed from the list.
        '''
        return self._deleteOnRemove

    def setDeleteonRemove(self, delete):
        '''
        Set whether whether a record should be deleted from the database when it
        is removed from the list.
        '''
        self._deleteOnRemove = delete

    def addUniqueColumnName(self, colName, replace=True):
        '''
        Set the name of the column whose values are to be unique.
        If 'replace' is True then the existing row will be replaced
        with one with the new value; else, the new row will not be added to the list.
        '''
        headers = list(self._dbmodel.displayMapping().values())
        colIndex = getIndex(headers, colName)

        if colIndex != -1:
            self.addUniqueColumnIndex(colIndex, replace)

    def addUniqueColumnIndex(self, colIndex, replace=True):
        '''
        Set the index of the column whose values are to be unique. The column indices are
        zero-based.
        If 'replace' is True then the existing row will be replaced with the
        new value; else, the new row will not be added to the list.
        For multiple replace rules defined, then the first one added to the collection is the
        one that will be applied.
        '''
        self._uniqueValueColIndices[colIndex] = replace

    def onFilterEntity(self):
        """
        Slot raised to load the expression builder dialog.
        """
        vl, msg = self.vector_layer()

        if vl is None:
            msg = msg + "\n" + QApplication.translate("ForeignKeyMapper",
                                                      "The expression builder cannot be used at this moment.")
            QMessageBox.critical(self, QApplication.translate("ForeignKeyMapper",
                                                              "Expression Builder"), msg)

            return

        context = self._entity.short_name

        filter_dlg = ForeignKeyMapperExpressionDialog(vl, self, context=context)
        filter_dlg.setWindowTitle(QApplication.translate("ForeignKeyMapper",
                                                         "Filter By Expression"))
        filter_dlg.recordSelected[int].connect(self._onRecordSelectedEntityBrowser)

        res = filter_dlg.exec_()

    def _removeRow(self, rowNumber):
        '''
        Remove the row at the given index.
        '''
        self._tableModel.removeRows(rowNumber, 1)

    def onRemoveEntity(self):
        '''
        Slot raised on clicking to remove the selected entity.
        '''
        selectedRowIndices = self._tbFKEntity.selectionModel().selectedRows(0)

        deleted_rows = []
        if len(selectedRowIndices) == 0:
            msg = QApplication.translate(
                "ForeignKeyMapper",
                "Please select the record to be removed."
            )
            self._notifBar.clear()
            self._notifBar.insertWarningNotification(msg)
            return

        for selectedRowIndex in selectedRowIndices:
            # Delete record from database if flag has been set to True
            recId = selectedRowIndex.data()

            dbHandler = self._dbmodel()
            delRec = dbHandler.queryObject().filter(self._dbmodel.id == recId).first()

            if not delRec is None:
                self.entityRemoved.emit(delRec)

                if self._deleteOnRemove:
                    delRec.delete()

            self._removeRow(selectedRowIndex.row())

            deleted_rows.append(selectedRowIndex.row())

        self.deletedRows.emit(deleted_rows)

    def _recordIds(self):
        '''
        Returns the primary keys of the records in the table.
        '''
        recordIds = []

        if self._tableModel:
            rowCount = self._tableModel.rowCount()

            for r in range(rowCount):
                # Get ID value
                modelIndex = self._tableModel.index(r, 0)
                modelId = modelIndex.data()
                recordIds.append(modelId)

        return recordIds

    def entities(self):
        '''
        Returns the model instance(s) depending on the configuration specified by the user.
        '''
        recIds = self._recordIds()

        modelInstances = self._modelInstanceFromIds(recIds)

        if len(modelInstances) == 0:
            if self._supportsLists:
                return []

            else:
                return None

        else:
            if self._supportsLists:
                return modelInstances

            else:
                return modelInstances[0]

    def setEntities(self, entities):
        '''
        Insert entities into the table.
        '''
        if isinstance(entities, list):
            for entity in entities:
                self._insertModelToView(entity)

        else:
            self._insertModelToView(entities)

    def searchModel(self, columnIndex, columnValue):
        '''
        Searches for 'columnValue' in the column whose index is specified by 'columnIndex' in all
        rows contained in the model.
        '''
        if isinstance(columnValue, QVariant):
            columnValue = str(columnValue.toString())

        if not isinstance(columnValue, str):
            columnValue = str(columnValue)

        columnValue = columnValue.strip()

        proxy = QSortFilterProxyModel(self)
        proxy.setSourceModel(self._tableModel)
        proxy.setFilterKeyColumn(columnIndex)
        proxy.setFilterFixedString(columnValue)
        # Will return model index containing the primary key.
        matchingIndex = proxy.mapToSource(proxy.index(0, 0))

        return matchingIndex

    def _modelInstanceFromIds(self, ids):
        '''
        Returns the model instance based the value of its primary key.
        '''
        dbHandler = self._dbmodel()

        modelInstances = []

        for modelId in ids:
            modelObj = dbHandler.queryObject().filter(self._dbmodel.id == modelId).first()
            if not modelObj is None:
                modelInstances.append(modelObj)

        return modelInstances

    def _onRecordSelectedEntityBrowser(self, rec, row_number=-1):
        '''
        Slot raised when the user has clicked the select button
        in the 'EntityBrowser' dialog
        to add the selected record to the table's list.
        Add the record to the foreign key table using the mappings.
        '''
        # Check if the record exists using the primary key so as to ensure
        # only one instance is added to the table
        if isinstance(rec, int):
            recIndex = getIndex(self._recordIds(), rec)

            if recIndex != -1:
                return

            dbHandler = self._dbmodel()
            modelObj = dbHandler.queryObject().filter(self._dbmodel.id == rec).first()

        elif isinstance(rec, object):
            modelObj = rec

        else:
            return

        if modelObj is not None:
            # Raise before entity added signal
            self.beforeEntityAdded.emit(modelObj)

            # Validate for unique value configurations
            '''
            if not self._validate_unique_columns(modelObj, row_number):
                return
            '''

            if not self._supportsLists and self._tableModel.rowCount() > 0:
                self._removeRow(0)

            insert_position = self._insertModelToView(modelObj, row_number)

            if isinstance(rec, object):
                self._deferred_objects[insert_position] = modelObj

    def _validate_unique_columns(self, model, exclude_row=-1):
        """
        Loop through the attributes of the model to assert
        for existing row values that should be unique based on
        the configuration of unique columns.
        """
        for colIndex, replace in list(self._uniqueValueColIndices.items()):
            attrName = list(self._dbmodel.displayMapping().keys())[colIndex]
            attrValue = getattr(model, attrName)

            # Check to see if there are cell formatters so
            # that the correct value is searched for in the model
            if attrName in self._cell_formatters:
                attrValue = self._cell_formatters[attrName](attrValue)

            matchingIndex = self.searchModel(colIndex, attrValue)

            if matchingIndex.isValid() and matchingIndex.row() != exclude_row:
                if replace:
                    existingId = matchingIndex.data()

                    # Delete old record from db
                    entityModels = self._modelInstanceFromIds([existingId])

                    if len(entityModels) > 0:
                        entityModels[0].delete()

                    self._removeRow(matchingIndex.row())

                    return True

                else:
                    # Break. Do not add item to the list.
                    return False

        return True

    def _insertModelToView(self, model_obj, row_number=-1):
        """
        Insert the given database model instance into the view
        at the given row number position.
        """
        if row_number == -1:
            row_number = self._tableModel.rowCount()
            self._tableModel.insertRows(row_number, 1)

        # In some instances, we will need to get the model object with
        # backrefs included else exceptions will be raised on missing
        # attributes
        q_objs = self._modelInstanceFromIds([model_obj.id])
        if len(q_objs) == 0:
            return

        model_obj = q_objs[0]

        for i, attr in enumerate(self._entity_attrs):
            prop_idx = self._tableModel.index(row_number, i)
            attr_val = getattr(model_obj, attr)

            '''
            Check if there are display formatters and apply if one exists
            for the given attribute.
            '''
            if attr in self._cell_formatters:
                formatter = self._cell_formatters[attr]
                attr_val = formatter.format_column_value(attr_val)

            self._tableModel.setData(prop_idx, attr_val)


        # Raise signal once entity has been inserted
        self.afterEntityAdded.emit(model_obj, row_number)

        self._tbFKEntity.resizeColumnsToContents()

        return row_number

    def insert_model_to_table(self, model_obj, row_number=-1):
        """
         Insert the given database model instance into the view
         at the given row number position.
         """
        if row_number == -1:
            row_number = self._tableModel.rowCount()
            self._tableModel.insertRows(row_number, 1)
        # In some instances, we will need to get the model object with
        # backrefs included else exceptions will be raised on missing
        # attributes
        q_objs = self._modelInstanceFromIds([model_obj.id])

        if len(q_objs) == 0:
            return

        model_obj = q_objs[0]

        for i, attr in enumerate(self._entity_attrs):
            prop_idx = self._tableModel.index(row_number, i)
            attr_val = getattr(model_obj, attr)

            # Check if there are display formatters and apply if one exists
            # for the given attribute.

            if attr in self._cell_formatters:
                formatter = self._cell_formatters[attr]
                attr_val = formatter.format_column_value(attr_val)

            self._tableModel.setData(prop_idx, attr_val)

        #self._tbFKEntity.resizeColumnsToContents()
        self._tbFKEntity.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        return row_number

    def remove_rows(self):
        """
        Removes rows from the fk browser.
        """
        row_count = self._tbFKEntity.model().rowCount()

        self._tbFKEntity.model().removeRows(0, row_count)

    def vector_layer(self):
        """
        Returns a QgsVectorLayer based on the configuration information
        specified in the mapper including the system-wide data connection
        properties.
        """
        from stdm.data.pg_utils import vector_layer

        if self._dbmodel is None:
            msg = QApplication.translate("ForeignKeyMapper",
                                         "Primary database model object not defined.")
            return None, msg

        filter_layer = vector_layer(self._entity.name)
        if filter_layer is None:
            msg = QApplication.translate("ForeignKeyMapper",
                                         "Vector layer could not be constructed from the database table.")

            return None, msg

        if not filter_layer.isValid():
            trans_msg = QApplication.translate("ForeignKeyMapper",
                                               "The vector layer for '{0}' table is invalid.")
            msg = trans_msg.format(self._entity.name)

            return None, msg

        return filter_layer, ""

    def onAddEntity(self):
        """
        Slot raised on selecting to add related entities that will be mapped to the primary
        database model instance.
        """
        self._entitySelector.buttonBox.button(QDialogButtonBox.Cancel).setVisible(False)

        # Clear any previous selections in the entity browser
        self._entitySelector.clear_selection()

        # Clear any previous notifications
        self._entitySelector.clear_notifications()

        self._entitySelector.exec_()
