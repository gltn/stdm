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
from stdm.data  import data_types, setCollectiontypes, geometry_collections
from stdm.data.config_utils import UserData
from stdm.settings import ProjectionSelector

class GeometryProperty(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        
        
        #add control to the dialog
        self.label = QLabel()
        self.label.setText(QApplication.translate("GeometryProperty","Select Geometry Type"))
        self.comboField = QComboBox()
        self.sridButton = QPushButton()
        self.sridButton.setText(QApplication.translate("GeometryProperty","Select Coordinate System "))
        self.textField = QLineEdit()

        setCollectiontypes(geometry_collections, self.comboField)
       
        self.buttons=QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        self.sridButton.clicked.connect(self.projectionsSettings)
        
        layout = QGridLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.comboField)
        layout.addWidget(self.sridButton)
        layout.addWidget(self.textField)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
        self.setWindowTitle(QApplication.translate("GeometryProperty","Geometry Column Property"))
        
        self.buttons.accepted.connect(self.setGeometrySetting)
        self.buttons.rejected.connect(self.cancel)
        
    def projectionsSettings(self):
        '''let user select the projections for the data'''
        projSelect=ProjectionSelector(self)
        projection=projSelect.load_available_systems()
        self.textField.setText(str(projection))
        
    def setGeometrySetting(self):
        if self.textField.text() == '':
            self.ErrorInfoMessage(QApplication.translate("GeometryProperty", "Projections is not selected"))
            return
        
        self.value = self.textField.text()[5:]
        geomType=UserData(self.comboField)
        self.geomCollection = [self.value,geomType]
        self.accept()
        
    def cancel(self):
        self.close()
        
    def ErrorInfoMessage(self, Message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(QApplication.translate("GeometryProperty", "Geometry Settings"))
        msg.setText(Message)
        msg.exec_() 
       
        
        
        
        