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

class ADDLookupValue(QDialog):
    def __init__(self,parent):
        QDialog.__init__(self,parent)
        
        
        #add control to the dialog
        self.label=QLabel()
        self.label.setText("Add lookup text")
        self.textField=QLineEdit()
        #self.textField.setPlaceHolderText("Lookup value to be added to the list")
        #self.textField.setLineWrapMode(QTextEdit.WidgetWidth)
        self.buttons=QDialogButtonBox()
        self.buttons.addButton(QDialogButtonBox.Ok)
        self.buttons.addButton(QDialogButtonBox.Cancel)
        
        layout = QGridLayout()
        layout.addWidget(self.label)
        
        layout.addWidget(self.textField)
        layout.addWidget(self.buttons)
        self.setLayout(layout)
        self.setWindowTitle("lookup Text")
        
        self.buttons.accepted.connect(self.addLookup)
        self.buttons.rejected.connect(self.cancel)
    
    def addLookup(self):
        self.value=self.textField.text()
        self.accept()
        
    def cancel(self):
        self.close()
       
        
        
        
        