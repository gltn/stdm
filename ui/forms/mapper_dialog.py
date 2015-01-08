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
from stdm.data import STDMDb
from stdm.ui.ui_base_form import Ui_Dialog
from stdm.ui.notification import NotificationBar
from .property_mapper import TypePropertyMapper
from .attribute_datatype import AttributePropretyType


class MapperDialog(QDialog,Ui_Dialog):
    def __init__(self,parent):
        QDialog.__init__(self)
        self.setupUi(self)

        #MapperMixin.__init__(self, model)
        #self.setWindowTitle("STDM data entry")
        
        self._notifBar = NotificationBar(self.vlNotification)
        self.center()
             
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
class CustomFormDialog(MapperDialog, MapperMixin):
    def __init__(self, parent, model=None):
        MapperDialog.__init__(self, parent)
        MapperMixin.__init__(self, model)
        
        self.buttonBox.accepted.connect(self.closeAct)
        self.buttonBox.rejected.connect(self.cancel)
        
        if callable(model):
            self._table = model.__name__
        else:
            self._table = model.__class__.__name__
        self.setWindowTitle("{0} Entity Editor".format(self._table))
        self.frmLayout.setLabelAlignment(Qt.AlignLeft)
        self.loadMapperDialog()

    def loadMapperDialog(self):
        """
        :return: Mapper dialog form
        """
        self.property = AttributePropretyType(self._table.lower())
        # start loading table attribute properties
        table_properties = self.property.attributeType()

        property_mapper = TypePropertyMapper(table_properties)
        widgets = property_mapper.setProperty()
        for attrib, widgetProp in widgets.iteritems():
            if hasattr(self._model, attrib):
                self.controlWidget(widgetProp)
                self.addMapping(attrib, self.control, False, attrib)
                self.frmLayout.addRow(self.userLabel(attrib), self.control)
        self.frmLayout.setLabelAlignment(Qt.AlignJustify)

    def userLabel(self, attr):
            return attr.replace("_", " ").title()
        
    def lookupOptions(self, widget, widgetOptions):
        try:
            widget.setOptions(widgetOptions)
        except Exception as ex:
            QMessageBox.information(self, QApplication.translate("CustomFormDialog", "Loading lookup"), str(ex.message))

    def controlWidget(self, prop):
        """
        Add controls to the form and controls options for lookup choices
        """
        self.widgetCls = prop[0]()
        self.control = self.widgetCls.Factory()
        if prop[1]:
            self.lookupOptions(self.widgetCls, prop[2])
        self.widgetCls.adopt()

    def resetSessionMapping(self):
        """Since only one instance of model can be mapped at a time, ensure the current table model has its correct mapping
        :return table model attribute mapping- dict:
        """
        self.property.displayMapping()

    def closeAct(self):
        try:
            self.resetSessionMapping()
            self.submit()
            self.accept()

        except Exception as ex:
            self._notifBar.insertWarningNotification(str(ex.message))
        finally:
            STDMDb.instance().session.rollback()