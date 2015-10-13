"""
/***************************************************************************
name                 : Mapper Dialog
Description          : classes for generating form controls at run time from the passed model attributes
Date                 : 30/June/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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

        self.buttonBox.accepted.connect(self.close_event)
        self.buttonBox.rejected.connect(self.cancel)

        if callable(model):
            self._table = model.__name__
        else:
            self._table = model.__class__.__name__
        self.set_window_title()

        self.setLayout(self.frmLayout)
        self.load_mapper_dialog()

    def load_mapper_dialog(self):
        """
        :return: Mapper dialog form
        """
        try:
            self.property_mapper = TypePropertyMapper(self._table.lower())
            widgets_property_collection = self.property_mapper.setProperty()
            for attrib, widget_prop in widgets_property_collection.iteritems():
                if hasattr(self._model, attrib):
                    #self.control_widget(widget_prop)
                    form_widget_loader = FormWidgetLoader(widget_prop)
                    control_type = form_widget_loader.control_widget(attrib)
                    self.addMapping(attrib, control_type, False, attrib)

                    self.frmLayout.addRow(QT_TRANSLATE_NOOP("ModuleSettings", self.user_label(attrib)), control_type)

        except Exception as ex:
            pass

    def user_label(self, attr):
            return attr.replace("_", " ").title()
        
    def lookup_options(self, widget, widgetOptions):
        try:
            widget.setOptions(widgetOptions)

        except Exception as ex:
            QMessageBox.information(self, QApplication.translate("CustomFormDialog", "Loading lookup"),
                                    QApplication.translate("CustomFormDialog","Error loading lookup values: %s")%ex.message)

    def reset_session_mapping(self):
        """Since only one instance of model can be mapped at a time, ensure the current table model has its correct mapping
        :return table model attribute mapping- dict:
        """
        self.property_mapper.display_mapping()

    def close_event(self):
        try:
            self.reset_session_mapping()
            self.submit()
            self.accept()

        except Exception as ex:
            self._notifBar.insertWarningNotification(unicode(ex.message))

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
    Class to add widget control and the data  into the user form
    """
    def __init__(self, widget_property, parent=None):
        self.widget_property = widget_property

    def control_widget(self, attr):
        """
        Add controls to the form and controls options for lookup choices
        """
        self.init_widget_cls = self.widget_property[0]()
        control_type = self.init_widget_cls.Factory()
        if self.widget_property[1]:
            self.lookup_options(self.init_widget_cls, self.widget_property[2])
        if self.widget_property[3]:
            if self.widget_property[3].add_table_formatters() or len(self.widget_property.add_table_formatters())>0:
                self.init_widget_cls.foreign_key_formatter(attr, self.widget_property[3])
        self.init_widget_cls.adopt()
        return control_type

    def lookup_options(self, widget, widgetOptions):
        """
        Add lookup items on the widget control
        :param widget: QObject
        :param widgetOptions: Sqlalchemy model of the items
        :return:
        """
        widget.setOptions(widgetOptions)
