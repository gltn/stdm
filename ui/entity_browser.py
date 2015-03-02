"""
/***************************************************************************
Name                 : Entity Browser Dialog
Description          : Dialog for browsing entity data based on the specified
                       database model.
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
from datetime import date

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.data import Enumerator,Witness,Survey
from stdm.navigation import TableContentGroup
from .admin_unit_manager import VIEW,MANAGE,SELECT
from .ui_entity_browser import Ui_EntityBrowser
from .helpers import SupportsManageMixin
from .notification import NotificationBar, ERROR, WARNING,INFO
from .base_person import WitnessEditor
from stdm.data import BaseSTDMTableModel
from stdm.data import STDMDb, tableCols,dateFormatter,tableColType
from .stdmdialog import DeclareMapping
from stdm.ui.forms import (
        CustomFormDialog,
        LookupModeller
)
 

__all__ = ["EntityBrowser","EnumeratorEntityBrowser","EntityBrowserWithEditor", \
           "ContentGroupEntityBrowser","RespondentEntityBrowser","WitnessEntityBrowser", \
           "FarmerEntityBrowser","SurveyEntityBrowser"]

class EntityBrowser(QDialog,Ui_EntityBrowser,SupportsManageMixin):
    '''
    Database model entity browser.
    ''' 
    
    '''
    Custom signal that is raised when the dialog is in SELECT state. It contains
    the record id of the selected row.
    '''
    recordSelected = pyqtSignal(int)
    
    def __init__(self,parent=None,dataModel = None,state = MANAGE):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        SupportsManageMixin.__init__(self,state)
        
        self._dbmodel = dataModel
        self._state = state
        self._tableModel = None
        self._dataInitialized = False
        self._notifBar = NotificationBar(self.vlNotification)
        self._cellFormatters = {}
        #self._dateFormatter = dateFormatter
        
        #Connect signals
        self.connect(self.buttonBox,SIGNAL("accepted ()"),self.onAccept)
        self.connect(self.tbEntity,SIGNAL("doubleClicked (const QModelIndex&)"),self.onDoubleClickView)
        
    def setDatabaseModel(self,databaseModel):
        '''
        Set the database model that represents the entity for browsing its corresponding records.
        '''
        self._dbmodel = databaseModel
        
    def dateFormatter(self):
        """
        Function for formatting date values
        """
        return self._dateFormatter
    
    def setDateFormatter(self,formatter):
        """
        Sets the function for formatting date values. Overrides the default function. 
        """
        self._dateFormatter = formatter
          
    def state(self):
        '''
        Returns the current state that the dialog has been configured in.
        '''
        return self._state
    
    def setState(self,state):
        '''
        Set the state of the dialog.
        '''
        self._state = state
        
    def title(self):
        '''
        Set the title of the entity browser dialog.
        Protected method to be overriden by subclasses.
        '''
        return ""
    
    def setCellFormatters(self,formattermapping):
        '''
        Dictionary of attribute mappings and corresponding functions for 
        formatting the attribute value to the display value.
        '''
        self._cellFormatters = formattermapping
        
    def addCellFormatter(self,attributeName,formatterFunc):
        '''
        Add a new cell formatter configuration to the collection
        '''
        self._cellFormatters[attributeName] = formatterFunc
    
    def showEvent(self,showEvent):
        '''
        Override event for loading the database records once the dialog is visible.
        This is for improved user experience i.e. to prevent the dialog from taking
        long to load.
        '''
        self.setWindowTitle(self.title())
        
        if self._dataInitialized:
            return
        
        if self._dbmodel != None:
            self._initializeData()
            
        self._dataInitialized = True
    
    def hideEvent(self,hideEvent):
        '''
        Override event which just sets a flag to indicate that the data records have already been
        initialized.
        '''
        pass
    
    def recomputeRecordCount(self):
        '''
        Get the number of records in the specified table and updates the window title.
        '''
        entity = self._dbmodel()
        
        #Get number of records
        numRecords = entity.queryObject().count()
        
        rowStr = "row" if numRecords == 1 else "rows"
        windowTitle = "{0} - {1} {2}".format(str(self.title()), \
                                                  str(QApplication.translate("EntityBrowser", str(numRecords))),rowStr)
        self.setWindowTitle(windowTitle)
        
        return numRecords
    
    def _initializeData(self):
        '''
        Set table model and load data into it.
        '''
        if self._dbmodel != None:
            headers = self._dbmodel.displayMapping().values()
            modelAttrs = self._dbmodel.displayMapping().keys()
            
            '''
            Load entity data. There might be a better way in future in order to ensure that
            there is a balance between user data discovery experience and performance.
            '''
            numRecords = self.recomputeRecordCount()
                        
            #Load progress dialog
            progressLabel = QApplication.translate("EntityBrowser", "Fetching Records...")
            progressDialog = QProgressDialog(progressLabel,"",0,numRecords,self)
            
            entity = self._dbmodel()
            entityRecords = entity.queryObject().filter().all()
            #entityRecordsList = [[getattr(er,attr)for attr in modelAttrs]for er in entityRecords]
            
            #Add records to nested list for enumeration in table model
            entityRecordsList = []
            for i,er in enumerate(entityRecords):
                entityRowInfo = []
                progressDialog.setValue(i)
                try:
                    for attr in modelAttrs:
                        attrVal = getattr(er,attr)

                        #Check if there are display formatters and apply if one exists for the given attribute
                        if attr in self._cellFormatters:
                            attrVal = self._cellFormatters[attr](attrVal)

                        if not attr in self._cellFormatters and isinstance(attrVal,date):
                            attrVal = dateFormatter(attrVal)

                        entityRowInfo.append(attrVal)
                except Exception as ex:
                    QMessageBox.information(None, QApplication.translate("EntityBrowser", "Loading dialog"), str(ex.message) )
                    return

                entityRecordsList.append(entityRowInfo)
                
            #Set maximum value of the progress dialog
            progressDialog.setValue(numRecords)
        
            self._tableModel = BaseSTDMTableModel(entityRecordsList,headers,self)
            
            #Add filter columns
            self.cboFilterColumn.addItems(headers)
            
            #Use sortfilter proxy model for the view
            self._proxyModel = QSortFilterProxyModel()
            self._proxyModel.setDynamicSortFilter(True)
            self._proxyModel.setSourceModel(self._tableModel)
            self._proxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
            self._proxyModel.setFilterKeyColumn(1) 
            
            self.tbEntity.setModel(self._proxyModel)
            self.tbEntity.setSortingEnabled(True)
            self.tbEntity.sortByColumn(1,Qt.AscendingOrder)
            
            #First (ID) column will always be hidden
            self.tbEntity.hideColumn(0)
            self.cboFilterColumn.removeItem(0)
            
            self.tbEntity.horizontalHeader().setResizeMode(QHeaderView.Stretch)
            
            #Connect signals
            self.connect(self.cboFilterColumn, SIGNAL("currentIndexChanged (int)"),self.onFilterColumnChanged)
            self.connect(self.txtFilterPattern, SIGNAL("textChanged(const QString&)"),self.onFilterRegExpChanged)
            
    def onFilterColumnChanged(self,index):
        '''
        Set the filter column for the proxy model.
        '''
        self._proxyModel.setFilterKeyColumn((index + 1))
        
    def onFilterRegExpChanged(self,text):
        '''
        Slot raised whenever the filter text changes.
        '''
        regExp =QRegExp(text,Qt.CaseInsensitive,QRegExp.FixedString)
        self._proxyModel.setFilterRegExp(regExp) 
        
    def onDoubleClickView(self,modelindex):
        '''
        Slot raised upon double clicking the table view.
        To be implemented by subclasses.
        '''
        pass
        
    def _selectedIds(self):
        '''
        Get the IDs of the selected row in the table view.
        '''
        self._notifBar.clear()
        
        selectedIds = []        
        selRowIndices = self.tbEntity.selectionModel().selectedRows(0)
        
        if len(selRowIndices) == 0:
            msg = QApplication.translate("EntityBrowser", 
                                         "Please select a record from the table.")             
            self._notifBar.insertWarningNotification(msg)
            return selectedIds
        
        for proxyRowIndex in selRowIndices:
            #Get the index of the source or else the row items will have unpredictable behavior
            rowIndex = self._proxyModel.mapToSource(proxyRowIndex)
            entityId = rowIndex.data(Qt.DisplayRole)
            selectedIds.append(entityId)
                
        return selectedIds
        
    def onAccept(self):
        '''
        Slot raised when user clicks to accept the dialog. The resulting action will be dependent 
        on the state that the browser is currently configured in.
        '''
        selIDs = self._selectedIds()
        if len(selIDs) == 0:
            return
        
        if self._mode == SELECT:
            #Get the first selected id
            selId = selIDs[0]
            self.recordSelected.emit(selId)
            self._notifBar.insertInfoNotification(QApplication.translate("EntityBrowser", "Record has been selected"))
            
    def addModelToView(self,modelObj):
        '''
        Convenience method for adding model info into the view.
        '''
        try:
            insertPosition = self._tableModel.rowCount()
            self._tableModel.insertRows(insertPosition,1)

            for i,attr in enumerate(self._dbmodel.displayMapping().keys()):
                propIndex = self._tableModel.index(insertPosition, i)
                if hasattr(modelObj, attr):
                    attrVal = getattr(modelObj, attr)
                #QMessageBox.information(self, 'model',"propertyindex;{0}\nattributeVal;{1}".format(str(propIndex), str(attrVal)))
                #Check if there re display formatters and apply if one exists for the given attribute
                if attr in self._cellFormatters:
                    attrVal = self._cellFormatters[attr](attrVal)
                if not attr in self._cellFormatters and isinstance(attrVal, date):
                    attrVal = dateFormatter(attrVal)

                self._tableModel.setData(propIndex, attrVal)
        except Exception as ex:
            QMessageBox.information(self, QApplication.translate("EntityBrowser", "Updating row"), str(ex.message))
            return
            
    def _modelFromID(self,recordid):
        '''
        Convenience method that returns the model object based on its ID.
        '''
        dbHandler = self._dbmodel()
        modelObj = dbHandler.queryObject().filter(self._dbmodel.id == recordid).first()
        
        return modelObj if modelObj != None else None
    
class EntityBrowserWithEditor(EntityBrowser):
    '''
    Entity browser with added functionality for carrying out CRUD operations directly.
    '''
    def __init__(self,dataModel,parent = None,state = VIEW|MANAGE):
        EntityBrowser.__init__(self, parent, dataModel, state)
        
        #Add action toolbar if the state contains Manage flag
        if (state & MANAGE) != 0:
            tbActions = QToolBar()
            tbActions.setIconSize(QSize(16,16))
            
            self._newEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/add.png"),
                                  QApplication.translate("EntityBrowserWithEditor","New"),self)
            self.connect(self._newEntityAction,SIGNAL("triggered()"),self.onNewEntity)
            
            self._editEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/edit.png"),
                                  QApplication.translate("EntityBrowserWithEditor","Edit"),self)
            self.connect(self._editEntityAction,SIGNAL("triggered()"),self.onEditEntity)
        
            self._removeEntityAction = QAction(QIcon(":/plugins/stdm/images/icons/remove.png"),
                                  QApplication.translate("EntityBrowserWithEditor","Remove"),self)
            self.connect(self._removeEntityAction,SIGNAL("triggered()"),self.onRemoveEntity)
            
            tbActions.addAction(self._newEntityAction)
            tbActions.addAction(self._editEntityAction)
            tbActions.addAction(self._removeEntityAction)
            
            self.vlActions.addWidget(tbActions)
            
            self._editorDialog = None  
            
    def onNewEntity(self):
        '''
        Load editor dialog for adding new information.
        '''
        if callable(self._editorDialog):
            addEntityDlg = self._editorDialog(self, self._dbmodel)
        else:
            addEntityDlg = self._editorDialog
            
        result = addEntityDlg.exec_()
        
        if result == QDialog.Accepted:
            modelObj = addEntityDlg.model()
            self.addModelToView(modelObj)
            self.recomputeRecordCount()
            
    def onEditEntity(self):
        '''
        Slot raised to load the editor for the selected row.
        '''
        self._notifBar.clear()
        
        selRowIndices = self.tbEntity.selectionModel().selectedRows(0)
        
        if len(selRowIndices) == 0:
            msg = QApplication.translate("EntityBrowserWithEditor", 
                                         "Please select a record in the table below for editing.")             
            self._notifBar.insertWarningNotification(msg)
            return
        
        rowIndex = self._proxyModel.mapToSource(selRowIndices[0])
        recordid = rowIndex.data()
        self._loadEditorDialog(recordid,rowIndex.row())
            
    def onRemoveEntity(self):
        '''
        Load editor dialog for editing an existing record.
        '''
        self._notifBar.clear()
        
        selRowIndices = self.tbEntity.selectionModel().selectedRows(0)
        
        if len(selRowIndices) == 0:
            msg = QApplication.translate("EntityBrowserWithEditor", 
                                         "Please select a record in the table below to be deleted.")             
            self._notifBar.insertWarningNotification(msg)
            return
        
        rowIndex = self._proxyModel.mapToSource(selRowIndices[0])
        recordid = rowIndex.data()
        self._deleteRecord(recordid,rowIndex.row())
            
    def _loadEditorDialog(self,recid,rownumber):
        '''
        Load editor dialog based on the selected model instance with the given ID.
        '''
        modelObj = self._modelFromID(recid)
        if callable(self._editorDialog):
            editEntityDlg = self._editorDialog(self, modelObj)
        else:
            editorDlg = self._editorDialog.__class__
            editEntityDlg = editorDlg(self, model=modelObj)
            
        result = editEntityDlg.exec_()
        
        if result == QDialog.Accepted:
            updatedModelObj = editEntityDlg.model()
            for i, attr in enumerate(self._dbmodel.displayMapping().keys()):
                propIndex = self._tableModel.index(rownumber, i)
                attrVal = getattr(updatedModelObj, attr)
                #Check if there re display formatters and apply if one exists for the given attribute
                if attr in self._cellFormatters:
                    attrVal = self._cellFormatters[attr](attrVal)
                self._tableModel.setData(propIndex, attrVal)
        
    def _deleteRecord(self, recid, rownumber):
        '''
        Delete the record with the given id and remove it from the table view.
        '''
        msg = QApplication.translate("EntityBrowserWithEditor",
                                             "Are you sure you want to delete the selected record?\nOnce deleted it cannot be recovered.")
        response = QMessageBox.warning(self,QApplication.translate("RespondentEntityBrowser","Delete Record"), msg,
                                    QMessageBox.Yes|QMessageBox.No, QMessageBox.No)
                
        if response == QMessageBox.Yes:
            
            self._tableModel.removeRows(rownumber,1) 
                                     
            #Remove record from the database
            dbHandler = self._dbmodel()
            entity = dbHandler.queryObject().filter(self._dbmodel.id == recid).first()
            
            if entity:
                entity.delete()

                #Clear previous notifications
                self._notifBar.clear()
                        
                #User notification
                delMsg = QApplication.translate("EntityBrowserWithEditor", 
                                         "Record has been successfully deleted!")
                self._notifBar.insertInfoNotification(delMsg)     

    def onDoubleClickView(self, modelindex):
        '''
        Override for loading editor dialog.
        '''
        rowIndex = self._proxyModel.mapToSource(modelindex)
        rowNumber = rowIndex.row()
        recordIdIndex  = self._tableModel.index(rowNumber, 0)
    
        recordId = recordIdIndex.data()
        self._loadEditorDialog(recordId,recordIdIndex.row())  
        
class ContentGroupEntityBrowser(EntityBrowserWithEditor):
    """
    Entity browser that loads editing tools based on the content permission
    settings defined by the administrator.
    This is an abstract class that needs to be implemented for subclasses
    representing specific entities.
    """
    def __init__(self,dataModel,tableContentGroup,parent = None,state = VIEW|MANAGE):
        EntityBrowserWithEditor.__init__(self, dataModel, parent, state)
        
        self.resize(700,500)
        
        if not isinstance(tableContentGroup,TableContentGroup):
            raise TypeError("Content group is not of type 'TableContentGroup'")
        
        self._tableContentGroup = tableContentGroup
        
        #Enable/disable tools based on permissions
        if (state & MANAGE) != 0:
            QMessageBox.information(None, "content", str(self._tableContentGroup._groupName) +str(self._tableContentGroup.canCreate()))
            if not self._tableContentGroup.canCreate():
                self._newEntityAction.setVisible(False)
                    
            if not self._tableContentGroup.canUpdate():
                self._editEntityAction.setVisible(False)
                    
            if not self._tableContentGroup.canDelete():
                self._removeEntityAction.setVisible(False)
                
        self._setFormatters() 
        
    def _setFormatters(self):
        """
        Specify formatting mappings.
        Subclasses to implement.
        """   
        pass
    
    def onDoubleClickView(self, modelindex):
        """
        Checks if user has permission to edit.
        """
        if self._tableContentGroup.canUpdate():
            super(ContentGroupEntityBrowser,self).onDoubleClickView(modelindex)
    
    def tableContentGroup(self):
        """
        Returns the content group instance used in the browser.
        """
        return self._tableContentGroup
    
class EnumeratorEntityBrowser(EntityBrowser):
    '''
    Browser for enumerator records.
    '''
    def __init__(self,parent = None,state = VIEW|MANAGE):
        EntityBrowser.__init__(self, parent, Enumerator, state)
        
    def title(self):
        return QApplication.translate("EnumeratorEntityBrowser", "Enumerator Records")
    
class RespondentEntityBrowser(EntityBrowserWithEditor):
    '''
    Browser for respondent records.
    '''
    def __init__(self,parent = None,state = VIEW|MANAGE):
        
        mapping=DeclareMapping.instance()
        tableCls=mapping.tableMapping('respondent')
        
        EntityBrowserWithEditor.__init__(self, tableCls, parent, state)
        #self._editorDialog = RespondentEditor  
        self._editorDialog=CustomFormDialog(self,tableCls)     
        
    def title(self):
        return QApplication.translate("RespondentEntityBrowser", "Respondent Records")
            
class WitnessEntityBrowser(EntityBrowserWithEditor):
    '''
    Browser for witness records.
    '''
    def __init__(self,parent = None,state = VIEW|MANAGE):
                
        EntityBrowserWithEditor.__init__(self, Witness, parent, state)
        self._editorDialog = WitnessEditor  
        
    def title(self):
        return QApplication.translate("WitnessEntityBrowser", "Witness Records")
    
class FarmerEntitySelector(EntityBrowser):
    '''
    Browser for simply selecting peson records.
    '''
    
    def __init__(self,parent = None, state = MANAGE):
        mapping=DeclareMapping.instance()
        model = mapping.tableMapping('party')
       
        EntityBrowser.__init__(self, parent, model, state)
        
    def title(self):
        return QApplication.translate("EnumeratorEntityBrowser", "Party Records")
    
class FarmerEntityBrowser(ContentGroupEntityBrowser):
    '''
    Browser for farmer records.
    '''
    def __init__(self,tableContentGroup,parent = None,state = MANAGE):
        ContentGroupEntityBrowser.__init__(self, Farmer, tableContentGroup, parent, state)
        self._editorDialog = FarmerEditor      
        
    def _setFormatters(self):
        """
        Specify formatting mappings.
        """   
        self.addCellFormatter("GenderID",genderFormatter)
        self.addCellFormatter("MaritalStatusID",maritalStatusFormatter)
        
    def title(self):
        return QApplication.translate("FarmerEntityBrowser", "Farmer Records Manager")



class STDMEntityBrowser(ContentGroupEntityBrowser):
    '''
    Browser for farmer records.
    '''
    def __init__(self,tableContentGroup,table=None,parent = None,state = MANAGE):

        mapping = DeclareMapping.instance()
        self._tableCls = mapping.tableMapping(table)

        self.tbEntityClass = table
        #columnsData=tableColType(table)
        #columns=columnsData.keys()
        
        ContentGroupEntityBrowser.__init__(self, self._tableCls, tableContentGroup, parent, state)
        
        #QMessageBox.information(self,"module",str(tableCls.__name__))
        #QMessageBox.information(self,"module",str( mapping.attDictionary))
        self._editorDialog = CustomFormDialog
        

    def _setFormatters(self):
        """
        Specify formatting mappings.
        """
        lk_function= self.create_lookup_setter('gender')
        self.addCellFormatter('Female',lk_function)
        #self.addCellFormatter("MaritalStatusID",maritalStatusFormatter)

    def title(self):
        return QApplication.translate("STDMEntityBrowser", "{0} Records Manager".format(self.tbEntityClass.title()))

    modeller = LookupModeller()
    def create_lookup_setter(self, attr_name):
        """
        :return lookup formatter
        """
        lkName ='gender'
        def lookupformatter(lookupvalue):
            lkformatter = modeller.lookupModel('check_gender')
            return lkformatter.setDisplay(lookupvalue)
        return lookupformatter
    
class SurveyEntityBrowser(ContentGroupEntityBrowser):
    '''
    Browser for survey records.
    '''
    def __init__(self,tableContentGroup,parent = None,state = MANAGE):
        from .survey_editor import SurveyEditor
        
        ContentGroupEntityBrowser.__init__(self, Survey, tableContentGroup, parent, state)
        self._editorDialog = SurveyEditor  
        
    def _setFormatters(self):
        """
        
        Specify formatting mappings.
        """   
        #self.addCellFormatter("EnumeratorID",enumeratorNamesFormatter)
        # self.addCellFormatter("RespondentID",respondentNamesFormatter)
        pass
        
    def title(self):
        return QApplication.translate("SurveyEntityBrowser", "Survey Records Manager")

    
    
        
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    