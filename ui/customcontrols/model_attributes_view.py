"""
/***************************************************************************
Name                 : Model Attributes ListView
Description          : Custom QListView implementation that displays checkable
                       model attributes.
Date                 : 22/May/2014 
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

from PyQt4.QtGui import (
                         QListView,
                         QStandardItemModel,
                         QStandardItem
                         )
from PyQt4.QtCore import Qt

__all__ = ["ModelAtrributesView"]

class ModelAtrributesView(QListView):
    """
    Custom QListView implementation that displays checkable model attributes.
    """
    def __init__(self,parent=None,dataModel = None):
        QListView.__init__(self, parent)
        
        self._dataModel = dataModel
        self._selectedDisplayMapping = OrderedDict()
        self._modelDisplayMapping = OrderedDict()
        self._attrModel = QStandardItemModel(self)
        
    def dataModel(self):
        """
        Returns the data model instance.
        """
        return self._dataModel
    
    def setDataModel(self,dataModel):
        """
        Sets the data model. Should be a callable class rather than the class
        instance.
        """
        if callable(dataModel):
            self._dataModel = dataModel
            
        else:
            self._dataModel = dataModel.__class__
    
    def modelDisplayMapping(self):
        '''
        Returns the colname and display name
        '''
        return self._modelDisplayMapping
    
    def setModelDisplayMapping(self,dataMapping):   
        '''
        Sets the mapping dictory for the table object
        '''
        if dataMapping!=None:
            self._modelDisplayMapping=dataMapping
        else:
            return self.modelDisplayMapping   
        
    def load(self):
        """
        Load the model's attributes into the list view.
        """
        if self._dataModel == None:
            return
        
        try:
            self._loadAttrs(self._dataModel.displayMapping())
#           self._loadAttrs(self._modelDisplayMapping)
        except AttributeError:
            #Ignore error if model does not contain the displayMapping static method
            pass
        
    def _loadAttrs(self,attrMapping):
        """
        Loads display mapping into the list view.
        """
        self._attrModel.clear()
        self._attrModel.setColumnCount(2)
        
        for attrName,displayName in attrMapping.iteritems():
            #Exclude row ID in the list, other unique identifier attributes in the model can be used
            if attrName != "id":
                displayNameItem = QStandardItem(displayName)
                displayNameItem.setCheckable(True)
                attrNameItem = QStandardItem(attrName)
                
                self._attrModel.appendRow([displayNameItem,attrNameItem])
            
        self.setModel(self._attrModel)
        
    def selectedMappings(self):
        """
        Return a dictionary of field names and their corresponding display values.
        """
        selectedAttrs = {}
        
        for i in range(self._attrModel.rowCount()):
            displayNameItem = self._attrModel.item(i,0)
            
            if displayNameItem.checkState() == Qt.Checked:
                attrNameItem = self._attrModel.item(i,1)  
                selectedAttrs[attrNameItem.text()] = displayNameItem.text()
        
        return selectedAttrs