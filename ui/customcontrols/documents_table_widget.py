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
from PyQt4.QtGui import (
    QAbstractItemView,
    QFileDialog,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem
)
from PyQt4.QtCore import (
    pyqtSignal,
    Qt
)
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
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
        self.uploaded = False
        self.document_type_id = -1


class DocumentTableWidget(QTableWidget):
    """
    A table widget that provides a quick access menus for uploading and
    viewing supporting documents.
    """
    # Signals raised when specific user actions are carried out
    browsed = pyqtSignal(object)
    view_requested= pyqtSignal(object)
    remove_requested = pyqtSignal(object)

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
        self._doc_prop = 'doc_info'
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
        status_item = QTableWidgetItem('Not Uploaded')
        self.setItem(row_count, 2, status_item)

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

        last_doc_path = last_document_path()
        if not last_doc_path:
            last_doc_path = '~/'
        doc_file_path = QFileDialog.getOpenFileName(
            self,
            u'Browse {0} file'.format(doc_info.document_type),
            last_doc_path,
            'PDF File (*.pdf)'
        )
        if doc_file_path:
            # Update the source file name
            doc_info.source_filename = doc_file_path

            # Update registry setting
            set_last_document_path(doc_file_path)

        # Emit signal
        self.browsed.emit(doc_info)

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

        # Emit signal
        self.view_requested.emit(doc_info)

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

        # Emit signal
        self.remove_requested.emit(doc_info)

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