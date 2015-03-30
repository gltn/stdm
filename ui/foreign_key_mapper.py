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

from stdm.data import BaseSTDMTableModel
from stdm.utils import getIndex
from .admin_unit_manager import VIEW,MANAGE,SELECT
from stdm.ui.customcontrols import FKBrowserProperty

__all__=["ForeignKeyMapper"]

class ForeignKeyMapper(QWidget):
    '''
    Foreign key mapper widget.
    ''' 
    
    #Custom signals
    beforeEntityAdded = pyqtSignal("PyQt_PyObject")
    afterEntityAdded = pyqtSignal("PyQt_PyObject")
    entityRemoved = pyqtSignal("PyQt_PyObject")
    
    def __init__(self,parent=None):
        QWidget.__init__(self,parent)
        
        self._tbFKEntity = QTableView(self)
        self._tbFKEntity.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._tbFKEntity.setAlternatingRowColors(True)
        self._tbFKEntity.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        tbActions = QToolBar()
        tbActions.setIconSize(QSize(16,16))
        
        self._addEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/add.png"),
                                  QApplication.translate("ForeignKeyMapper","Add"),self)
        self.connect(self._addEntityAction,SIGNAL("triggered()"),self.onAddEntity)
        
        self._removeEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/remove.png"),
                                  QApplication.translate("ForeignKeyMapper","Remove"),self)
        self.connect(self._removeEntityAction,SIGNAL("triggered()"),self.onRemoveEntity)
        
        tbActions.addAction(self._addEntityAction)
        tbActions.addAction(self._removeEntityAction)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setMargin(5)
        
        layout.addWidget(tbActions)
        layout.addWidget(self._tbFKEntity)
        
        #Instance variables
        self._dbModel = None
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
        
    def initialize(self):
        '''
        Configure the mapper based on the user settings.
        '''
        #Load headers
        if self._dbModel != None:
            headers = self._dbModel.displayMapping().values()
            self._tableModel = BaseSTDMTableModel([],headers,self)
            self._tbFKEntity.setModel(self._tableModel)
            
            #First (ID) column will always be hidden
            self._tbFKEntity.hideColumn(0)
            
            self._tbFKEntity.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        
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
    
    def setEntitySelector(self,selector,state=SELECT):
        '''
        Set the dialog for selecting entity objects.
        Selector must be a callable.
        '''
        self._entitySelector = selector
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
        if self._tableModel:
            rowCount = self._tableModel.rowCount()
            recordIds = []
            
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
            return None
        else:
            if self._supportsLists:
                return modelInstances
            else:
                return modelInstances[0]
            
    def setEntities(self,entities):
        '''
        Insert entities into the table.
        '''
        if isinstance(entities,list):
            for entity in entities:
                self._insertModelToView(entity)
                
        else:
            self._insertModelToView(entities)
            
    def searchModel(self,columnIndex,columnValue):
        '''
        Searches for 'columnValue' in the column whose index is specified by 'columnIndex' in all 
        rows contained in the model.
        '''
        if isinstance (columnValue,QVariant):
            columnValue = str(columnValue.toString())
            
        if not isinstance(columnValue,str):
            columnValue = str(columnValue)
            
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
            if modelObj != None:
                modelInstances.append(modelObj)
            
        return modelInstances
        
    def _onRecordSelectedEntityBrowser(self,recid):
        '''
        Slot raised when the user has clicked the select button in the 'EntityBrowser' dialog
        to add the selected record to the table's list.
        Add the record to the foreign key table using the mappings.
        '''
        #Check if the record exists using the primary key so as to ensure only one instance is added to the table
        try:
            recIndex = getIndex(self._recordIds(),id)
            if recIndex != -1:
                return
        except:
            pass
        
        dbHandler = self._dbModel()
        modelObj = dbHandler.queryObject().filter(self._dbModel.id == recid).first()
              
        if modelObj != None:
            #Raise before entity added signal
            self.beforeEntityAdded.emit(modelObj)
            
            #Validate for unique value configurations
            for colIndex,replace in self._uniqueValueColIndices.items():
                attrName = self._dbModel.displayMapping().keys()[colIndex]
                attrValue = getattr(modelObj,attrName)
                #Check to see if there are cell formatters so that the correct value is searched for in the model
                if attrName in self._cellFormatters:
                    attrValue = self._cellFormatters[attrName](attrValue)
                    
                matchingIndex = self.searchModel(colIndex, attrValue)
                
                if matchingIndex.isValid():
                    if replace:
                        existingId = matchingIndex.data()
                        
                        #Delete old record from db
                        entityModels = self._modelInstanceFromIds([existingId])
                        if len(entityModels) > 0:
                            entityModels[0].delete()
                        self._removeRow(matchingIndex.row())
                        break
                    else:
                        #Break. Do not add item to the list.
                        return
            if self._tableModel:
                if not self._supportsLists and self._tableModel.rowCount() > 0:
                    self._removeRow(0)
                self._insertModelToView(modelObj)
            else:
                item_id = getattr(modelObj, 'id')
                col_list = self._dbModel.displayMapping().keys()
                item_key =getattr(modelObj, str(col_list[1]))
                #self.global_id[item_id] = item_key
                self.global_id = FKBrowserProperty(item_id, item_key)
                #return fk_browser
            
    def _insertModelToView(self,modelObj):    
        '''
        Insert the given database model instance into the view.
        '''
        insertPosition = self._tableModel.rowCount()
        self._tableModel.insertRows(insertPosition, 1)
        
        for i,attr in enumerate(self._dbModel.displayMapping().keys()):
            propIndex = self._tableModel.index(insertPosition,i)
            attrVal = getattr(modelObj,attr)
              
            #Check if there are display formatters and apply if one exists for the given attribute
            if attr in self._cellFormatters:
                attrVal = self._cellFormatters[attr](attrVal)
            self._tableModel.setData(propIndex, attrVal)
            
        #Raise signal once entity has been inserted
        self.afterEntityAdded.emit(modelObj)
    
    def onAddEntity(self):
        '''
        Slot raised on selecting to add related entities that will be mapped to the primary
        database model instance.
        '''
        if self._entitySelector != None:           
            entitySelector = self._entitySelector(self,self._entitySelectorState)
            #Cascade cell formatters
            entitySelector.setCellFormatters(self._cellFormatters)
            self.connect(entitySelector, SIGNAL("recordSelected(int)"),self._onRecordSelectedEntityBrowser)
            #self.connect(entitySelector, SIGNAL("destroyed(QObject *)"),self.onEntitySelectorDestroyed)
            
            retStatus = entitySelector.exec_()
            if retStatus == QDialog.Accepted:
                pass
                
        else:
            if self._notifBar != None:
                msg = QApplication.translate("ForeignKeyMapper","Null instance of entity selector.")   
                self._notifBar.clear()
                self._notifBar.insertErrorNotification(msg)           
                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        