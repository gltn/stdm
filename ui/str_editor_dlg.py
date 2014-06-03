"""
/***************************************************************************
Name                 : Social Tenure Relationship Editor Dialog
Description          : Dialog for editing existing social tenure relationship
                       definitions.
Date                 : 23/December/2013 
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
from decimal import Decimal

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .ui_str_editor import Ui_frmSTREditor
from stdm.data import CheckSocialTenureRelationship
from .notification import NotificationBar,ERROR,INFO, WARNING
'''
from .helpers import ControlDirtyTrackerCollection,CheckBoxValueHandler, \
ComboBoxValueHandler
'''
from stdm.utils import loadComboSelections,setComboCurrentIndexWithItemData, \
setModelAttrFromCombo

class STREditorDialog(QDialog, Ui_frmSTREditor):
    '''
    This widget provides an interface for editing an existing social tenure relationship
    definition.
    '''
    def __init__(self,parent,socialtenure):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        self.socialtenure = socialtenure  
        
        #GUI initialization
        self.initGui()   
        
        #Load STR info
        loadComboSelections(self.cboSTRType, CheckSocialTenureRelationship)
        setComboCurrentIndexWithItemData(self.cboSTRType,socialtenure.SocialTenureType)
        
        if socialtenure.AgreementAvailable:
            self.chkSTRAgreement.setChecked(True)        

        #Setup notification 
        self.notifBar = NotificationBar(self.vlNotification)   
        
        #Setup dirty state control monitor
        self._strDirtMonitor = ControlDirtyTrackerCollection()
        #Register controls for monitoring dirty state
        self._strDirtMonitor.addControl(self.cboSTRType)
        self._strDirtMonitor.addControl(self.chkSTRAgreement)   
        
        '''
        Flag for saving or updating the respondent on hitting enter. 
        This is useful for situations where you wish to defer saving
        or updating to be handled by another control.
        '''   
        self.saveUpdateOnEnter = True
         
    def initGui(self):
        '''
        Initialize GUI
        '''
        #Define slot for 'Save'  and 'Cancel' buttons
        btnSave = self.buttonBox.button(QDialogButtonBox.Save)                
        QObject.connect(btnSave, SIGNAL("clicked()"), self.acceptDlg)  
        btnCancel = self.buttonBox.button(QDialogButtonBox.Cancel)                
        QObject.connect(btnCancel, SIGNAL("clicked()"), self.rejectDlg)  
                        
    def validateInput(self):
        '''
        Assert whether required fields have been entered.
        '''   
        isValid = True 
        
        if str(self.cboSTRType.currentText()) == "":
            self.notifBar.clear()
            self.notifBar.insertErrorNotification(str(QApplication.translate("STREditorDialog", 
                                             "Please select the social tenure relationship type")))
            self.cboSTRType.setFocus()
            isValid = False
        
        return isValid
        
    def keyPressEvent(self,event):
        '''
        Capture the Enter key
        '''
        key = event.key()
        if key == Qt.Key_Return:            
            self._saveUpdate()
            
    def closeEvent(self,event):
        '''
        Raised when a request to close the window is received.
        Check the dirty state of input controls and prompt user to save 
        if dirty.
        ''' 
        isDirty,userResponse = self.checkDirty()
        
        if isDirty:
            if userResponse == QMessageBox.Yes:
                #We need to ignore the event so that validation and saving operations can be executed
                event.ignore()
                self._saveUpdate()
            elif userResponse == QMessageBox.No:
                event.accept()
            elif userResponse == QMessageBox.Cancel:
                event.ignore()
        else:
            event.accept()
            
    def checkDirty(self):
        '''
        Asserts whether the dialog contains dirty controls.
        '''
        isDirty = False
        msgResponse = None
        
        if self._strDirtMonitor.isDirty():
            isDirty = True
            msg = QApplication.translate("STREditorDialog","Would you like to save changes before closing?")
            prompt = QMessageBox.information(self, QApplication.translate("STREditorDialog","Save Changes"), msg, 
                                             QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            msgResponse = prompt
            
        return isDirty,msgResponse
        
    def _saveUpdate(self):
        '''
        Saves or updates respondent information entered by the user
        '''
        self.notifBar.clear()
        isValid = self.validateInput()
        
        if isValid:
            setModelAttrFromCombo(self.socialtenure,"SocialTenureType", self.cboSTRType)    
            self.socialtenure.AgreementAvailable = self.chkSTRAgreement.isChecked()  
                    
            if self.saveUpdateOnEnter:  
                self.socialtenure.update()
                
            self.accept()   
        
    def acceptDlg(self):
        '''
        On user clicking the save button - Add a new or update existing conflict information
        '''
        self._saveUpdate()
        
    def rejectDlg(self):
        '''
        Slot raised when user clicks the cancel button. Assert whether there are unsaved changes in the
        dialog and prompt the user for appropriate action.
        '''
        isDirty,userResponse = self.checkDirty()
        
        if isDirty:
            if userResponse == QMessageBox.Yes:
                self._saveUpdate()
            elif userResponse == QMessageBox.No:
                self.reject()
            elif userResponse == QMessageBox.Cancel:
                pass
        else:
            self.reject()
            
            
        
        
        
        
        
        
        
        
        
        
        