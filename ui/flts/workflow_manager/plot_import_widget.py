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
from qgis.gui import QgsGenericProjectionSelector
from stdm.ui.flts.workflow_manager.config import (
    SchemeMessageBox,
    StyleSheet,
    TabIcons,
)
from stdm.ui.flts.workflow_manager.plot import(
    PlotFile,
)
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.components.plot_import_component import PlotImportComponent


class PlotImportWidget(QWidget):
    """
    A widget to import and preview plots of a scheme.
    Called from the Import Plot module.
    """
    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)
        file_service = widget_properties["data_service"][0]
        file_service = file_service()
        self._plot_file = PlotFile(file_service)
        import_component = PlotImportComponent()
        toolbar = import_component.components
        self._add_button = toolbar["addFiles"]
        self._remove_button = toolbar["removeFiles"]
        self._preview_button = toolbar["Preview"]
        self._import_button = toolbar["Import"]
        header_style = StyleSheet().header_style
        self._file_table_view = QTableView(self)
        self.model = WorkflowManagerModel(file_service)
        self._file_table_view.setModel(self.model)
        self._file_table_view.setShowGrid(False)
        style = 'QHeaderView::section{color: #2F4F4F;}'
        self._file_table_view.horizontalHeader().setStyleSheet(style)
        self._file_table_view.setSelectionBehavior(QTableView.SelectRows)
        self._file_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self._preview_table_view = QTableView(self)
        self._preview_table_view.setShowGrid(False)
        self._preview_table_view.horizontalHeader().setStyleSheet(header_style)
        self._preview_table_view.setSelectionBehavior(QTableView.SelectRows)
        self._preview_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self._file_table_view)
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self._preview_table_view)
        file_groupbox = QGroupBox("Added files")
        preview_groupbox = QGroupBox("File content")
        file_groupbox.setLayout(file_layout)
        preview_groupbox.setLayout(preview_layout)
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
        self._add_button.clicked.connect(self._add_file)

    def _add_file(self):
        """
        Adds plot import file data properties into the file table view
        """
        test_folder = "D:/Projects/STDM/Namibia/FLTS/Sample_Inputs/WKT"
        path = QFileInfo(self._plot_file.file_path).path() \
            if self._plot_file.file_path else test_folder
        extensions = " ".join(self._plot_file.file_extensions())
        fpath = QFileDialog.getOpenFileName(
            self,
            "Workflow Manager - Plot Import Data Files",
            path,
            "Plot Import files {}".format(extensions)
        )
        if fpath and fpath not in self._plot_file.file_paths():
            self._plot_file.set_file_path(fpath)
            if not self.model.results:
                try:
                    self.model.load(self._plot_file)
                    self.model.refresh()
                except(IOError, OSError) as e:
                    QMessageBox.critical(
                        self,
                        self.tr("Plot Import Data Files"),
                        self.tr("Failed to load: {}".format(e))
                    )
            else:
                self._insert_file()
            self._file_table_view.horizontalHeader(). \
                setResizeMode(QHeaderView.ResizeToContents)
            self._file_table_view.resizeRowsToContents()
            self._file_table_view.horizontalHeader(). \
                setStretchLastSection(True)

    def _insert_file(self):
        """
        Inserts plot import file data properties into the table view
        """
        position = self.model.rowCount()
        self.model.insertRows(position)

    def _add_crs(self):
        """
        Add docstring
        :return:
        """
        proj_selector = QgsGenericProjectionSelector()
        proj_selector.exec_()
        auth_id = proj_selector.selectedAuthId()
        # Call model to edit and show in CRS field of selected file
