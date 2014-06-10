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

from stdm.data import MapperMixin,Enumerator,Respondent,CheckGender,CheckMaritalStatus, \
CheckRespondentType,CheckWitnessRelationship,Witness,Farmer,Household,HouseholdIncome, \
HouseholdSaving,savingOptionFormatter,Priority,inputServiceFormatter,Impact, \
socioEconImpactFormatter,UPDATE
from .ui_base_person import Ui_frmBasePerson
from .ui_farmer import Ui_frmFarmer
from .ui_household import Ui_frmHousehold
from helpers import LineEditValueHandler
from .foreign_key_editors import HouseholdIncomeEditor,HouseholdSavingsEditor,PriorityServiceEditor, \
ImpactEditor
from stdm.utils import loadComboSelections

class BasePersonDialogMixin(MapperMixin):
    '''
    Mixin for dialogs that represent person entities.
    '''
    def __init__(self,datamodel=None):
        MapperMixin.__init__(self,datamodel)
        #Load combobox items
        loadComboSelections(self.cboGender,CheckGender)
        loadComboSelections(self.cboMaritalStatus,CheckMaritalStatus)
        
        #Set current date as maximum date
        self.dtDoB.setMaximumDate(QDate.currentDate())
        
        #Input mask for controlling cellphone number entries.
        self.txtCellphone.setInputMask("9999-999999")
        self.txtCellphone.setCursorPosition(0)
        
        #Specify mappings
        self.addMapping("FirstName", self.txtFirstName, True)
        self.addMapping("LastName", self.txtLastName, True)
        self.addMapping("Cellphone", self.txtCellphone)
        self.addMapping("GenderID", self.cboGender,True,pseudoname="Gender")
        self.addMapping("MaritalStatusID", self.cboMaritalStatus,True,pseudoname="Marital Status")
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
        loadComboSelections(self.cboGender,CheckGender)
        loadComboSelections(self.cboMaritalStatus,CheckMaritalStatus)
        
        #Set current date as maximum date
        self.dtDoB.setMaximumDate(QDate.currentDate())
        
        #Input mask for controlling cellphone number entries.
        self.txtCellphone.setInputMask("9999-999999")
        self.txtCellphone.setCursorPosition(0)
        
        #Specify mappings
        self.addMapping("FirstName", self.txtFirstName, True)
        self.addMapping("LastName", self.txtLastName, True)
        self.addMapping("Cellphone", self.txtCellphone)
        self.addMapping("GenderID", self.cboGender,True,pseudoname="Gender")
        self.addMapping("MaritalStatusID", self.cboMaritalStatus,True,pseudoname="Marital Status")
        self.addMapping("DateofBirth", self.dtDoB)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
class RespondentEditor(BasePerson):
    '''
    Dialog for managing attributes for a respondent's record.
    '''
    def __init__(self,parent=None,datamodel = Respondent):
        BasePerson.__init__(self,parent,datamodel)
        
        self.setWindowTitle(QApplication.translate("RespondentEditor","Respondent Editor"))
        
        #Add widget for capturing the respondent role
        lblRole = QLabel(self)
        lblRole.setText(QApplication.translate("RespondentEditor","Role"))
        
        self.cboRole = QComboBox(self)
        self.cboRole.setMinimumHeight(30)
        loadComboSelections(self.cboRole,CheckRespondentType)
        
        #Specify additional mapping for respondent role
        self.addMapping("RoleID", self.cboRole,True,pseudoname="Respondent Role")
        
        rowCount = self.gridLayout.rowCount()
        self.gridLayout.removeWidget(self.buttonBox)
        self.gridLayout.addWidget(lblRole, rowCount-1, 0, 1, 1)
        self.gridLayout.addWidget(self.cboRole, rowCount-1, 1, 1, 1)
        self.gridLayout.addWidget(self.buttonBox,rowCount,0,1,2)
        
class WitnessEditor(BasePerson):
    '''
    Dialog for managing attributes for a witness's record.
    '''
    def __init__(self,parent=None,datamodel = Witness):
        BasePerson.__init__(self,parent,datamodel)
        
        self.setWindowTitle(QApplication.translate("WitnessEditor","Witness Editor"))
        
        #Add widget for capturing the witness relationship
        lblRelationship = QLabel(self)
        lblRelationship.setText(QApplication.translate("WitnessEditor","Relationship"))
        
        self.cboRelationship = QComboBox(self)
        self.cboRelationship.setMinimumHeight(30)
        loadComboSelections(self.cboRelationship,CheckWitnessRelationship)
        
        #Specify additional mapping for respondent role
        self.addMapping("RelationshipID", self.cboRelationship,True,pseudoname="Witness Relationship")
        
        rowCount = self.gridLayout.rowCount()
        self.gridLayout.removeWidget(self.buttonBox)
        self.gridLayout.addWidget(lblRelationship, rowCount-1, 0, 1, 1)
        self.gridLayout.addWidget(self.cboRelationship, rowCount-1, 1, 1, 1)
        self.gridLayout.addWidget(self.buttonBox,rowCount,0,1,2)
        
class HouseholdEditor(QDialog,Ui_frmHousehold,MapperMixin):
    '''
    Dialog for creating/editing household details.
    '''
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent=None,state = None,datamodel = Household):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        MapperMixin.__init__(self,datamodel)
        
        #Connect signals
        self.connect(self.buttonBox, SIGNAL("accepted()"),self.submit)
        self.connect(self.buttonBox, SIGNAL("rejected()"),self.cancel)
        
        #Configure household income FK mapper
        hhIncomeFKMapper = self.tabWidget.widget(0)
        hhIncomeFKMapper.setDatabaseModel(HouseholdIncome)
        hhIncomeFKMapper.setEntitySelector(HouseholdIncomeEditor)
        hhIncomeFKMapper.setSupportsList(True)
        hhIncomeFKMapper.setDeleteonRemove(True)
        hhIncomeFKMapper.setNotificationBar(self._notifBar)
        hhIncomeFKMapper.initialize()
        
        #Configure household savings option FK mapper
        hhSavingsFKMapper = self.tabWidget.widget(1)
        hhSavingsFKMapper.setDatabaseModel(HouseholdSaving)
        hhSavingsFKMapper.setEntitySelector(HouseholdSavingsEditor)
        hhSavingsFKMapper.setSupportsList(True)
        hhSavingsFKMapper.setDeleteonRemove(True)
        hhSavingsFKMapper.addCellFormatter("OptionID",savingOptionFormatter)
        hhSavingsFKMapper.setNotificationBar(self._notifBar)
        hhSavingsFKMapper.initialize()
        
        #Configure mappings
        self.addMapping("FemaleNumber", self.sbFemaleNumber)
        self.addMapping("MaleNumber", self.sbMaleNumber)
        self.addMapping("AggregateIncome", self.sbMonthlyIncome)
        self.addMapping("IncomeSources",hhIncomeFKMapper)
        self.addMapping("SavingOptions",hhSavingsFKMapper)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not applicable.
        '''
        pass

    def postSaveUpdate(self, dbmodel):
        '''
        Emit signal to notify receiver that the household record has been saved for subsequent selection.
        '''
        self.recordSelected.emit(dbmodel.id)

class FarmerEditor(QDialog,Ui_frmFarmer,BasePersonDialogMixin):
    '''
    Dialog for creating/editing a farmer's record.
    '''
    def __init__(self,parent=None,datamodel = Farmer):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        BasePersonDialogMixin.__init__(self,datamodel)
        
        #Configure validating line edit control to check existing farm numbers
        invalidMsg = "{} already exists."
        self.txtFarmerNumber.setModelAttr(datamodel,"FarmerNumber")
        self.txtFarmerNumber.setInvalidMessage(invalidMsg)
        self.txtFarmerNumber.setNotificationBar(self._notifBar)
        
        #Configure foreign key mappers
        householdFKMapper = self.tabWidget.widget(0)
        householdFKMapper.setDatabaseModel(Household)
        householdFKMapper.setEntitySelector(HouseholdEditor)
        householdFKMapper.setSupportsList(False)
        householdFKMapper.setNotificationBar(self._notifBar)
        householdFKMapper.initialize()
        
        priorityServiceFKMapper = self.tabWidget.widget(1)
        priorityServiceFKMapper.setDatabaseModel(Priority)
        priorityServiceFKMapper.setEntitySelector(PriorityServiceEditor)
        priorityServiceFKMapper.setSupportsList(True)
        priorityServiceFKMapper.setDeleteonRemove(True)
        priorityServiceFKMapper.addCellFormatter("itemID",inputServiceFormatter)
        priorityServiceFKMapper.setNotificationBar(self._notifBar)
        #Make sure services and rankings are unique
        priorityServiceFKMapper.addUniqueColumnIndex(1)
        priorityServiceFKMapper.addUniqueColumnIndex(3)
        priorityServiceFKMapper.initialize()
        
        impactFKMapper = self.tabWidget.widget(2)
        impactFKMapper.setDatabaseModel(Impact)
        impactFKMapper.setEntitySelector(ImpactEditor)
        impactFKMapper.setSupportsList(True)
        impactFKMapper.setDeleteonRemove(True)
        impactFKMapper.addCellFormatter("itemID",socioEconImpactFormatter)
        impactFKMapper.setNotificationBar(self._notifBar)
        #Make sure impacts and rankings are unique
        impactFKMapper.addUniqueColumnIndex(1)
        impactFKMapper.addUniqueColumnIndex(3)
        impactFKMapper.initialize()
        
        #Suppress signals for farmer number if the mode is UPDATE so that the control is not invalidated
        if self.saveMode() == UPDATE:
            self.txtFarmerNumber.blockSignals(True)
            self.txtFarmerNumber.setEnabled(False)
        
        #Additional farmer mappings
        self.addMapping("FarmerNumber", self.txtFarmerNumber,True,valueHandler=LineEditValueHandler)
        self.addMapping("Household", householdFKMapper, True)
        self.addMapping("Priorities", priorityServiceFKMapper,True)
        self.addMapping("Impacts",impactFKMapper,True)
        
        #Unblock signals in farmer number line edit control
        if self.txtFarmerNumber.signalsBlocked():
            self.txtFarmerNumber.blockSignals(False)

    def preSaveUpdate(self):
        """
        Validates if the farmer number already exists. If true, then the save operation
        will be halted.
        """
        return self.txtFarmerNumber.validate()

   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
