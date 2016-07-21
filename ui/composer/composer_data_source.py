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
from stdm.settings import current_profile
from stdm.utils.util import (
    profile_user_tables,
    setComboCurrentIndexWithText
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
        self.cboReferencedTable.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.curr_profile = current_profile()
        self.rbTables.toggled.connect(self.onShowTables)
        self.rbViews.toggled.connect(self.onShowViews)

        #Load tables
        self._tables = profile_user_tables(self.curr_profile, False)

        #Populate referenced tables
        self._populate_referenced_tables()

        #Flag for synchronizing data source item change to referenced table
        self._sync_data_source = False
        
        #Force views to be loaded
        self.rbViews.toggle()
        
        #Connect signal
        self.cboDataSource.currentIndexChanged[str].connect(self.onDataSourceSelected)

        self.cboReferencedTable.setEnabled(False)
        
    def onDataSourceSelected(self, dataSource):
        """
        Slot raised upon selecting a data source from the items.
        """
        #Enable/disable referenced table combo only if an item is selected
        if self.category() == 'View':
            if not dataSource:
                self.cboReferencedTable.setEnabled(False)
            else:
                self.cboReferencedTable.setEnabled(True)

        if self._sync_data_source:
            setComboCurrentIndexWithText(self.cboReferencedTable, dataSource)

    def _populate_referenced_tables(self):
        #Populate combo box with the list of tables names
        self.cboReferencedTable.addItem('')
        for table_name, short_name in self._tables.iteritems():
            #Check if there is supporting document
            if not self._contains_supporting_document(table_name):
                self.cboReferencedTable.addItem(short_name.lower(), table_name)

    def _contains_supporting_document(self, table):
        #Returns true if the table contains 'supporting_document' text
        res = table.find('supporting_document')
        if res == -1:
            return False

        return True
    
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

    def set_referenced_table(self, referenced_table):
        """
        Selects the specified table in the referenced table combobox.
        :param referenced_table: Name of the referenced table.
        :type: str
        """
        if self.category() == 'View':
            setComboCurrentIndexWithText(
                self.cboReferencedTable,
                referenced_table
            )

    def referenced_table_name(self):
        """
        :return: Returns the name of the currently selected referenced table
        name.
        :rtype: str
        """
        return self.cboReferencedTable.itemData(
            self.cboReferencedTable.currentIndex()
        )

    def _reset_referenced_table_combo(self):
        #Resets the referenced table combobox based on the category.
        if self.cboReferencedTable.count() > 0:
            self.cboReferencedTable.setCurrentIndex(0)

        category = self.category()
        if category == 'Table':
            self.cboReferencedTable.setEnabled(False)
            self._sync_data_source = True
        else:
            self.cboReferencedTable.setEnabled(True)
            self._sync_data_source = False
    
    def onShowTables(self,state):
        """
        Slot raised to show STDM database tables.
        """
        if state:
            self._reset_referenced_table_combo()

            self.cboDataSource.clear()
            self.cboDataSource.addItem('')

            for key, value in self._tables.iteritems():
                if not self._contains_supporting_document(key):
                    self.cboDataSource.addItem(value.lower(), key)
            
    def onShowViews(self,state):
        """
        Slot raised to show STDM database views.
        """
        if state:
            self._reset_referenced_table_combo()

            self.cboDataSource.clear()
            self.cboDataSource.addItem('')

            for value in pg_views():
                self.cboDataSource.addItem(value, value)