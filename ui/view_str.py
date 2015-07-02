"""
/***************************************************************************
Name                 : View STR Relationsips
Description          : Main Window for seaching and browsing the social tenure
                       relationship of the participating entities.
Date                 : 24/May/2013 
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from sqlalchemy import (
    func,
    String,Table
)
from sqlalchemy.orm import mapper

import stdm.data
from stdm.data import (
    STRTreeViewModel,
    app_dbconn,
    Content,
    Base,
    STDMDb
)
from stdm.navigation.socialtenure import (
    PersonNodeFormatter,
    STRNode,
    BaseSTRNode
)
from stdm.security import Authorizer

from ui_view_str import Ui_frmViewSTR
from ui_str_view_entity import Ui_frmSTRViewEntity
from notification import NotificationBar,ERROR,INFO, WARNING
from sourcedocument import (
    SourceDocumentManager,
    DOC_TYPE_MAPPING
)
from .stdmdialog import DeclareMapping

class ViewSTRWidget(QWidget, Ui_frmViewSTR):
    '''
    Search and browse the social tenure relationship of all participating entities.
    '''
    def __init__(self,plugin):
        QWidget.__init__(self,plugin.iface.mainWindow(),Qt.Window)
        self.setupUi(self)
        
        #Center me
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        
        #set whether currently logged in user has permissions to edit existing STR records
        self._canEdit = self._getEditPermissions()
        
        '''
        Variable used to store a reference to the currently selected social tenure relationship
        when displaying documents in the supporting documents tab window.
        This ensures that there are no duplicates when the same item is selected over and over again.
        '''
        self._strID = None
        #Used to store the root hash of the currently selected node.
        self._currRootNodeHash = ""
        self._sourceDocManager = SourceDocumentManager()
        self.connect(self._sourceDocManager,SIGNAL("documentRemoved(int)"),self.onSourceDocumentRemoved)
        self._sourceDocManager.setEditPermissions(self._canEdit)
        self.mapping=DeclareMapping.instance()
        self.initGui()
        
    def initGui(self):
        '''
        Initialize widget
        '''
        self.loadEntityConfig()
        #Hook up signals
        self.connect(self.tbSTREntity, SIGNAL("currentChanged(int)"),self.entityTabIndexChanged)
        self.connect(self.btnSearch, SIGNAL("clicked()"),self.searchEntityRelations)
        self.connect(self.btnClearSearch, SIGNAL("clicked()"),self.clearSearch)
        self.connect(self.tvSTRResults,SIGNAL("expanded(const QModelIndex&)"),self.onTreeViewItemExpanded)
        
        #Configure notification bars
        self.notifSearchConfig = NotificationBar(self.vlSearchEntity)
        
        #Set the results treeview to accept requests for context menus
        self.tvSTRResults.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connect(self.tvSTRResults,SIGNAL("customContextMenuRequested(const QPoint&)"),
                     self.onResultsContextMenuRequested)
                
        #Load async for the current widget
        self.entityTabIndexChanged(0)
        
        
    def loadEntityConfig(self):
        '''
        Specify the entity configurations.
        '''
        #Person configuration
        personCfg = EntityConfiguration()
        personCfg.Title = str(QApplication.translate("ViewSTR", "Person"))
        personCfg.filterColumns["family_name"] = str(QApplication.translate("ViewSTR", "First Name"))
        personCfg.filterColumns["other_names"] = str(QApplication.translate("ViewSTR", "Last Name"))
        personCfg.filterColumns["identification"] = str(QApplication.translate("ViewSTR", "Identification Number"))
        Person=self.mapping.tableMapping('party')
        personCfg.STRModel = Person
        personWidget = self.setEntityConfigWidget(personCfg)
        # QMessageBox.information(None,'test',)
        personWidget.setNodeFormatter(PersonNodeFormatter(self.tvSTRResults,self))
        
        #Property configuration
        propertyCfg = EntityConfiguration()
        propertyCfg.Title = str(QApplication.translate("ViewSTR", "Spatial Unit"))
        propertyCfg.filterColumns["code"] = str(QApplication.translate("ViewSTR", "Spatial Unit Code"))
        
        
        Property=self.mapping.tableMapping('spatial_unit')
        
    
        propertyCfg.STRModel = Property
        self.setEntityConfigWidget(propertyCfg)
    
    def setEntityConfigWidget(self,config):
        '''
        Set an entity configuration option and add it to the 'Search Entity' tab.
        '''
        entityWidg = STRViewEntityWidget(config)
        self.connect(entityWidg, SIGNAL("asyncStarted()"),self._progressStart)
        self.connect(entityWidg, SIGNAL("asyncFinished()"),self._progressFinish)
        tabIndex = self.tbSTREntity.addTab(entityWidg, config.Title)
        
        return entityWidg
        
    def entityTabIndexChanged(self,index):
        '''
        Raised when the tab index of the entity search tab widget changes.
        '''
        #Get the current widget in the tab container
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget,EntitySearchItem):
            entityWidget.loadAsync()
            
    def searchEntityRelations(self):
        '''
        Slot that searches for matching items for the specified entity and corresponding STR entities.
        '''
        self._resetTreeView()
        
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget,EntitySearchItem):
            valid,msg = entityWidget.validate()
            
            if not valid:
                self.notifSearchConfig.clear()
                self.notifSearchConfig.insertErrorNotification(msg)
                return
            
            formattedNode,results,searchWord = entityWidget.executeSearch()
            
            #Show error message 
            if len(results) == 0:
                noResultsMsg = QApplication.translate("ViewSTR", "No results found for '" + searchWord + "'")
                self.notifSearchConfig.clear()
                self.notifSearchConfig.insertErrorNotification(noResultsMsg)
                return
            
            if formattedNode is not None:
                self._loadRootNodeinTree(formattedNode)
                
    def clearSearch(self):
        '''
        Clear search input parameters (for current widget) and results.
        '''
        entityWidget = self.tbSTREntity.currentWidget()
        if isinstance(entityWidget,EntitySearchItem):
            entityWidget.reset()
            
        #Clear tree view
        self._resetTreeView()
        
        #Clear document listings
        self._deleteSourceDocTabs()
        
    def onSelectResults(self,selected,deselected):
        '''
        Slot which is raised when the selection is changed in the tree view 
        selection model.
        '''
        selIndexes = selected.indexes()
        
        #Check type of node and perform corresponding action
        for mi in selIndexes:
            if mi.isValid():
                node = mi.internalPointer()
                #Assert if node representing another entity has been clicked
                self._onNodeReferenceChanged(node.rootHash())
                if isinstance(node,STRNode):
                    srcDocs = node.sourceDocuments()
                    strId = node.id()
                    if strId != self._strID:
                        self._strID = strId
                        self._loadSourceDocuments(srcDocs)
                    break
                
    def onSourceDocumentRemoved(self,containerid):
        '''
        Slot raised when a source document is removed from the container.
        If there are no documents in the specified container then remove 
        the tab.
        '''
        for i in range(self.tbSupportingDocs.count()):
            docwidget = self.tbSupportingDocs.widget(i)
            if docwidget.containerId() == containerid:
                docCount = docwidget.container().count()
                if docCount == 0:
                    self.tbSupportingDocs.removeTab(i)
                    del docwidget
                    break
                
    def removeSourceDocumentWidget(self,containerid):
        '''
        Convenience method that removes the tab widget that lists the source documents
        with the given container id.
        '''
        for i in range(self.tbSupportingDocs.count()):
            docwidget = self.tbSupportingDocs.widget(i)
            if docwidget.containerId() == containerid:
                self.tbSupportingDocs.removeTab(i)
                self._sourceDocManager.removeContainer(containerid)
                del docwidget
                break
                
    def onTreeViewItemExpanded(self,modelindex):
        '''
        Raised when a tree view item is expanded.
        Reset the document listing and map view if the hash
        of the parent node is different.
        '''
        if modelindex.isValid():
            node = modelindex.internalPointer()
            #Assert if node representing another entity has been clicked
            self._onNodeReferenceChanged(node.rootHash())
    
    def onResultsContextMenuRequested(self,pnt):
        '''
        Slot raised when the user right-clicks on a node item to request the
        corresponding context menu.
        '''
        #Get the model index at the specified point
        mi = self.tvSTRResults.indexAt(pnt)
        if mi.isValid():
            node = mi.internalPointer()
            rMenu = QMenu(self)
            #Load node actions items into the context menu
            node.manageActions(mi,rMenu)
            rMenu.exec_(QCursor.pos())
    
    def _deleteSourceDocTabs(self):
        '''
        Removes all source document tabs and deletes their references.
        '''
        tabCount = self.tbSupportingDocs.count()
        
        while tabCount != 0:
            srcDocWidget = self.tbSupportingDocs.widget(tabCount-1)
            self.tbSupportingDocs.removeTab(tabCount-1)
            del srcDocWidget
            tabCount -= 1
            
        self._strID = None
        self._sourceDocManager.reset()
            
    def _resetTreeView(self):
        '''
        Clears the results tree view.
        '''
        #Reset tree view
        strModel = self.tvSTRResults.model()
        resultsSelModel = self.tvSTRResults.selectionModel()
        
        if strModel:
            strModel.clear()
            
        if resultsSelModel:
            self.disconnect(resultsSelModel, SIGNAL("selectionChanged(const QItemSelection&,const QItemSelection&)"),
                                     self.onSelectResults)
           
    def _loadRootNodeinTree(self,root):
        '''
        Load the search results (formatted into an object of type 'stdm.navigaion.STR') into
        the tree view.
        '''
        strTreeViewModel = STRTreeViewModel(root,view = self.tvSTRResults)
        self.tvSTRResults.setModel(strTreeViewModel)
        # Resize tree columns to fit contents
        self._resizeTreeColumns()
        
        #Capture selection changes signals when results are returned in the tree view
        resultsSelModel = self.tvSTRResults.selectionModel()
        self.connect(resultsSelModel, SIGNAL("selectionChanged(const QItemSelection&,const QItemSelection&)"),
                     self.onSelectResults)
        
    def _resizeTreeColumns(self):
        '''
        Adjusts the column sizes to fit its contents
        '''
        qModel = self.tvSTRResults.model()
        columnCount = qModel.columnCount()
        
        for i in range(columnCount):
            self.tvSTRResults.resizeColumnToContents(i)
            
        #Once resized then slightly increase the width of the first column so that text for 'No STR Defined' visible.
        currColWidth = self.tvSTRResults.columnWidth(0)
        newColWidth = currColWidth + 100
        self.tvSTRResults.setColumnWidth(0,newColWidth)
        
    def _loadSourceDocuments(self,sourcedocs):
        '''
        Load source documents into document listing widget.
        '''
        #Check the 
        #Configure progress dialog
        progressMsg = QApplication.translate("ViewSTR", "Loading supporting documents...")
        progressDialog = QProgressDialog(progressMsg,QString(),0,len(sourcedocs),self)
        progressDialog.setWindowModality(Qt.WindowModal)
        
        for i,doc in enumerate(sourcedocs):
            progressDialog.setValue(i)
            typeId = doc.DocumentType
            container = self._sourceDocManager.container(typeId)
            
            #Check if a container has been defined and create if none is found
            if container is None:
                srcDocWidget = SourceDocumentContainerWidget(typeId)
                container = srcDocWidget.container()
                self._sourceDocManager.registerContainer(container, typeId)
                #Add widget to tab container for source documents
                self.tbSupportingDocs.addTab(srcDocWidget, docTypeMapping[typeId])
                
            self._sourceDocManager.InsertDocFromModel(doc, typeId)
                
        progressDialog.setValue(len(sourcedocs))
        
    def _onNodeReferenceChanged(self,rootHash):
        '''
        Method for resetting document listing and map preview if another root node and its children
        are selected then the documents are reset as well as the map preview control.
        '''
        if rootHash != self._currRootNodeHash:
            self._deleteSourceDocTabs()
            self._currRootNodeHash = rootHash
    
    def _progressStart(self):
        '''
        Load progress dialog window.
        For items whose durations is unknown, 'isindefinite' = True by default.
        If 'isindefinite' is False, then 'rangeitems' has to be specified.
        '''
        pass
    
    def _progressFinish(self):
        '''
        Hide progress dialog window.
        '''
        pass
    
    def _getEditPermissions(self):
        '''
        Returns True/False whether the current logged in user has permissions to create new social tenure relationships.
        If true, then the system assumes that they can also edit STR records.
        '''
        canEdit = False
        userName = stdm.data.app_dbconn.User.UserName
        authorizer = Authorizer(userName)
        newSTRCode = "9576A88D-C434-40A6-A318-F830216CA15A"
        
        #Get the name of the content from the code
        cnt = Content()
        createSTRCnt = cnt.queryObject().filter(Content.code == newSTRCode).first()
        if createSTRCnt:
            name = createSTRCnt.name
            canEdit = authorizer.CheckAccess(name)
        
        return canEdit
        
class EntitySearchItem(QObject):
    '''
    Abstract class for implementation by widgets that enable users to search for entity records.
    '''
    #Signals to be raised by subclasses - There is an issue with new-style signals.
    asyncStarted = pyqtSignal()
    asyncFinished = pyqtSignal()
    
    def __init__(self,formatter=None):
        #Specify the formatter that should be applied on the result item. It should inherit from 'stdm.navigation.STRNodeFormatter'
        self.formatter = formatter
        
    def setNodeFormatter(self,formatter):
        '''
        Set the formatter that should be applied on the entity search results.
        '''
        self.formatter = formatter
        
    def validate(self):
        '''
        Method for validating the input arguments before a search is conducted.
        Should return bool indicating whether validation was successful and message (applicable if validation fails).
        '''
        raise NotImplementedError()
         
    def executeSearch(self):
        '''
        Implemented when the a search operation is executed.
        Should return tuple of formatted results for render in the tree view,raw object results and search word.
        '''
        raise NotImplementedError(str(QApplication.translate("ViewSTR", "Subclass must implement abstract method.")))
    
    def loadAsync(self):
        '''
        Any initialization that needs to be carried out when the parent container is activated.
        '''
        pass
    
    def errorHandler(self,error):
        '''
        Generic handler that logs error messages to the QGIS message log
        '''
        QgsMessageLog.logMessage(error,2)
        
    def reset(self):
        '''
        Clear search results.
        '''
        pass
            
class STRViewEntityWidget(QWidget,Ui_frmSTRViewEntity,EntitySearchItem):
    '''
    A widget that represents options for searching through an entity.
    '''
    def __init__(self,config,formatter = None,parent = None):
        QWidget.__init__(self,parent)
        EntitySearchItem.__init__(self, formatter)
        self.setupUi(self)
        self.config = config
        self.setConfigOptions()
        
        #Hook up signals
        self.connect(self.cboFilterCol, SIGNAL("currentIndexChanged(int)"),self._onColumnIndexChanged)
        
    def setConfigOptions(self):
        '''
        Apply configuration options.
        '''
        self.lblBrowseDescription.setText(self.config.browseDescription)
        #Set filter columns
        for k,v in self.config.filterColumns.iteritems():
            self.cboFilterCol.addItem(v, k)
            
    def loadAsync(self):
        '''
        Asynchronously loads entity attribute values.
        '''
        self.emit(SIGNAL("asyncStarted()")) 
        
        #Create model worker
        workerThread = QThread(self)
        modelWorker = ModelWorker()
        modelWorker.moveToThread(workerThread)
        
        #Connect signals
        self.connect(modelWorker, SIGNAL("error(QString)"),self.errorHandler)
        self.connect(workerThread, SIGNAL("started()"), 
                     lambda: modelWorker.fetch(self.config.STRModel,self.currentFieldName()))    
        self.connect(modelWorker, SIGNAL("retrieved(PyQt_PyObject)"),self._asyncFinished)
        self.connect(modelWorker, SIGNAL("retrieved(PyQt_PyObject)"),workerThread.quit)
        self.connect(workerThread, SIGNAL("finished()"),modelWorker.deleteLater)
        self.connect(workerThread, SIGNAL("finished()"),workerThread.deleteLater)
        
        #Start thread
        workerThread.start()
        
    def validate(self):
        '''
        Validate entity search widget
        '''
        isValid = True
        message = ""
        
        if self.txtFilterPattern.text() == "":
            message = QApplication.translate("ViewSTR", "Search word cannot be empty.")
            isValid = False
        
        return isValid,message
        
    def executeSearch(self):
        '''
        Base class override.
        Search for matching items for the specified entity and column.
        '''
        modelRootNode = None
        
        searchTerm = self._searchTerm()
        modelInstance = self.config.STRModel()
        
        modelQueryObj = modelInstance.queryObject()
        queryObjProperty = getattr(self.config.STRModel,self.currentFieldName())
        #Get property type so that the filter can be applied according to the appropriate type
        propType = queryObjProperty.property.columns[0].type
        
        if not isinstance(propType,String):
            results = modelQueryObj.filter(queryObjProperty == searchTerm).all()
        else:
            #Use of SQLAlchemy 'func' method to ensure that searches are case-insensitive
            results = modelQueryObj.filter(func.lower(queryObjProperty) == func.lower(searchTerm)).all()
        
        if self.formatter is not None:
            self.formatter.setData(results)
            modelRootNode = self.formatter.root()
            
        return modelRootNode,results,searchTerm
        
    def reset(self):
        '''
        Clear search input parameters.
        '''
        self.txtFilterPattern.clear()
        if self.cboFilterCol.count() > 0:
            self.cboFilterCol.setCurrentIndex(0)
        
    def currentFieldName(self):
        '''
        Returns the name of the database field from the current item in the combo box.
        '''
        currIndex = self.cboFilterCol.currentIndex()
        fieldName = self.cboFilterCol.itemData(currIndex)
        
        return str(fieldName)
    
    def _searchTerm(self):
        '''
        Returns the search term specified by the user.
        '''
        return str(self.txtFilterPattern.text())
        
    def _asyncFinished(self,modelValues):
        '''
        Slot raised when worker has finished retrieving items.
        '''
        #Create QCompleter and add values to it.
        self._updateCompleter(modelValues)
        self.emit(SIGNAL("asyncFinished()")) 
        
    def _updateCompleter(self,values):    
        #Get the items in a tuple and put them in a list
        modelVals = [str(mv[0]) for mv in values]
        #Configure completer   
        modCompleter = QCompleter(modelVals,self)         
        modCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        modCompleter.setCompletionMode(QCompleter.PopupCompletion)
        self.txtFilterPattern.setCompleter(modCompleter)  
        
    def _onColumnIndexChanged(self,int):
        '''
        Slot raised when the user selects a different filter column.
        '''
        self.txtFilterPattern.clear()
        self.loadAsync()
        
class EntityConfiguration(object):
    '''
    Specifies the configuration to apply when creating a new tab widget for performing entity searches.
    '''
    browseDescription = "Click on the browse button below to load entity records and their corresponding social tenure " \
    "relationship definitions."
    defaultFieldName = ""
    #Format of each dictionary item: property/db column name - display name
    filterColumns = OrderedDict()
    groupBy = ""
    STRModel = None
    Title = ""
    
    def __init__(self):
        #Reset filter columns container
        self.filterColumns = OrderedDict()
    
class ModelWorker(QObject):
    '''
    Worker for retrieving model attribute values stored in the database.
    '''
    retrieved = pyqtSignal('PyQt_PyObject')
    error = pyqtSignal('QString')
    
    pyqtSlot("PyQt_PyObject",'QString')  
    def fetch(self,model,fieldname):
        '''
        Fetch attribute values from the database for the specified model
        and corresponding column name.
        '''
        if hasattr(model,fieldname):
            try:
                modelInstance = model()
                objProperty = getattr(model,fieldname)
                #modelValues = modelInstance.queryObject([objProperty]).distinct() 
                modelValues = modelInstance.queryObject([objProperty]).all()       
                self.retrieved.emit(modelValues)
            except Exception as ex:
                self.error.emit(QString(ex))
                
class SourceDocumentContainerWidget(QWidget):
    '''
    Widget that enables source documents of one type to be displayed.
    '''
    def __init__(self,containerid = -1,parent = None):
        QWidget.__init__(self,parent)
        
        #Set overall layout for the widget
        vtLayout = QVBoxLayout()
        self.setLayout(vtLayout)
        
        self.docVtLayout = QVBoxLayout()
        vtLayout.addLayout(self.docVtLayout)
        
        #Id of the container 
        self._containerId = containerid
        
    def container(self):
        '''
        Returns the container in which source documents will rendered in.
        '''
        return self.docVtLayout
    
    def setContainerId(self,id):
        '''
        Sets the ID of the container.
        '''
        self._containerId = id
        
    def containerId(self):   
        '''
        Returns the ID of the container.
        '''
        return self._containerId
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
        