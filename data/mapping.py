"""
/***************************************************************************
Name                 : Database Model/Widget Mapping Classes
Description          : Classes that enable the mapping of database model 
                       attributes to the corresponding UI widgets for rapid
                       building of custom STDM forms.
Date                 : 28/January/2014 
copyright            : (C) 2014 by John Gitau
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
from PyQt4.QtCore import *
from PyQt4.QtGui import QApplication, QMessageBox, QDialog

from qgis.gui import *
from qgis.core import *

from stdm.ui.helpers import valueHandler, ControlDirtyTrackerCollection
from stdm.ui.notification import NotificationBar,ERROR,WARNING,INFO

__all__ = ["SAVE","UPDATE","MapperMixin","QgsFeatureMappperMixin"]

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
    def __init__(self, attributeName, qtControl, model,pseudoname="", isMandatory = False, \
                 customValueHandler = None,bindControlOnly = False):
        '''
        :param attributeName: Property name of the database model that is to be mapped.
        :param qtControl: Qt input widget that should be mapped to the model's attribute.
        :param model: STDM model to which the attribute name belongs to.
        :param isMandatory: Flag to indicate whether a value is required from the input control.
        :param customValueHandler: Instance of a custom value handler can be provided if it does not exist amongst 
        those in the registered list.
        :param bindControlOnly: The model will not be updated using the control's value. This is used to only 
        update the control value using the model value when the mapper is in 'Update' mode.
        '''
        self._attrName = attributeName
        self._control = qtControl
        self._model = model
        self._isMandatory = isMandatory
        self._bindControlOnly = bindControlOnly
        
        if customValueHandler == None:
            self._valueHandler = valueHandler(qtControl)()
        else:
            self._valueHandler = customValueHandler()
            
        if not self._valueHandler is None:
            self._valueHandler.setControl(qtControl)
            
        self._pseudoname = attributeName if pseudoname == "" else pseudoname
            
    def attributeName(self):
        '''
        Attribute name.
        '''
        return self._attrName
    
    def pseudoName(self):
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
    
    def valueHandler(self):
        '''
        Return value handler associated with this control.
        '''
        return self._valueHandler
    
    def controlValue(self):
        '''
        Returns the value in the control.
        '''
        return self._valueHandler.value()
    
    def isMandatory(self):
        '''
        Returns whether the field is mandatory.
        '''
        return self._isMandatory
    
    def setMandatory(self,mandatory):
        '''
        Set field should be mandatory
        '''
        self._isMandatory = mandatory
        
    def bindControl(self):
        '''
        Sets the value of the control using the model's attribute value.
        '''
        if hasattr(self._model,self._attrName):
            attrValue = getattr(self._model,self._attrName)
            self._valueHandler.setValue(attrValue)
            
    def bindModel(self):
        '''
        Set the model attribute value to the control's value.
        The handler is responsible for adapting Qt and Python types as expected
        and defined by the model.
        '''
        if hasattr(self._model,self._attrName):
            controlValue = self._valueHandler.value()
            setattr(self._model,self._attrName,controlValue)
    
class MapperMixin(object):
    '''
    Mixin class for use in a dialog or widget, and does the heavy lifting when it comes to managing attribute mapping.
    '''
    def __init__(self,model):
        '''
        :param model: Callable (new instances) or instance (existing instance for updating) of STDM model.
        '''
        if callable(model):
            self._model = model()
            self._mode = SAVE
        else:
            self._model = model
            self._mode = UPDATE
        
        self._attrMappers = []
        self._dirtyTracker = ControlDirtyTrackerCollection()
        self._notifBar = None
        
        #Initialize notification bar
        if hasattr(self,"vlNotification"):
            self._notifBar = NotificationBar(self.vlNotification)
        
        #Flag to indicate whether to close the widget or dialog once model has been submitted
        #self.closeOnSubmit = True
        
    def addMapping(self,attributeName,control,isMandatory = False,pseudoname = "",valueHandler = None,preloadfunc = None):
        '''
        Specify the mapping configuration.
        '''
        attrMapper = _AttributeMapper(attributeName,control,self._model,pseudoname,isMandatory,valueHandler)
        self.addMapper(attrMapper,preloadfunc)
        
    def addMapper(self,attributeMapper,preloadfunc = None):
        '''
        Add an attributeMapper object to the collection.
        Preloadfunc specifies a function that can be used to prepopulate the control's value only when
        the control is on SAVE mode.
        '''
        if self._mode == SAVE and preloadfunc != None:
            attributeMapper.valueHandler().setValue(preloadfunc)
        
        if self._mode == UPDATE:
            #Set control value based on the model attribute value
            attributeMapper.bindControl()
            
        #Add control to dirty tracker collection after control value has been set
        self._dirtyTracker.addControl(attributeMapper.control(), attributeMapper.valueHandler())
            
        self._attrMappers.append(attributeMapper)
        
    def saveMode(self):
        '''
        Return the mode that the mapper is currently configured in.
        '''
        return self._mode
    
    def setSaveMode(self,mode):
        '''
        Set the mapper's save mode.
        '''
        self._mode = mode
        
    def setModel(self,stdmModel):
        '''
        Set the model to be used by the mapper.
        '''
        self._model = stdmModel
        
    def model(self):
        '''
        Returns the model configured for the mapper.
        '''
        return self._model
        
    def setNotificationLayout(self,layout):
        '''
        Set the vertical layout instance that will be used to display notification messages.
        '''
        self._notifBar = NotificationBar(layout)
        
    def insertNotification(self,message,mtype):
        '''
        There has to be a vertical layout, named 'vlNotification', that
        enables for notifications to be inserted.
        '''
        if self._notifBar:
            self._notifBar.insertNotification(message, mtype)   
            
    def clearNotifications(self):         
        '''
        Clears all messages in the notification bar.
        '''
        if self._notifBar:
            self._notifBar.clear()
            
    def checkDirty(self):
        '''
        Asserts whether the dialog contains dirty controls.
        '''
        isDirty = False
        msgResponse = None
        
        if self._dirtyTracker.isDirty():
            isDirty = True
            msg = QApplication.translate("MappedDialog","Would you like to save changes before closing?")
            msgResponse = QMessageBox.information(self, QApplication.translate("MappedDialog","Save Changes"), msg, 
                                             QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            
        return isDirty,msgResponse
    
    def closeEvent(self,event):
        '''
        Raised when a request to close the window is received.
        Check the dirty state of input controls and prompt user to save if dirty.
        ''' 
        isDirty,userResponse = self.checkDirty()
        
        if isDirty:
            if userResponse == QMessageBox.Yes:
                #We need to ignore the event so that validation and saving operations can be executed
                event.ignore()
                self.submit()
            elif userResponse == QMessageBox.No:
                event.accept()
            elif userResponse == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()
    
    def cancel(self):
        '''
        Slot for closing the dialog.
        Checks the dirty state first before closing.
        '''
        isDirty,userResponse = self.checkDirty()
        
        if isDirty:
            if userResponse == QMessageBox.Yes:
                self.submit()
            elif userResponse == QMessageBox.No:
                self.reject()
            elif userResponse == QMessageBox.Cancel:
                pass
        else:
            self.reject()
    
    def preSaveUpdate(self):
        '''
        Mixin classes can override this method to specify any operations that need to be executed
        prior to saving or updating the model's values.
        It should return True prior to saving.
        '''
        return True
    
    def postSaveUpdate(self,dbmodel):
        '''
        Executed once a record has been saved or updated. 
        '''
        pass
    
    def submit(self):
        '''
        Slot for saving or updating the model. This will close the dialog on successful submission.
        '''
        if not self.preSaveUpdate():
            return
        
        self.clearNotifications()
        isValid= True
        
        #Validate mandatory fields have been entered by the user.
        for attrMapper in self._attrMappers:
            if attrMapper.isMandatory() and attrMapper.valueHandler().supportsMandatory():
                if attrMapper.valueHandler().value() == attrMapper.valueHandler().default():
                    #Notify user
                    msg = "{0} is a required field.".format(attrMapper.pseudoName())
                    self._notifBar.insertWarningNotification(msg)
                    isValid = False
                else:
                    attrMapper.bindModel()
                    
            else:
                attrMapper.bindModel()
        
        if not isValid:
            return
        
        self._persistModel()
            
    def _persistModel(self):
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
            self.postSaveUpdate(self._model)
            self.accept()
        
                
class _QgsFeatureAttributeMapper(_AttributeMapper):
    '''
    Manages a single instance of the mapping between a QgsFeature attribute and the corresponding UI widget.
    For use in the editor widget when digitizing new features.
    '''
    def bindControl(self):
        '''
        Base class override that sets the value of the control based on the value of the QgsField
        with the given attribute index instead of the name.
        '''
        try:
            attrVal = self._model.attribute(self._attrName)
            self._valueHandler.setValue(attrVal)
        except KeyError:
            #If the field is not found then log the message into the console.
            QgsMessageLog.logMessage(QApplication.translate("QgsFeatureAttributeMapper", \
                                                            "Attribute name '{0}' not found.".format(self._attrName)), \
                                     QgsMessageLog.CRITICAL)

    def bindModel(self):
        '''
        Base class override that sets the value of the feature attribute.
        '''
        try:
            ctlValue = self._valueHandler.value()
            self._model.setAttribute(self._attrName,ctlValue)
        except KeyError:
            #If the field is not found then log the message into the console.
            QgsMessageLog.logMessage(QApplication.translate("QgsFeatureAttributeMapper", \
                                                            "Attribute index '{0}' not found.".format(str(self._attrName))), \
                                     level = QgsMessageLog.CRITICAL)
            
class QgsFeatureMapperMixin(MapperMixin):
    '''
    Mixin class for mapping QgsFeature attributes. For use in a spatial editor widget.
    '''
    def __init__(self,layer,feature,mode = SAVE):
        #In this case, the feature will have to be instantiated rather than checking whether it is a callable.
        MapperMixin.__init__(self,feature)
        self._mode = mode
        self._layer = layer 
        
        #Initialize fields if its a new feature being created
        if self._mode == SAVE:
            fields = self._layer.pendingFields()
            self._model.initAttributes(fields.count())
            
        #Connect signals
        self._layer.featureAdded.connect(self.onFeatureAdded)
        
    def layer(self):
        '''
        Returns the layer being used by the mapper.
        '''
        return self._layer

    def addMapping(self, attributeName, control, isMandatory=False, pseudoname="", valueHandler=None, preloadfunc=None):
        '''
        Now create mapping using QgsFeatureAttributeMapper.
        We use the positional index of the field instead of the name since the feature cannot locate it 
        when you search the field by name. 
        '''
        attrIndex = self._layer.pendingFields().indexFromName(attributeName)
        if attrIndex != -1:
            attrMapper = _QgsFeatureAttributeMapper(attrIndex,control,self._model,pseudoname,isMandatory,valueHandler)
            self.addMapper(attrMapper,preloadfunc)

    def _persistModel(self):
        '''
        Persist feature to the vector layer.
        '''
        if not isinstance(self._layer,QgsVectorLayer):
            return
        
        ret = self._layer.addFeature(self._model)
        
        if ret:
            if isinstance(self, QDialog):
                self.postSaveUpdate(self._model)
                self.accept()
                
        else:
            QMessageBox.critical(self, QApplication.translate("MappedDialog","Error"), \
                                    QApplication.translate("MappedDialog","The feature could not be added."))
            
    def onFeatureAdded(self,fid):
        '''
        Slot raised when a new feature has been added to the layer
        '''
        pass



        
    
                
    
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        