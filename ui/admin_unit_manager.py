"""
/***************************************************************************
Name                 : Administrative Unit Manager Widget
Description          : Displays and manages the hierarchy of administrative 
                       spatial units.
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
from collections import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.data.qtmodels import STRTreeViewModel
from stdm.data.database import (
    AdminSpatialUnitSet,
    STDMDb,
    Base
)
from stdm.navigation.socialtenure import (
    STRNodeFormatter,
    BaseSTRNode
)

from .ui_adminUnitManager import Ui_frmAdminUnitManager
from .notification import NotificationBar
from sqlalchemy import Table

class _AdminSpatialUnitConfiguration(object):
    #Format of each dictionary item: property/db column name - display name
    displayColumns = OrderedDict()

    def __init__(self):
        #Reset filter and display columns
        self.displayColumns = OrderedDict()

class AdminUnitFormatter(STRNodeFormatter):
    """
    Renderer for administrative spatial unit nodes.
    """
    def __init__(self, treeview=None, parentwidget=None):
        """
        Initialize header labels then call base class constructor.
        """
        aus_cfg = _AdminSpatialUnitConfiguration()
        aus_cfg.displayColumns["name"] = QApplication.translate(
            "AdminUnitFormatter","Name"
        )
        aus_cfg.displayColumns["code"] = QApplication.translate(
            "AdminUnitFormatter","Code"
        )
        aus_cfg.displayColumns["id"] = QApplication.translate(
            "AdminUnitFormatter","ID"
        )

        super(AdminUnitFormatter,self).__init__(aus_cfg, treeview,
                                                parentwidget)
        
    def root(self):
        '''
        Override of base class method.
        '''

        adminSUSet = AdminSpatialUnitSet()
        
        #Get top-level items
        adminUnits = adminSUSet.queryObject().filter(AdminSpatialUnitSet.Parent
                                                     == None).order_by(AdminSpatialUnitSet.Name)
       
        for aus in adminUnits:
            nodeData = self._extractAdminUnitSetInfo(aus)
            ausNode = BaseSTRNode(nodeData, self.rootNode)
            self._populateAUSChildren(ausNode, aus)
        
        return self.rootNode
    
    def _populateAUSChildren(self,parentNode,ausModel):
        '''
        Populate the parent node with its corresponding children.
        Using depth-first search approach.
        '''
        if len(ausModel.Children) > 0:
            for ausChild in ausModel.Children:
                cNodeData = self._extractAdminUnitSetInfo(ausChild)  
                ausNode = BaseSTRNode(cNodeData,parentNode)    
                self._populateAUSChildren(ausNode, ausChild)     
    
    def _extractAdminUnitSetInfo(self,aus):
        '''
        Returns the properties of the admin unit set object.
        '''
        return [aus.Name,aus.Code,aus.id]
        
#Widget States
VIEW = 2301
MANAGE = 2302
SELECT = 2303 #When widget is used to select one or more records from the table list

class AdminUnitManager(QWidget, Ui_frmAdminUnitManager):
    '''
    Administrative Unit Manager Widget
    '''
    #Signal raised when the state (view/manage) of the widet changes.
    stateChanged = pyqtSignal('bool')
    
    def __init__(self, parent=None, State=VIEW):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        
        self._defaultEditTriggers = self.tvAdminUnits.editTriggers()
    
        self._state = State
        self._onStateChange()
        
        self._notifBar = NotificationBar(self.vlNotification)
        
        #Configure validating line edit controls
        # invalidMsg = "{} already exists."
        # self.txtUnitCode.setModelAttr(AdminSpatialUnitSet,"Code")
        # self.txtUnitCode.setInvalidMessage(invalidMsg)
        # self.txtUnitCode.setNotificationBar(self._notifBar)
        
        '''
        Initialize formatter for the rendering the admin unit nodes and insert
        the root node into the tree view model.
        '''
        self._adminUnitNodeFormatter = AdminUnitFormatter(
            self.tvAdminUnits,
            self
        )
        self._rtNode = self._adminUnitNodeFormatter.rootNode
        
        self._adminUnitTreeModel = STRTreeViewModel(
            self._adminUnitNodeFormatter.root(),
            view=self.tvAdminUnits
        )
        self.tvAdminUnits.setModel(self._adminUnitTreeModel)
        self.tvAdminUnits.hideColumn(2)
        self.tvAdminUnits.setColumnWidth(0,220)
        
        #Connects slots
        self.connect(self.btnAdd, SIGNAL("clicked()"), self.onCreateAdminUnit)
        self.connect(self.btnClear, SIGNAL("clicked()"), self.onClearSelection)
        self.connect(self.btnRemove, SIGNAL("clicked()"), self.onDeleteSelection)
        self.connect(self._adminUnitTreeModel, SIGNAL("dataChanged(const QModelIndex&,const QModelIndex&)"), self.onModelDataChanged)
        
    def model(self):
        """
        :return: Returns the model associated with the administrative unit
        view.
        :rtype: STRTreeViewModel
        """
        return self._adminUnitTreeModel

    def selection_model(self):
        """
        :return: Returns the selection model associated with the
        administrative unit tree view.
        :rtype: QItemSelectionModel
        """
        return self.tvAdminUnits.selectionModel()

    def state(self):
        '''
        Returns the current state that the widget has been configured in.
        '''
        return self._state
    
    def setState(self,state):
        '''
        Set the state of the widget.
        '''
        self._state = state
        self._onStateChange()
        
    def notificationBar(self):
        '''
        Returns the application notification widget.
        '''
        return self._notifBar
    
    def _onStateChange(self):
        '''
        Configure controls upon changing the state of the widget.
        '''           
        manageControls = False if self._state == VIEW else True
            
        self.btnRemove.setVisible(manageControls)
        self.btnClear.setVisible(manageControls)
        self.gbManage.setVisible(manageControls)
        
        if manageControls:
            self.tvAdminUnits.setEditTriggers(self._defaultEditTriggers)
            
        else:
            self.tvAdminUnits.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.stateChanged.emit(manageControls)
            
    def onCreateAdminUnit(self):
        '''
        Slot raised on clicking to add a new administrative unit.
        '''
        self._notifBar.clear()
        
        if self.txtUnitName.text() == "":
            msg = QApplication.translate("AdminUnitManager","Name of the administrative unit cannot be empty.")
            self._notifBar.insertErrorNotification(msg)
            self.txtUnitName.setFocus()
            return
        
        if not self.txtUnitName.validate():
            return
            
        if self.txtUnitCode.text() == "":
            msg = QApplication.translate("AdminUnitManager","Code of the administrative unit cannot be empty.")
            self._notifBar.insertErrorNotification(msg)
            self.txtUnitCode.setFocus()
            return
        
        # if not self.txtUnitCode.validate():
        #     return
        
        #Get current row selection
        selIndexes = self.tvAdminUnits.selectionModel().selectedRows(0)
        
        if len(selIndexes) == 0:
            #Get the number of items in the tree view
            rootIndex = self.tvAdminUnits.rootIndex()
            rowCount = self._adminUnitTreeModel.rowCount(rootIndex)
            
            if rowCount > 0:
                msg = QApplication.translate("AdminUnitManager",
                                             "You have not selected any parent node for the new administrative unit. Do " \
                                             "you want to add it as one of the topmost administrative units?\nClick Yes to " \
                                             "proceed or No to cancel.")
                selOption = QMessageBox.warning(self,QApplication.translate("AdminUnitManager","No Parent Node Selected"),msg,
                                                QMessageBox.Yes|QMessageBox.No)
                
                if selOption == QMessageBox.Yes:
                    parentNode = self._rtNode
                    #We are interested in the model index of the root node
                    parentModelIndex = rootIndex
                    parentModel = None
                    
                else:
                    return
                
            #Do not prompt user and immediately add the administrative unit to the root node.
            else:
                parentNode = self._rtNode
                parentModelIndex = rootIndex
                parentModel = None
            
        else:
            #Get model index for the first column as this is where the new node will be added as the child
            parentModelIndex = selIndexes[0]
            parentNode = self._adminUnitTreeModel._getNode(parentModelIndex)
                      
            parentID = parentNode.data(2)
            ausModel = AdminSpatialUnitSet()
            parentModel = ausModel.queryObject().filter(AdminSpatialUnitSet.id == parentID).first()
            
        adminUnitModel = AdminSpatialUnitSet(self.txtUnitName.text(), self.txtUnitCode.text(), parentModel)
            
        #Commit transaction to the database
        adminUnitModel.save()
        
        #Extract properties from the model
        ausProps = self._adminUnitNodeFormatter._extractAdminUnitSetInfo(adminUnitModel)
        
        childNode = BaseSTRNode(ausProps, parentNode)
        
        #Insert row into the view
        self._adminUnitTreeModel.insertRows(parentNode.childCount(), 1, parentModelIndex)
        
        self.clearInputs()
        
    def onClearSelection(self):
        '''
        Slot that removes any existing selections in the tree view.
        '''
        self.tvAdminUnits.selectionModel().clearSelection()
        
    def onModelDataChanged(self,oldindex,newindex):
        '''
        Slot raised when the model data is changed.
        '''
        #Get model index containing ID property
        refNode = self._adminUnitTreeModel._getNode(newindex)
        ausID = refNode.data(2)
        
        ausHandler = AdminSpatialUnitSet()
        ausObj = ausHandler.queryObject().filter(AdminSpatialUnitSet.id == ausID).first()
        
        if ausObj != None:
            attrColumn = newindex.column()
            if attrColumn == 0:
                ausObj.Name = refNode.data(0)
            elif attrColumn == 1:
                ausObj.Code = refNode.data(1)
                
            ausObj.update()
        
    def onDeleteSelection(self):
        '''
        Slot raised to delete current selection of administrative unit.
        '''
        self._notifBar.clear()
        #Get current row selection
        selIndexes = self.tvAdminUnits.selectionModel().selectedRows(2)
        
        if len(selIndexes) == 0:
            msg = QApplication.translate("AdminUnitManager",
                                         "Please select the administrative unit to delete.")
            self._notifBar.insertWarningNotification(msg)
            
        else:
            delmsg = QApplication.translate("AdminUnitManager",
                                         "This action will delete the selected administrative unit plus any " \
                                         "existing children under it. It cannot be undone.\nClick Yes to " \
                                         "delete or No to cancel.")
            selOption = QMessageBox.warning(self,QApplication.translate("AdminUnitManager","Confirm deletion"),delmsg,
                                            QMessageBox.Yes|QMessageBox.No)
            
            if selOption == QMessageBox.Yes:         
                #Get the node in the current selection
                delIndex = selIndexes[0]
                ausNode = self._adminUnitTreeModel._getNode(delIndex)
                ausId = ausNode.data(2)
                ausHandler = AdminSpatialUnitSet()
                ausObj = ausHandler.queryObject().filter(AdminSpatialUnitSet.id == ausId).first() 
                
                if not ausObj is None:
                    ausObj.delete()     
                    
                    #Remove item in tree view
                    self._adminUnitTreeModel.removeRows(delIndex.row(), 1, delIndex.parent())
                    
                    #Notify user
                    self._notifBar.clear()
                    successmsg = QApplication.translate("AdminUnitManager",
                                         "Administrative unit successfully deleted.") 
                    self._notifBar.insertSuccessNotification(successmsg)
        
    def selectedAdministrativeUnit(self):
        '''
        Returns the selected administrative unit object otherwise, if there is no
        selection then it returns None.
        '''
        selIndexes = self.tvAdminUnits.selectionModel().selectedRows(2)
        
        if len(selIndexes) == 0:
            selAdminUnit = None
            
        else:
            selIndex = selIndexes[0]
            ausNode = self._adminUnitTreeModel._getNode(selIndex)
            ausId = ausNode.data(2)
            ausHandler = AdminSpatialUnitSet()
            selAdminUnit = ausHandler.queryObject().filter(AdminSpatialUnitSet.id == ausId).first() 
            
        return selAdminUnit
          
    def clearInputs(self):
        '''
        Clears the input controls.
        '''
        self.txtUnitCode.clear()
        self.txtUnitName.clear()
        
        
        
        
        
        
        
        
        
        
            

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        