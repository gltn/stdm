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
from stdm.ui.flts.workflow_manager.delegates.plot_file_delegate import PlotFileDelegate
from stdm.ui.flts.workflow_manager.components.plot_import_component import PlotImportComponent

NAME, IMPORT_AS, DELIMITER, HEADER_ROW, CRS_ID, \
GEOM_FIELD, GEOM_TYPE= range(7)


class PlotImportWidget(QWidget):
    """
    A widget to import and preview plots of a scheme.
    Called from the Import Plot module.
    """
    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)
        self._file_service = widget_properties["data_service"][0]
        self._file_service = self._file_service()
        self._plot_file = PlotFile(self._file_service)
        import_component = PlotImportComponent()
        toolbar = import_component.components
        self._add_button = toolbar["addFiles"]
        self._remove_button = toolbar["removeFiles"]
        self._set_crs_button = toolbar["setCRS"]
        self._preview_button = toolbar["Preview"]
        self._import_button = toolbar["Import"]
        header_style = StyleSheet().header_style
        self._file_table_view = QTableView(self)
        self.model = WorkflowManagerModel(self._file_service)
        self._file_table_view.setModel(self.model)
        file_delegate = PlotFileDelegate(self._file_service, self)
        file_delegate = file_delegate.delegate()
        self._file_table_view.setItemDelegate(file_delegate)
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
        self._file_table_view.clicked.connect(self._on_file_select)
        self._add_button.clicked.connect(self._add_file)
        self._remove_button.clicked.connect(self._remove_file)
        self._set_crs_button.clicked.connect(self._set_crs)

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
            "Workflow Manager - Plot Add Files",
            path,
            "Plot Import files {}".format(extensions)
        )
        if fpath and fpath not in self._plot_file.file_paths:
            try:
                self._plot_file.set_file_path(fpath)
                if not self.model.results:
                    self.model.load(self._plot_file)
                    self.model.refresh()
                else:
                    self._insert_file()
            except(IOError, OSError, Exception) as e:
                self._show_critical_message(
                    "Workflow Manager - Plot Add Files",
                    "Failed to load: {}".format(e)
                )
            else:
                self._file_table_view.verticalHeader().setDefaultSectionSize(21)
                self._file_table_view.horizontalHeader().\
                    setStretchLastSection(True)

    def _insert_file(self):
        """
        Inserts plot import file data properties into the table view
        """
        position = self.model.rowCount()
        self.model.insertRows(position)

    def _on_file_select(self, index):
        """
        Enables toolbar buttons on selecting a file record
        :param index: Table view item identifier
        :type index: QModelIndex
        """
        self._enable_widgets(self._toolbar_buttons)
        self._enable_crs_button()

    def _remove_file(self):
        """
        Removes plot import file and its properties
        """
        index = self._current_index(self._file_table_view)
        if index is None:
            return
        row = index.row()
        fname = self.model.data(self.model.index(row, NAME))
        title = "Workflow Manager - Plot Add Files"
        msg = 'Remove "{}" and its properties?'.format(fname)
        if not self._show_question_message(title, msg):
            return
        fpath = self.model.results[row].get("fpath")
        self.model.removeRows(row)
        self._plot_file.remove_filepath(fpath)
        self._enable_crs_button()
        if not self.model.results:
            self._disable_widgets(self._toolbar_buttons)
            self._set_crs_button.setEnabled(False)

    def _show_critical_message(self, title, msg):
        """
        Message box to communicate critical message
        :param title: Title of the message box
        :type title: String
        :param msg: Message to be communicated
        :type msg: String
        """
        QMessageBox.critical(
            self,
            self.tr(title),
            self.tr(msg)
        )

    def _show_question_message(self, title, msg):
        """
        Message box to communicate a question
        :param title: Title of the message box
        :type title: String
        :param msg: Message to be communicated
        :type msg: String
        """
        if QMessageBox.question(
            self, self.tr(title), self.tr(msg),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            return False
        return True

    @property
    def _toolbar_buttons(self):
        """
        Returns toolbar buttons
        :return buttons: Toolbar buttons
        :return buttons: List
        """
        buttons = [
            self._remove_button,
            self._preview_button, self._import_button
        ]
        return buttons

    @staticmethod
    def _enable_widgets(widgets):
        """
        Enables list of widgets
        :param widgets: List of QWidget
        :rtype widgets: List
        """
        for widget in widgets:
            if widget:
                widget.setEnabled(True)

    @staticmethod
    def _disable_widgets(widgets):
        """
        Disables list of widgets
        :param widgets: List of QWidget
        :rtype widgets: List
        """
        for widget in widgets:
            if widget:
                widget.setEnabled(False)

    def _set_crs(self):
        """
        Sets coordinate reference system (CRS) to
        property to a plot import file
        """
        index = self._current_index(self._file_table_view)
        if index is None:
            return
        row = index.row()
        index = self.model.create_index(row, CRS_ID)
        value = self._crs_authority_id()
        items = self.model.results[row].get("items")
        del items[CRS_ID]
        self.model.setData(index, value)

    def _enable_crs_button(self):
        """
        Enables/disables Set CRS button
        """
        index = self._current_index(self._file_table_view)
        if index is None:
            return
        fpath = self.model.results[index.row()].get("fpath")
        if self._plot_file.is_pdf(fpath):
            self._set_crs_button.setEnabled(False)
        else:
            self._set_crs_button.setEnabled(True)

    @staticmethod
    def _crs_authority_id():
        """
        Returns selected coordinate
        reference system (CRS) authority ID
        :return auth_id: CRS authority ID
        :return auth_id: String
        """
        proj_selector = QgsGenericProjectionSelector()
        proj_selector.exec_()
        auth_id = proj_selector.selectedAuthId()
        return auth_id

    @staticmethod
    def _current_index(table_view):
        """
        Returns index of the current selected rowe
        :return table_view: Table view object
        :type table_view: QTableView
        :return: Current row index
        :rtype: Integer
        """
        index = table_view.currentIndex()
        if not index.isValid():
            return
        return index
