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
    Qt
)


class DocumentTableWidget(QTableWidget):
    """
    A table widget that provides a quick access menus for uploading and
    viewing supporting documents.
    """
    def __init__(self, parent=None):
        super(DocumentTableWidget, self).__init__(parent)
        self._docs_info = OrderedDict()
        self._doc_prop = 'doc_info'
        self._init_ui()

    def _init_ui(self):
        # Set up the basic columns
        self.setRowCount(0)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            self.tr('Document Type'),
            self.tr('Action'),
            self.tr('Status'),
            self.tr('Action')
        ])
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().resizeSection(0, 300)

        # Make 'Document Type' to be bold
        doc_type_item = self.horizontalHeaderItem(0)
        dt_font = doc_type_item.font()
        dt_font.setBold(True)
        #doc_type_item.setFont(dt_font)

    def add_document_type(self, name):
        # Insert document type
        row_count = self.rowCount()
        self.setRowCount(row_count + 1)
        doc_item = QTableWidgetItem(name)
        self.setItem(row_count, 0, doc_item)

        # Create object for storing the document info in the label
        doc_info = DocumentRowInfo()
        doc_info.row_num = row_count
        doc_info.document_type = name

        # Add it to the collection
        self._docs_info[row_count] = doc_info

        # Insert action links
        lbl_browse = self.create_hyperlink_widget(self.tr('Browse'), doc_info)
        lbl_browse.linkActivated.connect(self.on_browse_activate)
        lbl_view = self.create_hyperlink_widget(self.tr('View'), doc_info)
        self.setCellWidget(row_count, 1, lbl_browse)
        self.setCellWidget(row_count, 3, lbl_view)

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
        dialog for browsing files.
        :param link: Hyperlink stored in the link property.
        :type link: str
        """
        sender = self.sender()
        if not sender:
            QMessageBox.critical(
                self,
                self.tr('Error'),
                self.tr(
                    'Error in identifying the source of the click action'
                )
            )
            return

        doc_info = sender.property(self._doc_prop)
        doc_file_path = QFileDialog.getOpenFileName(
            self,
            u'Browse {0} file'.format(doc_info.document_type),
            '~/',
            'PDF File (*.pdf)'
        )
        if doc_file_path:
            # Update the source file name
            doc_info.source_filename = doc_file_path

            # Update Status
            status_item = self.item(doc_info.row_num, 2)
            status_item.setText('Uploaded')


class DocumentRowInfo(object):
    """
    Container for document type information in the table widget.
    """
    def __init__(self):
        self.document_type = ''
        self.row_num = -1
        self.source_filename = ''
        self.uuid = ''
        self.uploaded = False