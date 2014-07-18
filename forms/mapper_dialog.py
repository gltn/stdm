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
from stdm.ui.notification import NotificationBar
from stdm.data.config_utils import tableColType
from .property_mapper import TypePropertyMapper
from .attribute_datatype import AttributePropretyType

<<<<<<< HEAD
class MapperDailog(QDialog):
    def __init__(self, parent, model):
        QDialog.__init__(self,parent)
=======

class MapperDialog(QDialog,Ui_Dialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.setupUi(self)
>>>>>>> b61dd4fdf353fe3d1408f903e1c014ce14bae7eb
        #MapperMixin.__init__(self, model)
        self.setWindowTitle("STDM data entry")
        
        self._notifBar = NotificationBar(self.vlNotification)
        self.center()
             
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
    
        
class CustomFormDialog(MapperDialog, MapperMixin):
    def __init__(self,parent,model=None):
        MapperDialog.__init__(self, parent)
        MapperMixin.__init__(self, model)
        
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
        if callable(model):
            self._table = model.__name__
        else:
            self._table=model.__class__.__name__
                
        tableProperties = self.tableProperty()
        propertyMapper = TypePropertyMapper(tableProperties)
        widgets=propertyMapper.setProperty()
        
        self.frmLayout. setLabelAlignment(Qt.AlignLeft)
        for attrib, widget in widgets.iteritems():
            if hasattr(model, attrib):
                widgetCls=widget()
                widgetControl=widgetCls.Factory()
                widgetCls.adopt()
                self.addMapping(attrib, widgetControl, False,attrib)
                self.frmLayout.addRow(self.userLabel(attrib),widgetControl)
       
    def userLabel(self,attr):
            return attr.replace("_", " ").title()
        
    def userAttribute(self,attr):
        pass
    
    def tableProperty(self):
        property = AttributePropretyType(self._table.lower())
        return property.attributeType()
   
            
