"""
/***************************************************************************
Name                 : Workflow Manager Widget
Description          : Widget for managing workflow and notification in
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
Date                 : 24/December/2019
copyright            : (C) 2019
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PlotImportWidget(QWidget):
    """
    A widget to import and preview plots of a scheme.
    Called from the Import Plot module.
    """
    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)

        self.model = None

        self.add_button = QPushButton("Add file(s)...")
        self.remove_button = QPushButton("Remove file(s)")
        self.preview_button = QPushButton("Preview")
        self.import_button = QPushButton("Import")
        self.close_button = QPushButton("Close")

        test_editor = QTextEdit()

        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(self.add_button)
        toolbar_layout.addWidget(self.remove_button)
        toolbar_layout.addWidget(self.preview_button)
        toolbar_layout.addWidget(self.import_button)
        toolbar_layout.addStretch()

        parent.paginationFrame.hide()
        # pagination_layout = QHBoxLayout()
        # pagination_layout.addStretch()
        # pagination_layout.addWidget(self.import_button)
        # pagination_layout.addWidget(self.close_button)

        file_layout = QVBoxLayout()
        # file_layout.addWidget(test_editor)
        preview_layout = QVBoxLayout()
        # preview_layout.addWidget(test_editor)

        file_groupbox = QGroupBox("Added files")
        preview_groupbox = QGroupBox("Preview")
        file_groupbox.setLayout(file_layout)
        preview_groupbox.setLayout(preview_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(file_groupbox)
        splitter.addWidget(preview_groupbox)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        layout = QVBoxLayout()
        layout.addLayout(toolbar_layout)
        layout.addWidget(splitter)
        # layout.addLayout(pagination_layout)
        self.setLayout(layout)



