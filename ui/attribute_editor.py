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
import os
import collections
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from collections import OrderedDict
from .ui_attribute_editor import Ui_editor
from .lookupDlg import LookupDialog
from stdm.data  import (
    data_types,
    nullable,
    ConfigTableReader,
    writeTableColumn,
    setCollectiontypes,
    editTableColumn,
    postgres_defaults,
    RESERVED_ID,
    writeGeomConstraint
)
from stdm.data.config_utils import *
from .geometry import GeometryProperty

class AttributeEditor(QDialog,Ui_editor):
    #class constructor
    def __init__(self,profile,tableName,parent, args=None):
        #Initialize the Qwidget parent
        QDialog.__init__(self, parent)
        #Initialize the Qt designer form
        #Iniherit the form controls to this class
        self.setupUi(self)
        
        self.profile = profile
        self.tableName = tableName
        self.args = args
        self.lookup = None
        self.geomCollection = []
        self.cboDatatype.currentIndexChanged.connect(self.postgresDataTypeDefaults)
        self.btnTableList.clicked.connect(self.lookupDialog)
        self.initControls()
        
    def initControls(self):
        self.defaults = postgres_defaults
        tableHandler = ConfigTableReader()
        model = tableHandler.on_main_table_selection()
        self.cboTabList.setModel(model)
        index = self.cboTabList.findText(self.tableName,Qt.MatchExactly)
        if index != -1:
            self.cboTabList.setCurrentIndex(index)
        setCollectiontypes(data_types, self.cboDatatype)
        setCollectiontypes(nullable, self.cboNull)
       
        dIndex=self.cboDatatype.findText('Short text',Qt.MatchExactly)
        if dIndex != -1:
            self.cboDatatype.setCurrentIndex(dIndex)
            self.txtAttrib.setText('50')
        self.cboNull.setCurrentIndex(1)
        self.reloadColumnValues()
        self.initializeValidator()
        
    def initializeValidator(self):
        intValidator = QIntValidator(1, 500, self)
        self.txtAttrib.setValidator(intValidator)

    def reloadColumnValues(self):
        '''provide user with already defined data for editing if it is editing session'''
        if self.args:
            self.txtCol.setText(self.args[0])
            self.txtColDesc.setText(self.args[1])
            self.txtAttrib.setText(self.args[3])
            dIndex = self.cboDatatype.findData(self.args[2],role = Qt.UserRole)
            if dIndex != -1:
                self.cboDatatype.setCurrentIndex(dIndex)    
    
    def attributeData(self,sizeVal):
        #Read the new attribute data from the dialog and pass to config for writing
        # get user inputs to a dictionary
        attribDict={}
        attribDict['name'] = formatColumnName(self.txtCol.text())
        if self.chkPrimaryKey.isChecked():
            attribDict['fullname'] = str(self.txtColDesc.text())
            attribDict['key'] = "1"
        if self.chkPrimaryKey.checkState() == 0:
            attribDict['fullname'] = str(self.txtColDesc.text())
        attribDict['type'] = UserData(self.cboDatatype)
        attribDict['size'] = sizeVal
        attribDict['null'] = UserData(self.cboNull)
        if str(self.txtDefault.text()) != '':
            attribDict['default'] = str(self.txtDefault.text())
        if self.lookup:
            attribDict['lookup'] = self.lookup
        return attribDict
    
    def postgresDataTypeDefaults(self):
        self.txtAttrib.clear()
        atType = UserData(self.cboDatatype)
        if atType in self.defaults:
            self.txtAttrib.setEnabled(False)
            self.txtAttrib.setPlaceholderText('default for postgres')
        if atType not in self.defaults:
            self.txtAttrib.setEnabled(True)
            self.txtAttrib.setPlaceholderText('Enter attribute length')
        self.geometryTypeSelected()
        
    def writeAttributeData(self):
        #Flush the new attribute data to the xml file
        atType = UserData(self.cboDatatype)
        if atType in self.defaults:
            sizeval = ''
        if atType not in self.defaults:
            sizeval = self.txtAttrib.text()
        attribData = self.attributeData(sizeval)
        self.tableName = self.cboTabList.currentText()
        if str(self.tableName).startswith("check"):
            writeTableColumn(attribData,self.profile,'lookup',self.tableName,'columns')
        else:
            if atType == 'geometry':
                self.InfoMessage(QApplication.translate("AttributeEditor",
                    "Geometry column will not appear in the list of column but it is loaded in the background"))
                self.geomtag()
                self.enforceProjection()
            else:
                writeTableColumn(attribData,self.profile,'table',self.tableName,'columns')
    
    def setTableRelation(self):
        '''add new relation to the table in the config file'''
        attribDict={}
        
        attribDict['name'] = formatColumnName(self.txtCol.text())+"_id"
        attribDict['table'] = self.lookup
        attribDict['column'] = "id"
        attribDict['ondelete'] = "NO ACTION"
        attribDict['onupdate'] = "NO ACTION"
        writeTableColumn(attribDict,self.profile,'table',self.tableName,'relations')            
        
                
    def updateColumnData(self):
        '''Delete existing data and set new data defined by the user for this column'''
        atType = UserData(self.cboDatatype)
        if atType in self.defaults:
            sizeval=''
        if atType not in self.defaults:
            sizeval = self.txtAttrib.text()
        desc = self.txtColDesc.text()
        try:
            editTableColumn(self.profile, self.tableName, 'name', self.args[0], formatColumnName(self.txtCol.text()),atType,sizeval, desc)
        except:
            self.ErrorInfoMessage(QApplication.translate('AttributeEditor','Unable to update the column data'))
            return
         
    def clearControls(self):
        self.txtCol.setText('')
        self.txtColDesc.setText('')
        self.txtAttrib.setText('')
    
    def lookupDialog(self):    
        lookUpDlg = LookupDialog(self)
        if lookUpDlg.exec_() == QDialog.Accepted:
            self.lookup = lookUpDlg.tableName
        else:
            self.ErrorInfoMessage("Not lookup selected")
    
    def geometryTypeSelected(self):        
        atType = UserData(self.cboDatatype)
        if atType == 'geometry':
            geomSelect = GeometryProperty(self)
            if geomSelect.exec_() == QDialog.Accepted:
                self.geomCollection = geomSelect.geomCollection
        else:
            pass
        
    def enforceProjection(self):
        if self.geomCollection:
            geom={}
            geom['table'] = self.tableName
            geom['srid'] = self.geomCollection[0]
            geom['column'] = formatColumnName(self.txtCol.text())
            geom['type'] = self.geomCollection[1]
            geom['arguments'] = '2'
            writeTableColumn(geom,self.profile,'table',self.tableName,'geometryz')
    
    def geomtag(self):
        """Add tag on the table with geometry to ensure that it added correctly
        """
        add_geom_tag = writeGeomConstraint(self.profile, 'table', self.tableName)
        return add_geom_tag
            
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("AttributeEditor","STDM"))
        msg.setText(Message)
        msg.exec_()  
    
    def InfoMessage(self,message):
        #Information message box        
        msg=QMessageBox()
        msg.setWindowTitle(unicode(self.windowTitle()))
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()  
                
    def accept(self):
        if str(self.txtCol.text()).lower()== RESERVED_ID or str(self.txtCol.text()).lower() in self.defaults:
            self.ErrorInfoMessage(QApplication.translate('AttributeEditor',"(%s) "
                        "is a reserved word and cannot be used for column name")%str(self.txtCol.text()))
            return
        if self.tableName==None:
            self.ErrorInfoMessage(QApplication.translate('AttributeEditor','No selected table found'))
            return
        if UserData(self.cboDatatype) not in self.defaults and self.txtAttrib.text()=="":
            self.ErrorInfoMessage(QApplication.translate("AttributeEditor","Attribute length is not given"))
            return
        if self.txtCol.text()=="":
            self.ErrorInfoMessage(QApplication.translate("AttributeEditor","Column name is not given"))
            return
        if self.args!=None:
            self.updateColumnData()
        if self.args==None:
            self.writeAttributeData()
        self.clearControls()
        self.close()

    def rejectAct(self):
        self.close()
        
        