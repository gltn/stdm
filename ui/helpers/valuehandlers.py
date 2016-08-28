"""
/***************************************************************************
Name                 : Control Value Handlers
Description          : Classes for getting and setting values for Qt input 
                       controls.
Date                 : 27/January/2014
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

from PyQt4.QtGui import (
    QLineEdit,
    QCheckBox,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QApplication,
    QMessageBox,
    QDateTimeEdit,
    QSpinBox,
    QDoubleSpinBox
)

from stdm.ui.sourcedocument import SourceDocumentManager
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.customcontrols import CoordinatesWidget
from stdm.utils.util import setComboCurrentIndexWithItemData
from stdm.ui.customcontrols  import MultipleChoiceCombo
#from stdm.ui.attribute_browser import AttributeBrowser
from stdm.ui.customcontrols.relation_line_edit import (
    AdministrativeUnitLineEdit,
    RelatedEntityLineEdit
)
from stdm.ui.customcontrols.multi_select_view import MultipleSelectTreeView

class ControlValueHandler(object):
    control = None
    handlers = {}
    '''
    Abstract class that provides a mechanism for subclasses to define how 
    values for specific controls are set and extracted.
    Setter injection of the control.
    '''     
    def setControl(self,control):
        self.control = control
    
    @classmethod
    def register(cls):
        '''
        Used to register control value handler classes for use in the factory.
        '''
        try:
            ctlClassName = cls.controlType.staticMetaObject.className()
            ControlValueHandler.handlers[ctlClassName] = cls
        except AttributeError:
            #Should be logged
            raise AttributeError("Attribute not found")
    
    def isControlTypeValid(self):
        '''
        Raise type error if the type of control does not match the instance type.
        '''
        if self.control == None or not isinstance(self.control,self.controlType):
            raise TypeError
        else:
            return True
        
    def value(self):
        raise NotImplementedError
    
    def setValue(self,value):
        raise NotImplementedError
    
    def supportsMandatory(self):
        '''
        Indicates whether the control has a default state/value and whether either of these
        states can be used to support mandatory values.
        '''
        raise NotImplementedError
    
    def default(self):
        '''
        Returns the default value of the control. This complements 'supportsMandatory' method 
        for comparison purposes with the current value.
        '''
        raise NotImplementedError
    
class LineEditValueHandler(ControlValueHandler):
    '''
    QLineEdit text reader.
    '''
    controlType = QLineEdit
    
    def value(self):
        return self.control.text()
    
    def setValue(self,value):
        self.control.setText(value)
        
    def supportsMandatory(self):
        return True
    
    def default(self):
        return ''
    
LineEditValueHandler.register()


class AdministrativeUnitLineEditValueHandler(LineEditValueHandler):
    """
    Value handler for AdministrativeUnitLineEdit control.
    """
    controlType = AdministrativeUnitLineEdit

    def value(self):
        if not self.control.current_item is None:
            return self.control.current_item.id

        return None

    def setValue(self, value):
        if not value is None:
            self.control.load_current_item_from_id(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return None

AdministrativeUnitLineEditValueHandler.register()


class RelatedEntityLineEditValueHandler(AdministrativeUnitLineEditValueHandler):
    """
    Value handler for RelatedEntityLineEdit control.
    """
    controlType = RelatedEntityLineEdit

RelatedEntityLineEditValueHandler.register()


class MultipleSelectTreeViewValueHandler(ControlValueHandler):
    """
    Value handler for MultipleSelectTreeView control.
    """
    controlType = MultipleSelectTreeView

    def value(self):
        return self.control.selection()

    def setValue(self, value):
        if not value is None:
            self.control.set_selection(value)

    def supportsMandatory(self):
        return True

    def default(self):
        return []

MultipleSelectTreeViewValueHandler.register()

    
class CheckBoxValueHandler(ControlValueHandler):
    '''
    QCheckBox state reader.
    '''
    controlType = QCheckBox
    
    def value(self):
        return self.control.isChecked()
    
    def setValue(self,value):
        if isinstance(value, str) or \
                isinstance(value, unicode):
            if value.lower() in ("yes", "true", "t", "1"):
                self.control.setChecked(True)
            else:
                self.control.setChecked(False)
        else:
            if value is None:
                self.control.setChecked(False)
            else:
                self.control.setChecked(False)

    def supportsMandatory(self):
        return False
    
CheckBoxValueHandler.register()
    
class TextEditValueHandler(LineEditValueHandler):
    '''
    TextEdit value reader.
    '''
    controlType = QTextEdit
    
    def value(self):
        return self.control.toPlainText()
    
    def setValue(self,value):
        self.control.setText(value)
    
TextEditValueHandler.register()
    
class ComboBoxValueHandler(LineEditValueHandler):
    '''
    Combo box current selection value reader.
    Returns the current displayed string.
    '''
    controlType = QComboBox
    
    def value(self):
        dataID = self.control.itemData(self.control.currentIndex())
        
        return dataID
    
    def setValue(self,value):
        setComboCurrentIndexWithItemData(self.control,value)
    
    def supportsMandatory(self):
        return True
    
    def default(self):
        return None
    
ComboBoxValueHandler.register()
    
class DateEditValueHandler(ControlValueHandler):
    '''
    DateEdit value reader.
    '''
    controlType = QDateEdit

    def value(self):
        return self.control.date()

    def setValue(self, value):
        if value is not None:
            try:
                self.control.setDate(value)
            except RuntimeError:
                QMessageBox.warning(
                    None,
                    QApplication.translate(
                        'DateEditValueHandler',
                        "Attribute Table Error"
                    ),
                    'The change is not saved. '
                    'Please use the form to edit data.'
                )
            except TypeError:
                pass

    def supportsMandatory(self):
        return False
    
DateEditValueHandler.register()


class DateTimeEditValueHandler(ControlValueHandler):
    '''
    DateTimeEdit value reader.
    '''
    controlType = QDateTimeEdit

    def value(self, for_spatial_unit=False):

            return self.control.dateTime()

    def setValue(self,value, for_spatial_unit=False):

        try:
            self.control.setDateTime(value)
        except RuntimeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'DateTimeEditValueHandler',
                    "Attribute Table Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            pass

    def supportsMandatory(self):
        return False

DateTimeEditValueHandler.register()

    
class SourceDocManagerValueHandler(ControlValueHandler):
    '''
    Source Document Manager value handler.
    '''
    controlType = SourceDocumentManager

    def value(self):
        #Get source document objects
        return self.control.model_objects()
    
    def setValue(self,value):
        if not value is None:
            self.control.set_source_documents(value)
    
    def supportsMandatory(self):
        return True
    
    def default(self):
        return []
    
SourceDocManagerValueHandler.register()


class ForeignKeyMapperValueHandler(ControlValueHandler):
    '''
    ForeignKeyMapper value handler.
    '''
    controlType = ForeignKeyMapper
    
    def value(self):
        return self.control.entities()
    
    def setValue(self,value):
        self.control.setEntities(value)

    def default(self):
        return None

    def supportsMandatory(self):
        return True

ForeignKeyMapperValueHandler.register()

class SpinBoxValueHandler(ControlValueHandler):
    '''
    QSpinBox value handler.
    '''
    controlType = QSpinBox
    
    def value(self):
        return self.control.value()
    
    def setValue(self,value):
        if value != None:
            self.control.setValue(value)
        else:
            self.control.setValue(0)
    
    def supportsMandatory(self):
        return False
    
    def default(self):
        return None
    
SpinBoxValueHandler.register()

class DoubleSpinBoxValueHandler(SpinBoxValueHandler):
    '''
    QDoubleSpinBox value handler.
    '''
    controlType = QDoubleSpinBox
    
DoubleSpinBoxValueHandler.register()

class CoordinatesWidgetValueHandler(ControlValueHandler):
    '''
    Value handler for CoordinatesWidget.
    '''
    controlType = CoordinatesWidget
    
    def value(self):
        return self.control.toEWKT()
    
    def setValue(self,value):
        pass
    
    def supportsMandatory(self):
        return False
    
    def default(self):
        return None
    
CoordinatesWidgetValueHandler.register()


class MultipleChoiceComboBox(ControlValueHandler):

    controlType = MultipleChoiceCombo

    def value(self):
        ctlValue = self.control.values()
        return ctlValue

    def setValue(self,value):
        if value:
            self.control.set_values(value)

MultipleChoiceComboBox.register()





















