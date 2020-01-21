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
from stdm.settings.registryconfig import (
    last_document_path,
    set_last_document_path
)
from stdm.ui.flts.workflow_manager.config import (
    SchemeMessageBox,
    StyleSheet,
    TabIcons,
)
from stdm.ui.flts.workflow_manager.plot import(
    PlotFile,
    PlotPreview,
)
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.delegates.plot_file_delegate import PlotFileDelegate
from stdm.ui.flts.workflow_manager.components.plot_import_component import PlotImportComponent


NAME, IMPORT_AS, DELIMITER, HEADER_ROW, CRS_ID, \
GEOM_FIELD, GEOM_TYPE = range(7)


class PlotImportWidget(QWidget):
    """
    A widget to import and preview plots of a scheme.
    Called from the Import Plot module.
    """
    def __init__(self, widget_properties, profile, scheme_id, scheme_number, parent=None):
        super(QWidget, self).__init__(parent)
        data_service = widget_properties["data_service"]
        self._file_service = data_service["plot_file"]
        self._file_service = self._file_service()
        self._preview_service = data_service["plot_preview"]
        self._preview_service = self._preview_service()
        self._scheme_number = scheme_number
        self._scheme_id = scheme_id
        self._plot_file = PlotFile(self._file_service)
        self._plot_preview = self._layer = self._previewed = None
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
        self._preview_model = WorkflowManagerModel(self._preview_service)
        self._preview_table_view.setModel(self._preview_model)
        self._preview_table_view.setAlternatingRowColors(True)
        self._preview_table_view.setShowGrid(False)
        self._preview_table_view.horizontalHeader().setStyleSheet(header_style)
        self._preview_table_view.setSelectionBehavior(QTableView.SelectRows)
        self._preview_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        file_layout = QVBoxLayout()
        file_layout.addWidget(self._file_table_view)
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(self._preview_table_view)
        file_groupbox = QGroupBox("Added files")
        self._preview_groupbox = QGroupBox("File content")
        file_groupbox.setLayout(file_layout)
        self._preview_groupbox.setLayout(preview_layout)
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(file_groupbox)
        splitter.addWidget(self._preview_groupbox)
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
        self._preview_button.clicked.connect(self._preview)
        _selection_model = self._preview_table_view.selectionModel()
        _selection_model.selectionChanged.connect(self._on_preview_select)
        QTimer.singleShot(0, self._set_file_path)

    def _set_file_path(self):
        """
        Sets plot import file absolute path
        """
        fpath = last_document_path()
        if not fpath or not QFile.exists(fpath):
            fpath = "."
        self._plot_file.set_file_path(fpath)

    def _add_file(self):
        """
        Adds plot import file data settings into the file table view
        """
        fpath = QFileInfo(self._plot_file.file_path).path()
        extensions = " ".join(self._plot_file.file_extensions())
        fpath = QFileDialog.getOpenFileName(
            self,
            "Workflow Manager - Plot Add Files",
            fpath,
            "Plot Import files {}".format(extensions)
        )
        if fpath and fpath not in self._plot_file.file_paths:
            try:
                self._plot_file.set_file_path(fpath)
                set_last_document_path(fpath)
                if not self.model.results:
                    self._load(self.model, self._plot_file)
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
        Inserts plot import file data settings into the table view
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
        Removes plot import file and its settings from table view
        """
        index = self._current_index(self._file_table_view)
        if index is None:
            return
        row = index.row()
        fname = self.model.data(self.model.index(row, NAME))
        title = "Workflow Manager - Plot Add Files"
        msg = 'Remove "{}" and its settings?'.format(fname)
        if not self._show_question_message(title, msg):
            return
        fpath = self.model.results[row].get("fpath")
        self.model.removeRows(row)
        self._plot_file.remove_filepath(fpath)
        if self._plot_preview:
            self._plot_preview.remove_layer_by_id(fpath)
        self._reset_preview(fpath)
        self._set_preview_groupbox_title()
        self._enable_crs_button()
        if not self.model.results:
            self.model.reset()
            self._disable_widgets(self._toolbar_buttons)
            self._set_crs_button.setEnabled(False)

    def _reset_preview(self, fpath):
        """
        Resets preview QTableView
        :param fpath: Plot import file absolute path
        :type fpath: String
        """
        if fpath == self._previewed:
            self._preview_model.reset()
            self._previewed = fpath

    def _preview(self):
        """
        Previews selected plot import file content
        """
        index = self._current_index(self._file_table_view)
        if index is None:
            return
        row = index.row()
        settings = self._file_settings(row)
        fpath = settings.get("fpath")
        if not self._plot_file.is_pdf(fpath):
            if self._crs_not_set(row):
                return
            if self._plot_preview and self._layer:
                self._plot_preview.clear_feature(self._layer)
            self._plot_preview = PlotPreview(
                self._preview_service,
                settings,
                self._scheme_id,
                self._scheme_number,
                fpath
            )
            self._preview_load()
            self._set_preview_groupbox_title(settings[NAME])
            self._layer = self._plot_preview.layer
            self._previewed = fpath

    def _file_settings(self, row):
        """
        Returns plot import file data settings
        :param row: Table view item identifier
        :type row: Integer
        :return: Plot import file data settings
        :rtype: Dictionary
        """
        return self.model.results[row]

    def _crs_not_set(self, row):
        """
        Returns Tru if CRS is not set
        :param row: Table view item identifier
        :type row: Integer
        :return True: True if CRS is not set
        :return True: Boolean
        """
        if not self._is_crs(row):
            title = "Workflow Manager - Plot Preview"
            msg = "Coordinate reference system (CRS) is missing.\n" \
                  "Do you want to set it to preview?"
            if not self._show_question_message(title, msg):
                return True
            self._set_crs()

    def _is_crs(self, row):
        """
        Returns true if coordinate reference
        system (CRS) has been set. Otherwise none
        :param row: Table view item identifier
        :type row: Integer
        :return: True
        :return: Boolean
        """
        crs_id = self.model.data(self.model.index(row, CRS_ID))
        if crs_id:
            return True

    def _preview_load(self):
        """
        Loads selected plot import file content
        """
        try:
            self._load(self._preview_model, self._plot_preview)
        except(IOError, OSError, Exception) as e:
            self._show_critical_message(
                "Workflow Manager - Plot Preview",
                "Failed to load: {}".format(e)
            )
        else:
            self._preview_table_view.horizontalHeader().\
                setStretchLastSection(True)

    @staticmethod
    def _load(model, data_source):
        """
        Loads model data
        :param model: Table view model
        :type model: QAbstractTableModel
        :param data_source: Data source object
        :rtype data_source: Object
        """
        model.layoutAboutToBeChanged.emit()
        model.load(data_source)
        model.layoutChanged.emit()

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

    def _set_preview_groupbox_title(self, title=None):
        """
        Sets the preview groupbox title
        :param title: Groupbox title
        :type title: String
        """
        default = "File content"
        if title:
            if len(title) > 20:
                title = "{0}{1}".format(title[:20], "...")
            title = "{0}: {1}".format(default, title)
        else:
            title = default
        self._preview_groupbox.setTitle(title)

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
        items[CRS_ID] = None
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

    def _on_preview_select(self, selected):
        """
        Selects a layer feature on table view row
        :param selected: Currently selected items
        :type selected: QItemSelection
        """
        index = selected.indexes()[0]
        self._plot_preview.clear_feature()
        self._plot_preview.select_feature(index.row() + 1)
