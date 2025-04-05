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
import logging
from collections import OrderedDict
from datetime import datetime

import sqlalchemy
from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QFile,
    QFileInfo,
    QDir,
    QObject,
    pyqtSignal,
    QEvent,
    QThread,
    QRect
)
from qgis.PyQt.QtGui import (
    QPixmap,
    QImage
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QWidget,
    QMessageBox,
    QLayout
)

from stdm.data.configuration import entity_model
from stdm.network.filemanager import (
    NetworkFileManager,
    DocumentTransferWorker
)
from stdm.settings import (
    current_profile
)
from stdm.settings.registryconfig import (
    RegistryConfig,
    NETWORK_DOC_RESOURCE,
    LOCAL_SOURCE_DOC,
    COMPOSER_OUTPUT
)
from stdm.ui.document_viewer import DocumentViewManager
from stdm.ui.gui_utils import GuiUtils
from stdm.utils.filesize import size
from stdm.utils.util import (
    entity_id_to_attr
)
from stdm.utils.util import getIndex

# Document Type Enumerations
DEFAULT_DOCUMENT = 2020
STATUTORY_REF_PAPER = 2021
SURVEYOR_REF = 2022
NOTARY_REF = 2023
TAX_RECEIPT_PRIVATE = 2024
TAX_RECEIPT_STATE = 2025

# Display text for document types
DOC_TYPE_MAPPING = {
    DEFAULT_DOCUMENT: str(QApplication.translate("sourceDocument",
                                                 "Supporting Document"))
}

# Display text for STR document types
STR_DOC_TYPE_MAPPING = {}
document_type_class = {}
# Mode for initializing the document widget
UPLOAD_MODE = 2100
DOWNLOAD_MODE = 2101
LOGGER = logging.getLogger('stdm')


class SourceDocumentManager(QObject):
    """
    Manages the display of source documents in vertical layout container(s).
    """
    # Signal raised when a document is removed from its container.
    documentRemoved = pyqtSignal(int, str, list)
    fileUploaded = pyqtSignal('PyQt_PyObject')

    def __init__(self, entity_document, document_model, parent=None):
        QObject.__init__(self, parent)
        self.containers = OrderedDict()
        self._canEdit = True

        self.document_model = document_model
        self.curr_profile = current_profile()

        self.entity_supporting_doc = entity_document.document_type_entity

        check_doc_type_model = entity_model(self.entity_supporting_doc)
        doc_type_obj = check_doc_type_model()
        doc_type_list = doc_type_obj.queryObject().all()
        self.doc_types = [(doc.id, doc.value) for doc in doc_type_list]
        self.doc_types = dict(self.doc_types)

        for id in self.doc_types.keys():
            document_type_class[id] = self.document_model

        # Container for document references based on their unique IDs
        self._docRefs = []

        # Set default manager for document viewing
        self._doc_view_manager = DocumentViewManager(self.parent_widget())

        self.doc_type_mapping = OrderedDict()

        for id, value in self.doc_types.items():
            self.doc_type_mapping[id] = value

    def reset(self):
        """
        Removes all ids and corresponding containers.
        """
        containers = self.containers
        self.containers.clear()
        del self._docRefs[:]
        return containers

    def clear(self):
        """
        Clears all document widgets from all containers.
        """
        for cont_id, container in self.containers.items():
            doc_widgets = container.parentWidget().findChildren(DocumentWidget)
            for doc_widget in doc_widgets:
                doc_widget.deleteLater()
                doc_widget = None

    def parent_widget(self):
        """
        :return: Instance of widget that is the parent container of this document manager.
        """
        parent_widg = self.parent()

        if isinstance(parent_widg, QWidget):
            return parent_widg

        return None

    def setEditPermissions(self, state):
        '''
        Sets whether the user can edit existing source document records.
        This applies for all containers managed by this class.
        '''
        self._canEdit = state

    def registerContainer(self, container: QLayout, id):
        '''
        Register a container for displaying the document widget
        '''
        if container is not None:
            self.containers[id] = container

    def removeContainer(self, containerid):
        """
        Removes the container with the specified ID from the
        document manager.
        """
        if containerid in self.containers:
            del self.containers[containerid]

    def container(self, containerid):
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
        return list(self.containers.keys())

    def insertDocumentFromFile(self, path: str, doc_type_id: int, entity, record_count=1, upload_mode=""):
        """
        Insert a new document into one of the registered containers with the
        document type id. This document is registered
        :param path: The local user path of the document
        :type path: String
        :param doc_type_id: The entity document type id
        :type doc_type_id: Integer
        :param entity: The entity in which the document is inserted into.
        :type entity: Entity class
        :param record_count: The number of records for which a
        document is uploaded. Default is 1. For instance, more
        records could be used in STR wizard in multi-party.
        :type record_count: Integer
        :return: None
        :rtype: NoneType
        """

        if len(self.containers) == 0:
            return

        if doc_type_id in self.containers:
            container = self.containers[doc_type_id]

            # Check if the file exists
            if QFile.exists(path):

                network_location = network_document_path()

                if not network_location:
                    self._doc_repository_error()
                    return

                # Check if the directory exists
                doc_dir = QDir(network_location)

                if not doc_dir.exists():
                    msg = QApplication.translate(
                        "sourceDocumentManager",
                        "The root document "
                        "repository '{0}' does "
                        "not exist.\nPlease "
                        "check the path settings."
                    )
                    parent = self.parent()
                    if not isinstance(parent, QWidget):
                        parent = None

                    QMessageBox.critical(
                        parent,
                        QApplication.translate(
                            "sourceDocumentManager",
                            "Document Manager"
                        ),
                        msg.format(network_location)
                    )
                    return


                for i in range(record_count):
                    # Use the default network file manager
                    networkManager = NetworkFileManager(
                        network_location, self.parent()
                    )

                    # Add document widget
                    docWidg = DocumentWidget(
                        self.document_model,
                        networkManager,
                        parent=self.parent(),
                        view_manager=self._doc_view_manager
                    )

                    # Connect slot once the document
                    # has been successfully uploaded.
                    docWidg.fileUploadComplete.connect(
                        lambda: self.onFileUploadComplete(doc_type_id)
                    )

                    self._linkWidgetRemovedSignal(docWidg)

                    doc_type_entity = entity.supporting_doc.document_type_entity
                    doc_type_value = entity_id_to_attr(
                        doc_type_entity, 'value', doc_type_id
                    )

                    docWidg.setFile(
                        path, entity.name, doc_type_value, doc_type_id, upload_mode=upload_mode
                    )

                    container.addWidget(docWidg)

    def onFileUploadComplete(self, documenttype):
        """
        Slot raised when a source file has been successfully
        uploaded into the central document repository.
        Raises a signal that passes the resulting source
        document from the upload operation.
        """
        docWidget = self.sender()
        if isinstance(docWidget, DocumentWidget):
            doc_source = docWidget.sourceDocument(documenttype)
            self.fileUploaded.emit(doc_source)
            self._docRefs.append(docWidget.fileUUID)

    def set_source_documents(self, source_docs):
        """
        :param source_docs: Supporting document objects
        to be inserted in their respective containers.
        :type source_docs: list
        """
        for source_doc in source_docs:
            if hasattr(source_doc, 'document_type'):
                document_type = source_doc.document_type
                self.insertDocFromModel(source_doc, document_type)

    def insertDocFromModel(self, sourcedoc, containerid):
        """
        Renders the source document info from a subclass of 'SupportingDocumentMixin'.
        """
        # Check if the document has already been inserted in the manager.
        docIndex = getIndex(self._docRefs, sourcedoc.document_identifier)
        if docIndex != -1:
            return

        if len(self.containers) > 0:
            if containerid in self.containers:
                container = self.containers[containerid]

                network_location = source_document_location('')

                if not network_location:
                    self._doc_repository_error()

                    return

                networkManager = NetworkFileManager(network_document_path())
                # Add document widget
                docWidg = DocumentWidget(
                    self.document_model,
                    networkManager,
                    mode=DOWNLOAD_MODE,
                    canRemove=self._canEdit,
                    view_manager=self._doc_view_manager
                )

                self._linkWidgetRemovedSignal(docWidg)
                docWidg.setModel(sourcedoc)
                container.addWidget(docWidg)

                self._docRefs.append(sourcedoc.document_identifier)

    def _doc_repository_error(self):
        msg = QApplication.translate(
            "sourceDocumentManager",
            "Document repository could not be found.\nPlease "
            "check the path settings."
        )
        QMessageBox.critical(None,
                             QApplication.translate("sourceDocumentManager",
                                                    "Document Manager"), msg)

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

    def attributeMapping(self, editing=False):
        """
        Returns the mapping of source document information for display of the summary
        documents contained in a stdm.navigation.TreeLoader object.
        """
        srcDocMapping = OrderedDict()

        for k, v in self.containers.items():

            if not v is None:
                docItems = OrderedDict()
                widgCount = v.count()

                for w in range(widgCount):
                    docWidg = v.itemAt(w).widget()
                    if editing:
                        srcFilePath = str(docWidg._displayName)
                        locTr = QApplication.translate(
                            "sourceDocumentManager", "File Name"
                        )
                    else:
                        srcFilePath = str(docWidg.fileInfo.absoluteFilePath())
                        locTr = QApplication.translate(
                            "sourceDocumentManager", "Location"
                        )
                    locTxt = "%s %s" % (locTr, str(w + 1))
                    docItems[locTxt] = srcFilePath

                docTypeText = "%s (%s)" % (self.doc_type_mapping[k], str(widgCount))
                srcDocMapping[docTypeText] = docItems

        return srcDocMapping

    def model_objects(self, dtype=None) -> list[QLayout]:
        """
        Returns all supporting document models based on
        the file uploads contained in the document manager.
        """
        all_doc_objs = []
        for doc_type_id, container in self.containers.items():
            doc_widget_count = container.count()
            # loop through all document
            # widgets and get their objects.
            for doc_widget in range(doc_widget_count):
                docWidg = container.itemAt(doc_widget).widget()
                source_doc = docWidg.sourceDocument(doc_type_id)
                all_doc_objs.append(source_doc)

        return all_doc_objs

    def clean_up(self):
        """
        Clears all unsaved files that had initially
        been uploaded in the corresponding containers.
        :return: Document widgets whose referenced
        files could not be deleted.
        :rtype: list
        """
        delete_error_docs = []

        for k, v in self.containers.items():
            layout_item = v.takeAt(0)

            while layout_item is not None:
                doc_widg = layout_item.widget()

                if not doc_widg.clean_up():
                    delete_error_docs.append(doc_widg)

                layout_item = v.takeAt(0)

        return delete_error_docs

    def onDocumentRemoved(self, containerid):
        """
        Slot raised when a document is removed from the container.
        Propagate signal.
        """
        remDocWidget = self.sender()

        doc_uuid = None
        if remDocWidget:
            self.container(containerid).removeWidget(remDocWidget)

            # Remove document reference in the list
            if remDocWidget.mode() == UPLOAD_MODE:
                doc_uuid = remDocWidget.fileUUID

            elif remDocWidget.mode() == DOWNLOAD_MODE:
                doc_uuid = remDocWidget.fileUUID

            if doc_uuid:
                # Remove corresponding viewer
                self._doc_view_manager.remove_viewer(doc_uuid)

                try:
                    self._docRefs.remove(doc_uuid)

                except ValueError:
                    pass
            remDocWidget.deleteLater()

        self.documentRemoved.emit(
            containerid,
            remDocWidget.fileUUID,
            remDocWidget.removed_doc
        )

    def eventFilter(self, watched, e):
        '''
        Intercept signals raised by the
        widgets managed by this container.
        For future implementations.
        '''
        pass

    def _addDocumentReference(self, docid):
        """
        Add a document reference to the
        list that the document manager
        contains
        """
        docIndex = getIndex(self._docRefs, docid)

        if docIndex == -1:
            self._docRefs.append(docid)

    def documentReferences(self):
        """
        Returns a list of document ids in the document manager.
        """
        return self._docRefs

    def _installEventFilter(self, widget):
        """
        Installs an event filter for the
        widget so that the class can now handle the
        events raised by widget.
        """
        widget.installEventFilter(self)

    def _linkWidgetRemovedSignal(self, widget):
        """
        Connects 'destroyed' signal raised
        when a widget is removed from the container.
        """
        widget.referencesRemoved.connect(self.onDocumentRemoved)


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_doc_item.ui'))


class DocumentWidget(WIDGET, BASE):
    """
    Widget for displaying source document details
    """
    # Reference removed signal is raised prior
    # to destroying the widget.
    referencesRemoved = pyqtSignal(int)
    fileUploadComplete = pyqtSignal()

    def __init__(
            self,
            document_model=None,
            fileManager=None,
            mode=UPLOAD_MODE,
            parent=None,
            canRemove=True,
            view_manager=None
    ):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.lblClose.setPixmap(GuiUtils.get_icon_pixmap('close.png'))

        self.initGui()
        self.fileInfo = None
        self.fileUUID = None
        self.document_model = document_model
        self.fileManager = fileManager
        self._mode = mode
        self._displayName = ""
        self._docSize = 0
        self._srcDoc = None
        self._fileName = ""
        self._canRemove = canRemove
        self._view_manager = view_manager

        self.curr_profile = current_profile()
        self.removed_doc = []
        self.lblClose.installEventFilter(self)
        self.lblName.installEventFilter(self)
        self._source_entity = ""
        self._doc_type = ""
        self._doc_type_id = None
        # Set defaults
        self.fileNameColor = "#5555ff"
        self.fileMetaColor = "#8f8f8f"

        self.workerThread = QThread(self) 
        self.docWorker = None

    def eventFilter(self, watched, e):
        """
        Capture label mouse release events
        for deleting and opening a source
        document respectively.
        """
        if QEvent is None:
            return False

        if watched == self.lblClose and e.type() == QEvent.MouseButtonRelease:
            self.removeDocument()
            return True

        elif watched == self.lblName and e.type() == QEvent.MouseButtonRelease:
            self.openDocument()
            return True

        else:
            return QWidget.eventFilter(self, watched, e)

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
        response = QMessageBox.warning(self.parent(),
                                       QApplication.translate("DocumentWidget", "Delete Source Document"),
                                       msgConfirm, QMessageBox.Yes | QMessageBox.No)

        if response == QMessageBox.No:
            return

        self._remove_doc()

    def clean_up(self):
        """
        Remove the referenced uploaded
        file which has not yet been saved.
        :return: True to indicate that the document was
        successfully removed or False if an error was encountered.
        :rtype: bool
        """
        if self._mode == UPLOAD_MODE:
            return self._remove_doc(True)

        return True

    def _remove_doc(self, suppress_messages=False):
        """
        :param suppress_messages: Set whether user messages
        should be displayed or the system should continue with
        execution.
        :type suppress_messages: bool
        :return: True to indicate that the document was
        successfully removed or False if an error was encountered.
        :rtype: bool
        """
        status = True
        if self._mode == UPLOAD_MODE:
            status = self.fileManager.deleteDocument()
        else:
            doc_type = self.doc_type_value()
            self.removed_doc.append(self._srcDoc)
            # Before anything, we check if file exist!
            if self.fileManager.file_exist(self._srcDoc, doc_type):
                status = self.fileManager.deleteDocument(self._srcDoc, doc_type)

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
            # Try to delete document and suppress error if it does not exist
            try:
                self._srcDoc.delete()
                # Remove the same document from supporting
                # doc table linked to other str record as the file doesn't exist.
                doc_obj = self.document_model()
                other_party_doc = doc_obj.queryObject().filter(
                    self.document_model.document_identifier ==
                    self._srcDoc.document_identifier
                ).all()

                for docs in other_party_doc:
                    self.removed_doc.append(docs)
                    docs.delete()

            except sqlalchemy.exc.SQLAlchemyError as exc:
                LOGGER.debug(str(exc))

        # Emit signal to indicate the widget is ready to be removed
        self.referencesRemoved.emit(self._doc_type_id)

        self.deleteLater()

        return True

    def openDocument(self):
        """
        Open the document referenced by this widget.
        """
        if not self._view_manager is None:
            self._view_manager.load_viewer(self)

    def setCanRemoveDocument(self, state):
        """
        Disable the close button so that users are not able to remove the
        document from the list.
        """
        self.lblClose.setVisible(state)

    def setFile(self, dfile, source_entity, doc_type, doc_type_id, upload_mode=""):
        """
        Set the absolute file path including the name, that is to be associated
        with the document widget.
        """
        if self._mode == UPLOAD_MODE:
            self.fileInfo = QFileInfo(dfile)
            self._displayName = str(self.fileInfo.fileName())
            self._docSize = self.fileInfo.size()
            self._source_entity = source_entity
            self._doc_type = doc_type
            self._doc_type_id = doc_type_id

            if upload_mode == "SERIAL":
                self.upload_doc_sequential()
            else:
                self.uploadDoc()
                self.buildDisplay()

    def setModel(self, sourcedoc):
        """
        Set the SourceDocument model that is to be associated with the widget.
        Only valid if the widget mode is in DOWNLOAD_MODE.
        """
        self.pgBar.setVisible(False)

        if self._mode == DOWNLOAD_MODE:
            self._displayName = sourcedoc.filename
            self._docSize = sourcedoc.document_size
            self.fileUUID = sourcedoc.document_identifier
            self._srcDoc = sourcedoc
            self._source_entity = sourcedoc.source_entity
            self._doc_type_id = sourcedoc.document_type
            self.buildDisplay()

    def doc_type_value(self):
        """
        Returns the document type value.
        :return: the document type value in
        which a document is uploaded.
        :type: String
        :rtype: String
        """
        entity = self.curr_profile.entity_by_name(self._source_entity)

        doc_type_entity = entity.supporting_doc.document_type_entity
        self._doc_type = entity_id_to_attr(
            doc_type_entity, 'value', self._doc_type_id
        )
        return self._doc_type

    def doc_source_entity(self):
        """
        Returns the document type (enumeration) that the widget currently references.
        """
        return self._source_entity

    def set_source_entity(self, source_entity):
        """
        Set the document type using its code. See enumeration options.
        """
        self._source_entity = source_entity

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

    def sourceDocument(self, doc_type_id):
        """
        Builds the database model for the source document file reference.
        """
        if self._mode == UPLOAD_MODE:
            entity_doc_obj = self.document_model()
            entity_doc_obj.document_identifier = self.fileUUID
            entity_doc_obj.filename = self.fileInfo.fileName()
            entity_doc_obj.document_size = self._docSize
            entity_doc_obj.creation_date = datetime.now()
            entity_doc_obj.source_entity = self._source_entity
            entity_doc_obj.document_type = doc_type_id
            self._srcDoc = entity_doc_obj

        return self._srcDoc

    def set_thumbnail(self):
        """
        Sets thumbnail to the document widget by
        cropping if necessary.
        :return: None
        :rtype: NoneType
        """
        extension = self._displayName[self._displayName.rfind('.'):]

        QApplication.processEvents()
        doc_path = '{}{}/{}/{}/{}{}'.format(
            source_document_location(),
            str(self.curr_profile.name),
            str(self._source_entity),
            str(self.doc_type_value()).replace(' ', '_'),
            str(self.fileUUID),
            str(extension)
        ).lower()

        ph_image = QImage(doc_path)
        ph_pixmap = QPixmap.fromImage(ph_image)
        # If width is larger than height, use height as width and height
        if ph_pixmap.width() > ph_pixmap.height():
            rectangle = QRect(0, 0, ph_pixmap.height(), ph_pixmap.height())
            ph_pixmap = ph_pixmap.copy(rectangle)
        # If height is larger than width, use width as width and height
        elif ph_pixmap.height() > ph_pixmap.width():
            rectangle = QRect(0, 0, ph_pixmap.width(), ph_pixmap.width())
            ph_pixmap = ph_pixmap.copy(rectangle)

        self.lblThumbnail.setPixmap(ph_pixmap)
        self.lblThumbnail.setScaledContents(True)

    def buildDisplay(self):
        """
        Build html text for displaying file information.
        """

        if not self._docSize is None:
            display_doc_size = str(size(self._docSize))
        else:
            display_doc_size = '0'

        html = '<html>' \
               '<head/>' \
               '<body>' \
               '<p>' \
               '<span ' \
               'style="font-weight:600;' \
               'text-decoration: underline;' \
               'color:#5555ff;"' \
               '>' \
               '{}</span>' \
               '<span ' \
               'style="font-weight:600;' \
               'color:#8f8f8f;"' \
               '>&nbsp;({})' \
               '</span>' \
               '</p>' \
               '</body>' \
               '</html>'.format(
            str(self._displayName),
            display_doc_size
        )
        self.lblName.setText(html)

        # Enable/disable close
        self.setCanRemoveDocument(self._canRemove)

        # Disable link if no view manager has been configured
        if self._view_manager is None:
            self.lblName.setEnabled(False)

        self.set_thumbnail()

    def print_thread(self):
        print('** Document transfer thread finished **')

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
            #self.workerThread = QThread(self)

            self.docWorker = DocumentTransferWorker(
                self.fileManager,
                self.fileInfo,
                "%s" % (self._source_entity),
                "%s" % (self._doc_type),
            )
            self.docWorker.moveToThread(self.workerThread)

            self.workerThread.started.connect(self.docWorker.transfer)

            self.docWorker.blockWrite.connect(self.onBlockWritten)
            self.docWorker.complete.connect(self.onCompleteTransfer)

            self.workerThread.finished.connect(self.docWorker.deleteLater)
            self.workerThread.finished.connect(self.workerThread.deleteLater)

            self.workerThread.start()
            # Call transfer() to get fileUUID early
            # self.docWorker.transfer()
            self.fileUUID = self.docWorker.file_uuid

    def upload_doc_sequential(self):
        """
        Upload the file to central repository on the SAME thread using specified file manager
        """
        if isinstance(self.fileManager, NetworkFileManager):
            self._docSize = self.fileInfo.size()

            self.docWorker = DocumentTransferWorker(
                self.fileManager,
                self.fileInfo,
                "%s" % (self._source_entity),
                "%s" % (self._doc_type)
            )

            self.docWorker.transfer_serial()
            self.fileUUID = self.docWorker.file_uuid


    def onBlockWritten(self, size):
        """
        Raised when a block of data is written to the central repository.
        Updates the progress bar with the bytes transferred as a percentage.
        """
        progress = (size * 100) / self._docSize

        self.pgBar.setValue(int(progress))
        #QgsApplication.processEvents()

    def onCompleteTransfer(self, fileid):
        """
        Slot raised when file has been successfully transferred.
        """
        self.pgBar.setVisible(False)
        self.fileUUID = str(fileid)
        self.fileUploadComplete.emit()

        if self.workerThread:
            if self.workerThread.isRunning():
                self.workerThread.quit()

def source_document_location(default="/home") ->str:
    """
    :return: Last used source directory for
    source documents prior to uploading.
    """
    source_doc_dir = default

    reg_config = RegistryConfig()
    doc_path_info = reg_config.read([LOCAL_SOURCE_DOC])

    if len(doc_path_info) > 0:
        doc_path_info = doc_path_info[LOCAL_SOURCE_DOC]

        if len(doc_path_info.strip()) > 0:
            source_doc_dir = doc_path_info

    return source_doc_dir

def output_document_location(default:str='/home'):
    """
    Returns the output document location
    """
    output_doc_dir = default

    reg_config = RegistryConfig()
    doc_path_info = reg_config.read([COMPOSER_OUTPUT])

    if len(doc_path_info) > 0:
        doc_path_info = doc_path_info[COMPOSER_OUTPUT]

        if len(doc_path_info.strip()) > 0:
            output_doc_dir = doc_path_info

    return output_doc_dir


def set_source_document_location(doc_path):
    """
    Set the latest source directory of uploaded source documents.
    :param doc_path: Directory path or file path. The system will
     attempt to extract the directory path from the file name.
    """
    doc_dir_path = ""
    # Check if it is a file or directory
    doc_dir = QDir(doc_path)

    if not doc_dir.exists():
        doc_file_info = QFileInfo(doc_path)

        if doc_file_info.exists():
            doc_dir_path = doc_file_info.dir().path()

    else:
        doc_dir_path = doc_path

    if len(doc_dir_path) > 0:
        reg_config = RegistryConfig()
        reg_config.write({LOCAL_SOURCE_DOC: doc_dir_path})

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
