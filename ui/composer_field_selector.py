"""
/***************************************************************************
Name                 : Composer Data Field Selector
Description          : Widget for seleting a data field based on the 
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
from PyQt4.QtGui import (
                         QWidget,
                         QMessageBox
                         )

from stdm.data import table_column_names

from .ui_composer_data_field import Ui_frmComposerFieldEditor

class ComposerFieldSelector(QWidget,Ui_frmComposerFieldEditor):
    """
    Widget for selecting the field from a database table or view. 
    """
    def __init__(self,composerWrapper,label,parent = None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        self._composerWrapper = composerWrapper
        self._label = label
        
        #Load fields if the data source has been specified
        dsName = self._composerWrapper.selectedDataSource()
        self._loadFields(dsName)
        
        #Connect signals
        self._composerWrapper.dataSourceSelected.connect(self.onDataSourceChanged)
        self.cboDataField.currentIndexChanged[str].connect(self.onFieldNameChanged)
        
    def onDataSourceChanged(self,dataSourceName):
        """
        When the user changes the data source then update the fields.
        """
        self._loadFields(dataSourceName)
        
    def onFieldNameChanged(self,fieldName):
        """
        Slot raised when the field selection changes.
        """
        if fieldName == "":
            self._label.setText("[STDM Data Field]")
            
        else:
            self._label.setText("[" + self._composerWrapper.selectedDataSource() + "." + \
                                self.fieldName() + "]")
            
        self._composerWrapper.composition().update()
        
    def fieldName(self):
        """
        Return the name of the selected field.
        """
        return self.cboDataField.currentText()
    
    def selectFieldName(self,fieldName):
        """
        Select the specified field name from the items in the combobox.
        """
        fieldIndex = self.cboDataField.findText(fieldName)
        
        if fieldIndex != -1:
            self.cboDataField.setCurrentIndex(fieldIndex)
        
    def _loadFields(self,dataSourceName):
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