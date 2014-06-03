"""
/***************************************************************************
Name                 : STR Nodes
Description          : Module provides classes which act as proxies for
                       representing social tenure relationship information
                       in a QTreeView
Date                 : 10/November/2013 
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
from collections import OrderedDict
from decimal import Decimal

from PyQt4.QtGui import QIcon,QApplication,QAction, QDialog,QMessageBox,QMenu, \
QFileDialog, QVBoxLayout
from PyQt4.QtCore import SIGNAL

from qgis.core import *

from stdm import resources_rc
from stdm.utils import *
from stdm.data import SocialTenureRelationshipMixin, LookupFormatter, CheckSocialTenureRelationship
from stdm.ui.sourcedocument import TITLE_DEED,STATUTORY_REF_PAPER,SURVEYOR_REF,NOTARY_REF,TAX_RECEIPT_PRIVATE, \
        TAX_RECEIPT_STATE,SourceDocumentManager
from stdm.ui.str_editor_dlg import STREditorDialog

EDIT_ICON = QIcon(":/plugins/stdm/images/icons/edit.png")
DELETE_ICON = QIcon(":/plugins/stdm/images/icons/delete.png")
NO_ACTION_ICON = QIcon(":/plugins/stdm/images/icons/no_action.png")

class BaseSTRNode(object):
    '''
    Base class for all STR nodes.
    '''
    def __init__(self,data,parent=None,view = None, parentWidget = None,
                 isChild = False, styleIfChild = True, rootDepthForHash = 1):
        self._data = data
        self._children = []
        self._parent = parent
        self._rootNodeHash = ""
        self._view = view
        self._parentWidget = parentWidget
        
        if parent is not None:
            parent.addChild(self)
            #Inherit view from parent
            self._view = parent.treeView()
            self._parentWidget = parent.parentWidget()
            
        '''
        Set the hash of the node that will be taken as the root parent node.
        In this case it will be level one.      
        Level zero will not have any hash specified (just be an empty string). 
        '''
        if self.depth() == rootDepthForHash:
            self._rootNodeHash = gen_random_string()
        elif self.depth() > rootDepthForHash:
            self._rootNodeHash = self._parent.rootHash()
        
        #Separator for child text
        self.separator = " : "
        
        if isChild:
            if styleIfChild:
                self._styleIfChild = True
        else:
            self._styleIfChild = False
            
        #Default actions that will be most commonly used by the nodes with data management capabilities
        self.editAction = QAction(EDIT_ICON,
                             QApplication.translate("BaseSTRNode","Edit..."),None)
        self.deleteAction = QAction(DELETE_ICON,
                             QApplication.translate("BaseSTRNode","Delete"),None)
            
    def addChild(self,child):
        '''
        Add child to the parent node.
        '''
        self._children.append(child)
        
    def insertChild(self,position,child):
        '''
        Append child at the specified position in the list
        '''
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        
        return True
    
    def removeChild(self,position):
        '''
        Remove child at the specified position.
        '''
        if position < 0 or position >= len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None
        
        return True
    
    def clear(self):
        '''
        Removes all children in the node.
        '''
        try:
            del self._children[:]
            return True
        except:
            return False
        
    def child(self,row):
        '''
        Get the child node at the specified row.
        '''
        if row < 0 or row >= len(self._children):
            return None
        
        return self._children[row]
    
    def childCount(self):
        '''
        Number of children node with the current node as the parent.
        '''
        return len(self._children)
    
    def children(self):
        '''
        Returns all the node's children as a list.
        '''
        return self._children
    
    def hasParent(self):
        '''
        True if the node has a parent. Otherwise returns False.
        '''
        return True if self._parent else False
    
    def parent(self):
        '''
        The parent of this node.
        '''
        return self._parent
    
    def treeView(self):
        '''
        Returns the tree view that contains this node.
        '''
        return self._view
    
    def parentWidget(self):
        '''
        Returns the main widget that displays the social tenure relationship information.
        '''
        return self._parentWidget
    
    def row(self):
        '''
        Return the position of this node in the parent container.
        '''
        if self._parent:
            return self.parent()._children.index(self)
        
        return 0
        
    def icon(self):
        '''
        Return a QIcon for decorating the node.
        To be implemented by subclasses.
        '''
        return None
    
    def id(self):
        '''
        Returns the ID of the model it represents.
        '''
        return -1
    
    def depth(self):
        '''
        Returns the depth/hierarchy of this node.
        '''
        depth = 0
        item = self.parent()
        
        while item is not None:
            item = item.parent()
            depth += 1
        
        return depth
    
    def rootHash(self):
        '''
        Returns a hash key that is used to identify the lineage of the child nodes i.e.
        which node exactly is the forefather.
        '''
        return self._rootNodeHash
    
    def styleIfChild(self):
        '''
        Style the parent title if set to 'True'.
        This is a read only property.
        '''
        return self._styleIfChild
    
    def data(self,column):
        '''
        Returns the data item in the specified specified column index within the list.
        '''
        if column < 0 or column >= len(self._data):
            raise IndexError
        
        return self._data[column]
    
    def setData(self,column,value):
        '''
        Set the value of the node data at the given column index.
        '''
        if column < 0 or column >= len(self._data):
            return False
        
        self._data[column] = value
        
        return True
    
    def columnCount(self):
        '''
        Return the number of columns. 
        '''
        return len(self._data)
    
    def column(self,position):
        '''
        Get the data in the specified column.
        '''
        if position < 0 and position >= len(self._data):
            return None
        
        return self._data[position]
    
    def removeColumns(self,position,columns):
        '''
        Removes columns in the STR node.
        '''
        if position < 0 or position >= len(self._data):
            return False
        
        for c in range(columns):
            self._data.pop(position)
            
        return True
    
    def clearColumns(self):
        '''
        Removes all columns in the node.
        '''
        del self._data[:]
        
    def typeInfo(self):
        return "BASE_NODE"
    
    def __repr__(self):
        return self.typeInfo()
    
    def manageActions(self,modelindex,menu):
        '''
        Returns the list of actions to be loaded into the context menu
        of this node when a user right clicks in the treeview.
        Default action is a notification that no action item has been 
        defined for the current node item.
        To be inherited by subclasses for custom actions.
        '''
        nullAction = QAction(NO_ACTION_ICON,
                             QApplication.translate("BaseSTRNode", "No User Action"),self.parentWidget())
        nullAction.setEnabled(False)
        
        menu.addAction(nullAction)
    
    def onEdit(self,index):
        '''
        Slot triggered when the Edit action of the node is triggered by the user.
        Subclasses to implement.
        '''
        pass
    
    def onDelete(self,index):
        '''
        Slot triggered when the Delete action of the node is triggered by the user.
        Subclasses to implement.
        '''
        pass
    
    def signalReceivers(self,action,signal = "triggered()"):
        '''
        Convenience method that returns the number of receivers connected to the signal of the action object.
        '''
        return action.receivers(SIGNAL(signal))
    
class PersonNode(BaseSTRNode):
    '''
    Node for rendering person information in the tree view.
    '''
    def __init__(self,person,parent=None):
        super(PersonNode,self).__init__(person,parent)
        
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/user.png")
    
    def typeInfo(self):
        return "PERSON_NODE"
    
class NoSTRNode(BaseSTRNode):
    '''
    Node for showing that no STR relationship exists.
    '''
    def __init__(self,parent=None):
        noSTRText = str(QApplication.translate("NoSTRNode","No STR Defined"))
        super(NoSTRNode,self).__init__([noSTRText],parent)
        
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/remove.png")
    
    def typeInfo(self):
        return "NO_STR_NODE"
    
class STRNode(BaseSTRNode):
    '''
    Node for rendering specific social tenure relationship information.
    '''
    def __init__(self,strmodel,parent = None, isChild = True, styleIfChild = True):
        self.strModel = strmodel
        
        self._objValues = []
        
        #Define property names
        self.propNameSTRType = "SocialTenureType"
        self.propNameHasAgreement = "AgreementAvailable"
        
        self.propertyLabels = OrderedDict({
                       self.propNameSTRType : str(QApplication.translate("STRNode","Type")),
                       self.propNameHasAgreement : str(QApplication.translate("STRNode","Has Agreement"))
                       })
        
        #Set object values
        self._setObjectValues()
        
        self._parentTitle = str(QApplication.translate("STRNode","Social Tenure"))
        
        if not isChild:
            super(STRNode,self).__init__([self._objValues],parent, isChild, styleIfChild)
            
        else:
            super(STRNode,self).__init__([self._parentTitle],parent, isChild, styleIfChild)
            self._setChildren()
            
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/social_tenure.png")
    
    def sourceDocuments(self):
        '''
        Returns a list of source documents defined for this social tenure relationship.
        Combine the listing of source documents as well as tax documents if available.
        '''
        srcDocs = []
        srcDocs.extend(self.strModel.SourceDocuments)
        if self.strModel.hasTaxation():
            taxDoc = self.strModel.Taxation.Document
            if taxDoc:
                srcDocs.append(taxDoc)
        
        return srcDocs
    
    def id(self):
        '''
        Returns the ID of the model it represents.
        '''
        return self.strModel.id
    
    def _setObjectValues(self):
        '''
        Returns the object values as a list.
        '''
        for prop,label in self.propertyLabels.iteritems():
            if prop == self.propNameSTRType:
                strLoookupFormatter = LookupFormatter(CheckSocialTenureRelationship)
                strAttrVal = getattr(self.strModel,self.propNameSTRType)
                strText = str(strLoookupFormatter.setDisplay(strAttrVal).toString())
            elif prop == self.propNameHasAgreement:
                strText = "Yes" if getattr(self.strModel,prop) else "No"
            
            self._objValues.append(strText)
    
    def _setChildren(self):
        '''
        Add text information as children to this node describing the STR info.
        '''
        propValues = self.propertyLabels.values()
        for i in range(len(propValues)):
            label = propValues[i]
            value = self._objValues[i]
            nodeText = label + self.separator + value
            strInfoNode = BaseSTRNode([nodeText],self)
            
    def typeInfo(self):
        return "STR_NODE"
    
    def onEdit(self, index):
        '''
        Edit STR information.
        '''
        #Show STR editor dialog
        strEditor = STREditorDialog(self.parentWidget(),self.strModel)
        
        if strEditor.exec_() == QDialog.Accepted:
            self.strModel = strEditor.socialtenure
            model = self._view.model()
            model.removeRows(0,self.childCount(),index)
                
            del self._objValues[:]
            self._setObjectValues()
            self._setChildren()
            model.insertRows(0,2,index)
        
    def onDelete(self, index):
        '''
        Delete STR information.
        '''
        delMsg = QApplication.translate("STRNode", 
                                     "This action will remove the social tenure relationship and dependent supporting documents, conflict" \
                                     " and tax information from the database. This action cannot be undone and once removed, it can" \
                                     "  only be recreated through" \
                                     " the 'New Social Tenure Relationship' wizard. Would you like to proceed?" \
                                     "\nClick Yes to proceed or No to cancel.")
        delResult = QMessageBox.warning(self.parentWidget(),QApplication.translate("STRNode","Delete Social Tenure Relationship"),delMsg,
                                        QMessageBox.Yes|QMessageBox.No)
        if delResult == QMessageBox.Yes:
            model = self._view.model()
            model.removeAllChildren(index.row(),self.childCount(),index.parent()) 
            #Remove source documents listings
            self.parentWidget()._deleteSourceDocTabs()
            self.strModel.delete()
            
            #Insert NoSTR node
            noSTRNode = NoSTRNode(self.parent())
            
            #Notify model that we have inserted a new child i.e. NoSTRNode
            model.insertRows(index.row(),1,index.parent())
        
    def onAddSourceDocument(self,doctype):
        '''
        Slot raised when the user has selected to add a new source document.
        '''
        
        #Create a proxy source document manager for inserting documents.
        srcDocManager = SourceDocumentManager(self.parentWidget())
        vBoxProxy = QVBoxLayout(self._parentWidget)
        self._parentWidget.connect(srcDocManager,SIGNAL("fileUploaded(PyQt_PyObject)"),
                       self._onSourceDocUploaded)
                
        if doctype == TITLE_DEED:
            dialogTitle = QApplication.translate("STRNode", 
                                             "Specify Title Deed File Location")
        elif doctype == STATUTORY_REF_PAPER:
            dialogTitle = QApplication.translate("STRNode", 
                                             "Specify Statutory Reference Paper File Location")
        elif doctype == SURVEYOR_REF:
            dialogTitle = QApplication.translate("STRNode", 
                                             "Specify Surveyor Reference File Location")
        elif doctype == NOTARY_REF:
            dialogTitle = QApplication.translate("STRNode", 
                                             "Specify Notary Reference File Location")
        else:
            return
            
        docPath = self._selectSourceDocumentDialog(dialogTitle)
        
        if not docPath.isNull():
            #Register container then upload document
            srcDocManager.registerContainer(vBoxProxy, doctype)
            srcDocManager.insertDocumentFromFile(docPath,doctype)
        
    def _onSourceDocUploaded(self,sourcedocument):
        '''
        Slot raised once a new document has been uploaded into the central repository.
        '''
        self.strModel.SourceDocuments.append(sourcedocument)
        self.strModel.update()
        
        #Update the source document listing in the main widget
        self.parentWidget()._loadSourceDocuments([sourcedocument])
       
    def _selectSourceDocumentDialog(self,title):
        '''
        Displays a file dialog for a user to specify a source document
        '''
        filePath = QFileDialog.getOpenFileName(self._parentWidget,title,"/home","Source Documents (*.pdf)")
        return filePath  
    
    def onCreateConflict(self,index):
        '''
        Slot raised when user selects to define new conflict information.
        '''
        confEditorDialog = ConflictEditorDialog(self.parentWidget())
            
        if confEditorDialog.exec_() == QDialog.Accepted:
            strParent = self.parent()
            conflictNode = ConflictNode(confEditorDialog.conflict,strParent)
            self.strModel.Conflict = confEditorDialog.conflict
            
            #Force tree view to update
            numChildren = strParent.childCount()
            self._view.model().insertRows(numChildren,1,index.parent())
        
    def onCreateTaxation(self,index):
        '''
        Slot raised when user selects to define tax information.
        '''
        taxEditor = TaxInfoDialog(self.parentWidget())
        
        if taxEditor.exec_() == QDialog.Accepted:
            strParent = self.parent()
            taxNode = TaxationNode(taxEditor.taxation,strParent)
            self.strModel.Taxation = taxEditor.taxation
            self.strModel.update()
            
            '''
            Get the parent node of this STRNode then get the number of children below it
            since we want to add the new taxation node at the end of the children nodes.
            Insert rows with respect to the parent model index of the node that received
            the context menu request.
            '''
            numChildren = strParent.childCount()
            self._view.model().insertRows(numChildren,1,index.parent())
            
            #Incorporate tax document in the document listing if it has been specified
            if taxEditor.taxation.Document:
                self.parentWidget()._loadSourceDocuments([taxEditor.taxation.Document])
    
    def manageActions(self,modelindex,menu):
        '''
        Returns a menu for managing social tenure relationship information.
        '''
        editReceivers = self.signalReceivers(self.editAction)
        if editReceivers > 0:
            self.editAction.triggered.disconnect()
            
        deleteReceivers = self.signalReceivers(self.deleteAction)
        if deleteReceivers > 0:
            self.deleteAction.triggered.disconnect()
            
        #Add new entities menu
        entityAddMenu = QMenu(QApplication.translate("STRNode","Add"),self.parentWidget())
        entityAddMenu.setIcon(QIcon(":/plugins/stdm/images/icons/add.png"))
        
        #Define actions for adding related STR entities
        confAction = QAction(QIcon(":/plugins/stdm/images/icons/conflict.png"),
                                 QApplication.translate("STRNode","Conflict Information"),self._view)
        confAction.triggered.connect(lambda: self.onCreateConflict(modelindex))
        #Check if conflict information already exists. If so, then no need of defining twice
        if self.strModel.hasConflict():
            confAction.setEnabled(False)
        entityAddMenu.addAction(confAction)
        
        taxAction = QAction(QIcon(":/plugins/stdm/images/icons/receipt.png"),
                                 QApplication.translate("STRNode","Tax Information"),self._view)
        taxAction.triggered.connect(lambda: self.onCreateTaxation(modelindex))
        if self.strModel.hasTaxation():
            taxAction.setEnabled(False)
        entityAddMenu.addAction(taxAction)
        
        #Add source documents menu
        addSrcDocMenu = QMenu(QApplication.translate("STRNode","Source Documents"),self.parentWidget())
        addSrcDocMenu.setIcon(QIcon(":/plugins/stdm/images/icons/attachment.png"))
        titleDeedAction = QAction(QApplication.translate("STRNode","Title Deed"),self._view)
        titleDeedAction.triggered.connect(lambda: self.onAddSourceDocument(TITLE_DEED))
        addSrcDocMenu.addAction(titleDeedAction)
        notaryRefAction = QAction(QApplication.translate("STRNode","Notary Reference"),self._view)
        notaryRefAction.triggered.connect(lambda: self.onAddSourceDocument(NOTARY_REF))
        addSrcDocMenu.addAction(notaryRefAction)
        statRefPaperAction = QAction(QApplication.translate("STRNode","Statutory Reference Paper"),self._view)
        statRefPaperAction.triggered.connect(lambda: self.onAddSourceDocument(STATUTORY_REF_PAPER))
        addSrcDocMenu.addAction(statRefPaperAction)
        surveyorRefAction = QAction(QApplication.translate("STRNode","Surveyor Reference"),self._view)
        surveyorRefAction.triggered.connect(lambda: self.onAddSourceDocument(SURVEYOR_REF))
        addSrcDocMenu.addAction(surveyorRefAction)
        
        entityAddMenu.addMenu(addSrcDocMenu)
        
        menu.addMenu(entityAddMenu)
        menu.addAction(self.editAction)
        menu.addAction(self.deleteAction)
        
        #Disable if the user does not have permission.
        if not self.parentWidget()._canEdit:
            menu.setEnabled(False)
            
        self.editAction.triggered.connect(lambda: self.onEdit(modelindex))
        self.deleteAction.triggered.connect(lambda: self.onDelete(modelindex))
            
class PropertyNode(BaseSTRNode):
    '''
    Node for rendering property information.
    '''
    def __init__(self,property,parent = None, isChild = False, styleIfChild = True):
        self.property = property
        
        self._objValues = []
        
        #Define property names
        self.propNamePropertyID = "PropertyID"
        self.propNameUseType = "UseTypeID" 
        self.propNameDescription = "DescriptionID"
        self.propNumFloors = "NumFloors"
        self.propRoofType = "RoofTypeID"
        self.propNatureWalls = "NatureWalls"
        self.propBoundaryType = "BoundaryType"
        self.propNumRooms = "NumRooms"
        self.propLandValue = "LandValue"
        self.propBuildingValue = "BuildingValue"
        self.propLandAccession = "LandAccessionID"
        self.propLandAccessYear = "LandAccessionYear"
        self.propBuildingAccession = "BuildingAccessionID"
        self.propBuildingAccessYear = "BuildingAccessionYear"
        
        self.propertyLabels = OrderedDict({
                       self.propNamePropertyID : str(QApplication.translate("PropertyNode","Identity")),
                       self.propNameUseType : str(QApplication.translate("PropertyNode","Use")),
                       self.propNameDescription : str(QApplication.translate("PropertyNode","Description")),
                       self.propNumFloors : str(QApplication.translate("PropertyNode","Number of Floors")),
                       self.propRoofType : str(QApplication.translate("PropertyNode","Roof Type")),
                       self.propNatureWalls : str(QApplication.translate("PropertyNode","Nature of Walls")),
                       self.propBoundaryType : str(QApplication.translate("PropertyNode","Boundary Type")),
                       self.propNumRooms : str(QApplication.translate("PropertyNode","Number of Rooms")),
                       self.propLandValue : str(QApplication.translate("PropertyNode","Land Value")),
                       self.propBuildingValue : str(QApplication.translate("PropertyNode","Building Value")),
                       self.propLandAccession : str(QApplication.translate("PropertyNode","Land Accession")),
                       self.propLandAccessYear : str(QApplication.translate("PropertyNode","Land Accession Year")),
                       self.propBuildingAccession : str(QApplication.translate("PropertyNode","Building Accession")),
                       self.propBuildingAccessYear : str(QApplication.translate("PropertyNode","Building Accession Year"))
                       })
        
        #Set object values
        self._setObjectValues()
        
        self._parentTitle = str(QApplication.translate("PropertyNode","Property"))
        
        if not isChild:
            super(PropertyNode,self).__init__([self._objValues],parent, isChild, styleIfChild)
            
        else:
            super(PropertyNode,self).__init__([self._parentTitle],parent, isChild, styleIfChild)
            self._setChildren()
            
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/property.png")
    
    def id(self):
        '''
        Returns the property id.
        '''
        return self.property.id
    
    def _setObjectValues(self):
        '''
        Returns the object values as a list.
        '''
        for prop,label in self.propertyLabels.iteritems():
            if prop == self.propNameUseType:
                lkFormatter = LookupFormatter(CheckBuildingUseType)
                attrVal = getattr(self.property,self.propNameUseType)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propNameDescription:
                lkFormatter = LookupFormatter(CheckBuildingDescription)
                attrVal = getattr(self.property,self.propNameDescription)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propRoofType:
                lkFormatter = LookupFormatter(CheckRoofType)
                attrVal = getattr(self.property,self.propRoofType)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propNatureWalls:
                lkFormatter = LookupFormatter(CheckWallNature)
                attrVal = getattr(self.property,self.propNatureWalls)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propBoundaryType:
                lkFormatter = LookupFormatter(CheckBoundaryType)
                attrVal = getattr(self.property,self.propBoundaryType)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propLandAccession:
                lkFormatter = LookupFormatter(CheckAccessionMode)
                attrVal = getattr(self.property,self.propLandAccession)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propBuildingAccession:
                lkFormatter = LookupFormatter(CheckAccessionMode)
                attrVal = getattr(self.property,self.propBuildingAccession)
                strText = unicode(lkFormatter.setDisplay(attrVal).toString())
            elif prop == self.propBuildingValue or prop == self.propLandValue:
                if getattr(self.property,prop) == None:
                    strText = "Not defined"
                else:
                    decAmount = Decimal(getattr(self.property,prop))
                    strText = moneyfmt(decAmount)
            else:
                strText = unicode(getattr(self.property,prop))
            
            self._objValues.append(strText)
    
    def _setChildren(self):
        '''
        Add text information as children to this node describing the STR info.
        '''
        propValues = self.propertyLabels.values()
        for i in range(len(propValues)):
            label = propValues[i]
            value = self._objValues[i]
            nodeText = label + self.separator + value
            strInfoNode = BaseSTRNode([nodeText],self)
            
    def typeInfo(self):
        return "PROPERTY_NODE"
    
class ConflictNode(BaseSTRNode):
    '''
    Node for rendering conflict information.
    '''
    def __init__(self,conflict,parent = None,styleIfChild = True):
        self.conflict = conflict
        
        self._objValues = []
        
        #Define property names
        self.propNameDescription = "Description"
        self.propNameSolution= "Solution" 
        
        self.propertyLabels = OrderedDict({
                       self.propNameDescription : str(QApplication.translate("ConflictNode","Description")),
                       self.propNameSolution : str(QApplication.translate("ConflictNode","Solution"))
                       })
        
        #Set object values
        self._setObjectValues()
        
        self._parentTitle = str(QApplication.translate("STRNode","Conflict"))
        
        super(ConflictNode,self).__init__([self._parentTitle],parent, True, styleIfChild)
        
        self._setChildren()
            
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/conflict.png")
    
    def _setObjectValues(self):
        '''
        Returns the object values as a list.
        '''
        for prop,label in self.propertyLabels.iteritems():
            strText = str(getattr(self.conflict,prop))
            self._objValues.append(strText)
    
    def _setChildren(self):
        '''
        Add text information as children to this node describing the STR info.
        '''
        propValues = self.propertyLabels.values()
        for i in range(len(propValues)):
            label = propValues[i]
            value = self._objValues[i]
            nodeText = label + self.separator + value
            strInfoNode = BaseSTRNode([nodeText],self)
    
    def id(self):
        '''
        Returns the conflict id.
        '''
        return self.conflict.id        
    
    def typeInfo(self):
        return "CONFLICT_NODE"
    
    def onEdit(self,index):
        '''
        Slot raised when the user select the edit action in this node's context menu.
        '''
        
        confEditorDialog = ConflictEditorDialog(self.parentWidget(),self.conflict)
            
        if confEditorDialog.exec_() == QDialog.Accepted:
            self.conflict = confEditorDialog.conflict
        
            #Use the model of the view to remove items
            if self._view:
                model = self._view.model()
                model.removeRows(0,self.childCount(),index)
                
                #Delete previous conflict info and insert the updated conflict information
                del self._objValues[:]
                self._setObjectValues()
                self._setChildren()
                model.insertRows(0,2,index)
                
    def onDelete(self,index):
        '''
        Slot raised when the user selects the delete action to remove conflict
        information for the selected social tenure relationship.
        '''
        delMsg = QApplication.translate("ConflictNode", 
                                     "This action will remove the conflict information associated with the social tenure relationship." \
                                     "\nClick Yes to proceed or No to cancel.")
        delResult = QMessageBox.warning(self.parentWidget(),QApplication.translate("ConflictNode","Delete Conflict Information"),delMsg,
                                        QMessageBox.Yes|QMessageBox.No)
        if delResult == QMessageBox.Yes:
            if self._view:
                model = self._view.model()
                model.removeRow(index.row(),index.parent()) 
                self.conflict.delete()    
        
    def manageActions(self,modelindex,menu):
        '''
        Actions for editing or deleting conflict information for the particular STR record.
        '''
        #Disconnect existing signals from their slots, otherwise the slot will be activated multiple times.
        editReceivers = self.signalReceivers(self.editAction)
        if editReceivers > 0:
            self.editAction.triggered.disconnect()
            
        deleteReceivers = self.signalReceivers(self.deleteAction)
        if deleteReceivers > 0:
            self.deleteAction.triggered.disconnect()
        
        #Disable if the user does not have permission.
        if not self.parentWidget()._canEdit:
            self.editAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            
        self.editAction.triggered.connect(lambda:self.onEdit(modelindex))
        self.deleteAction.triggered.connect(lambda: self.onDelete(modelindex))
        
        menu.addAction(self.editAction)
        menu.addAction(self.deleteAction)
        
class TaxationNode(BaseSTRNode):
    '''
    Node for rendering taxation information.
    '''
    def __init__(self,taxation,parent = None, isChild = False, styleIfChild = True):
        self.taxation = taxation
        
        self._objValues = []
        
        #Use tax office as a flag to determine whether it is for private or stateland
        self._setTaxType(taxation)
        
        #Define model attributes
        self.propNameRefDate = "ReferenceDate"
        self.propNameAmount = "Amount"
        self.propNameLeaseDate = "LeaseDate"
        self.propNameTaxOffice = "TaxOffice" 
            
        self._setDisplayLabels()
        
        #Set object values
        self._setObjectValues()
        
        self._parentTitle = str(QApplication.translate("TaxationNode","Taxation"))
        
        super(TaxationNode,self).__init__([self._parentTitle],parent, True, styleIfChild)
        
        self._setChildren()
        
    def _setDisplayLabels(self):
        if self.taxType == TAX_RECEIPT_PRIVATE:
            self.propertyLabels = OrderedDict({
                       self.propNameRefDate : str(QApplication.translate("TaxationNode","Last Year CFBP Was Paid")),
                       self.propNameAmount : str(QApplication.translate("TaxationNode","Amount of CFBP"))
                       })
        else:
            self.propertyLabels = OrderedDict({
                       self.propNameRefDate : str(QApplication.translate("TaxationNode","Date of Latest Receipt")),
                       self.propNameAmount : str(QApplication.translate("TaxationNode","Amount of Last Receipt")),
                       self.propNameLeaseDate : str(QApplication.translate("TaxationNode","Start of Leasing Year")),
                       self.propNameTaxOffice : str(QApplication.translate("TaxationNode","Tax Office"))
                       })
            
    def _setTaxType(self,tax):
        '''
        Set tax type based on the object properties.
        '''
        if tax.TaxOffice:
            self.taxType = TAX_RECEIPT_STATE
        else:
            self.taxType = TAX_RECEIPT_PRIVATE
            
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/receipt.png")
    
    def id(self):
        '''
        Returns the taxation id.
        '''
        return self.taxation.id
    
    def _setObjectValues(self):
        '''
        Returns the object values as a list.
        '''
        for prop,label in self.propertyLabels.iteritems():
            if getattr(self.taxation,prop) == None:
                strText = "Not Defined"
            else:
                if prop == self.propNameRefDate and self.taxType == TAX_RECEIPT_PRIVATE:
                    refDate = getattr(self.taxation,prop)
                    strText = str(refDate.year)
                elif prop == self.propNameLeaseDate and self.taxType == TAX_RECEIPT_STATE:
                    leaseDate = getattr(self.taxation,prop)
                    strText = str(leaseDate.year)
                elif prop == self.propNameAmount:
                    decAmount = Decimal(getattr(self.taxation,prop))
                    strText = moneyfmt(decAmount)
                else:
                    strText = unicode(getattr(self.taxation,prop))
            
            self._objValues.append(strText)
    
    def _setChildren(self):
        '''
        Add text information as children to this node describing the STR info.
        '''
        propValues = self.propertyLabels.values()
        for i in range(len(propValues)):
            label = propValues[i]
            value = self._objValues[i]
            nodeText = label + self.separator + value
            strInfoNode = BaseSTRNode([nodeText],self)
            
    def typeInfo(self):
        return "TAXATION_NODE"
    
    def manageActions(self,modelindex,menu):
        #Disconnect existing signals from their slots, otherwise the slot will be activated multiple times.
        editReceivers = self.signalReceivers(self.editAction)
        if editReceivers > 0:
            self.editAction.triggered.disconnect()
            
        deleteReceivers = self.signalReceivers(self.deleteAction)
        if deleteReceivers > 0:
            self.deleteAction.triggered.disconnect()
        
        #Disable if the user does not have permission.
        if not self.parentWidget()._canEdit:
            self.editAction.setEnabled(False)
            self.deleteAction.setEnabled(False)
            
        self.editAction.triggered.connect(lambda:self.onEdit(modelindex))
        self.deleteAction.triggered.connect(lambda: self.onDelete(modelindex))
        
        menu.addAction(self.editAction)
        menu.addAction(self.deleteAction)
    
    def onEdit(self,index):
        '''
        Slot raised when the user select the edit action in this node's context menu.
        '''
        taxEditor = TaxInfoDialog(self.parentWidget(),self.taxation)
        initialTaxType = self.taxType
        
        if taxEditor.exec_() == QDialog.Accepted:
            self.taxation = taxEditor.taxation
            model = self._view.model()
            model.removeRows(0,self.childCount(),index)
                
            del self._objValues[:]
            self._setTaxType(self.taxation)
            self._setDisplayLabels()
            self._setObjectValues()
            self._setChildren()
            model.insertRows(0,2,index)
            
            #Remove tax document references
            self.parentWidget().removeSourceDocumentWidget(initialTaxType)
            
            #Update tax document listing
            if self.taxation.Document:
                self.parentWidget()._loadSourceDocuments([self.taxation.Document])                
               
    def onDelete(self,index):
        delMsg = QApplication.translate("TaxationNode", 
                                     "This action will remove taxation information associated with the social tenure relationship." \
                                     "\nClick Yes to proceed or No to cancel.")
        delResult = QMessageBox.warning(self.parentWidget(),QApplication.translate("TaxationNode","Delete Taxation Information"),delMsg,
                                        QMessageBox.Yes|QMessageBox.No)
        if delResult == QMessageBox.Yes:
            if self._view:
                model = self._view.model()
                model.removeRow(index.row(),index.parent()) 
                self.removeSourceDocReferences()
                self.taxation.delete()
                
    def removeSourceDocReferences(self):
        '''
        Removes the tab widgets that list the tax documents associated with the current taxation node.
        This is called when the tax node has been deleted.
        '''
        if self.taxation.Document:
            self.parentWidget().removeSourceDocumentWidget(self.taxType)
        
        

    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        