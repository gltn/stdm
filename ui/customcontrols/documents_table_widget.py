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
from PyQt4.QtGui import (
    QAbstractItemView,
    QLabel,
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

        # Insert action links
        lbl_browse = self.create_hyperlink_widget(self.tr('Browse'))
        lbl_view = self.create_hyperlink_widget(self.tr('View'))
        self.setCellWidget(row_count, 1, lbl_browse)
        self.setCellWidget(row_count, 3, lbl_view)

        # Insert status
        status_item = QTableWidgetItem('Not Uploaded')
        self.setItem(row_count, 2, status_item)

    def create_hyperlink_widget(self, name):
        """
        Creates a clickable QLabel widget that appears like a hyperlink.
        :param name: Display name of the hyperlink.
        :type name: str
        :return: Returns the QLabel widget with appearance of a hyperlink.
        :rtype: QLabel
        """
        lbl_link = QLabel()
        lbl_link.setObjectName('lbl_name')
        lbl_link.setText(u'<a href=\'placeholder\'>{0}</a>'.format(name))
        lbl_link.setTextInteractionFlags(Qt.TextBrowserInteraction)

        return lbl_link