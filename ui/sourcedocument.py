"""
/***************************************************************************
Name                 : Source Document Manager
Description          : Provides source document management classes
Date                 : 6/August/2013 
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

from ui_doc_item import Ui_frmDocumentItem
from stdm.utils import size,getIndex
from stdm.network import NetworkFileManager, DocumentTransferWorker
#from stdm.data import SourceDocument
from stdmdialog import DeclareMapping
from stdm.settings import RegistryConfig,NETWORK_DOC_RESOURCE

#Document Type Enumerations
TITLE_DEED = 2020
STATUTORY_REF_PAPER = 2021
SURVEYOR_REF = 2022
NOTARY_REF = 2023
TAX_RECEIPT_PRIVATE = 2024
TAX_RECEIPT_STATE = 2025

#Display text for document types
docTypeMapping = {
                  TITLE_DEED:str(QApplication.translate("sourceDocument", "Supporting Document")),
                  STATUTORY_REF_PAPER:str(QApplication.translate("sourceDocument", "Statutory Reference Paper")),
                  SURVEYOR_REF:str(QApplication.translate("sourceDocument", "Surveyor Reference")),
                  NOTARY_REF:str(QApplication.translate("sourceDocument", "Notary Reference")),
                  TAX_RECEIPT_PRIVATE:str(QApplication.translate("sourceDocument", "Tax Receipt")),
                  TAX_RECEIPT_STATE:str(QApplication.translate("sourceDocument", "Tax Receipt"))
                  }

#Mode for initializing the document widget
UPLOAD_MODE = 2100
DOWNLOAD_MODE = 2101

class SourceDocumentManager(QObject):
    '''
    Manages the display of source documents in vertical layout container(s).
    '''
    #Signal raised when a document is removed from its container.
    documentRemoved = pyqtSignal(int)
    fileUploaded = pyqtSignal('PyQt_PyObject')
    
    def __init__(self,parent = None):
        QObject.__init__(self,parent)
        self.containers = OrderedDict()
        self._canEdit = True
        
        #Container for document references based on their unique IDs
        self._docRefs = []
        
    def reset(self):
        '''
        Removes all ids and corresponding containers.
        '''
        self.containers.clear()
        del self._docRefs[:]
        
    def setEditPermissions(self,state):
        '''
        Sets whether the user can edit existing source document records.
        This applies for all containers managed by this class.
        '''
        self._canEdit = state
        
    def registerContainer(self,container,id):
        '''
        Register a container for displaying the document widget
        '''
        self.containers[id] = container
        
    def removeContainer(self,containerid):
        '''
        Removes the container with the specified ID from the 
        document manager.
        '''
        try:
            del self.containers[containerid]
        except KeyError:
            pass
        
    def container(self,containerid):
        '''
        Get the container from the given id
        '''
        container = None
        if containerid in self.containers:
            container = self.containers[containerid]
            
        return container
    
    def registeredIds(self):
        '''
        Returns a list of registered Ids.
        '''
        return self.containers.keys()
        
    def insertDocumentFromFile(self,path,containerid):
        '''
        Insert a new document into one of the registered containers with the
        specified id. If there is no container is specified then the document widget
        will be inserted in the first container available.
        '''
        if len(self.containers) > 0:
            if containerid in self.containers:
                container = self.containers[containerid]
                
                #Check if the file exists
                if QFile.exists(path):
                    #Use the default network file manager 
                    networkManager = NetworkFileManager(self.networkResource(),self.parent())
                    
                    #Add document widget
                    docWidg = DocumentWidget(networkManager,parent = self.parent())
                    #connect slot once the document has been successfully uploaded.
                    self.connect(docWidg,SIGNAL("fileUploadComplete()"),lambda: self.onFileUploadComplete(containerid))
                    self._linkWidgetRemovedSignal(docWidg)
                    docWidg.setFile(path,containerid)
                    container.addWidget(docWidg) 
                    
    def onFileUploadComplete(self,documenttype):
        '''
        SLot raised when a source file has been successfully uploaded into the central document
        repository.
        Raises a signal that passes the resulting source document from the upload operation. 
        ''' 
        docWidget = self.sender()
        if isinstance(docWidget, DocumentWidget):
            self.fileUploaded.emit(docWidget.sourceDocument(documenttype))
            self._docRefs.append(docWidget.fileUUID)
                    
    def InsertDocFromModel(self,sourcedoc,containerid):
        '''
        Renders the source document info from 'SourceDocument' model.
        '''
        #Check if the document has already been inserted in the manager.
        docIndex = getIndex(self._docRefs, sourcedoc.document_id)
        if docIndex != -1:
            return
        
        if len(self.containers) > 0:
            if containerid in self.containers:
                container = self.containers[containerid]
                networkManager = NetworkFileManager(self.networkResource())
                
                #Add document widget
                docWidg = DocumentWidget(networkManager,mode = DOWNLOAD_MODE,canRemove = self._canEdit)
                self._linkWidgetRemovedSignal(docWidg)
                docWidg.setModel(sourcedoc)
                container.addWidget(docWidg)  
                self._docRefs.append(sourcedoc.document_id)
                    
    def networkResource(self): 
        '''
        Get the network resource location from the registry.
        '''
        regConfig = RegistryConfig()
        networkResReg = regConfig.read([NETWORK_DOC_RESOURCE])
        
        if len(networkResReg) == 0:
            networkLocation = "C:/"
        else:
            networkLocation = networkResReg[NETWORK_DOC_RESOURCE]
            
        return networkLocation
                    
    def attributeMapping(self):
        '''
        Returns the mapping of source document information for display of the summary
        documents contained in a stdm.navigation.TreeLoader object.
        '''  
        srcDocMapping = {} 
        
        for k,v in self.containers.iteritems():
            if v != None:
                docItems = OrderedDict()
                widgCount = v.count()
                
                for w in range(widgCount):
                    docWidg = v.itemAt(w).widget()
                    srcFilePath = str(docWidg.fileInfo.absoluteFilePath())
                    locTr = str(QApplication.translate("sourceDocumentManager", "Location"))
                    locTxt = "%s %s"%(locTr,str(w+1))
                    docItems[locTxt] = srcFilePath
                
                docTypeText = "%s (%s)"%(docTypeMapping[k],str(widgCount))
                srcDocMapping[docTypeText] = docItems
        
        return srcDocMapping 
    
    def sourceDocuments(self,dtype=TITLE_DEED):
        '''
        Returns the source/tax document models based on the file uploads
        contained in the document manager.
        '''
        sourceDocuments = []
        
        for k,v in self.containers.iteritems():
            widgCount = v.count()
            
            for w in range(widgCount):
                docWidg = v.itemAt(w).widget()
                sourceDoc = docWidg.sourceDocument(dtype)
                sourceDocuments.append(sourceDoc)
        
        return sourceDocuments
    
    def onDocumentRemoved(self,doctype):
        '''
        Slot raised when a document is removed from the container.
        Propagate signal.
        '''
        remDocWidget = self.sender()
        if remDocWidget:
            self.container(doctype).removeWidget(remDocWidget)
            remDocWidget.deleteLater()
            
            #Remove document reference in the list
            if remDocWidget.mode() == UPLOAD_MODE:
                docId = remDocWidget.fileUUID
            elif remDocWidget.mode() == DOWNLOAD_MODE:
                docId = remDocWidget._srcDoc.DocumentID
                
            if docId:
                try:
                    self._docRefs.remove(docId)
                except ValueError:
                    pass
            
        self.documentRemoved.emit(doctype)
    
    def eventFilter(self,watched,e):
        '''
        Intercept signals raised by the widgets managed by this container.
        For future implementations.
        '''
        pass
    
    def _addDocumentReference(self,docid):
        '''
        Add a document reference to the list that the document manager
        contains
        '''
        docIndex = getIndex(self._docRefs,docid)
        if docIndex == -1:
            self._docRefs.append(docid)
    
    def documentReferences(self):
        '''
        Returns a list of document ids in the document manager.
        '''
        return self._docRefs
    
    def _installEventFilter(self,widget):
        '''
        Installs an event filter for the widget so that the class can now handle the 
        events raised by widget.
        '''
        widget.installEventFilter(self)
    
    def _linkWidgetRemovedSignal(self,widget):
        '''
        Connects 'destroyed' signal raised when a widget is removed from the container.
        '''
        self.connect(widget, SIGNAL("referencesRemoved(int)"),self.onDocumentRemoved)
        
class DocumentWidget(QWidget,Ui_frmDocumentItem):
    '''
    Widget for displaying source document details
    '''
    #Reference removed signal is raised prior to destroying the widget.
    referencesRemoved = pyqtSignal(int)
    fileUploadComplete = pyqtSignal()
    
    def __init__(self,fileManager = None,mode = UPLOAD_MODE,parent = None,canRemove = True):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        self.initGui()
        self.fileInfo = None
        self.fileUUID = None
        self.fileManager = fileManager
        self._mode = mode
        self._displayName = ""
        self._docSize = 0
        self._srcDoc = None
        self._fileName = ""
        self._canRemove = canRemove
        
        self.lblClose.installEventFilter(self)
        self._docType = -1
        
        #Set defaults
        self.fileNameColor = "#5555ff"
        self.fileMetaColor = "#8f8f8f" 
        
    def eventFilter(self,watched,e):      
        '''
        Capture label mouse release events for deleting and opening a source 
        document respectively.
        '''
        if watched == self.lblClose and e.type() == QEvent.MouseButtonRelease:
            self.removeDocument()
            return True
        
        elif watched == self.lblName and e.type() == QEvent.MouseButtonRelease:
            self.openDocument()
            return True
        
        else:
            return QWidget.eventFilter(self,watched,e)
          
    def initGui(self):
        '''
        Initialize GUI
        '''
        self.lblName.clear()
        self.pgBar.setVisible(False)
        self.pgBar.setValue(0)
        
    def mode(self):
        '''
        Returns the mode that the widget is configured to run.
        Returns either UPLOAD_MODE or DOWNLOAD_MODE.
        '''
        return self._mode
                    
    def removeDocument(self):
        '''
        Destroy the document widget and removes file references in the network drive
        and corresponding database record.
        '''
        msgConfirm = QApplication.translate("DocumentWidget", 
                                         """Are you sure you want to delete this document? This action cannot be undone.
                                         \nClick Yes to proceed or No to cancel.""")
        response = QMessageBox.warning(self.parent(), QApplication.translate("DocumentWidget", "Delete Source Document"), 
                                 msgConfirm, QMessageBox.Yes | QMessageBox.No)
        
        if response == QMessageBox.No:
            return
        
        if self._mode == UPLOAD_MODE:
            status = self.fileManager.deleteDocument()
        else:
            status = self.fileManager.deleteDocument(self._srcDoc)
            
        if not status:
            msg = QApplication.translate("DocumentWidget", 
                                         "The system could not delete the document. Please check your document repository settings.")
            QMessageBox.critical(self.parent(), QApplication.translate("DocumentWidget", "Delete Source Document"), 
                                 msg)
            return 
        
        if self._mode == DOWNLOAD_MODE:
            self._srcDoc.delete()
        
        #Emit signal to indicate the widget is ready to be removed
        self.referencesRemoved.emit(self._docType)
        self.deleteLater()
        
    def openDocument(self):
        '''
        Open the file referenced by the widget.
        TODO:
        '''
        pass
        
    def setCanRemoveDocument(self,state):
        '''
        Disable the close button so that users are not able to remove the
        document from the list.
        '''
        self.lblClose.setVisible(state)
        
    def setFile(self,dfile,documenttype):
        '''
        Set the absolute file path including the name, that is to be associated 
        with the document widget.
        '''
        if self._mode == UPLOAD_MODE:
            self.fileInfo = QFileInfo(dfile)
            
            self._displayName = str(self.fileInfo.fileName())
            self._docSize = self.fileInfo.size()
        
            self.buildDisplay()
            self.uploadDoc()
            self._docType = documenttype
        
    def setModel(self,sourcedoc):
        '''
        Set the SourceDocument model that is to be associated with the widget.
        Only valid if the widget mode is in DOWNLOAD_MODE.
        '''
        self.pgBar.setVisible(False)
        
        if self._mode == DOWNLOAD_MODE:
            self._displayName = sourcedoc.FileName
            self._docSize = sourcedoc.Size
            
            self.buildDisplay()  
            self._srcDoc = sourcedoc   
            self._docType = sourcedoc.DocumentType
            
    def documentType(self):     
        '''
        Returns the document type (enumeration) that the widget currently references.
        '''  
        return self._docType

    def sourceDocument(self,dtype=TITLE_DEED):
        '''
        Builds the database model for the source document file reference.
        '''
        if self._mode == UPLOAD_MODE:
            #if dtype == TAX_RECEIPT_PRIVATE or dtype == TAX_RECEIPT_STATE:
            #    srcDoc = TaxDocument()
            #else:
            self.mapping=DeclareMapping.instance()
            srcDoc=self.mapping.tableMapping('supporting_document')
            #srcDoc = SourceDocument()
                
            srcDoc.document_id = self.fileUUID
            srcDoc.filename = str(self.fileInfo.fileName())
            #srcDoc.Size = self._docSize
            srcDoc.document_type = dtype
            
            self._srcDoc  = srcDoc
            
        return self._srcDoc
        
    def buildDisplay(self):
        '''
        Build html text for displaying file information.
        '''
        html = '<html><head/><body><p><span style="font-weight:600;text-decoration: underline;' + \
        'color:#5555ff;">'+ str(self._displayName) + '</span><span style="font-weight:600;color:#8f8f8f;">&nbsp;(' + \
        str(size(self._docSize)) + ')</span></p></body></html>'
        self.lblName.setText(html)
        
        #Enable/disable close
        self.setCanRemoveDocument(self._canRemove)
        
    def uploadDoc(self):
        '''
        Upload the file to the central repository in a separate thread using the specified file manager
        '''
        if isinstance(self.fileManager,NetworkFileManager):
            self.pgBar.setVisible(True)
            self._docSize = self.fileInfo.size()
            '''
            Create document transfer helper for multi-threading capabilities.
            Use of queued connections will guarantee that signals and slots are captured
            in any thread.
            '''
            workerThread = QThread(self)
            docWorker = DocumentTransferWorker(self.fileManager,self.fileInfo,self)
            docWorker.moveToThread(workerThread)
            
            self.connect(workerThread, SIGNAL("started()"),docWorker.transfer)
            self.connect(docWorker, SIGNAL("blockWrite(int)"),self.onBlockWritten)
            self.connect(docWorker, SIGNAL("complete(QString)"),self.onCompleteTransfer)
            self.connect(workerThread, SIGNAL("finished()"),docWorker.deleteLater)
            self.connect(workerThread, SIGNAL("finished()"),workerThread.deleteLater)
            
            workerThread.start()

    def onBlockWritten(self,size):
        '''
        Raised when a block of data is written to the central repository.
        Updates the progress bar with the bytes transferred as a percentage.
        '''
        progress = (size * 100)/self._docSize
        self.pgBar.setValue(progress)
        
    def onCompleteTransfer(self,fileid):
        '''
        Slot raised when file has been successfully transferred.
        '''
        self.pgBar.setVisible(False)
        self.fileUUID = str(fileid)
        self.fileUploadComplete.emit()
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        