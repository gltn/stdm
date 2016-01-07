"""
/***************************************************************************
Name                 : Composer Data Source Selector
Description          : Widget for selecting a database table or view that will
                       be used across the composition by the STDM data labels.
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
    QComboBox
)

from stdm.data.pg_utils import (
    pg_tables,
    pg_views
)

from .ui_composer_data_source import Ui_frmComposerDataSource

class ComposerDataSourceSelector(QWidget,Ui_frmComposerDataSource):
    """
    Widget for selecting a database table or view. 
    """
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        self.cboDataSource.setInsertPolicy(QComboBox.InsertAlphabetically)
        
        self.rbTables.toggled.connect(self.onShowTables)
        self.rbViews.toggled.connect(self.onShowViews)
        
        #Force views to be loaded
        self.rbViews.toggle()
        
        #Connect signal
        #self.cboDataSource.currentIndexChanged[str].connect(self.onDataSourceSelected)
        
    def onDataSourceSelected(self,dataSource):
        """
        Slot raised upon selecting a data source from the items.
        """
        pass
    
    def category(self):
        """
        Returns the category (view or table) that the data source belongs to.
        """
        if self.rbTables.isChecked():
            return "Table"
        
        elif self.rbViews.isChecked():
            return "View"
        
    def setCategory(self,categoryName):
        """
        Set selected radio button.
        """
        if categoryName == "Table":
            self.rbTables.toggle()
            
        elif categoryName == "View":
            self.rbViews.toggle()
            
    def setSelectedSource(self,dataSourceName):
        """
        Set the data source name if it exists in the list.
        """
        sourceIndex = self.cboDataSource.findText(dataSourceName)
        
        if sourceIndex != -1:
            self.cboDataSource.setCurrentIndex(sourceIndex)
    
    def onShowTables(self,state):
        """
        Slot raised to show STDM database tables.
        """
        if state:
            self.cboDataSource.clear()
            self.cboDataSource.addItem("")
            self.cboDataSource.addItems(pg_tables())
            
    def onShowViews(self,state):
        """
        Slot raised to show STDM database views.
        """
        if state:
            self.cboDataSource.clear()
            self.cboDataSource.addItem("")
            self.cboDataSource.addItems(pg_views())