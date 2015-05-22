"""
/***************************************************************************
Name                 : Mapper Dialog
Description          : classes for generating form controls at run time from the passed model attributes
Date                 : 30/June/2014
copyright            : (C) 2014 by Solomon Njogu
email                : njoroge.solomon.@yahoo.com
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
        boxLayout = QVBoxLayout()
        self.setLayout(boxLayout)

        self._notifBar = NotificationBar(self.vlNotification)
        self.frmLayout.setLabelAlignment(Qt.AlignLeft)
        self.frmLayout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.setWindowModality(Qt.NonModal)
        self.center()
             
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        
class CustomFormDialog(MapperDialog, MapperMixin):
    def __init__(self, parent, model=None):
        self._model = model

        MapperDialog.__init__(self, parent)
        MapperMixin.__init__(self, self._model)
        #QMessageBox.information(self,"Model instance",str(self._model))
        self.buttonBox.accepted.connect(self.close_event)
        self.buttonBox.rejected.connect(self.cancel)
        #self.frmLayout.clicked.connect(self.form_event)
        if callable(model):
            self._table = model.__name__
        else:
            self._table = model.__class__.__name__
        self.set_window_title()

        self.setLayout(self.frmLayout)
        self.loadMapperDialog()

    def loadMapperDialog(self):
        """
        :return: Mapper dialog form
        """
        #try:
        self.property = AttributePropretyType(self._table.lower())
        # start loading table attribute properties
        table_properties = self.property.attribute_type()

        property_mapper = TypePropertyMapper(table_properties)
        widgets = property_mapper.setProperty()
        for attrib, widget_prop in widgets.iteritems():
            if hasattr(self._model, attrib):
                #self.control_widget(widget_prop)
                form_widget_loader = FormWidgetLoader(widget_prop)
                control_type = form_widget_loader.control_widget()
                self.addMapping(attrib, control_type, False, attrib)

                self.frmLayout.addRow(QT_TRANSLATE_NOOP("ModuleSettings",self.userLabel(attrib)), control_type)
        self.frmLayout.setLabelAlignment(Qt.AlignJustify)
        #except Exception as ex:
           # self._notifBar.insertWarningNotification(str(ex.message))

    def userLabel(self, attr):
            return attr.replace("_", " ").title()
        
    def lookupOptions(self, widget, widgetOptions):
        try:
            widget.setOptions(widgetOptions)
        except Exception as ex:
            QMessageBox.information(self, QApplication.translate("CustomFormDialog", "Loading lookup"),
                                    QApplication.translate("CustomFormDialog","Error loading lookup values: %s")%ex.message)

    def reset_session_mapping(self):
        """Since only one instance of model can be mapped at a time, ensure the current table model has its correct mapping
        :return table model attribute mapping- dict:
        """
        self.property.display_mapping()

    def close_event(self):
        try:
            self.reset_session_mapping()
            self.submit()
            self.accept()

        except Exception as ex:
            self._notifBar.insertWarningNotification(str(ex.message))
        finally:
            STDMDb.instance().session.rollback()

    def set_window_title(self):
        """
        Set the dialog title from the model name
        :return: string
        """
        self.setWindowTitle(QApplication.translate("CustomFormDialog", self._table + " Entity Editor"))

class FormWidgetLoader(object):
    """
    Class to format a widget control into data control on the form
    """
    def __init__(self, widget_property, parent=None):
        self.widget_property = widget_property

    def control_widget(self):
        """
        Add controls to the form and controls options for lookup choices
        """
        self.init_widget_cls = self.widget_property[0]()
        control_type = self.init_widget_cls.Factory()
        if self.widget_property[1]:
            self.lookupOptions(self.init_widget_cls, self.widget_property[2])
        self.init_widget_cls.adopt()
        return control_type

    def lookupOptions(self, widget, widgetOptions):
        """
        Add lookup items on the widget control
        :param widget: QObject
        :param widgetOptions: Sqlalchemy model of the items
        :return:
        """
        widget.setOptions(widgetOptions)
