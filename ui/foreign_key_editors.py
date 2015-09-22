"""
/***************************************************************************
Name                 : Foreign Key Mapper Editors
Description          : These modules consists of those widgets that replace
                       are used in place of entity browsers in Foreign Key 
                       Mappers.
Date                 : 18/February/2014 
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

from stdm.data import MapperMixin,HouseholdIncome,HouseholdSaving, \
Priority,FoodCrop,GardenSurveyPoint
from .admin_unit_manager import VIEW,MANAGE,SELECT
from stdm.utils import loadComboSelections
from customcontrols import ComboBoxWithOther
from .ui_food_crop_editor import Ui_frmFoodCropEditor
from .ui_coordinates_editor import Ui_frmCoordinatesEditor

__all__ = ["HouseholdIncomeEditor","HouseholdSavingsEditor","PriorityServiceEditor","ImpactEditor", \
           "FoodCropEditor","SpatialCoordinatesEditor","GardenSurveyPointEditor"]


class HouseholdIncomeEditor(QDialog,MapperMixin):
    '''
    Dialog for specifying household income sources.
    ''' 
    
    #See EntityBrowser base class for details on implementation.
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent=None, state = None, dataModel=HouseholdIncome):
        QDialog.__init__(self,parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MapperMixin.__init__(self, dataModel)
        
        self.resize(290,175)
        self.setWindowTitle(QApplication.translate("HouseholdIncomeEditor","Household Income Editor"))
        self.gridLayout = QGridLayout(self)
        
        self.vlNotification = QVBoxLayout()
        self.vlNotification.setMargin(0)
        self.gridLayout.addLayout(self.vlNotification,0,0,1,2)
        
        #Add vertical layout for the notification bar
        self.setNotificationLayout(self.vlNotification)
        
        self.lblActivity = QLabel(self)
        self.lblActivity.setText(QApplication.translate("HouseholdIncomeEditor","Activity"))
        self.gridLayout.addWidget(self.lblActivity,1,0,1,1)
        self.txtActivityName = QLineEdit(self)
        self.txtActivityName.setMinimumSize(QSize(0, 30))
        self.txtActivityName.setMaxLength(30)
        self.gridLayout.addWidget(self.txtActivityName,1,1,1,1)
        
        self.lblAmount = QLabel(self)
        self.lblAmount.setText(QApplication.translate("HouseholdIncomeEditor","Estimate Income"))
        self.gridLayout.addWidget(self.lblAmount,2,0,1,1)
        self.sbEstimateIncome = QSpinBox(self)
        self.sbEstimateIncome.setMinimumSize(QSize(0, 30))
        self.sbEstimateIncome.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.sbEstimateIncome.setMaximum(1000000000)
        self.gridLayout.addWidget(self.sbEstimateIncome,2,1,1,1)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.buttonBox,3,0,1,2)
        
        #Configure mappings
        self.addMapping("Activity",self.txtActivityName,True)
        self.addMapping("EstimateIncome",self.sbEstimateIncome,True)
        
        #Connect signals
        self.connect(self.buttonBox, SIGNAL("accepted()"),self.submit)
        self.connect(self.buttonBox, SIGNAL("rejected()"),self.cancel)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not implemented.
        '''
        pass

    def postSaveUpdate(self, dbmodel):
        '''
        Base class override for sending the record select signal to receivers
        and clear input controls.
        '''
        self.recordSelected.emit(dbmodel.id)
        self.txtActivityName.clear()
        self.sbEstimateIncome.clear()
        
class HouseholdSavingsEditor(QDialog,MapperMixin):
    '''
    Dialog for specifying household saving option.
    ''' 
    
    #See EntityBrowser base class for details on implementation.
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent=None, state = None, dataModel=HouseholdSaving):
        QDialog.__init__(self,parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MapperMixin.__init__(self, dataModel)
        
        self.resize(290,175)
        self.setWindowTitle(QApplication.translate("HouseholdSavingEditor","Household Saving Editor"))
        self.gridLayout = QGridLayout(self)
        
        self.vlNotification = QVBoxLayout()
        self.vlNotification.setMargin(0)
        self.gridLayout.addLayout(self.vlNotification,0,0,1,2)
        
        #Add vertical layout for the notification bar
        self.setNotificationLayout(self.vlNotification)
        
        self.lblSavingsOption = QLabel(self)
        self.lblSavingsOption.setText(QApplication.translate("HouseholdIncomeEditor","Savings Option"))
        self.gridLayout.addWidget(self.lblSavingsOption,1,0,1,1)
        self.cboSavingsOption = ComboBoxWithOther(self)
        self.cboSavingsOption.setMinimumSize(QSize(0, 30))
        self.gridLayout.addWidget(self.cboSavingsOption,1,1,1,1)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.buttonBox,3,0,1,2)
        
        #Load saving options
        loadComboSelections(self.cboSavingsOption.combo_box(),CheckSavingsOption)
        
        #Configure mappings
        self.addMapping("OptionID",self.cboSavingsOption.combo_box(),True, \
                        pseudoname=QApplication.translate("HouseholdSavingEditor","Saving option type"))
        self.addMapping("OtherOption",self.cboSavingsOption.line_edit())
        
        #Connect signals
        self.connect(self.buttonBox, SIGNAL("accepted()"),self.submit)
        self.connect(self.buttonBox, SIGNAL("rejected()"),self.cancel)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not implemented.
        '''
        pass
    
    def preSaveUpdate(self):
        '''
        Base class override for validating if Other option has been specified and value entered.
        '''
        isValid,msg = self.cboSavingsOption.validate()
        if not isValid:
            self._notifBar.clear()
            self._notifBar.insertErrorNotification(msg)
            
        return isValid

    def postSaveUpdate(self, dbmodel):
        '''
        Base class override for sending the record select signal to receivers.
        '''
        self.recordSelected.emit(dbmodel.id)
        
class PriorityServiceEditor(QDialog,MapperMixin):
    '''
    Dialog for specifying a farmer's priority.
    ''' 
    
    #See EntityBrowser base class for details on implementation.
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent=None, state = None, dataModel=Priority):
        QDialog.__init__(self,parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MapperMixin.__init__(self, dataModel)
        
        self.resize(290,200)
        self.setWindowTitle(QApplication.translate("PriorityServiceEditor","Priority Service Editor"))
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setMargin(10)
        
        self.vlNotification = QVBoxLayout()
        self.vlNotification.setMargin(0)
        self.gridLayout.addLayout(self.vlNotification,0,0,1,2)
        
        #Add vertical layout for the notification bar
        self.setNotificationLayout(self.vlNotification)
        
        self.lblPService = QLabel(self)
        self.lblPService.setText(QApplication.translate("PriorityServiceEditor","Service"))
        self.gridLayout.addWidget(self.lblPService,1,0,1,1)
        
        self.cboPService = ComboBoxWithOther(self)
        self.cboPService.line_edit().setMaxLength(30)
        self.gridLayout.addWidget(self.cboPService,1,1,1,1)
        
        self.lblRank = QLabel(self)
        self.lblRank.setText(QApplication.translate("PriorityServiceEditor","Rank"))
        self.gridLayout.addWidget(self.lblRank,2,0,1,1)
        
        self.cboRank = QComboBox(self)
        self.cboRank.setMinimumSize(QSize(0, 30))
        self.gridLayout.addWidget(self.cboRank,2,1,1,1)
        
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
        self.gridLayout.addWidget(self.buttonBox,3,0,1,2)
        
        #Load combobox options
        loadComboSelections(self.cboPService.combo_box(),CheckInputService)
        self.cboRank.addItem("")
        self.cboRank.addItem(QApplication.translate("PriorityServiceEditor","3 (Highest)"), 3)
        self.cboRank.addItem("2", 2)
        self.cboRank.addItem(QApplication.translate("PriorityServiceEditor","1 (Lowest)"), 1)
        
        #Configure mappings
        self.addMapping("itemID",self.cboPService.combo_box(),True, \
                        pseudoname=QApplication.translate("PriorityServiceEditor","Priority Service"))
        self.addMapping("OtherItem",self.cboPService.line_edit())
        self.addMapping("Rank",self.cboRank,True)
        
        #Connect signals
        self.connect(self.buttonBox, SIGNAL("accepted()"),self.submit)
        self.connect(self.buttonBox, SIGNAL("rejected()"),self.cancel)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not implemented.
        '''
        pass
    
    def preSaveUpdate(self):
        '''
        Base class override for validating if Other option has been specified and value entered.
        '''
        isValid,msg = self.cboPService.validate()
        if not isValid:
            self._notifBar.clear()
            self._notifBar.insertErrorNotification(msg)
            
        return isValid

    def postSaveUpdate(self, dbmodel):
        '''
        Base class override for sending the record select signal to receivers
        and clear input controls.
        '''
        self.recordSelected.emit(dbmodel.id)
        
# class ImpactEditor(QDialog,MapperMixin):
#     '''
#     Dialog for specifying VODP impact.
#     ''' 
#     
#     #See EntityBrowser base class for details on implementation.
#     recordSelected = pyqtSignal(int)
#     
#     def __init__(self,parent=None, state = None, dataModel=Impact):
#         QDialog.__init__(self,parent)
#         self.setAttribute(Qt.WA_DeleteOnClose)
#         MapperMixin.__init__(self, dataModel)
#         
#         self.resize(300,200)
#         self.setWindowTitle(QApplication.translate("ImpactEditor","Project Impact Editor"))
#         self.gridLayout = QGridLayout(self)
#         self.gridLayout.setMargin(10)
#         
#         self.vlNotification = QVBoxLayout()
#         self.vlNotification.setMargin(0)
#         self.gridLayout.addLayout(self.vlNotification,0,0,1,2)
#         
#         #Add vertical layout for the notification bar
#         self.setNotificationLayout(self.vlNotification)
#         
#         self.lblImpact = QLabel(self)
#         self.lblImpact.setText(QApplication.translate("ImpactEditor","Socio-Economic Impact"))
#         self.gridLayout.addWidget(self.lblImpact,1,0,1,1)
#         
#         self.cboImpact = ComboBoxWithOther(self)
#         self.cboImpact.lineEdit().setMaxLength(30)
#         self.gridLayout.addWidget(self.cboImpact,1,1,1,1)
#         
#         self.lblRank = QLabel(self)
#         self.lblRank.setText(QApplication.translate("ImpactEditor","Rank"))
#         self.gridLayout.addWidget(self.lblRank,2,0,1,1)
#         
#         self.cboRank = QComboBox(self)
#         self.cboRank.setMinimumSize(QSize(0, 30))
#         self.gridLayout.addWidget(self.cboRank,2,1,1,1)
#         
#         self.buttonBox = QDialogButtonBox(self)
#         self.buttonBox.setOrientation(Qt.Horizontal)
#         self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)
#         self.gridLayout.addWidget(self.buttonBox,3,0,1,2)
#         
#         #Load combobox options
#         loadComboSelections(self.cboImpact.comboBox(),CheckSocioEconomicImpact)
#         self.cboRank.addItem("")
#         self.cboRank.addItem(QApplication.translate("ImpactEditor","3 (Highest)"), 3)
#         self.cboRank.addItem("2", 2)
#         self.cboRank.addItem(QApplication.translate("ImpactEditor","1 (Lowest)"), 1)
#         
#         #Configure mappings
#         self.addMapping("itemID",self.cboImpact.comboBox(),True, \
#                         pseudoname=QApplication.translate("ImpactEditor","Priority Service"))
#         self.addMapping("OtherItem",self.cboImpact.lineEdit())
#         self.addMapping("Rank",self.cboRank,True)
#         
#         #Connect signals
#         self.connect(self.buttonBox, SIGNAL("accepted()"),self.submit)
#         self.connect(self.buttonBox, SIGNAL("rejected()"),self.cancel)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not implemented.
        '''
        pass
    
    def preSaveUpdate(self):
        '''
        Base class override for validating if Other option has been specified and value entered.
        '''
        isValid,msg = self.cboImpact.validate()
        if not isValid:
            self._notifBar.clear()
            self._notifBar.insertErrorNotification(msg)
            
        return isValid

    def postSaveUpdate(self, dbmodel):
        '''
        Base class override for sending the record select signal to receivers
        and clear input controls.
        '''
        self.recordSelected.emit(dbmodel.id)
        
class FoodCropEditor(QDialog,Ui_frmFoodCropEditor,MapperMixin):
    '''
    Dialog for entering new or updating existing info on food crops for a given garden.
    '''
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent = None,state = None, dataModel = FoodCrop):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MapperMixin.__init__(self,dataModel)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
        #Load combobox items
        loadComboSelections(self.cboCropCategory,CheckFoodCropCategory)
        
        #Define mappings
        self.addMapping("Acreage", self.sbAcreage)
        self.addMapping("CropName", self.txtCropName,True)
        self.addMapping("CategoryID", self.cboCropCategory,True,pseudoname="Food crop category")
        
    def setCellFormatters(self,formattermapping):
        '''
        Not applicable.
        '''
        pass
    
    def postSaveUpdate(self, dbmodel):
        '''
        Emit signal to notify receiver that the food crop record has been saved for subsequent selection.
        '''
        self.recordSelected.emit(dbmodel.id)
        
class SpatialCoordinatesEditor(QDialog,Ui_frmCoordinatesEditor):
    '''
    Dialog for entering new or updating existing info on a single coordinates pair in the map canvas when digitizing 
    a spatial unit.
    '''
    def __init__(self,parent = None,x=0,y=0):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        #Set coordinate values
        self.coordWidget.set_x_y(x, y)
        
    def xCoord(self):
        return self.sbXCoord.value()
    
    def yCoord(self):
        return self.sbYCoord.value()
    
    def XY(self):
        return (self.xCoord(),self.yCoord())
    
    def qgsPoint(self):
        return self.coordWidget.geom_point()
    
class GardenSurveyPointEditor(QDialog,Ui_frmCoordinatesEditor,MapperMixin):
    '''
    Dialog for entering new or updating existing info regarding a survey point.
    '''
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent = None,state = None,dataModel = GardenSurveyPoint):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        MapperMixin.__init__(self,dataModel)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
        self.coordWidget.set_srid(GardenSurveyPoint)
        
        #Define mappings
        self.addMapping("Geom", self.coordWidget)
        
    def setCellFormatters(self,formattermapping):
        '''
        Not applicable.
        '''
        pass
    
    def postSaveUpdate(self, dbmodel):
        '''
        Emit signal to notify receiver that a survey point record has been saved for subsequent selection.
        '''
        self.recordSelected.emit(dbmodel.id)
        
       
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        