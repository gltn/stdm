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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from stdm.data import dateFormatter
from datetime import date

class InputWidget(QWidget):
    def __init__(self):
        self.type = ''
        self.control = None
        
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

class CharacterWidget(InputWidget):
    def __init__(self):
        self.type="character varying"
        
    def Factory(self):
        self.control = QLineEdit()
        return self.control
    
    def adopt(self):
        self.control.setMinimumWidth(50)
        self.control.setText("")
          
class IntegerWidget(CharacterWidget):
    def __init__(self):
        self.type = 'integer'
    
    def Factory(self):
        self.control = QSpinBox()
        self.control.setMaximum(1000000000)
        return self.control
    
    def adopt(self):
        self.control.setValue(0)

class DoubleWidget(IntegerWidget):
    def __init__(self):
        self.type = "double"

    def Factory(self):
        self.control = QDoubleSpinBox()

    def adopt(self):
        self.control.setValue(0)

class ChoiceListWidget(CharacterWidget):
    def __init__(self, options=None):
        self.options = options

    def Factory(self):
        self.control = QComboBox()
        return self.control
    
    def setOptions(self, options):
        self.options = options

        return self.options

    def adopt(self):
        if self.options:
            self.control.addItem("")
            for item in self.options:
                self.control.addItem(item.value,item.id)
            self.control.setMinimumContentsLength(50)
            self.control.setDuplicatesEnabled(False)
            #self.control.setMaxVisibleItems(len(self.options))
            self.control.setCurrentIndex(0)

class TextAreaWidget(CharacterWidget):
    def __init__(self):
        self.type ='text'

    def Factory(self):
        self.control = QTextEdit()
        return self.control

    def adopt(self):
        self.control.acceptRichText()
        self.control.canPaste()

class BooleanWidget(CharacterWidget):
    def __init__(self):
        self.type = 'boolean'

    def Factory(self):
        self.control = QComboBox()
        return  self.control

    def adopt(self):
        self.options = {
            '1' : 'Yes',
            '0' : 'No'
        }
        for k, v in self.options.iteritems():
            self.control.addItem(v, k)
        self.control.setMinimumContentsLength(50)
        self.control.setMaxVisibleItems(len(self.options))

class DateWidget(InputWidget):
    def __init__(self):
        self.type= 'date'
        
    def Factory(self):
        self.control = QDateEdit()
        self.control.setCalendarPopup(True)
        return self.control
    
    def adopt(self):
        tDate=date.today()
        self.control.setDate(tDate)
        self.control.setMinimumWidth(50)

def widgetCollection():
    mapping = {
            'character varying': CharacterWidget,
            'integer': IntegerWidget,
            'bigint': IntegerWidget,
            'serial': IntegerWidget,
            'double precision': DoubleWidget,
            'choice': ChoiceListWidget,
            'date': DateWidget,
            'text': TextAreaWidget,
            'boolean': BooleanWidget
        }
    return mapping