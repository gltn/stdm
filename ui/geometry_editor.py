# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from stdm.data  import data_types, setCollectiontypes, geometry_collections, edit_geom_column
from stdm.data.config_utils import UserData
from stdm.settings import projectionSelector

class GeometryEditor(QDialog):
    def __init__(self,parent,profile, table, args= None):
        QDialog.__init__(self,parent)

        self.profile = profile
        self.tableName =  table
        self.geom_data = args
        self.oldText = self.geom_data[0]
        #add control to the dialog
        self.label = QLabel()
        self.labelName = QLabel()

        self.label.setText(QApplication .translate("GeometryEditor","Select Geometry Type"))
        self.comboField = QComboBox()
        self.labelName.setText(QApplication .translate("GeometryEditor","Edit Type Name"))
        self.textFieldName = QLineEdit()
        self.sridButton = QPushButton()
        self.sridButton.setText(QApplication .translate("GeometryEditor","Select Coordinate System "))
        self.textField = QLineEdit()

        setCollectiontypes(geometry_collections, self.comboField)
       
        self.buttons = QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.sridButton.clicked.connect(self.projectionsSettings)
        
        layout = QGridLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.comboField)
        layout.addWidget(self.labelName)
        layout.addWidget(self.textFieldName)
        layout.addWidget(self.sridButton)
        layout.addWidget(self.textField)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
        self.setWindowTitle(QApplication .translate("GeometryEditor","Geometry Column Property"))

        self.on_edit_session()
        self.buttons.accepted.connect(self.setGeometrySetting)
        self.buttons.rejected.connect(self.cancel)
        
    def projectionsSettings(self):
        '''let user select the projections for the data'''
        projSelect = projectionSelector(self)
        projection = projSelect.loadAvailableSystems()
        self.textField.setText(str(projection))

    def on_edit_session(self):
        self.textFieldName.setText(self.geom_data[0])
        self.textField.setText(self.geom_data[2])
        index = self.comboField.findData(self.geom_data[1], Qt.UserRole)
        if index:
            self.comboField.setCurrentIndex(index)
        else:
            self.comboField.setCurrentIndex(0)

    def setGeometrySetting(self):
        if self.textField.text() == '':
            self.ErrorInfoMessage(QApplication.translate("GeometryEditor", "Projections is not selected"))
            return
        
        self.value = self.textField.text()[5:]
        if not self.value:
            self.value = self.textField.text()
        geomType=UserData(self.comboField)
        edit_geom_column(self.profile,self.tableName,'column',str(self.oldText),str(self.textFieldName.text()),str(geomType),str(self.value))
        QMessageBox.information(None,QApplication.translate("GeometryEditor","Saving geometry"),
                                QApplication.translate("GeometryEditor","New data Saved successfully"))
        self.accept()
        
    def cancel(self):
        self.close()
        
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("GeometryEditor", "Geometry Settings"))
        msg.setText(Message)
        msg.exec_() 
       
        
        
        
        