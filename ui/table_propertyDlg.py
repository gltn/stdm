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
import os
import collections
from PyQt4.QtGui import QDialog, QMessageBox, QComboBox, QApplication 
from PyQt4.QtCore import *


from stdm.data import actions, constraints,writeTableColumn,ConfigTableReader,setCollectiontypes
from ui_table_property import Ui_TableProperty
from stdm.data.config_utils import *

class TableProperty(QDialog,Ui_TableProperty):
    def __init__(self,usrProf,tableName,parent):
        QDialog.__init__(self,parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.tableName=tableName
        self.userProfile=usrProf
        self.initControls()
        
        QObject.connect(self.rbRelation, SIGNAL('clicked()'), self.propertyType)
        QObject.connect(self.rbConstrain, SIGNAL('clicked()'), self.propertyType)
        QObject.connect(self.cboTable, SIGNAL("currentIndexChanged(int)"), self.relationColumns)
        QObject.connect(self.cboTable_2, SIGNAL("currentIndexChanged(int)"), self.constraintColumns)
        #QObject.connect(self.listView,SIGNAL('clicked(QModelIndex)'),self.selectedIndex)
        
    def initControls(self):
        '''Initialize defualt dialog properties'''
        self.rbRelation.setChecked(True)
        self.gpConstraint.setVisible(False)
        self.tableList(self.cboTable)
        setCollectiontypes(actions,self.cboDelAct)
        setCollectiontypes(actions,self.cboUpAct)
        setCollectiontypes(constraints,self.cboType)
        self.cboColumn.insertItems(0,tableCols(self.cboTable.currentText()))
        self.cboColumn_2.insertItems(0,tableCols(self.cboTable.currentText())) 
        self.cboRefCol.insertItems(0,tableCols(self.tableName))                   
              
    def tableList(self,comboBox):
        tableModel=ConfigTableReader()
        model=tableModel.tableListModel(self.userProfile)
        comboBox.setModel(model)
        index=comboBox.findText(self.tableName,Qt.MatchExactly)
        if index!=-1:
            comboBox.setCurrentIndex(index-1) 
    
    def propertyType(self):
        if self.rbRelation.isChecked():
            self.gpRelation.setVisible(True)
            self.gpConstraint.hide()
            self.tableList(self.cboTable)
            self.relationColumns()
            self.localColumns()
        if self.rbConstrain.isChecked():
            self.gpConstraint.setVisible(True)
            self.gpRelation.hide()
            self.tableList(self.cboTable_2)
            self.constraintColumns()
   
    def setCollectiontypes(self,collectionType,combo):
        #method to read defult  to a sql relations and constraint type to combo box
        ordDict=collections.OrderedDict(collectionType.items())
        combo.clear()
        for k, v in ordDict.iteritems():
            combo.addItem(k,v)
            combo.setInsertPolicy(QComboBox.InsertAlphabetically)
        
        combo.setMaxVisibleItems(len(collectionType))
    
    def relationColumns(self):
        '''update columns set for the selected table'''
        self.cboColumn.clear()
        referenceTable=self.cboTable.currentText()
        self.cboColumn.insertItems(0,tableCols(referenceTable))
        
    def localColumns(self):
        '''update columns set for the selected table'''
        self.cboRefCol.clear()
        self.cboRefCol.insertItems(0,tableCols(self.tableName))
        
    def constraintColumns(self):
        '''update columns set for the selected table'''
        self.cboColumn_2.clear()
        referenceTable=self.cboTable_2.currentText()
        self.cboColumn_2.insertItems(0,tableCols(referenceTable))  
        
    def selectedData(self,comboBox):
        #get the user data from the combo box display item
        text=comboBox.currentText()
        index=comboBox.findText(text, Qt.MatchExactly)
        if index!=-1:
            userData=comboBox.itemData(int(index))
            return userData
        
    def setTableRelation(self):
        '''add new relation to the table in the config file'''
        delAct=UserData(self.cboDelAct)
        updateAct=UserData(self.cboUpAct)
        attribDict={}
        attribDict['name']=formatColumnName(self.txtName.text())
        attribDict['table']=self.cboTable.currentText()
        attribDict['fk']=self.cboRefCol.currentText()
        attribDict['column']=self.cboColumn.currentText()
        attribDict['ondelete']=delAct
        attribDict['onupdate']=updateAct
        writeTableColumn(attribDict,self.userProfile,'table',self.tableName,'relations')
        
    def accept(self):
        if self.rbRelation.isChecked() and self.txtName.text()=='':
            self.ErrorInfoMessage(QApplication.translate("TableProperty","Relation Name is not given"))
            return
        if self.rbRelation.isChecked():
            self.setTableRelation()
            self.close()
            
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor","STDM"))
        msg.setText(Message)
        msg.exec_() 