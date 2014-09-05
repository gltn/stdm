# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdmDialog
                                 A QGIS plugin
 Securing land and property rights for all
                             -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : gltn_stdm@unhabitat.org
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
import sys
from stdm.data import XMLTableElement,tableColumns,tableRelations,ConfigTableReader, activeProfile,writeLookup

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui_lookup import Ui_Lookup
from addtable import TableEditor
from lookup_values_dlg import ADDLookupValue

class LookupDialog(QDialog, Ui_Lookup):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.tableName = None
        self.initControls()
        #QObject.connect(self.listView,SIGNAL('clicked(QModelIndex)'),self.selectedIndex)
        self.btnNew.clicked.connect(self.addLookUp)
        self.cboTable.currentIndexChanged.connect(self.currentTableChanged)
        self.btnChoice.clicked.connect(self.addNewLookupChoice)
        
    def initControls(self):
        #perform initialization of controls
        self.profile = activeProfile()
        self.handler = ConfigTableReader()
        Lkupmodel = self.handler.lookupTableModel()
        self.cboTable.setModel(Lkupmodel)
        self.showDefinedLookupChoices()
    
    def showDefinedLookupChoices(self):
        '''
        show preview of defined lookup choices when the lookup table is selected
        '''
        self.lstData.clear()
        lkChoices = self.handler.readLookupList(self.cboTable.currentText())
        if lkChoices:
            self.lstData.addItems(lkChoices)
    
    def currentTableChanged(self,int):
        '''Load lookup choices based on the selected lookup table'''
        self.showDefinedLookupChoices()
    
    def addNewLookupChoice(self):
        '''Add new choice to lookup table'''
        lkDlg = ADDLookupValue(self)
        if lkDlg.exec_()== QDialog.Accepted:
            lkName = lkDlg.value
            self.handler.addLookupValue(self.cboTable.currentText(), lkName)
        self.showDefinedLookupChoices()
          
    def addLookUp(self):     
        #add new lookup table"
        actionState = [self.profile, QApplication.translate("WorkspaceLoader","Add Lookup")]
        dlg = TableEditor(actionState, None, self)
        dlg.exec_()
        self.initControls()
 
    def acceptDlg(self):
        '''return user selected table''' 
        self.tableName = self.cboTable.currentText()
        self.accept()

    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  
