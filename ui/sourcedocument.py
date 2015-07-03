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

from PyQt4.QtCore import (
    QDir,
    QFile,
    QFileInfo,
    QDir,
    QObject,
    pyqtSignal,
    SIGNAL,
    QEvent,
    QThread
)
from PyQt4.QtGui import *

import sqlalchemy

from stdm.utils import (
    size,
    getIndex
)
from stdm.network import (
    NetworkFileManager,
    DocumentTransferWorker
)
#from stdm.data import SourceDocument
from stdmdialog import DeclareMapping
from stdm.settings import (
    RegistryConfig,
    NETWORK_DOC_RESOURCE,
    LOCAL_SOURCE_DOC
)

from .document_viewer import DocumentViewManager
from ui_doc_item import Ui_frmDocumentItem

#Document Type Enumerations
TITLE_DEED = 2020
STATUTORY_REF_PAPER = 2021
SURVEYOR_REF = 2022
NOTARY_REF = 2023
TAX_RECEIPT_PRIVATE = 2024
TAX_RECEIPT_STATE = 2025

#Display text for document types
DOC_TYPE_MAPPING = {
                  TITLE_DEED:str(QApplication.translate("sourceDocument", "Supporting Document")),
                  STATUTORY_REF_PAPER:str(QApplication.translate("sourceDocument", "Statutory Reference Paper")),
                  SURVEYOR_REF:str(QApplication.translate("sourceDocument", "Surveyor Reference")),
                  NOTARY_REF:str(QApplication.translate("sourceDocument", "Notary Reference")),
                  TAX_RECEIPT_PRIVATE:str(QApplication.translate("sourceDocument", "Tax Receipt")),
                  TAX_RECEIPT_STATE:str(QApplication.translate("sourceDocument", "Tax Receipt"))
                  }

#Display text for STR document types
STR_DOC_TYPE_MAPPING = {}

#Register for document types and corresponding db classes
document_type_class = {}

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

        #Set default manager for document viewing
        self._doc_view_manager = DocumentViewManager(self.parent_widget())
        
    def reset(self):
        """
        Removes all ids and corresponding containers.
        """
        self.containers.clear()
        del self._docRefs[:]

    def parent_widget(self):
        """
        :return: Instance of widget that is the parent container of this document manager.
        """
        parent_widg = self.parent()

        if isinstance(parent_widg, QWidget):
            return parent_widg

        return None
        
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
        """
        Removes the container with the specified ID from the
        document manager.
        """
        if containerid in self.containers:
            del self.containers[containerid]
        
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
        
    def insertDocumentFromFile(self, path, containerid):
        """
        Insert a new document into one of the registered containers with the
        specified id. If there is no container is specified then the document widget
        will be inserted in the first container available.
        """
        if len(self.containers) > 0:
            if containerid in self.containers:
                container = self.containers[containerid]
                
                #Check if the file exists
                if QFile.exists(path):

                    network_location = network_document_path()

                    if network_location == "":
                        self._doc_repository_error()
                        return

                    #Check if the directory exists
                    doc_dir = QDir(network_location)
                    if not doc_dir.exists():
                        msg = QApplication.translate("sourceDocumentManager",
                                                     u"The root document "
                                                     u"repository '{0}' does "
                                                     u"not exist.\nPlease "
                                                     u"check the path settings.")
                        parent = self.parent()
                        if not isinstance(parent, QWidget):
                            parent = None
                        QMessageBox.critical(parent,
                                             QApplication.translate("sourceDocumentManager","Document Manager"),
                                             msg.format(network_location))

                        return

                    #Use the default network file manager
                    networkManager = NetworkFileManager(network_location,self.parent())

                    #Add document widget
                    docWidg = DocumentWidget(networkManager, parent = self.parent(),
                                             view_manager = self._doc_view_manager)

                    #Connect slot once the document has been successfully uploaded.
                    docWidg.fileUploadComplete.connect(lambda: self.onFileUploadComplete(containerid))
                    self._linkWidgetRemovedSignal(docWidg)
                    docWidg.setFile(path,containerid)
                    container.addWidget(docWidg) 
                    
    def onFileUploadComplete(self, documenttype):
        """
        Slot raised when a source file has been successfully uploaded into the central document
        repository.
        Raises a signal that passes the resulting source document from the upload operation.
        """
        docWidget = self.sender()
        if isinstance(docWidget, DocumentWidget):
            self.fileUploaded.emit(docWidget.sourceDocument())
            self._docRefs.append(docWidget.fileUUID)
            
    def set_source_documents(self,source_docs):
        """
        :param source_docs: Supporting document objects to be inserted in their respective containers.
        :type source_docs: list
        """
        for source_doc in source_docs:
            if hasattr(source_doc, "doc_type"):
                document_type = source_doc.doc_type

                self.insertDocFromModel(source_doc, document_type)
                    
    def insertDocFromModel(self,sourcedoc,containerid):
        """
        Renders the source document info from a subclass of 'SupportingDocumentMixin'.
        """
        #Check if the document has already been inserted in the manager.
        docIndex = getIndex(self._docRefs, sourcedoc.doc_identifier)

        if docIndex != -1:
            return

        if len(self.containers) > 0:
            if containerid in self.containers:
                container = self.containers[containerid]

                network_location = source_document_location("")

                if network_location == "":
                    self._doc_repository_error()
                    return

                networkManager = NetworkFileManager(network_document_path())
                #Add document widget
                docWidg = DocumentWidget(networkManager,mode = DOWNLOAD_MODE,
                                         canRemove = self._canEdit,
                                         view_manager = self._doc_view_manager)
                self._linkWidgetRemovedSignal(docWidg)
                docWidg.setModel(sourcedoc)
                container.addWidget(docWidg)
                self._docRefs.append(sourcedoc.doc_identifier)

    def _doc_repository_error(self):
        msg = QApplication.translate("sourceDocumentManager","Document repository could not be found.\nPlease "
                                                             "check the path settings.")
        QMessageBox.critical(None,QApplication.translate("sourceDocumentManager","Document Manager"),msg)
                    
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
        """
        Returns the mapping of source document information for display of the summary
        documents contained in a stdm.navigation.TreeLoader object.
        """
        srcDocMapping = {}

        for k,v in self.containers.iteritems():
            if not v is None:
                docItems = OrderedDict()
                widgCount = v.count()

                for w in range(widgCount):
                    docWidg = v.itemAt(w).widget()
                    srcFilePath = unicode(docWidg.fileInfo.absoluteFilePath())
                    locTr = QApplication.translate("sourceDocumentManager", "Location")
                    locTxt = "%s %s"%(locTr, str(w+1))
                    docItems[locTxt] = srcFilePath

                docTypeText = "%s (%s)"%(DOC_TYPE_MAPPING[k],str(widgCount))
                srcDocMapping[docTypeText] = docItems

        return srcDocMapping
    
    def sourceDocuments(self):
        """
        Returns all supporting document models based on the file uploads
        contained in the document manager.
        """
        source_documents = {}

        for k,v in self.containers.iteritems():
            widg_count = v.count()

            type_docs = []

            for w in range(widg_count):
                docWidg = v.itemAt(w).widget()
                source_doc = docWidg.sourceDocument()
                type_docs.append(source_doc)

            source_documents[k] = type_docs

        return source_documents

    def clean_up(self):
        """
        Removes all unsaved files that had initially been uploaded in the corresponding containers.
        :return: Document widgets whose referenced files could not be removed.
        :rtype: list
        """
        delete_error_docs = []

        for k,v in self.containers.iteritems():
            layout_item = v.takeAt(0)

            while layout_item is not None:
                doc_widg = layout_item.widget()

                if not doc_widg.clean_up():
                    delete_error_docs.append(doc_widg)

                layout_item = v.takeAt(0)

        return delete_error_docs

    def onDocumentRemoved(self,doctype):
        """
        Slot raised when a document is removed from the container.
        Propagate signal.
        """
        remDocWidget = self.sender()

        if remDocWidget:
            self.container(doctype).removeWidget(remDocWidget)
            remDocWidget.deleteLater()

            #Remove document reference in the list
            if remDocWidget.mode() == UPLOAD_MODE:
                docId = remDocWidget.fileUUID

            elif remDocWidget.mode() == DOWNLOAD_MODE:
                docId = remDocWidget._srcDoc.doc_identifier

            if docId:
                #Remove corresponding viewer
                self._doc_view_manager.remove_viewer(docId)

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
        """
        Add a document reference to the list that the document manager
        contains
        """
        docIndex = getIndex(self._docRefs,docid)

        if docIndex == -1:
            self._docRefs.append(docid)

    def documentReferences(self):
        """
        Returns a list of document ids in the document manager.
        """
        return self._docRefs

    def _installEventFilter(self,widget):
        """
        Installs an event filter for the widget so that the class can now handle the
        events raised by widget.
        """
        widget.installEventFilter(self)
    
    def _linkWidgetRemovedSignal(self,widget):
        """
        Connects 'destroyed' signal raised when a widget is removed from the container.
        """
        widget.referencesRemoved.connect(self.onDocumentRemoved)
        
class DocumentWidget(QWidget,Ui_frmDocumentItem):
    """
    Widget for displaying source document details
    """
    #Reference removed signal is raised prior to destroying the widget.
    referencesRemoved = pyqtSignal(int)
    fileUploadComplete = pyqtSignal()

    def __init__(self, fileManager = None, mode = UPLOAD_MODE, parent = None, canRemove = True,
                 view_manager = None):
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
        self._view_manager = view_manager

        self.lblClose.installEventFilter(self)
        self.lblName.installEventFilter(self)
        self._docType = -1

        #Set defaults
        self.fileNameColor = "#5555ff"
        self.fileMetaColor = "#8f8f8f"

    def eventFilter(self,watched,e):
        """
        Capture label mouse release events for deleting and opening a source
        document respectively.
        """
        if watched == self.lblClose and e.type() == QEvent.MouseButtonRelease:
            self.removeDocument()
            return True

        elif watched == self.lblName and e.type() == QEvent.MouseButtonRelease:
            self.openDocument()
            return True

        else:
            return QWidget.eventFilter(self,watched,e)

    def initGui(self):
        """
        Initialize GUI
        """
        self.lblName.clear()
        self.pgBar.setVisible(False)
        self.pgBar.setValue(0)

    def mode(self):
        """
        Returns the mode that the widget is configured to run.
        Returns either UPLOAD_MODE or DOWNLOAD_MODE.
        """
        return self._mode

    def view_manager(self):
        """
        Manager for viewing the document contents.
        """
        return self._view_manager

    def removeDocument(self):
        """
        Destroy the document widget and removes file references in the network drive
        and corresponding database record.
        """
        msgConfirm = QApplication.translate("DocumentWidget",
                                         """Are you sure you want to delete this document? This action cannot be undone.
                                         \nClick Yes to proceed or No to cancel.""")
        response = QMessageBox.warning(self.parent(), QApplication.translate("DocumentWidget", "Delete Source Document"),
                                 msgConfirm, QMessageBox.Yes | QMessageBox.No)

        if response == QMessageBox.No:
            return

        self._remove_doc()

    def clean_up(self):
        """
        Remove the referenced uploaded file which has not yet been saved.
        :return: True to indicate that the document was successfully removed or False if an error was encountered.
        :rtype: bool
        """
        if self._mode == UPLOAD_MODE:
            return self._remove_doc(True)

        return True

    def _remove_doc(self,suppress_messages = False):
        """
        :param suppress_messages: Set whether user messages should be displayed or the system should continue with
        execution.
        :type suppress_messages: bool
        :return: True to indicate that the document was successfully removed or False if an error was encountered.
        :rtype: bool
        """
        if self._mode == UPLOAD_MODE:
            status = self.fileManager.deleteDocument()
        else:
            status = self.fileManager.deleteDocument(self._srcDoc)

        if not status:
            if not suppress_messages:
                msg = QApplication.translate("DocumentWidget",
                        "The system could not delete the document. Please "
                        "check your document repository settings.")
                QMessageBox.critical(self.parent(),
                                     QApplication.translate("DocumentWidget",
                                                            "Delete Source Document"),
                                     msg)
            return False

        if self._mode == DOWNLOAD_MODE:
            #Try to delete document and suppress error if it does not exist
            try:
                self._srcDoc.delete()

            except sqlalchemy.exc.SQLAlchemyError,exc:
                #TODO: Log this information
                pass

        #Emit signal to indicate the widget is ready to be removed
        self.referencesRemoved.emit(self._docType)
        self.deleteLater()

        return True

    def openDocument(self):
        """
        Open the document referenced by this widget.
        """
        if not self._view_manager is None:
            self._view_manager.load_viewer(self)

    def setCanRemoveDocument(self,state):
        """
        Disable the close button so that users are not able to remove the
        document from the list.
        """
        self.lblClose.setVisible(state)

    def setFile(self,dfile,documenttype):
        """
        Set the absolute file path including the name, that is to be associated
        with the document widget.
        """
        if self._mode == UPLOAD_MODE:
            self.fileInfo = QFileInfo(dfile)

            self._displayName = unicode(self.fileInfo.fileName())
            self._docSize = self.fileInfo.size()

            self.buildDisplay()
            self._docType = documenttype
            self.uploadDoc()

    def setModel(self,sourcedoc):
        """
        Set the SourceDocument model that is to be associated with the widget.
        Only valid if the widget mode is in DOWNLOAD_MODE.
        """
        self.pgBar.setVisible(False)

        if self._mode == DOWNLOAD_MODE:
            self._displayName = sourcedoc.file_name
            self._docSize = sourcedoc.doc_size
            self.fileUUID = sourcedoc.doc_identifier

            self.buildDisplay()
            self._srcDoc = sourcedoc
            self._docType = sourcedoc.doc_type

    def documentType(self):
        """
        Returns the document type (enumeration) that the widget currently references.
        """
        return self._docType

    def setDocumentType(self,doc_type):
        """
        Set the document type using its code. See enumeration options.
        """
        self._docType = doc_type

    def displayName(self):
        """
        Returns the original file name of the supporting document.
        """
        return self._displayName

    def file_identifier(self):
        """
        Returns the unique identifier of the file generated by the system upon
        uploading.
        """
        return self.fileUUID

    def sourceDocument(self):
        """
        Builds the database model for the source document file reference.
        """
        if self._mode == UPLOAD_MODE:
            if self._docType in document_type_class:
                src_doc = document_type_class[self._docType]()

                src_doc.doc_identifier = self.fileUUID
                src_doc.file_name = self.fileInfo.fileName()
                src_doc.doc_size = self._docSize
                src_doc.doc_type = self._docType

                self._srcDoc = src_doc

        return self._srcDoc

    def buildDisplay(self):
        """
        Build html text for displaying file information.
        """
        html = '<html><head/><body><p><span style="font-weight:600;text-decoration: underline;' + \
        'color:#5555ff;">'+ str(self._displayName) + '</span><span style="font-weight:600;color:#8f8f8f;">&nbsp;(' + \
        str(size(self._docSize)) + ')</span></p></body></html>'
        self.lblName.setText(html)

        #Enable/disable close
        self.setCanRemoveDocument(self._canRemove)

        #Disable link if no view manager has been configured
        if self._view_manager is None:
            self.lblName.setEnabled(False)

    def uploadDoc(self):
        """
        Upload the file to the central repository in a separate thread using the specified file manager
        """
        if isinstance(self.fileManager, NetworkFileManager):
            self.pgBar.setVisible(True)
            self._docSize = self.fileInfo.size()
            '''
            Create document transfer helper for multi-threading capabilities.
            Use of queued connections will guarantee that signals and slots are captured
            in any thread.
            '''
            workerThread = QThread(self)
            docWorker = DocumentTransferWorker(self.fileManager, self.fileInfo,
                                               "%d"%(self._docType), self)
            docWorker.moveToThread(workerThread)

            workerThread.started.connect(docWorker.transfer)
            docWorker.blockWrite.connect(self.onBlockWritten)
            docWorker.complete.connect(self.onCompleteTransfer)
            workerThread.finished.connect(docWorker.deleteLater)
            workerThread.finished.connect(workerThread.deleteLater)

            workerThread.start()

    def onBlockWritten(self,size):
        """
        Raised when a block of data is written to the central repository.
        Updates the progress bar with the bytes transferred as a percentage.
        """
        progress = (size * 100)/self._docSize
        self.pgBar.setValue(progress)

    def onCompleteTransfer(self,fileid):
        """
        Slot raised when file has been successfully transferred.
        """
        self.pgBar.setVisible(False)
        self.fileUUID = str(fileid)
        self.fileUploadComplete.emit()

def source_document_location(default = "/home"):
    """
    :return: Last used source directory for source documents prior to uploading.
    :rtype: str
    """
    source_doc_dir = default

    reg_config = RegistryConfig()
    doc_path_info = reg_config.read([LOCAL_SOURCE_DOC])

    if len(doc_path_info) > 0:
        doc_path_info = doc_path_info[LOCAL_SOURCE_DOC]

        if len(doc_path_info.strip()) > 0:
            source_doc_dir = doc_path_info

    return source_doc_dir

def set_source_document_location(doc_path):
    """
    Set the latest source directory of uploaded source documents.
    :param doc_path: Directory path or file path. The system will attempt to extract the directory path from the
    file name.
    """
    doc_dir_path = ""

    #Check if it is a file or directory
    doc_dir = QDir(doc_path)

    if not doc_dir.exists():
        doc_file_info = QFileInfo(doc_path)

        if doc_file_info.exists():
            doc_dir_path = doc_file_info.dir().path()

    else:
        doc_dir_path = doc_path

    if len(doc_dir_path) > 0:
        reg_config = RegistryConfig()
        reg_config.write({LOCAL_SOURCE_DOC:doc_dir_path})

def network_document_path():
    """
    Get the network resource location from the registry.
    """
    regConfig = RegistryConfig()
    networkResReg = regConfig.read([NETWORK_DOC_RESOURCE])

    if len(networkResReg) == 0:
        networkLocation = ""

    else:
        networkLocation = networkResReg[NETWORK_DOC_RESOURCE].strip()

    return networkLocation
        


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        