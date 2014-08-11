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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from stdm.data import dateFormatter
from datetime import date

class InputWidget(QWidget):
    def __init__(self, options=None):
        self.type = ''
        self.control = None
        self.options = options
        
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
    

class BlankIntValidator(QIntValidator):
    def validate(self, input, pos):
        if input == "":
            return QValidator.Acceptable, input, pos
        else:
            return QIntValidator.validate(self,input,pos)
        
class CharacterWidget(InputWidget):
    def __init__(self):
        self.type="character varying"
        
    def Factory(self):
        self.control = QLineEdit()
        return self.control
    
    def adopt(self):
        self.control.setText("")
          
class IntegerWidget(InputWidget):
    def __init__(self):
        self.type = 'integer'
    
    def Factory(self):
        self.control = QSpinBox()
        self.control.setMaximum(1000000000)
        return self.control
    
    def adopt(self):
        self.control.setValue(0)
        

class BlankFloatValidator(QDoubleValidator):
    def validate(self, input, pos):
        if input == "":
            return QValidator.Acceptable, input, pos
        else:
            return QDoubleValidator.validate(self, input, pos)
        
class DoubleWidget(IntegerWidget):
    def __init__(self):
        self.type = "double"
            
    def adopt(self):
        self.control.setValue(0)
        #self.control.setValidator(BlankFloatValidator(self.control))

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
            self.control.insertItems(0, self.options)
        self.control.setMaximumWidth(300)
        self.control.setCurrentIndex(0)

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

def widgetCollection():
    mapping = \
        {
            'integer': IntegerWidget,
            'serial': IntegerWidget,
            'double precision': DoubleWidget,
            'character varying': CharacterWidget,
            'choice': ChoiceListWidget,
            'date': DateWidget
        }
    return mapping