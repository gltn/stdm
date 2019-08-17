"""
/***************************************************************************
Name                 : DocumentTableWidget
Description          : A table widget that provides a quick access menus for
                       uploading and viewing supporting documents.
Date                 : 16/July/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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
from cmislib.exceptions import (
    CmisException
)
from cmislib.domain import (
    Document
)
from PyQt4.QtGui import (
    QAbstractItemView,
    QColor,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QIcon,
    QLabel,
    QListView,
    QMessageBox,
    QProgressBar,
    QStandardItem,
    QStandardItemModel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout
)
from PyQt4.QtCore import (
    pyqtSignal,
    Qt,
    QDir,
    QThread
)
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.network.cmis_manager import (
    CmisDocumentMapperException
)
from stdm.ui.notification import (
    NotificationBar
)


class DocumentRowInfo(object):
    """
    Container for document type information in the table widget.
    """
    def __init__(self):
        self.document_type = ''
        self.row_num = -1
        self.source_filename = ''
        self.target_path = ''
        self.uuid = ''
        self.upload_status = DocumentTableWidget.NOT_UPLOADED
        self.document_type_id = -1
        self.doc_obj = None


class DocumentTableWidget(QTableWidget):
    """
    A table widget that provides a quick access menus for uploading and
    viewing supporting documents.
    """
    # Signals raised when specific user actions are carried out
    browsed = pyqtSignal(object)
    view_requested= pyqtSignal(object)
    remove_requested = pyqtSignal(object)

    # Upload state
    NOT_UPLOADED, UPLOADED, SUCCESS, ERROR = range(4)

    def __init__(self, parent=None, doc_info_cls=None):
        super(DocumentTableWidget, self).__init__(parent)

        # A custom document information container, sub-classed from
        # DocumentRowInfo can be specified.
        self._doc_info_cls = doc_info_cls
        if not self._doc_info_cls:
            self._doc_info_cls = DocumentRowInfo

        # Validate doc_info_cls is a sub-class of DocumentRowInfo
        if not issubclass(self._doc_info_cls, DocumentRowInfo):
            raise TypeError(
                self.tr(
                    'Container for document information should be a subclass '
                    'of <DocumentRowInfo>'
                )
            )

        self._docs_info = OrderedDict()
        # Container for uploaded documents based on type
        self._doc_types_upload = OrderedDict()
        self._doc_prop = 'doc_info'
        self._not_uploaded_txt = self.tr('Not uploaded')
        self._success_txt = self.tr('Uploaded')
        self._error_txt = self.tr('Error!')
        self.cmis_entity_doc_mapper = None
        self.file_filters = 'PDF File (*.pdf)'
        self._init_ui()

    def _init_ui(self):
        # Set up the basic columns
        self.setRowCount(0)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            self.tr('Document Type'),
            self.tr('Action'),
            self.tr('Status'),
            self.tr('Action'),
            self.tr('Action')
        ])
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().resizeSection(0, 250)

        # Make 'Document Type' to be bold
        doc_type_item = self.horizontalHeaderItem(0)
        dt_font = doc_type_item.font()
        dt_font.setBold(True)
        #doc_type_item.setFont(dt_font)

    @property
    def document_information(self):
        """
        :return: Returns a collection containing document information stored
        in the widget.
        :rtype: OrderedDict
        """
        return self._docs_info

    @property
    def uploaded_documents(self):
        """
        :return: Returns a collection containing the uploaded Document
        object (or None) indexed by the document type.
        :rtype: dict
        """
        s_docs = {}
        uploaded_docs = self.cmis_entity_doc_mapper.uploaded_documents
        for dt, docs in uploaded_docs.iteritems():
            doc = docs[0] if len(docs) > 0 else None
            s_docs[dt] = doc

        return s_docs

    def uploaded_document_by_type(self, doc_type):
        """
        Gets the uploaded documents based on the document type.
        :param doc_type: Name of the document type.
        :type doc_type: str
        :return: Returns the uploaded document based on the
        document type or None if no document has been uploaded for the given
        type or if the document type does not exist in the collection of
        uploaded documents.
        :rtype: cmislib.domain.Document
        """
        return self.uploaded_documents.get(doc_type, None)

    def row_document_information(self, idx):
        """
        Gets the DocumentRowInfo for the row with the given index.
        :param idx: The row number containing the document type.
        :type idx: int
        :return: Returns the DocumentRowInfo for the given row index, else
        None if not found.
        :rtype: DocumentRowInfo
        """
        return self._docs_info.get(idx, None)

    def row_document_info_from_type(self, doc_type):
        """
        Get the DocumentRowInfo for the row representing the given document
        type.
        :param doc_type: Document type
        :type doc_type: str
        :return: Returns the DocumentRowInfo for the given row index, else
        None if not found.
        :rtype: DocumentRowInfo
        """
        return next(
            (
                di for di in self._docs_info.values()
                if di.document_type == doc_type
            ),
            None
        )

    def add_document_type(self, name):
        """
        Add a new document type to the collection.
        :param name: Name of the document type.
        :type name: str.
        """
        if not name:
            return

        # Insert document type
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)
        doc_item = QTableWidgetItem(name)
        self.setItem(row_count, 0, doc_item)

        # Create object for storing the document info in the label
        doc_info = self._doc_info_cls()
        doc_info.row_num = row_count
        doc_info.document_type = name

        # Add document info to the collection
        self._docs_info[row_count] = doc_info

        # Specify action links
        lbl_browse = self.create_hyperlink_widget(self.tr('Browse'), doc_info)
        lbl_browse.linkActivated.connect(self.on_browse_activate)
        lbl_view = self.create_hyperlink_widget(self.tr('View'), doc_info)
        lbl_view.linkActivated.connect(self.on_view_activated)
        lbl_remove = self.create_hyperlink_widget(self.tr('Remove'), doc_info)
        lbl_remove.linkActivated.connect(self.on_remove_activated)

        # Insert action links
        self.setCellWidget(row_count, 1, lbl_browse)
        self.setCellWidget(row_count, 3, lbl_view)
        self.setCellWidget(row_count, 4, lbl_remove)

        # Insert status
        status_item = QTableWidgetItem(self._not_uploaded_txt)
        self.setItem(row_count, 2, status_item)

        # Update collections with empty list
        self._doc_types_upload[name] = []

    def document_types(self):
        """
        :return: Returns a list containing the names of the document types.
        :rtype: list
        """
        return self._doc_types_upload.keys()

    def create_hyperlink_widget(self, name, document_info):
        """
        Creates a clickable QLabel widget that appears like a hyperlink.
        :param name: Display name of the hyperlink.
        :type name: str
        :param document_info: Container for document information that is
        embedded as a property in the label.
        :type document_info: DocumentRowInfo
        :return: Returns the QLabel widget with appearance of a hyperlink.
        :rtype: QLabel
        """
        lbl_link = QLabel()
        lbl_link.setAlignment(Qt.AlignHCenter)
        lbl_link.setText(u'<a href=\'placeholder\'>{0}</a>'.format(name))
        lbl_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        lbl_link.setProperty(self._doc_prop, document_info)

        return lbl_link

    def on_browse_activate(self, link):
        """
        Slot raised when the Browse link has been clicked. Open the
        dialog for browsing files then raises the 'browsed' signal.
        :param link: Hyperlink stored in the link property, which is
        not applied in this case.
        :type link: str
        """
        sender = self.sender()
        if not self._is_sender_valid(sender):
            return

        doc_info = sender.property(self._doc_prop)

        # Clear error hints
        row_idx = doc_info.row_num
        self.clear_error_success_hints(row_idx)

        last_doc_path = last_document_path()
        if not last_doc_path:
            last_doc_path = '~/'

        doc_file_path = QFileDialog.getOpenFileName(
            self,
            u'Browse {0}'.format(doc_info.document_type),
            last_doc_path,
            self.file_filters
        )
        if doc_file_path:
            # Update registry setting
            set_last_document_path(doc_file_path)

            # Update the source file name
            doc_info.source_filename = doc_file_path

            # Upload document content
            self.upload_document(doc_file_path, doc_info.document_type)

        # Emit signal
        self.browsed.emit(doc_info)

    def upload_document(self, doc_file_path, doc_type):
        """
        Upload the document in doc_file_path to the document repository. The
        entity document mapper should have been set as it handles the
        communication to the CMIS server.
        :param doc_file_path: Path to the document to be uploaded.
        :type doc_file_path: str
        :param doc_type: Type of the document.
        :type doc_type: str
        """
        if self.cmis_entity_doc_mapper:
            # Remove previously uploaded document, if any
            self.remove_document_by_doc_type(doc_type)

            # Upload the new one
            upload_thread = CmisDocumentUploadThread(
                doc_file_path,
                self.cmis_entity_doc_mapper,
                doc_type,
                self
            )
            # Connect signals
            upload_thread.error.connect(
                self.on_upload_error
            )
            upload_thread.succeeded.connect(
                self.on_successful_upload
            )

            # Disable widgets and show upload progress bar
            self._before_upload(doc_type)

            upload_thread.start()

    def _before_upload(self, doc_type):
        """
        Activated just before an upload. It disables user actions and shows
        a progress bar.
        """
        doc_info = self.row_document_info_from_type(doc_type)
        if not doc_info:
            return

        row_num = doc_info.row_num

        # Disable user actions in the given row
        self._enable_user_action_widgets(
            row_num,
            False
        )

        # Show progress bar
        pg_bar = QProgressBar()
        pg_bar.setRange(0, 0)
        pg_bar.setTextVisible(False)
        # Remove text before showing progress bar
        ti = self.item(row_num, 2)
        ti.setText('')
        self.setCellWidget(row_num, 2, pg_bar)

    def _after_upload(self, doc_type, status, extras=None):
        doc_info = self.row_document_info_from_type(doc_type)
        if not doc_info:
            return

        row_num = doc_info.row_num
        # Remove progress bar
        self.removeCellWidget(row_num, 2)

        # Insert status text and set cell styling
        # Not uploaded
        ti = self.item(row_num, 2)
        if status == DocumentTableWidget.NOT_UPLOADED:
            ti.setText(self._not_uploaded_txt)
            ti.setBackgroundColor(Qt.white)
            ti.setTextColor(Qt.black)
            doc_info.upload_status = DocumentTableWidget.NOT_UPLOADED
            doc_info.uuid = ''
            # Remove any error or success styling cues
            self.clear_error_success_hints(row_num)

        # Successfully uploaded
        elif status == DocumentTableWidget.SUCCESS:
            ti.setText(self._success_txt)
            ti.setTextColor(Qt.white)
            ti.setBackgroundColor(QColor('#00b300'))
            doc_info.upload_status = DocumentTableWidget.SUCCESS
            # Set the document uuid
            if extras:
                doc_info.uuid = extras

        # Error while uploading
        elif status == DocumentTableWidget.ERROR:
            ti.setText(self._error_txt)
            ti.setTextColor(Qt.white)
            ti.setBackgroundColor(Qt.red)
            doc_info.upload_status = DocumentTableWidget.ERROR

        # Enable user actions, hide progress bar and set status message
        self._enable_user_action_widgets(row_num)

    def _enable_user_action_widgets(self, row_num, enable=True):
        # Enable/disable Browse, View, Remove widgets in a tuple
        lbl_browse = self.cellWidget(row_num, 1)
        lbl_view = self.cellWidget(row_num, 3)
        lbl_remove = self.cellWidget(row_num, 4)

        lbl_browse.setEnabled(enable)
        lbl_view.setEnabled(enable)
        lbl_remove.setEnabled(enable)

    def on_view_activated(self, link):
        """
        Slot raised when the View link has been clicked. Raises the
        'view_requested' signal and passes the DocumentRowInfo object.
        :param link: Hyperlink stored in the link property, which is
        not applied in this case.
        :type link: str
        """
        sender = self.sender()
        if not self._is_sender_valid(sender):
            return

        doc_info = sender.property(self._doc_prop)

        # Get status of the upload
        status = doc_info.upload_status
        if status == DocumentTableWidget.ERROR:
            msg = self.tr(
                'The document cannot be viewed as there was an error while '
                'uploading it.'
            )
            QMessageBox.critical(
                self,
                self.tr('Error in Viewing Document'),
                msg
            )
        elif status == DocumentTableWidget.NOT_UPLOADED:
            msg = self.tr(
                'Please upload a document for viewing.'
            )
            QMessageBox.warning(
                self,
                self.tr('Upload Document'),
                msg
            )
        elif status == DocumentTableWidget.SUCCESS:
            # Load document viewer
            pass

        # Emit signal
        self.view_requested.emit(doc_info)

    def on_upload_error(self, error_info):
        """
        Slot raised when there is an error when uploading a document.
        :param error_info: Tuple containing the document type and
        corresponding error message.
        :type error_info: tuple(doc_type, error_msg)
        """
        self.show_document_type_error(error_info[0], error_info[1])

    def on_successful_upload(self, res_info):
        """
        Slot raised by the upload thread when a document has been
        successfully uploaded to the repository. The UUID is set in the
        DocumentRowInfo object.
        :param res_info: Tuple containing the document type and cmislib
        document object.
        :type res_info: tuple(doc_type, document object)
        """
        doc_type = res_info[0]
        doc_obj= res_info[1]

        row_info = self.row_document_info_from_type(doc_type)
        if not row_info:
            return

        ti = self.item(row_info.row_num, 0)
        if not ti:
            return

        # Set success icon
        ti.setIcon(
            QIcon(':/plugins/stdm/images/icons/success.png')
        )

        cmis_props = doc_obj.getProperties()
        doc_uuid = cmis_props['cmis:versionSeriesId']
        self._after_upload(doc_type, DocumentTableWidget.SUCCESS, doc_uuid)

    def show_document_type_error(self, doc_type, op_error):
        """
        Shows an error icon next to the document type text in the table cell.
        :param doc_type: Type of document for which to show the error.
        :type doc_type: str
        :param op_error: Description of the error which will be shown as a
        tooltip.
        :type op_error: str
        """
        # Try to get DocumentInfo object from document type
        row_info = self.row_document_info_from_type(doc_type)
        if not row_info:
            return

        ti = self.item(row_info.row_num, 0)
        if not ti:
            return

        # Set error icon
        ti.setIcon(
            QIcon(':/plugins/stdm/images/icons/warning.png')
        )
        # Set tooltip
        ti.setToolTip(op_error)

        # Update status column
        self._after_upload(doc_type, DocumentTableWidget.ERROR, op_error)

    def clear_error_success_hints(self, row_idx):
        # Clears the error icon and tooltip for the row in the given index.
        ti = self.item(row_idx, 0)
        if not ti:
            return

        # Clear hints if any
        ti.setIcon(QIcon())
        ti.setToolTip('')

    def remove_document_by_doc_type(self, doc_type):
        """
        Remove document based on the given document type.
        :param doc_type: Document type
        :type doc_type: str
        """
        row_info = self.row_document_info_from_type(doc_type)
        if not row_info:
            return

        self.remove_document_by_doc_info(row_info)

    def remove_document_by_doc_info(self, doc_info):
        """
        Removes a document based on the given document info.
        :param doc_info: Container with document row information.
        :type doc_info: DocumentRowInfo
        """
        if doc_info.upload_status != DocumentTableWidget.SUCCESS:
            return

        # Remove document using separate thread
        uuid = doc_info.uuid
        doc_type = doc_info.document_type
        delete_thread = CmisDocumentDeleteThread(
            self.cmis_entity_doc_mapper,
            doc_type,
            uuid,
            self
        )

        # connect signals
        delete_thread.succeeded.connect(
            self._on_remove_document_succeeded
        )
        delete_thread.error.connect(
            self._on_remove_document_error
        )
        delete_thread.start()

    def on_remove_activated(self, link):
        """
        Slot raised when the Remove link has been clicked. Raises the
        'remove_requested' signal and passes the DocumentRowInfo object.
        :param link: Hyperlink stored in the link property, which is
        not applied in this case.
        :type link: str
        """
        sender = self.sender()
        if not self._is_sender_valid(sender):
            return

        doc_info = sender.property(self._doc_prop)

        status = doc_info.upload_status
        row_num = doc_info.row_num
        if status == DocumentTableWidget.ERROR:
            msg = self.tr(
                'The document cannot be removed as there was an error while '
                'uploading it.'
            )
            QMessageBox.critical(
                self,
                self.tr('Error in Removing Document'),
                msg
            )
        elif status == DocumentTableWidget.NOT_UPLOADED:
            msg = self.tr(
                'No document was uploaded.'
            )
            QMessageBox.warning(
                self,
                self.tr('Remove Document'),
                msg
            )
        elif status == DocumentTableWidget.SUCCESS:
            # Disable user actions in the given row
            self._enable_user_action_widgets(
                row_num,
                False
            )

            # Remove document
            self.remove_document_by_doc_info(doc_info)

        # Emit signal
        self.remove_requested.emit(doc_info)

    def _on_remove_document_succeeded(self, status_info):
        # Slot raised after the document deletion thread has finished.
        doc_type, status = status_info
        if not status:
            msg = u'{0} could not be removed.'.format(
                doc_type
            )
            QMessageBox.warning(
                self,
                self.tr('Remove Document'),
                msg
            )

            return

        # Reset document type status
        self._after_upload(doc_type, DocumentTableWidget.NOT_UPLOADED)

    def _on_remove_document_error(self, error_info):
        # Slot raised when an error occured when document deletion failed.
        doc_type, error_msg = error_info

        QMessageBox.critical(
            self,
            self.tr('Remove Document Error'),
            error_msg
        )

        # Enable user actions
        doc_info = self.row_document_info_from_type(doc_type)
        if not doc_info:
            return

        row_num = doc_info.row_num
        self._enable_user_action_widgets(row_num)

    def _is_sender_valid(self, sender):
        # Assert if the sender of the signal can be extracted
        if not sender:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr(
                    'Error in identifying the source of the click action'
                )
            )
            return False

        return True


class CmisDocumentUploadThread(QThread):
    """
    Handles the the upload of a document using a separate thread.
    """
    error = pyqtSignal(tuple) # (doc_type, error_msg)
    succeeded = pyqtSignal(tuple) # (doc_type, Document)

    def __init__(self, path, cmis_doc_mapper, doc_type, parent=None):
        super(CmisDocumentUploadThread, self).__init__(parent)
        self._doc_mapper = cmis_doc_mapper
        self._file_path = path
        self._doc_type = doc_type

    def run(self):
        # Upload the document content through the doc mapper
        try:
            doc = self._doc_mapper.upload_document(
                self._file_path,
                self._doc_type
            )
            self.succeeded.emit((self._doc_type, doc))
        except CmisDocumentMapperException as cdmex:
            self.error.emit((self._doc_type, str(cdmex)))
        except CmisException as cex:
            self.error.emit((self._doc_type, cex.status))
        except Exception as ex:
            self.error.emit((self._doc_type, str(ex)))


class CmisDocumentDeleteThread(QThread):
    """
    Handles deletion of a document from the CMIS repository.
    """
    succeeded = pyqtSignal(tuple) # (doc_type, delete_status)
    error = pyqtSignal(tuple) # (doc_type, error_msg)

    def __init__(self, cmis_doc_mapper, doc_type, doc_uuid, parent=None):
        super(CmisDocumentDeleteThread, self).__init__(parent)
        self._doc_mapper = cmis_doc_mapper
        self._doc_type = doc_type
        self._doc_uuid = doc_uuid

    def run(self):
        # Delete the document.
        try:
            status = self._doc_mapper.remove_document(
                self._doc_type,
                self._doc_uuid
            )
            self.succeeded.emit((self._doc_type, status))
        except CmisException as cex:
            self.error.emit((self._doc_type, cex.status))
        except Exception as ex:
            self.error.emit((self._doc_type, str(ex)))


class DirDocumentTypeSelector(QDialog):
    """
    Dialog for selecting supporting documents from a given directory. Default
    filter searches for PDF files only.
    """
    def __init__(self, dir, doc_types, parent=None, filters=None):
        super(DirDocumentTypeSelector, self).__init__(parent)
        self.setWindowTitle(
            self.tr('Documents in Folder')
        )
        self._filters = filters
        # Use PDF as default filter
        if not self._filters:
            self._filters = ['*.pdf']

        self._init_ui()
        self._dir = QDir(dir)
        self._dir.setNameFilters(self._filters)
        self._doc_types = doc_types

        self._attr_model = QStandardItemModel(self)
        self._sel_doc_types = OrderedDict()

        # Notification bar
        self._notif_bar = NotificationBar(self.vl_notif)

        self.resize(320, 350)

        # Load documents
        self.load_document_types()

    @property
    def selected_document_types(self):
        """
        :return: Returns a dictionary of the document types and the
        corresponding file paths as selected by the user.
        :rtype: dict
        """
        return self._sel_doc_types

    def _init_ui(self):
        # Draw UI widgets
        layout = QVBoxLayout()
        # Add layout for notification bar
        self.vl_notif = QVBoxLayout()
        layout.addLayout(self.vl_notif)
        self.lbl_info = QLabel()
        self.lbl_info.setObjectName('lbl_info')
        self.lbl_info.setText(self.tr(
            'The selected document types have been found in the directory, '
            'check/uncheck to specify which ones to upload.'
        ))
        self.lbl_info.setWordWrap(True)
        layout.addWidget(self.lbl_info)
        self.lst_docs = QListView()
        layout.addWidget(self.lst_docs)
        self.lbl_warning = QLabel()
        self.lbl_warning.setTextFormat(Qt.RichText)
        self.lbl_warning.setText(self.tr(
            '<html><head/><body><p><span style=" font-style:italic;">'
            '* Previously uploaded documents will be replaced.</span></p>'
            '</body></html>'
        ))
        self.lbl_warning.setWordWrap(True)
        layout.addWidget(self.lbl_warning)
        self.btn_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        layout.addWidget(self.btn_box)
        self.setLayout(layout)

        # Connect signals
        self.btn_box.accepted.connect(
            self.set_selected_document_types
        )
        self.btn_box.rejected.connect(
            self.reject
        )

    def set_selected_document_types(self):
        """
        Sets the collections of accepted document types and their
        corresponding file paths and accepts the dialog.
        """
        self._sel_doc_types = OrderedDict()
        for i in range(self._attr_model.rowCount()):
            doc_type_item = self._attr_model.item(i, 0)

            if doc_type_item.checkState() == Qt.Checked:
                path_item = self._attr_model.item(i, 1)
                self._sel_doc_types[doc_type_item.text()] = path_item.text()

        if len(self._sel_doc_types) == 0:
            self._notif_bar.clear()
            msg = self.tr('No matching documents found or selected.')
            self._notif_bar.insertWarningNotification(msg)

            return

        self.accept()

    def load_document_types(self):
        """
        Load all document types to the list view and enable/check the items
        for those types that have been found.
        """
        self._attr_model.clear()
        self._attr_model.setColumnCount(2)

        file_infos = self._dir.entryInfoList(
            QDir.Readable | QDir.Files,
            QDir.Name
        )

        # Index file info based on name
        idx_file_infos = {fi.completeBaseName().lower(): fi for fi in file_infos}

        for d in self._doc_types:
            doc_type_item = QStandardItem(d)
            doc_type_item.setCheckable(True)
            path_item = QStandardItem()

            item_enabled = False
            check_state = Qt.Unchecked
            dl = d.lower()
            if dl in idx_file_infos:
                item_enabled = True
                check_state = Qt.Checked
                path = idx_file_infos[dl].filePath()
                path_item.setText(path)
                doc_type_item.setToolTip(path)

            doc_type_item.setEnabled(item_enabled)
            doc_type_item.setCheckState(check_state)

            self._attr_model.appendRow([doc_type_item, path_item])

        self.lst_docs.setModel(self._attr_model)

