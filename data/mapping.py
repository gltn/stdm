"""
/***************************************************************************
Name                 : Database Model/Widget Mapping Classes
Description          : Classes that enable the mapping of database model 
                       attributes to the corresponding UI widgets for rapid
                       building of custom STDM forms.
Date                 : 28/January/2014 
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
from PyQt4.QtGui import QApplication, QMessageBox, QDialog

from qgis.gui import *
from qgis.core import *

from stdm.ui.helpers import valueHandler
from stdm.ui.helpers import ControlDirtyTrackerCollection
from stdm.ui.notification import NotificationBar
from stdm.ui.notification import ERROR
from stdm.ui.notification import WARNING
from stdm.ui.notification import INFO

__all__ = ["SAVE", "UPDATE", "MapperMixin", "QgsFeatureMappperMixin"]

'''
Save mode enum for specifying whether a widget is in 'Save' mode - when creating 
a new record or 'Update' mode, which is used when updating an existing record.
'''
SAVE = 2200
UPDATE = 2201

class _AttributeMapper(object):
    '''
    Manages a single instance of the mapping between a database model's attribute
    and the corresponding UI widget.
    '''
    def __init__(self, attribute_name, qtcontrol, model, pseudoname="", is_mandatory=False, \
                 custom_value_handler=None, bind_control_only=False):
        '''
        :param attribute_name: Property name of the database model that is to be mapped.
        :param qtControl: Qt input widget that should be mapped to the model's attribute.
        :param model: STDM model to which the attribute name belongs to.
        :param isMandatory: Flag to indicate whether a value is required from the input control.
        :param customValueHandler: Instance of a custom value handler can be provided if it does not exist amongst 
        those in the registered list.
        :param bindControlOnly: The model will not be updated using the control's value. This is used to only 
        update the control value using the model value when the mapper is in 'Update' mode.
        '''
        self._attr_name = attribute_name
        self._control = qtcontrol
        self._model = model
        self._is_mandatory = is_mandatory
        self._bind_control_only = bind_control_only
        
        if custom_value_handler == None:
            self._value_handler = valueHandler(qtControl)()
        else:
            self._value_handler = customValueHandler()
            
        if not self._value_handler is None:
            self._value_handler.setControl(qtcontrol)
            
        self._pseudoname = attribute_name if pseudoname == "" else pseudoname
            
    def attribute_name(self):
        '''
        Attribute name.
        '''
        return self._attr_name
    
    def pseudoname(self):
        '''
        Returns the pseudoname of the mapper. This is useful when the attribute name refers to a foreign key
        and as such cannot be used for displaying user-friendly text; then in such a case, the pseudoname can
        be used for displaying a user friendly name.
        '''
        return self._pseudoname
    
    def control(self):
        '''
        Referenced Qt input widget.
        '''
        return self._control
    
    def value_handler(self):
        '''
        Return value handler associated with this control.
        '''
        return self._value_handler
    
    def control_value(self):
        '''
        Returns the value in the control.
        '''
        return self._value_handler.value()
    
    def is_mandatory(self):
        '''
        Returns whether the field is mandatory.
        '''
        return self._is_mandatory
    
    def set_mandatory(self, mandatory):
        '''
        Set field should be mandatory
        '''
        self._is_mandatory = mandatory
        
    def bind_control(self):
        '''
        Sets the value of the control using the model's attribute value.
        '''
        if hasattr(self._model, self._attr_name):
            attr_value = getattr(self._model, self._attr_name)
            self._value_handler.setValue(attr_value)
            
    def bind_model(self):
        '''
        Set the model attribute value to the control's value.
        The handler is responsible for adapting Qt and Python types as expected
        and defined by the model.
        '''
        if hasattr(self._model, self._attr_name):
            control_value = self._value_handler.value()
            setattr(self._model,self._attr_name, control_value)
    
class MapperMixin(object):
    '''
    Mixin class for use in a dialog or widget, and does the heavy lifting when it comes to managing attribute mapping.
    '''
    def __init__(self, model):
        '''
        :param model: Callable (new instances) or instance (existing instance for updating) of STDM model.
        '''
        if callable(model):
            self._model = model()
            self._mode = SAVE
        else:
            self._model = model
            self._mode = UPDATE
        
        self._attr_mappers = []
        self._attr_mapper_collection={}
        self._dirty_tracker = ControlDirtyTrackerCollection()
        self._notif_bar = None
        
        #Initialize notification bar
        if hasattr(self, "vlNotification"):
            self._notif_bar = NotificationBar(self.vlNotification)
        
        #Flag to indicate whether to close the widget or dialog once model has been submitted
        #self.closeOnSubmit = True
        
    def add_mapping(self, attribute_name, control, is_mandatory=False, pseudoname="", value_handler=None, preload_func=None):
        '''
        Specify the mapping configuration.
        '''
        attr_mapper = _AttributeMapper(attribute_name, control, self._model, pseudoname, is_mandatory, value_handler)
        self.add_mapper(attr_mapper, preload_func)
        
    def add_mapper(self, attribute_mapper, preload_func=None):
        '''
        Add an attributeMapper object to the collection.
        Preload_func specifies a function that can be used to prepopulate the control's value only when
        the control is on SAVE mode.
        '''
        if self._mode == SAVE and preload_func != None:
            attribute_mapper.value_handler().setValue(preload_func)
        
        if self._mode == UPDATE:
            #Set control value based on the model attribute value
            attribute_mapper.bind_control()
            
        #Add control to dirty tracker collection after control value has been set
        self._dirty_tracker.addControl(attribute_mapper.control(), attribute_mapper.valueHandler())
            
        self._attr_mappers.append(attribute_mapper)
        self._attr_mapper_collection[attribute_mapper.attribute_name()] = attribute_mapper
        
    def save_mode(self):
        '''
        Return the mode that the mapper is currently configured in.
        '''
        return self._mode

    def attribute_mapper(self, attribute_name):
        """
        Returns attribute mapper object corresponding to the the given
        attribute.
        :param attribute_name: Name of the attribute
        :type attribute_name: str
        :return: Attribute mapper
        :rtype: _AttributeMapper
        """
        return self._attr_mapper_collection.get(attribute_name, None)

    def attribute_exists(self, attribute_name):
        """
        :param attribute_name: Attribute name
        :type attribute_name: str
        :return: True if the attribute exists in the collection. Otherwise,
        False.
        :rtype: bool
        """
        attr_mapper = self.attribute_exists(attribute_name)
        if attr_mapper is None:
            return False
        else:
            return True
    
    def set_save_mode(self, mode):
        '''
        Set the mapper's save mode.
        '''
        self._mode = mode
        
    def set_model(self, stdm_model):
        '''
        Set the model to be used by the mapper.
        '''
        self._model = stdm_model
        
    def model(self):
        '''
        Returns the model configured for the mapper.
        '''
        return self._model
        
    def set_notification_layout(self, layout):
        '''
        Set the vertical layout instance that will be used to display notification messages.
        '''
        self._notif_bar = NotificationBar(layout)
        
    def insert_notification(self, message, mtype):
        '''
        There has to be a vertical layout, named 'vlNotification', that
        enables for notifications to be inserted.
        '''
        if self._notif_bar:
            self._notif_bar.insert_notification(message, mtype)   
            
    def clear_notifications(self):         
        '''
        Clears all messages in the notification bar.
        '''
        if self._notif_bar:
            self._notif_bar.clear()
            
    def check_dirty(self):
        '''
        Asserts whether the dialog contains dirty controls.
        '''
        isDirty = False
        msgResponse = None
        
        if self._dirty_tracker.isDirty():
            isDirty = True
            msg = QApplication.translate("MappedDialog", "Would you like to save changes before closing?")
            msgResponse = QMessageBox.information(self, QApplication.translate("MappedDialog","Save Changes"), msg, 
                                             QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            
        return isDirty,msgResponse
    
    def close_event(self,event):
        '''
        Raised when a request to close the window is received.
        Check the dirty state of input controls and prompt user to save if dirty.
        ''' 
        isDirty, user_response = self.check_dirty()
        
        if isDirty:
            if user_response == QMessageBox.Yes:
                #We need to ignore the event so that validation and saving operations can be executed
                event.ignore()
                self.submit()
            elif user_response == QMessageBox.No:
                event.accept()
            elif user_response == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()
    
    def cancel(self):
        '''
        Slot for closing the dialog.
        Checks the dirty state first before closing.
        '''
        isDirty, user_response = self.check_dirty()
        
        if isDirty:
            if user_response == QMessageBox.Yes:
                self.submit()
            elif user_response == QMessageBox.No:
                self.reject()
            elif user_response == QMessageBox.Cancel:
                pass
        else:
            self.reject()
    
    def pre_save_update(self):
        '''
        Mixin classes can override this method to specify any operations that need to be executed
        prior to saving or updating the model's values.
        It should return True prior to saving.
        '''
        return True
    
    def post_save_update(self, dbmodel):
        '''
        Executed once a record has been saved or updated. 
        '''
        pass
    
    def submit(self):
        '''
        Slot for saving or updating the model. This will close the dialog on successful submission.
        '''
        if not self.pre_save_update():
            return
        
        self.clear_notifications()
        isValid= True
        
        #Validate mandatory fields have been entered by the user.
        for attr_mapper in self._attr_mappers:
            if attr_mapper.is_mandatory() and attr_mapper.value_handler().supports_mandatory():
                if attr_mapper.value_handler().value() == attrMapper.value_handler().default():
                    #Notify user
                    msg = QApplication.translate("MappedDialog", "(%s) is a required field.")%str(attr_mapper.pseudoname())
                    self._notif_bar.insert_warning_notification(msg)
                    isValid = False
                else:
                    attr_mapper.bind_model()
                    
            else:
                attr_mapper.bind_model()
        
        if not isValid:
            return
        
        self._persist_model()
            
    def _persist_model(self):
        #Persist the model to its corresponding store.
        if self._mode == SAVE:
            self._model.save()
            QMessageBox.information(self, QApplication.translate("MappedDialog","Record Saved"), \
                                    QApplication.translate("MappedDialog","New record has been successfully saved"))
            
        else:
            self._model.update()
            QMessageBox.information(self, QApplication.translate("MappedDialog","Record Updated"), \
                                    QApplication.translate("MappedDialog","Record has been successfully updated"))
            
        #Close the dialog
        if isinstance(self, QDialog):
            self.post_save_update(self._model)
            self.accept()

class _QgsFeatureAttributeMapper(_AttributeMapper):
    '''
    Manages a single instance of the mapping between a QgsFeature attribute and the corresponding UI widget.
    For use in the editor widget when digitizing new features.
    '''
    def bind_control(self):
        '''
        Base class override that sets the value of the control based on the value of the QgsField
        with the given attribute index instead of the name.
        '''
        try:
            attr_val = self._model.attribute(self._attr_name)
            self._value_handler.setValue(attr_val)
        except KeyError:
            #If the field is not found then log the message into the console.
            QgsMessageLog.logMessage(QApplication.translate("QgsFeatureAttributeMapper", \
                                                            "Attribute name '%s' not found.")%str(self._attr_name), \
                                     QgsMessageLog.CRITICAL)

    def bind_model(self):
        '''
        Base class override that sets the value of the feature attribute.
        '''
        try:
            ctlValue = self._value_handler.value()
            self._model.setAttribute(self._attr_name, ctlValue)
        except KeyError:
            #If the field is not found then log the message into the console.
            QgsMessageLog.logMessage(QApplication.translate("QgsFeatureAttributeMapper", \
                                                            "Attribute index '%s' not found.")
                                     %str(self._attr_name),level = QgsMessageLog.CRITICAL)
            
class QgsFeatureMapperMixin(MapperMixin):
    '''
    Mixin class for mapping QgsFeature attributes. For use in a spatial editor widget.
    '''
    def __init__(self, layer, feature, mode = SAVE):
        #In this case, the feature will have to be instantiated rather than checking whether it is a callable.
        MapperMixin.__init__(self, feature)
        self._mode = mode
        self._layer = layer 
        
        #Initialize fields if its a new feature being created
        if self._mode == SAVE:
            fields = self._layer.pendingFields()
            self._model.initAttributes(fields.count())
            
        #Connect signals
        self._layer.featureAdded.connect(self.on_feature_added)
        
    def layer(self):
        '''
        Returns the layer being used by the mapper.
        '''
        return self._layer

    def add_mapping(self, attribute_name, control, isMandatory=False, pseudoname="", value_handler=None, preload_func=None):
        '''
        Now create mapping using QgsFeatureAttributeMapper.
        We use the positional index of the field instead of the name since the feature cannot locate it 
        when you search the field by name. 
        '''
        attr_index = self._layer.pendingFields().indexFromName(attribute_name)
        if attr_index != -1:
            attr_mapper = _QgsFeatureAttributeMapper(attrIndex, control, self._model, pseudoname, isMandatory, value_handler)
            self.add_mapper(attr_mapper, preload_func)

    def _persist_model(self):
        '''
        Persist feature to the vector layer.
        '''
        if not isinstance(self._layer, QgsVectorLayer):
            return
        
        ret = self._layer.add_feature(self._model)
        
        if ret:
            if isinstance(self, QDialog):
                self.post_save_update(self._model)
                self.accept()
                
        else:
            QMessageBox.critical(self, QApplication.translate("MappedDialog","Error"), \
                                    QApplication.translate("MappedDialog","The feature could not be added."))
            
    def on_feature_added(self, fid):
        '''
        Slot raised when a new feature has been added to the layer
        '''
        pass
        
