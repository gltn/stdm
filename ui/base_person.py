
"""
/***************************************************************************
Name                 : Base Person Dialog
Description          : Dialog for creating or editing a person's core 
                       attributes.
Date                 : 17/March/2014 
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
from PyQt4.QtGui import *

from stdm.data import MapperMixin,Enumerator,Witness,Priority,UPDATE
from .ui_base_person import Ui_frmBasePerson
from .ui_farmer import Ui_frmFarmer
from .ui_household import Ui_frmHousehold
from helpers import LineEditValueHandler
#from .foreign_key_editors import HouseholdIncomeEditor,HouseholdSavingsEditor,PriorityServiceEditor, \
#ImpactEditor
from stdm.utils import loadComboSelections

class BasePersonDialogMixin(MapperMixin):
    '''
    Mixin for dialogs that represent person entities.
    '''
    def __init__(self,datamodel=None):
        MapperMixin.__init__(self,datamodel)
        #Load combobox items
        #loadComboSelections(self.cboGender,CheckGender)
        #loadComboSelections(self.cboMaritalStatus,CheckMaritalStatus)
        
        #Set current date as maximum date
        self.dtDoB.setMaximumDate(QDate.currentDate())
        
        #Input mask for controlling cellphone number entries.
        self.txtCellphone.setInputMask("9999-999999")
        self.txtCellphone.setCursorPosition(0)
        
        #Specify mappings
        self.addMapping("FirstName", self.txtFirstName, True)
        self.addMapping("LastName", self.txtLastName, True)
        self.addMapping("Cellphone", self.txtCellphone)
        #self.addMapping("GenderID", self.cboGender,True,pseudoname="Gender")
        #self.addMapping("MaritalStatusID", self.cboMaritalStatus,True,pseudoname="Marital Status")
        self.addMapping("DateofBirth", self.dtDoB)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
class BasePerson(QDialog,Ui_frmBasePerson,BasePersonDialogMixin):
    '''
    Base dialog for managing attributes for a person's record.
    ''' 
    def __init__(self,parent=None,datamodel=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        BasePersonDialogMixin.__init__(self,datamodel)
        
        #Load combobox items
        #loadComboSelections(self.cboGender,CheckGender)
        #loadComboSelections(self.cboMaritalStatus,CheckMaritalStatus)
        
        #Set current date as maximum date
        self.dtDoB.setMaximumDate(QDate.currentDate())
        
        #Input mask for controlling cellphone number entries.
        self.txtCellphone.setInputMask("9999-999999")
        self.txtCellphone.setCursorPosition(0)
        
        #Specify mappings
        self.addMapping("FirstName", self.txtFirstName, True)
        self.addMapping("LastName", self.txtLastName, True)
        self.addMapping("Cellphone", self.txtCellphone)
        #self.addMapping("GenderID", self.cboGender,True,pseudoname="Gender")
        #self.addMapping("MaritalStatusID", self.cboMaritalStatus,True,pseudoname="Marital Status")
        self.addMapping("DateofBirth", self.dtDoB)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        

        
class WitnessEditor(BasePerson):
    '''
    Dialog for managing attributes for a witness's record.
    '''
    def __init__(self,parent=None,datamodel = Witness):
        BasePerson.__init__(self,parent,datamodel)
        
        self.setWindowTitle(QApplication.translate("WitnessEditor","Witness Editor"))
        
        #Add widget for capturing the witness relationship
        lblRelationship = QLabel(self)
        #lblRelationship.setText(QApplication.translate("WitnessEditor","Relationship"))
        
        self.cboRelationship = QComboBox(self)
        self.cboRelationship.setMinimumHeight(30)
        #loadComboSelections(self.cboRelationship,CheckWitnessRelationship)
        
        #Specify additional mapping for respondent role
        #self.addMapping("RelationshipID", self.cboRelationship,True,pseudoname="Witness Relationship")
        
        rowCount = self.gridLayout.rowCount()
        #self.gridLayout.removeWidget(self.buttonBox)
        #self.gridLayout.addWidget(lblRelationship, rowCount-1, 0, 1, 1)
        #self.gridLayout.addWidget(self.cboRelationship, rowCount-1, 1, 1, 1)
        #self.gridLayout.addWidget(self.buttonBox,rowCount,0,1,2)
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
