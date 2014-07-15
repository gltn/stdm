"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
email                : njoroge.solomon.com
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
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from stdm.data import MapperMixin
from stdm.ui.ui_base_form import Ui_Dialog
from stdm.ui.notification import NotificationBar, ERROR, WARNING,INFO
from stdm.data.config_utils import tableColType
from .property_mapper import TypePropertyMapper
from .attribute_datatype import AttributePropretyType


class MapperDialog(QDialog,Ui_Dialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.setupUi(self)
        #MapperMixin.__init__(self, model)
        self.setWindowTitle("STDM data entry")
        
        self._notifBar = NotificationBar(self.layout)
        self.center()
             
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    def accept(self):
        self.submit()
        self.accept(self)
        
class CustomFormDialog(MapperDialog, MapperMixin):
    def __init__(self,parent,table,model):
        MapperDialog.__init__(self, parent)
        MapperMixin.__init__(self, model)
        
        self._table=table
        self._model=model
                
        tableProperties = self.tableProperty()
        #QMessageBox.information(self,"columns",str(tableProperties))
        propertyMapper = TypePropertyMapper(tableProperties)
        
        widgets=propertyMapper.setProperty()
        
        self.frmLayout. setLabelAlignment(Qt.AlignLeft)
        
        for attrib, widget in widgets.iteritems():
            widgetCls=widget()
            widgetControl=widgetCls.Factory()
            widgetCls.adopt()
            self.addMapping(attrib, widgetControl, True)
            self.frmLayout.addRow(self.userLabel(attrib),widgetControl)
        self.checkDirty()
        
    def userLabel(self,attr):
        if hasattr(self.model(), attr):
            return attr.replace("_", " ").title()
        
    def userAttribute(self,attr):
        pass
    
    def tableProperty(self):
        property = AttributePropretyType(self._table)
        return property.attributeType()
   
            