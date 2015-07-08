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
from decimal import Decimal

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import (
    QgsExpression,
    QgsVectorLayer,
    QGis
)
from qgis.gui import QgsExpressionBuilderDialog

from stdm.data import BaseSTDMTableModel
from stdm.data.config_utils import foreign_key_table_reference
from stdm.utils import getIndex
from .admin_unit_manager import (
    VIEW,
    MANAGE,
    SELECT
)
from .stdmdialog import DeclareMapping
from stdm.ui.customcontrols import FKBrowserProperty

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

        exp.prepare(self._ref_layer.pendingFields())

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

        #Notify user if no results were returned
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
    
    #Custom signals
    beforeEntityAdded = pyqtSignal("PyQt_PyObject")
    afterEntityAdded = pyqtSignal("PyQt_PyObject")
    entityRemoved = pyqtSignal("PyQt_PyObject")
    
    def __init__(self, parent=None):
        QWidget.__init__(self,parent)
        
        self._tbFKEntity = QTableView(self)
        self._tbFKEntity.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tbFKEntity.setAlternatingRowColors(True)
        self._tbFKEntity.setSelectionBehavior(QAbstractItemView.SelectRows)

        self._add_entity_btn = QToolButton(self)
        self._add_entity_btn.setToolTip(QApplication.translate("ForeignKeyMapper","Add"))
        self._add_entity_btn.setIcon(QIcon(":/plugins/stdm/images/icons/add.png"))
        self._add_entity_btn.clicked.connect(self.onAddEntity)

        self._edit_entity_btn = QToolButton(self)
        self._edit_entity_btn.setVisible(False)
        self._edit_entity_btn.setToolTip(QApplication.translate("ForeignKeyMapper","Edit"))
        self._edit_entity_btn.setIcon(QIcon(":/plugins/stdm/images/icons/edit.png"))

        self._filter_entity_btn = QToolButton(self)
        self._filter_entity_btn.setVisible(False)
        self._filter_entity_btn.setToolTip(QApplication.translate("ForeignKeyMapper","Select by expression"))
        self._filter_entity_btn.setIcon(QIcon(":/plugins/stdm/images/icons/filter.png"))
        self._filter_entity_btn.clicked.connect(self.onFilterEntity)

        self._delete_entity_btn = QToolButton(self)
        self._delete_entity_btn.setToolTip(QApplication.translate("ForeignKeyMapper","Remove"))
        self._delete_entity_btn.setIcon(QIcon(":/plugins/stdm/images/icons/remove.png"))
        self._delete_entity_btn.clicked.connect(self.onRemoveEntity)

        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setMargin(5)

        grid_layout = QGridLayout(self)
        grid_layout.setHorizontalSpacing(5)
        grid_layout.addWidget(self._add_entity_btn, 0, 0, 1, 1)
        grid_layout.addWidget(self._filter_entity_btn, 0, 1, 1, 1)
        grid_layout.addWidget(self._edit_entity_btn, 0, 2, 1, 1)
        grid_layout.addWidget(self._delete_entity_btn, 0, 3, 1, 1)
        grid_layout.setColumnStretch(4, 5)

        layout.addLayout(grid_layout)
        layout.addWidget(self._tbFKEntity)
        
        #Instance variables
        self._dbModel = None
        self._ds_name = ""
        self._omitPropertyNames = []
        self._entitySelector = None
        self._entitySelectorState = None
        self._supportsLists = True
        self._tableModel = None
        self._notifBar = None
        self._cellFormatters = {}
        self._deleteOnRemove = False
        self._uniqueValueColIndices = OrderedDict()
        self.global_id = None
        self.display_column = None
        self._deferred_objects = {}
        self._use_expression_builder = False
        
    def initialize(self):
        """
        Configure the mapper based on the user settings.
        """
        from stdm.data import numeric_varchar_columns

        #Load headers
        if not self._dbModel is None:
            headers = []

            display_cols = numeric_varchar_columns(self._ds_name)

            #Ensure only displayable values are included
            for c, dc in self._dbModel.displayMapping().iteritems():
                if c in display_cols:
                    headers.append(dc)

            self._tableModel = BaseSTDMTableModel([],headers,self)
            self._tbFKEntity.setModel(self._tableModel)
            
            #First (ID) column will always be hidden
            self._tbFKEntity.hideColumn(0)
            
            self._tbFKEntity.horizontalHeader().setResizeMode(QHeaderView.Stretch)

            '''
            If expression builder is enabled then disable edit button since
            mapper cannot work in both selection and editing mode.
            '''
            if self._use_expression_builder:
                self._filter_entity_btn.setVisible(True)
                self._edit_entity_btn.setVisible(False)
        
    def databaseModel(self):
        '''
        Returns the database model that represents the foreign key entity.
        '''
        return self._dbModel
    
    def setDatabaseModel(self,model):
        '''
        Set the database model that represents the foreign key entity.
        Model has to be a callable.
        '''
        self._dbModel = model

    def data_source_name(self):
        """
        :return: Returns the name of the data source (as specified in the
        database).
        :rtype: str
        """
        return self._ds_name

    def set_data_source_name(self, ds_name):
        """
        Set the name of the data source (as specified in the database). This
        will be used to construct the vector layer when filtering records
        using the expression builder.
        We are using this option since we cannot extract the table/view name
        from the database model.
        :param ds_name: Name of the data source.
        :type ds_name: str
        """
        self._ds_name = ds_name
        
    def setEmitPropertyNames(self,propnames):
        '''
        Set the property names to be omitted from the display in the table list view.
        '''
        self._omitPropertyNames = propnames
        
    def omitPropertyNames(self):
        '''
        Returns the property names to be omitted from the display in the table list view.
        '''
        return self._omitPropertyNames
    
    def setCellFormatters(self,formattermapping):
        '''
        Dictionary of attribute mappings and corresponding functions for 
        formatting the attribute value to the display value.
        '''
        self._cellFormatters = formattermapping
        
    def addCellFormatter(self,attributeName,formatterFunc):
        '''
        Add a new cell formatter configuration to the collection
        '''
        self._cellFormatters[attributeName] = formatterFunc
        
    def cellFormatters(self):
        """
        Returns a dictionary of cell formatters used by the foreign key mapper.
        """
        return self._cellFormatters
    
    def entitySelector(self):
        '''
        Returns the dialog for selecting the entity objects.
        '''
        return self._entitySelector
    
    def setEntitySelector(self, selector, state=SELECT):
        '''
        Set the dialog for selecting entity objects.
        Selector must be a callable.
        '''
        if callable(selector):
            self._entitySelector = selector
        else:
            self._entitySelector = selector.__class__

        self._entitySelectorState = state
        
    def supportList(self):
        '''
        Returns whether the mapper supports only one item or multiple entities i.e.
        one-to-one and one-to-many mapping. 
        Default is 'True'.
        '''
        return self._supportsLists
    
    def setSupportsList(self,supportsList):
        '''
        Sets whether the mapper supports only one item or multiple entities i.e.
        one-to-one (False) and one-to-many mapping (True).
        '''
        self._supportsLists = supportsList
        
    def setNotificationBar(self,notificationBar):
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
    
    def setDeleteonRemove(self,delete):
        '''
        Set whether whether a record should be deleted from the database when it 
        is removed from the list.
        '''
        self._deleteOnRemove = delete
        
    def addUniqueColumnName(self,colName,replace = True):
        '''
        Set the name of the column whose values are to be unique.
        If 'replace' is True then the existing row will be replaced
        with one with the new value; else, the new row will not be added to the list.
        '''
        headers = self._dbModel.displayMapping().values()
        colIndex = getIndex(headers,colName)
        
        if colIndex != -1:
            self.addUniqueColumnIndex(colIndex, replace)
        
    def addUniqueColumnIndex(self,colIndex,replace = True):
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

        if callable(self._dbModel):
            context = self._dbModel.__name__

        else:
            context = self._dbModel.__class__.__name__

        filter_dlg = ForeignKeyMapperExpressionDialog(vl, self, context=context)
        filter_dlg.setWindowTitle(QApplication.translate("ForeignKeyMapper",
                                                    "Filter By Expression"))
        filter_dlg.recordSelected[int].connect(self._onRecordSelectedEntityBrowser)

        res = filter_dlg.exec_()
    
    def _removeRow(self,rowNumber):
        '''
        Remove the row at the given index.
        '''
        self._tableModel.removeRows(rowNumber, 1)
        
    def onRemoveEntity(self):
        '''
        Slot raised on clicking to remove the selected entity.
        '''
        selectedRowIndices = self._tbFKEntity.selectionModel().selectedRows(0)
        
        if len(selectedRowIndices) == 0:
            msg = QApplication.translate("ForeignKeyMapper","Please select the record to be removed.")   
            self._notifBar.clear()
            self._notifBar.insertWarningNotification(msg)
            
        for selectedRowIndex in selectedRowIndices:
            #Delete record from database if flag has been set to True
            recId= selectedRowIndex.data()
            
            dbHandler = self._dbModel()
            delRec = dbHandler.queryObject().filter(self._dbModel.id == recId).first()
            
            if not delRec is None:
                self.entityRemoved.emit(delRec)
                
                if self._deleteOnRemove:
                    delRec.delete()
            
            self._removeRow(selectedRowIndex.row()) 
            
    def _recordIds(self):
        '''
        Returns the primary keys of the records in the table.
        '''
        recordIds = []

        if self._tableModel:
            rowCount = self._tableModel.rowCount()
            
            for r in range(rowCount):
                #Get ID value
                modelIndex = self._tableModel.index(r,0)
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
        if isinstance(entities,list):
            for entity in entities:
                self._insertModelToView(entity)
                
        else:
            self._insertModelToView(entities)
            
    def searchModel(self, columnIndex, columnValue):
        '''
        Searches for 'columnValue' in the column whose index is specified by 'columnIndex' in all 
        rows contained in the model.
        '''
        if isinstance (columnValue, QVariant):
            columnValue = unicode(columnValue.toString())

        if not isinstance(columnValue, str) or \
                not isinstance(columnValue, unicode):
            columnValue = unicode(columnValue)

        columnValue = columnValue.strip()

        proxy = QSortFilterProxyModel(self)
        proxy.setSourceModel(self._tableModel)
        proxy.setFilterKeyColumn(columnIndex)
        proxy.setFilterFixedString(columnValue)
        #Will return model index containing the primary key.
        matchingIndex = proxy.mapToSource(proxy.index(0,0))

        return matchingIndex
    
    def _modelInstanceFromIds(self,ids):
        '''
        Returns the model instance based the value of its primary key.
        '''
        dbHandler = self._dbModel()
        
        modelInstances = []
        
        for modelId in ids:
            modelObj = dbHandler.queryObject().filter(self._dbModel.id == modelId).first()
            if not modelObj is None:
                modelInstances.append(modelObj)

        return modelInstances
        
    def _onRecordSelectedEntityBrowser(self, rec, row_number=-1):
        '''
        Slot raised when the user has clicked the select button in the 'EntityBrowser' dialog
        to add the selected record to the table's list.
        Add the record to the foreign key table using the mappings.
        '''
        #Check if the record exists using the primary key so as to ensure only one instance is added to the table
        try:
            if isinstance(rec, int):
                recIndex = getIndex(self._recordIds(), rec)

                if recIndex != -1:
                    return


                dbHandler = self._dbModel()
                modelObj = dbHandler.queryObject().filter(self._dbModel.id == rec).first()

            elif isinstance(rec, object):
                modelObj = rec

            else:
                return

        except:
            pass

        dbHandler = self._dbModel()
        modelObj = dbHandler.queryObject().filter(self._dbModel.id == rec).first()

        if not modelObj is None:
            #Raise before entity added signal
            self.beforeEntityAdded.emit(modelObj)
            
            #Validate for unique value configurations
            if not self._validate_unique_columns(modelObj, row_number):
                return

            if self._tableModel:
                if not self._supportsLists and self._tableModel.rowCount() > 0:
                    self._removeRow(0)

                insert_position = self._insertModelToView(modelObj, row_number)

                if isinstance(rec, object):
                    self._deferred_objects[insert_position] = modelObj

            else:
                try:
                    self.global_id = self.onfk_lookup(modelObj)

                except Exception as ex:
                    QMessageBox.information(self,
                                    QApplication.translate("ForeignKeyMapper",
                                                        "Foreign Key Reference"),
                                            unicode(ex.message))

                    return

    def set_model_display_column(self, name):
        """
        :return:
        """
        self.display_column = name

    def onfk_lookup(self,obj, index=None):
        """
        :param Model obj:
        :param :
        :return:
        """
        display_label = None
        base_id = getattr(obj, 'id')
        col_list = self._dbModel.displayMapping().keys()

        if self.display_column:
            display_label = getattr(obj, self.display_column)

        else:
            display_label = getattr(obj, col_list[1])

        fk_reference = FKBrowserProperty(base_id, display_label)

        return fk_reference

    def _validate_unique_columns(self,model,exclude_row = -1):
        """
        Loop through the attributes of the model to assert for existing row values that should be unique based on
        the configuration of unique columns.
        """
        for colIndex,replace in self._uniqueValueColIndices.items():
            attrName = self._dbModel.displayMapping().keys()[colIndex]
            attrValue = getattr(model,attrName)

            #Check to see if there are cell formatters so that the correct value is searched for in the model
            if attrName in self._cellFormatters:
                attrValue = self._cellFormatters[attrName](attrValue)

            matchingIndex = self.searchModel(colIndex, attrValue)

            if matchingIndex.isValid() and matchingIndex.row() != exclude_row:
                if replace:
                    existingId = matchingIndex.data()

                    #Delete old record from db
                    entityModels = self._modelInstanceFromIds([existingId])

                    if len(entityModels) > 0:
                        entityModels[0].delete()

                    self._removeRow(matchingIndex.row())

                    return True

                else:
                    #Break. Do not add item to the list.
                    return False

        return True

    def _insertModelToView(self, model_obj, row_number = -1):
        """
        Insert the given database model instance into the view at the given row number position.
        """
        if row_number == -1:
            row_number = self._tableModel.rowCount()
            self._tableModel.insertRows(row_number, 1)

        '''
        Reset model so that we get the correct table mapping. This is a hack,
        will get a better solution in the future.
        '''
        model = DeclareMapping.instance().tableMapping(self._dbModel.__name__.lower())

        for i,attr in enumerate(self._dbModel.displayMapping().keys()):
            propIndex = self._tableModel.index(row_number,i)
            attrVal = getattr(model_obj, attr)

            #Check if there are display formatters and apply if one exists for the given attribute
            if attr in self._cellFormatters:
                attrVal = self._cellFormatters[attr](attrVal)

            self._tableModel.setData(propIndex, attrVal)

        #Raise signal once entity has been inserted
        self.afterEntityAdded.emit(model_obj)

        return row_number

    def vector_layer(self):
        """
        Returns a QgsVectorLayer based on the configuration information
        specified in the mapper including the system-wide data connection
        properties.
        """
        from stdm.data import vector_layer

        if self._dbModel is None:
            msg = QApplication.translate("ForeignKeyMapper",
                                         "Primary database model object not defined.")
            return None, msg

        filter_layer = vector_layer(self._ds_name)
        if filter_layer is None:
            msg = QApplication.translate("ForeignKeyMapper",
                "Vector layer could not be constructed from the database table.")

            return None, msg

        if not filter_layer.isValid():
            trans_msg = QApplication.translate("ForeignKeyMapper",
                u"The vector layer for '{0}' table is invalid.")
            msg = trans_msg.format(self._ds_name)

            return None, msg

        return filter_layer, ""
    
    def onAddEntity(self):
        """
        Slot raised on selecting to add related entities that will be mapped to the primary
        database model instance.
        """
        if self._tableModel:
            if not self._entitySelector is None:
                entitySelector = self._entitySelector(self, self._dbModel,
                                                    self._entitySelectorState)

                #Cascade cell formatters
                entitySelector.setCellFormatters(self._cellFormatters)
                entitySelector.recordSelected[int].connect(self._onRecordSelectedEntityBrowser)

                retStatus = entitySelector.exec_()
                if retStatus == QDialog.Accepted:
                    pass

            else:
                if not self._notifBar is None:
                    msg = QApplication.translate("ForeignKeyMapper","Null instance of entity selector.")
                    self._notifBar.clear()
                    self._notifBar.insertErrorNotification(msg)
        else:
            entitySelector = self._entitySelector(self,
                                                  self._dbModel,
                                                  self._entitySelectorState)
            entitySelector.recordSelected[int].connect(self._onRecordSelectedEntityBrowser)

            retStatus = entitySelector.exec_()
            if retStatus == QDialog.Accepted:
                pass
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        