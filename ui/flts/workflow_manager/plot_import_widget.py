"""
/***************************************************************************
Name                 : Plot Import Widget
Description          : Widget for managing importing of a scheme plot.
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
from stdm.ui.flts.workflow_manager.config import (
    SchemeMessageBox,
    StyleSheet,
    TabIcons,
)
from stdm.ui.flts.workflow_manager.components.plot_import_component import PlotImportComponent


class PlotImportWidget(QWidget):
    """
    A widget to import and preview plots of a scheme.
    Called from the Import Plot module.
    """
    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)

        self.model = None

        import_component = PlotImportComponent()
        toolbar = import_component.components
        self._add_button = toolbar["addFiles"]
        self._remove_button = toolbar["removeFiles"]
        self._details_button = toolbar["viewContent"]
        self._import_button = toolbar["Import"]

        header_style = StyleSheet().header_style
        self._file_table_view = QTableView()
        self._file_table_view.setShowGrid(False)
        self._file_table_view.horizontalHeader().setStyleSheet(header_style)
        self._file_table_view.setSelectionBehavior(QTableView.SelectRows)
        self._file_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._detail_table_view = QTableView()
        self._detail_table_view.setShowGrid(False)
        self._detail_table_view.horizontalHeader().setStyleSheet(header_style)
        self._detail_table_view.setSelectionBehavior(QTableView.SelectRows)
        self._detail_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self._file_table_view)
        detail_layout = QVBoxLayout()
        detail_layout.addWidget(self._detail_table_view)
        file_groupbox = QGroupBox("Added files")
        preview_groupbox = QGroupBox("File content")
        file_groupbox.setLayout(file_layout)
        preview_groupbox.setLayout(detail_layout)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(file_groupbox)
        splitter.addWidget(preview_groupbox)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        layout = QVBoxLayout()
        layout.addLayout(import_component.layout)
        layout.addWidget(splitter)
        self.setLayout(layout)
        parent.paginationFrame.hide()



