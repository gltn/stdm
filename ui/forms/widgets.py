"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
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
from datetime import date

from PyQt4.QtGui import *

from stdm.ui.customcontrols import SearchableLineEdit


class InputWidget(QWidget):
    #def __init__(self, parent =None):
    data_type = None

    def Factory(self):
        pass
       
    def adopt(self):
        pass
    
    def save(self):
        pass
    
    def update(self):
        pass

    def type(self):
        pass

    def setOptions(self, opt=None):
        pass

class LineEditWidget(InputWidget):
    data_type = 'string'
    def Factory(self):
        self.control = QLineEdit()
        return self.control
    
    def adopt(self):
        """Set mimimum character length"""
        self.control.setMinimumWidth(50)
        self.control.setText("")
          
class IntegerWidget(LineEditWidget):
    data_type = 'integer'
    def Factory(self):
        self.control = QSpinBox()
        self.control.setMaximum(1000000000)
        self.control.adjustSize()
        return self.control
    
    def adopt(self):
        self.control.setValue(0)

class DoubleWidget(IntegerWidget):
    data_type = 'floating'
    def Factory(self):
        self.control = QDoubleSpinBox()

    def adopt(self):
        self.control.setValue(0)

class ChoiceListWidget(InputWidget):
    data_type = 'list'

    def Factory(self):
        #self.control = MultipleChoiceCombo()
        self.control = QComboBox()
        return self.control
    
    def setOptions(self, options):
        self.options = options
        return self.options

    def adopt(self):
        try:
            if self.options:

                #self.control.set_value(options)
                self.control.addItem("")
                for item in self.options:
                    self.control.addItem(item.value,item.id)
                self.control.setMinimumContentsLength(60)
                self.control.setDuplicatesEnabled(False)
                #self.control.
                self.control.setCurrentIndex(0)
            else:
                return
        except Exception as ex:
            QMessageBox.information(None,QApplication.translate("InputWidget",
                        "Initializing Form Controls"),
            QApplication.translate("InputWidget",
                        "Error loading data for the widget:"))
            

class TextAreaWidget(LineEditWidget):
    data_type = 'long text'
    def Factory(self):
        self.control = QTextEdit()
        return self.control

    def adopt(self):
        self.control.acceptRichText()
        self.control.canPaste()

class BooleanWidget(LineEditWidget):
    data_type = 'boolean'
    def Factory(self):
        self.control = QComboBox()
        return self.control

    def adopt(self):
        self.options = {
            'Yes': 'Yes',
            'No': 'No'
        }
        for k, v in self.options.iteritems():
            self.control.addItem(v, k)
        self.control.setMaxVisibleItems(len(self.options))

class DateEditWidget(InputWidget):
    data_type = 'datetime'
    def Factory(self):
        self.control = QDateEdit()
        self.control.setCalendarPopup(True)
        return self.control
    
    def adopt(self):
        tDate = date.today()
        self.control.setDate(tDate)
        self.control.setMinimumWidth(50)


class ForeignKeyEdit(InputWidget):
    #control_type = SearchableLineEdit
    def Factory(self):
        self.control = SearchableLineEdit()
        self.control.signal_sender.connect(self.foreign_key_widget_activated)
        self.base_id = 0
        return self.control

    def adopt(self):
        self.control.setText("0")
        self.control.setReadOnly(True)

    def foreign_key_widget_activated(self):
        self.on_select_foreignkey()

    def on_select_foreignkey(self):
        from stdm.ui import FKMapperDialog
        mapper = FKMapperDialog()
        mapper.foreign_key_modeller()

        if not mapper.model_display_value():
            mapper.model_display_value() == self.base_id
        self.control.setText(str(mapper.model_display_value()))
        if not mapper.model_fkid():
            self.control.fk_id(self.base_id)
        else:
            self.base_id = mapper.model_fkid()
            self.control.fk_id(self.base_id)


def widgetCollection():
    mapping = {
            'character varying': LineEditWidget,
            'integer': IntegerWidget,
            'bigint': IntegerWidget,
            'serial': IntegerWidget,
            'double precision': DoubleWidget,
            'choice': ChoiceListWidget,
            'date': DateEditWidget,
            'text': TextAreaWidget,
            'foreign key': ForeignKeyEdit,
            'boolean': BooleanWidget

        }
    return mapping
