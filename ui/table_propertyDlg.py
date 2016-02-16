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

from stdm.data.config_table_reader import ConfigTableReader
from stdm.data.enums import (
    actions,
    constraints
)
from stdm.data.xmlconfig_writer import writeTableColumn
from stdm.data.config_utils import *

from ui_table_property import Ui_TableProperty

class TableProperty(QDialog, Ui_TableProperty):
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
        self.table_handler=ConfigTableReader()
        self.initControls()

        QObject.connect(self.cboTable, SIGNAL("currentIndexChanged(int)"), self.relationColumns)
        
    def initControls(self):
        '''Initialize defualt dialog properties'''
        self.tableList(self.cboTable)
        setCollectiontypes(actions,self.cboDelAct)
        setCollectiontypes(actions,self.cboUpAct)
        self.table_column_model(self.cboColumn,self.cboTable.currentText())
        self.table_column_model(self.cboRefCol,self.tableName)
        self.table_column_model(self.cboType, self.cboTable.currentText())
              
    def tableList(self,comboBox):
        model=self.table_handler.tableListModel(self.userProfile)
        comboBox.setModel(model)
        index=comboBox.findText(self.tableName,Qt.MatchExactly)
        if index!=-1:
            comboBox.setCurrentIndex(index-1)

    def table_column_model(self, combo, tableName):
        """
        Return a list of column as QAbstractListModel
        :param combo:
        :param tableName:
        :return:
        """
        col_list =tableCols(tableName)
        col_model = self.table_handler.column_labels(col_list)
        combo.setModel(col_model)
   
    def setCollectiontypes(self,collectionType,combo):
        #method to read defult  to a sql relations and constraint type to combo box
        ordDict=collections.OrderedDict(collectionType)
        combo.clear()
        for k, v in ordDict.iteritems():
            combo.addItem(k,v)
            combo.setInsertPolicy(QComboBox.InsertAlphabetically)
        combo.setMaxVisibleItems(len(collectionType))
    
    def relationColumns(self):
        '''update columns set for the selected table'''
        referenceTable=self.cboTable.currentText()
        self.table_column_model(self.cboColumn,referenceTable)
        self.table_column_model(self.cboType,referenceTable)
        
    def localColumns(self):
        '''update columns set for the selected table'''
        self.table_column_model(self.cboRefCol,self.tableName)

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
        attribDict['display_name']=self.cboType.currentText()
        attribDict['ondelete']=delAct
        attribDict['onupdate']=updateAct
        writeTableColumn(attribDict,self.userProfile,'table',self.tableName,'relations')
        
    def accept(self):
        if self.txtName.text()=='':
            self.ErrorInfoMessage(QApplication.translate("TableProperty","Relation Name is not given"))
            return
        if self.cboTable.currentText()=="":
            self.ErrorInfoMessage(QApplication.translate("TableProperty","Referenced Table is not selected"))
            return
        if self.cboTable.currentText()== self.tableName:
            self.ErrorInfoMessage(QApplication.translate("TableProperty","Table cannot draw a reference from itself"))
            return
        self.setTableRelation()
        self.close()
            
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor","STDM"))
        msg.setText(Message)
        msg.exec_() 