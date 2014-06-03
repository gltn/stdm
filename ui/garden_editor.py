"""
/***************************************************************************
Name                 : Garden Editor
Description          : Dialog for entering new or updating existing garden 
                       information.
Date                 : 9/April/2014 
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

from stdm.data import Garden,GardenSurveyPoint, MapperMixin,QgsFeatureMapperMixin, \
SAVE,UPDATE,FoodCrop,foodCropCategoryFormatter,geometryFormatter
from .ui_garden_editor import Ui_frmGardenEditor
from .foreign_key_editors import FoodCropEditor,GardenSurveyPointEditor
from .admin_unit_manager import VIEW, MANAGE,SELECT
from .admin_unit_selector import AdminUnitSelector
from .entity_browser import EnumeratorEntityBrowser,RespondentEntityBrowser, \
WitnessEntityBrowser
from .notification import NotificationBar
from .helpers import SpinBoxValueHandler

class PendingLayerEntities(object):
    '''
    In the spatial editor dialog, there are 2 data providers. The primary one is the vector data provider
    (postgres) in the case of STDM which is used to save the QgsFeature class instance. The second one is 
    the sqlalchemy object of related entities. We need to save the primary key of the spatial unit in the
    related entities. This class contains all the necessary information required to sync the two data sources
    when new features, added to the vector layer, have been committed to the spatial data repository.
    '''
    def __init__(self,modelAttributeName = "",featureAttributeName = "",layerId = ""):
        self._modelAttrName = modelAttributeName
        self._featAttrName = featureAttributeName
        self._layerId = layerId
        self._uniqValEntityMapping = {}
        
    def modelAttributeName(self):
        '''
        Return the attribute name of the related SQLAlchemy objects; this is the FK field.
        '''
        return self._modelAttrName
    
    def setModelAttributeName(self,attrName):
        self._modelAttrName = attrName
        
    def featureAttributeName(self):
        """
        Returns the name of the attribute that contains the unique value against which to search
        for the corresponding primary key.
        """
        return self._featAttrName
    
    def setFeatureAttributeName(self,attrName):
        self._featAttrName = attrName
        
    def layerId(self):
        '''
        Returns the unique ID of the layer being referenced by the current class instance.
        '''
        return self._layerId
    
    def setLayerId(self,layerId):
        self._layerId = layerId
        
    def addPendingEntity(self,uniqueValue,entity):
        '''
        Add a entity whose FK needs to be updated upon committing added features by using
        the unique value of the primary model's feature attribute name column.
        '''
        if entity == None:
            return
        
        if uniqueValue in self._uniqValEntityMapping:
            self._uniqValEntityMapping[uniqueValue].append(entity)
        else:
            uniqueValueList = [entity]
            self._uniqValEntityMapping[uniqueValue] = uniqueValueList
            
    def merge(self,pendingLayerEntities):
        '''
        Updates the FK entities with those from another class instance.
        '''
        self._uniqValEntityMapping.update(pendingLayerEntities.uniqueValueMappings())
    
    def uniqueValueMappings(self):    
        return self._uniqValEntityMapping
    
    def setPrimaryKey(self,uniqueValue,primaryKey):
        '''
        Set the entities which are represented by the given unique value with the 
        specified primary key value.
        '''
        if uniqueValue in self._uniqValEntityMapping:
            entityList = self._uniqValEntityMapping[uniqueValue]
            
            for e in entityList:
                setattr(e,self._modelAttrName,primaryKey)
                e.update()

class BaseGardenEditor(QDialog,Ui_frmGardenEditor):
    '''
    Base dialog for entering new or updating existing garden information.
    '''
    def __init__(self,parent = None):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        self.btnSelectAdminUnit.clicked.connect(self.onShowAdminUnitDialog)
        
        #Set current date as maximum date
        currDate = QDate.currentDate()
        self.dtPlantingYear.setMaximumDate(currDate)
        
        #Set administrative unit selector
        self._adminUnitSelector = AdminUnitSelector(self)
        self._adminUnitSelector.setManageMode(False)
        
        self._notifBar = NotificationBar(self.vlNotification)
        
        #Configure foreign key mappers
        self._foodCropFKMapper = self.tbRelations.widget(0)
        self._foodCropFKMapper.setDatabaseModel(FoodCrop)
        self._foodCropFKMapper.setEntitySelector(FoodCropEditor)
        self._foodCropFKMapper.addCellFormatter("CategoryID",foodCropCategoryFormatter)
        self._foodCropFKMapper.setSupportsList(True)
        self._foodCropFKMapper.setDeleteonRemove(True)
        self._foodCropFKMapper.setNotificationBar(self._notifBar)
        self._foodCropFKMapper.initialize()
        
        self._surveyPointFKMapper = self.tbRelations.widget(1)
        self._surveyPointFKMapper.setDatabaseModel(GardenSurveyPoint)
        self._surveyPointFKMapper.setEntitySelector(GardenSurveyPointEditor)
        self._surveyPointFKMapper.addCellFormatter("Geom",geometryFormatter)
        self._surveyPointFKMapper.setSupportsList(True)
        self._surveyPointFKMapper.setDeleteonRemove(True)
        self._surveyPointFKMapper.setNotificationBar(self._notifBar)
        self._surveyPointFKMapper.initialize()
        
    def onShowAdminUnitDialog(self):
        '''
        Slot raised to show the administrative unit dialog selector.
        '''
        if self._adminUnitSelector.exec_() == QDialog.Accepted:
            selectedAdminUnit = self._adminUnitSelector.selectedAdminUnit
            self._generateGardenID(selectedAdminUnit)
            
    def _generateGardenID(self,adminUnit):
        '''
        Generate Garden identifier based on the hierarchy of the administrative units
        and next value of the primary key of the garden table.
        '''
        hCode = adminUnit.hierarchyCode()
        
        #Get next value of the primary key of the Garden table.
        nextId = Garden.nextVal()
        
        #Build the code of the digitized spatial unit
        gardenId = "{0}/{1}".format(hCode,str(nextId))
        self.txtGardenIdentifier.setText(gardenId)
        
class GardenEditor(BaseGardenEditor,MapperMixin):
    '''
    Dialog for entering new or updating existing garden information in a generic table view.
    '''
    def __init__(self,parent,model = Garden):
        BaseGardenEditor.__init__(self,parent)
        MapperMixin.__init__(self,model)
        
        #specify mappings
        self.addMapping("Identifier", self.txtGardenIdentifier,True)
        self.addMapping("Acreage", self.sbAcreage)
        self.addMapping("AverageHarvest", self.sbAverageHarvest)
        self.addMapping("MonthlyEarning", self.sbMonthlyEarning)
        self.addMapping("MonthlyLabor", self.sbMonthlyLabor)
        self.addMapping("PlantingYear", self.dtPlantingYear)
        
class SpatialGardenEditor(BaseGardenEditor,QgsFeatureMapperMixin):
    '''
    Dialog for entering new or updating existing garden information in spatial editing mode.
    '''
    def __init__(self,parent,layer,feature,mode = SAVE):
        BaseGardenEditor.__init__(self,parent)
        QgsFeatureMapperMixin.__init__(self, layer, feature, mode)
        
        self._pendingLayerEntities = PendingLayerEntities("GardenID","identifier",layer.id())
        
        #specify mappings
        self.addMapping("identifier", self.txtGardenIdentifier,True,pseudoname="Garden Identifier")
        self.addMapping("acreage", self.sbAcreage)
        self.addMapping("average_harvest", self.sbAverageHarvest)
        self.addMapping("monthly_earning", self.sbMonthlyEarning)
        self.addMapping("monthly_labor", self.sbMonthlyLabor)
        self.addMapping("planting_year", self.dtPlantingYear)

    def postSaveUpdate(self, feature):
        '''
        Configure the pending layer entities class.
        '''
        gardenId = self.txtGardenIdentifier.text()
        
        foodCropEntities = self._foodCropFKMapper.entities()
        if foodCropEntities != None:
            self._addPendingEntity(gardenId, foodCropEntities)
        
        surveyPointEntities = self._surveyPointFKMapper.entities()
        if surveyPointEntities != None:
            self._addPendingEntity(gardenId, surveyPointEntities)
            
    def _addPendingEntity(self,gardenId,entity):
        if isinstance(entity,list):
            for ent in entity:
                self._pendingLayerEntities.addPendingEntity(gardenId, ent)
        else:
            self._addPendingEntity(gardenId, entity)

    def pendingLayerEntities(self):
        '''
        Returns an instance of the pendingLayerEntities class
        '''
        return self._pendingLayerEntities

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        