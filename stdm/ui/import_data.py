"""
/***************************************************************************
Name                 : Data Import Wizard
Description          : LEGACY CODE, NEEDS TO BE UPDATED.
                       Import spatial and textual data into STDM database
Date                 : 24/February/12
copyright            : (C) 2012 by John Gitau
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

import json
import os
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QFile,
    QSignalMapper,
    QDir,
    QFileInfo
)
from qgis.PyQt.QtGui import (
    QColor
)
from qgis.PyQt.QtWidgets import (
    QWizard,
    QMessageBox,
    QApplication,
    QAction,
    QMenu,
    QDialog,
    QListWidgetItem,
    QFileDialog,
    QComboBox
)
from qgis.core import QgsFileUtils

from stdm.data.importexport import (
    vectorFileDir,
    setVectorFileDir
)
from stdm.data.importexport.reader import OGRReader, ImportFeatureException
from stdm.data.pg_utils import (
    table_column_names
)
from stdm.settings import current_profile
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.importexport.translator_config import (
    ValueTranslatorConfig
)
from stdm.ui.importexport.translator_widget_base import (
    TranslatorWidgetManager
)
from stdm.utils.util import (
    profile_user_tables,
    profile_spatial_tables
)

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_import_data.ui'))

BACKUP_IMPORT_CONFIG_PATH = QDir.home().path() + '/.stdm/last_import_settings.json'


class ImportData(WIDGET, BASE):
    ROLE_TABLE_NAME = Qt.UserRole + 1

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self.btnSrcUp.setIcon(GuiUtils.get_icon('up.png'))
        self.btnSrcDown.setIcon(GuiUtils.get_icon('down.png'))
        self.btn_add_translator.setIcon(GuiUtils.get_icon('add.png'))
        self.btn_edit_translator.setIcon(GuiUtils.get_icon('edit.png'))
        self.btn_delete_translator.setIcon(GuiUtils.get_icon('remove.png'))
        self.btnDestUp.setIcon(GuiUtils.get_icon('up.png'))
        self.btnDestDown.setIcon(GuiUtils.get_icon('down.png'))

        self.curr_profile = current_profile()

        # Connect signals
        self.btnBrowseSource.clicked.connect(self.setSourceFile)
        self.lstDestTables.itemClicked.connect(self.destSelectChanged)
        self.btnSrcUp.clicked.connect(self.srcItemUp)
        self.btnSrcDown.clicked.connect(self.srcItemDown)
        self.btnSrcAll.clicked.connect(self.checkSrcItems)
        self.btnSrcNone.clicked.connect(self.uncheckSrcItems)
        self.btnDestUp.clicked.connect(self.targetItemUp)
        self.btnDestDown.clicked.connect(self.targetItemDown)
        self.lstSrcFields.currentRowChanged[int].connect(self.sourceRowChanged)
        self.lstTargetFields.currentRowChanged[int].connect(self.destRowChanged)
        self.lstTargetFields.currentRowChanged[int].connect(self._enable_disable_trans_tools)
        self.chk_virtual.toggled.connect(self._on_load_virtual_columns)
        self.button_save_configuration.clicked.connect(self._save_column_mapping)
        self.button_load_configuration.clicked.connect(self._load_column_mapping)

        self.targetTab = ''

        self.import_was_successful = False
        self.restored_config = {}

        # Data Reader
        self.dataReader = None

        # Init
        self.registerFields()

        # Geometry columns
        self.geom_cols = []

        # Initialize value translators from definitions
        self._init_translators()

        # self._set_target_fields_stylesheet()

        if os.path.exists(BACKUP_IMPORT_CONFIG_PATH):
            self._restore_previous_configuration()

    def closeEvent(self, event):
        self._save_if_unfinished()
        super().closeEvent(event)

    def reject(self):
        self._save_if_unfinished()
        super().reject()

    def accept(self):
        super().accept()
        self._save_if_unfinished()

    def _save_if_unfinished(self):
        """
        If an unfinished import is in progress, then automatically save the settings to a hidden file
        """
        if self.import_was_successful:
            return

        if not self.field("srcFile"):
            # user hasn't even started the process by picking a file, so we've nothing of value to save...
            return

        current_config = self._get_column_config()
        with open(BACKUP_IMPORT_CONFIG_PATH, 'wt') as f:
            f.write(json.dumps(current_config, indent=4))

    def _restore_previous_configuration(self):
        """
        Loads the previously unfinished configuration
        """
        with open(BACKUP_IMPORT_CONFIG_PATH, 'rt') as f:
            config = json.loads(''.join(f.readlines()))

        os.remove(BACKUP_IMPORT_CONFIG_PATH)
        if not config:
            return

        if QMessageBox.question(self,
                                self.tr('Import Data'),
                                self.tr(
                                    'A previously incomplete or unsuccessful import was detected. Would you like to restore the previous configuration and retry?'),
                                QMessageBox.Yes | QMessageBox.No,
                                QMessageBox.Yes
                                ) != QMessageBox.Yes:
            return

        self.restored_config = config
        self.txtDataSource.setText(self.restored_config.get('source_file'))

        self.rbTextType.setChecked(self.restored_config.get('is_text', True))
        self.rbSpType.setChecked(self.restored_config.get('is_spatial', False))

    def _init_translators(self):
        translator_menu = QMenu(self)

        self._trans_widget_mgr = TranslatorWidgetManager(self)
        self._trans_signal_mapper = QSignalMapper(self)

        for trans_name, config in ValueTranslatorConfig.translators.items():
            trans_action = QAction('{}...'.format(trans_name),
                                   translator_menu
                                   )

            self._trans_signal_mapper.setMapping(trans_action, trans_name)
            trans_action.triggered.connect(self._trans_signal_mapper.map)

            translator_menu.addAction(trans_action)

        if len(translator_menu.actions()) == 0:
            self.btn_add_translator.setEnabled(False)

        else:
            self.btn_add_translator.setMenu(translator_menu)

            self._trans_signal_mapper.mapped[str].connect(self._load_translator_dialog)

        self.btn_edit_translator.setEnabled(False)
        self.btn_delete_translator.setEnabled(False)

        self.btn_edit_translator.clicked.connect(self._on_edit_translator)
        self.btn_delete_translator.clicked.connect(self._on_delete_translator)

    def _load_translator_dialog(self, config_key):
        """
        Load translator dialog.
        """
        dest_column = self._selected_destination_column()
        src_column = self._selected_source_column()

        if dest_column:
            # Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            if trans_dlg is None:
                trans_config = ValueTranslatorConfig.translators.get(config_key, None)

                # Safety precaution
                if trans_config is None:
                    return

                try:
                    trans_dlg = trans_config.create(
                        self,
                        self._source_columns(),
                        self.targetTab,
                        dest_column,
                        src_column
                    )
                    trans_dlg.set_config_key(config_key)

                except RuntimeError as re:
                    QMessageBox.critical(
                        self,
                        QApplication.translate(
                            'ImportData',
                            'Value Translator'
                        ),
                        str(re)
                    )

                    return

            self._handle_translator_dlg(dest_column, trans_dlg)

    def _handle_translator_dlg(self, key, dlg):
        if dlg.exec_() == QDialog.Accepted:
            self._trans_widget_mgr.add_widget(key, dlg)

        self._enable_disable_trans_tools()

    def _on_edit_translator(self):
        """
        Slot to load the translator widget specific for the selected column for editing.
        """
        dest_column = self._selected_destination_column()

        if dest_column:
            # Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            self._handle_translator_dlg(dest_column, trans_dlg)

    def _on_delete_translator(self):
        """
        Slot for deleting the translator widget for the selected column.
        """
        dest_column = self._selected_destination_column()

        self._delete_translator(dest_column)

    def _delete_translator(self, destination_column):
        if not destination_column:
            return

        _ = self._trans_widget_mgr.remove_translator_widget(destination_column)

        self._enable_disable_trans_tools()

    def _enable_disable_trans_tools(self, index=-1):
        """
        Enable/disable appropriate value translator tools based on the selected
        column.
        """
        dest_column = self._selected_destination_column()

        if dest_column:
            # Check if there is an existing dialog in the manager
            trans_dlg = self._trans_widget_mgr.translator_widget(dest_column)

            if trans_dlg is None:
                self.btn_add_translator.setEnabled(True)
                self.btn_edit_translator.setEnabled(False)
                self.btn_delete_translator.setEnabled(False)

            else:
                self.btn_add_translator.setEnabled(False)
                self.btn_edit_translator.setEnabled(True)
                self.btn_delete_translator.setEnabled(True)

        else:
            self.btn_add_translator.setEnabled(False)
            self.btn_edit_translator.setEnabled(False)
            self.btn_delete_translator.setEnabled(False)

    def _selected_destination_column(self):
        dest_field_item = self.lstTargetFields.currentItem()

        if dest_field_item is None:
            return ""

        else:
            return dest_field_item.text()

    def _selected_source_column(self):
        src_field_item = self.lstSrcFields.currentItem()

        if src_field_item is None:
            return ""

        else:
            return src_field_item.text()

    def _set_target_fields_stylesheet(self):
        self.lstTargetFields.setStyleSheet("QListWidget#lstTargetFields::item:selected"
                                           " { selection-background-color: darkblue }")

    def registerFields(self):
        # Register wizard fields
        pgSource = self.page(0)
        pgSource.registerField("srcFile*", self.txtDataSource)
        pgSource.registerField("typeText", self.rbTextType)
        pgSource.registerField("typeSpatial", self.rbSpType)

        # Destination table configuration
        destConf = self.page(1)
        destConf.registerField("optAppend", self.rbAppend)
        destConf.registerField("optOverwrite", self.rbOverwrite)
        destConf.registerField("tabIndex*", self.lstDestTables)
        destConf.registerField("geomCol", self.geomClm, "currentText", QComboBox.currentIndexChanged[int])

    def initializePage(self, page_id):
        # Re-implementation of wizard page initialization
        if page_id == 1:
            # Reference to checked list widget item representing table name
            self.geomClm.clear()

            if self.field("typeText"):
                self.load_tables_of_type("textual", self.restored_config.get('dest_table'))
                self.geomClm.setEnabled(False)
            elif self.field("typeSpatial"):
                self.load_tables_of_type("spatial", self.restored_config.get('dest_table'))

                if self.selected_destination_table():
                    self.loadGeomCols(self.selected_destination_table())
                self.geomClm.setEnabled(True)

            if self.restored_config:
                if self.restored_config.get('overwrite', False):
                    self.rbOverwrite.setChecked(True)
                else:
                    self.rbAppend.setChecked(True)

        if page_id == 2:
            self.lstSrcFields.clear()
            self.lstTargetFields.clear()

            self.assignCols()
            if self.restored_config and self.selected_destination_table() == self.restored_config.get('dest_table'):
                self._restore_column_config(self.restored_config)

            self._enable_disable_trans_tools()

    def _source_columns(self):
        return self.dataReader.getFields()

    @staticmethod
    def format_name_for_matching(name: str) -> str:
        """
        Returns a column name formatted for tolerant matching, e.g. we ignore
        case, _ characters, etc
        """
        return name.strip().lower().replace(' ', '').replace('_', '').replace('-', '')

    @staticmethod
    def names_are_matching(name1: str, name2: str) -> bool:
        """
        Returns True if the specified column name pairs should be considered a tolerant
        match
        """
        return ImportData.format_name_for_matching(name1) == ImportData.format_name_for_matching(name2)

    def selected_destination_table(self) -> Optional[str]:
        """
        Returns the selected (checked) destination table
        """
        for i in range(self.lstDestTables.count()):
            item = self.lstDestTables.item(i)
            if item.checkState() == Qt.Checked:
                return item.data(ImportData.ROLE_TABLE_NAME)

        return None

    def assignCols(self):
        # Load source and target columns respectively
        source_columns = self._source_columns()

        # Destination Columns
        self.targetTab = self.selected_destination_table()
        target_columns = table_column_names(self.targetTab, False, True)

        # Remove geometry columns and 'id' column in the target columns list
        target_columns = [c for c in target_columns if c not in self.geom_cols and c != 'id']

        # now synchronize the lists, as much as possible
        # this consists of moving columns with matching names in the source and target lists to the same
        # placement at the top of the lists, and filtering out lists of remaining unmatched columns

        matched_source_columns = []
        unmatched_source_columns = source_columns[:]
        matched_target_columns = []
        unmatched_target_columns = target_columns[:]
        for source in source_columns:
            for target in unmatched_target_columns:
                if ImportData.names_are_matching(source, target):
                    matched_source_columns.append(source)
                    unmatched_source_columns = [c for c in unmatched_source_columns if c != source]
                    matched_target_columns.append(target)
                    unmatched_target_columns = [c for c in unmatched_target_columns if c != target]
                    break

        # any matching columns get added to the start of the lists, and unmatched get added
        # to the end of the list
        for c in matched_source_columns + unmatched_source_columns:
            src_item = QListWidgetItem(c, self.lstSrcFields)
            # automatically check any columns we could match
            src_item.setCheckState(Qt.Checked if c in matched_source_columns else Qt.Unchecked)
            src_item.setIcon(GuiUtils.get_icon("column.png"))
            self.lstSrcFields.addItem(src_item)

        self._add_target_table_columns(matched_target_columns + unmatched_target_columns)

    def _add_target_table_columns(self, items, style=False):
        entity = self.curr_profile.entity_by_name(self.targetTab)
        for item in items:
            list_item = QListWidgetItem(item)

            # Show lookup columns in a different color
            column = entity.column(item)
            if column: 
                if column.TYPE_INFO == "LOOKUP":
                    color = QColor(255, 85, 0)
                    list_item.setForeground(color)

            if style:
                color = QColor(0, 128, 255)
                list_item.setForeground(color)

            self.lstTargetFields.addItem(list_item)

    def _on_load_virtual_columns(self, state):
        """
        Load/unload relationships in the list of destination table columns.
        """
        virtual_columns = self.dataReader.entity_virtual_columns(self.targetTab)

        if state:
            if len(virtual_columns) == 0:
                msg = QApplication.translate("ImportData",
                                             "There are no virtual columns for the specified table.")
                QMessageBox.warning(
                    self,
                    QApplication.translate(
                        'ImportData',
                        'Import Data'
                    ),
                    msg
                )
                self.chk_virtual.setChecked(False)

                return

            self._add_target_table_columns(virtual_columns, True)

        else:
            self._remove_destination_table_fields(virtual_columns)

    def _remove_destination_table_fields(self, fields):
        """Remove the specified columns from the destination view."""
        for f in fields:
            list_items = self.lstTargetFields.findItems(f, Qt.MatchFixedString)
            if len(list_items) > 0:
                list_item = list_items[0]

                row = self.lstTargetFields.row(list_item)

                rem_item = self.lstTargetFields.takeItem(row)
                del rem_item

                # Delete translator if already defined for the given column
                self._delete_translator(f)

    def loadGeomCols(self, table):
        # Load geometry columns based on the selected table
        self.geom_cols = table_column_names(table, True, True)
        self.geomClm.clear()
        self.geomClm.addItems(self.geom_cols)

        if self.restored_config.get('geom_column'):
            self.geomClm.setCurrentIndex(self.geomClm.findText(self.restored_config['geom_column']))

    def load_tables_of_type(self, type: str, initial_selection: Optional[str] = None):
        """
        Load textual or spatial tables

        If initial_selection is specified then that table will be initially checked
        """
        self.lstDestTables.clear()
        tables = None
        if type == "textual":
            tables = profile_user_tables(self.curr_profile, False, True, include_read_only=False)
        elif type == "spatial":
            tables = profile_spatial_tables(self.curr_profile, include_read_only=False)

        if tables is not None:
            for table_name, table_label in tables.items():
                table_item = QListWidgetItem(table_label, self.lstDestTables)
                table_item.setData(ImportData.ROLE_TABLE_NAME, table_name)
                if initial_selection:
                    table_item.setCheckState(
                        Qt.Checked if ImportData.names_are_matching(table_name, initial_selection) else Qt.Unchecked)
                else:
                    table_item.setCheckState(Qt.Unchecked)
                table_item.setIcon(GuiUtils.get_icon("table.png"))
                self.lstDestTables.addItem(table_item)

    def validateCurrentPage(self):
        # Validate the current page before proceeding to the next one
        validPage = True

        if not QFile.exists(str(self.field("srcFile"))):
            self.show_error_message("The specified source file does not exist.")
            validPage = False

        else:
            if self.dataReader:
                self.dataReader.reset()
            self.dataReader = OGRReader(str(self.field("srcFile")))

            if not self.dataReader.isValid():
                self.show_error_message("The source file could not be opened."
                                        "\nPlease check is the given file type "
                                        "is supported")
                validPage = False

        if self.currentId() == 1:
            if self.selected_destination_table() is None:
                self.show_error_message("Please select the destination table.")
                validPage = False

        if self.currentId() == 2:
            self.import_was_successful = self.execImport()
            validPage = self.import_was_successful

        return validPage

    def setSourceFile(self):
        # Set the file path to the source file
        filters = "Comma Separated Value (*.csv);;ESRI Shapefile (*.shp);;AutoCAD DXF (*.dxf)"
        sourceFile, _ = QFileDialog.getOpenFileName(self, "Select Source File", vectorFileDir(), filters)
        if sourceFile:
            self.txtDataSource.setText(sourceFile)

    def get_source_dest_pairs(self) -> dict:
        """
        Builds a dictionary of source field to destination field name
        """
        mapping = {}
        for target_row in range(self.lstTargetFields.count()):
            if target_row < self.lstSrcFields.count():
                source_item = self.lstSrcFields.item(target_row)
                if source_item.checkState() == Qt.Checked:
                    dest_item = self.lstTargetFields.item(target_row)
                    mapping[source_item.text()] = dest_item.text()

        return mapping

    def set_source_dest_pairs(self, mapping: dict):
        """
        Sets the source to destination pairs for fields to match

        Any existing mapping will be cleared
        """
        self.uncheckSrcItems()

        index = 0
        for target_source, target_dest in mapping.items():
            # move source row up
            for source_row in range(self.lstSrcFields.count()):
                if ImportData.names_are_matching(target_source, self.lstSrcFields.item(source_row).text()):
                    source_item = self.lstSrcFields.takeItem(source_row)
                    self.lstSrcFields.insertItem(index, source_item)
                    source_item.setCheckState(Qt.Checked)

            # move target row up
            for dest_row in range(self.lstTargetFields.count()):
                if ImportData.names_are_matching(target_dest, self.lstTargetFields.item(dest_row).text()):
                    dest_item = self.lstTargetFields.takeItem(dest_row)
                    self.lstTargetFields.insertItem(index, dest_item)

            index += 1

    def execImport(self):
        # Initiate the import process
        success = False
        matchCols = self.get_source_dest_pairs()

        # Specify geometry column
        geom_column = None

        if self.field("typeSpatial"):
            geom_column = self.field("geomCol")

        # Ensure that user has selected at least one column if it is a
        # non-spatial table
        if len(matchCols) == 0:
            self.show_error_message("Please select at least one source column.")
            return success

        value_translator_manager = self._trans_widget_mgr.translator_manager()

        try:
            if self.field("optOverwrite"):
                entity = self.curr_profile.entity_by_name(self.targetTab)
                dependencies = entity.dependencies()
                view_dep = dependencies['views']
                entity_dep = [e.name for e in entity.children()]
                entities_dep_str = ', '.join(entity_dep)
                views_dep_str = ', '.join(view_dep)

                if len(entity_dep) > 0 or len(view_dep) > 0:
                    del_msg = QApplication.translate(
                        'ImportData',
                        "Overwriting existing records will permanently \n"
                        "remove records from other tables linked to the \n"
                        "records. The following tables will be affected."
                        "\n{}\n{}"
                        "\nClick Yes to proceed importing or No to cancel.".
                            format(entities_dep_str, views_dep_str)
                    )
                    del_result = QMessageBox.critical(
                        self,
                        QApplication.translate(
                            "ImportData",
                            "Overwrite Import Data Warning"
                        ),
                        del_msg,
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if del_result == QMessageBox.Yes:
                        self.dataReader.featToDb(
                            self.targetTab, matchCols, False, self, geom_column,
                            translator_manager=value_translator_manager
                        )
                        # Update directory info in the registry
                        setVectorFileDir(self.field("srcFile"))

                        self.show_info_message(
                            "All features have been imported successfully!"
                        )
                        success = True

                    else:
                        success = False
            else:
                self.dataReader.featToDb(
                    self.targetTab, matchCols, True, self, geom_column,
                    translator_manager=value_translator_manager
                )
                self.show_info_message(
                    "All features have been imported successfully!"
                )
                # Update directory info in the registry
                setVectorFileDir(self.field("srcFile"))
                success = True
        except ImportFeatureException as e:
            self.show_error_message(str(e))

        return success

    def _clear_dest_table_selections(self, exclude=None):
        # Clears checked items in destination table list view
        if exclude is None:
            exclude = []

        for i in range(self.lstDestTables.count()):
            item = self.lstDestTables.item(i)
            if item.checkState() == Qt.Checked and not item.data(ImportData.ROLE_TABLE_NAME) in exclude:
                item.setCheckState(Qt.Unchecked)

    def destSelectChanged(self, item):
        """
        Handler when a list widget item is clicked,
        clears previous selections
        """
        if item.checkState() == Qt.Checked:
            selected_table = item.data(ImportData.ROLE_TABLE_NAME)
            # Ensure other selected items have been cleared
            self._clear_dest_table_selections(exclude=[selected_table])

            # Load geometry columns if selection is a spatial table
            if self.field("typeSpatial"):
                self.loadGeomCols(selected_table)

    def syncRowSelection(self, srcList, destList):
        """
        Sync the selection of an srcList item to the corresponding one in
        the destination column list.
        """
        if (srcList.currentRow() + 1) <= destList.count():
            destList.setCurrentRow(srcList.currentRow())

    def sourceRowChanged(self):
        # Slot when the source list's current row changes
        self.syncRowSelection(self.lstSrcFields, self.lstTargetFields)

    def destRowChanged(self):
        # Slot when the destination list's current row changes
        self.syncRowSelection(self.lstTargetFields, self.lstSrcFields)

    def itemUp(self, listWidget):
        # Moves the selected item in the list widget one level up
        curIndex = listWidget.currentRow()
        curItem = listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex - 1, curItem)
        listWidget.setCurrentRow(curIndex - 1)

    def itemDown(self, listWidget):
        # Moves the selected item in the list widget one level down
        curIndex = listWidget.currentRow()
        curItem = listWidget.takeItem(curIndex)
        listWidget.insertItem(curIndex + 1, curItem)
        listWidget.setCurrentRow(curIndex + 1)

    def checkAllItems(self, listWidget, state):
        # Checks all items in the list widget
        for l in range(listWidget.count()):
            item = listWidget.item(l)
            if state:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

    def checkSrcItems(self):
        # Slot for checking all source table columns
        self.checkAllItems(self.lstSrcFields, True)

    def uncheckSrcItems(self):
        # Slot for unchecking all source table columns
        self.checkAllItems(self.lstSrcFields, False)

    def srcItemUp(self):
        # Slot for moving source list item up
        self.itemUp(self.lstSrcFields)

    def srcItemDown(self):
        # Slot for moving source list item down
        self.itemDown(self.lstSrcFields)

    def targetItemUp(self):
        # Slot for moving target item up
        self.itemUp(self.lstTargetFields)

    def targetItemDown(self):
        # Slot for moving target item down
        self.itemDown(self.lstTargetFields)

    def keyPressEvent(self, e):
        """
        Override method for preventing the dialog from
        closing itself when the escape key is hit
        """
        if e.key() == Qt.Key_Escape:
            pass

    def show_info_message(self, message):
        # Information message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()

    def show_error_message(self, message):
        # Error Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.exec_()

    def _save_column_mapping(self):
        """
        Exports the current column mapping to a JSON definition file
        """
        config = RegistryConfig()
        prev_folder = config.read(["LastImportConfigFolder"]).get("LastImportConfigFolder")
        if not prev_folder:
            prev_folder = QDir.homePath()

        dest_path, _ = QFileDialog.getSaveFileName(self, self.tr("Save Configuration"),
                                                   prev_folder,
                                                   "{0} (*.json)".format(self.tr('Configuration files')))

        if not dest_path:
            return

        dest_path = QgsFileUtils.ensureFileNameHasExtension(dest_path, ['.json'])

        config.write({"LastImportConfigFolder": QFileInfo(dest_path).path()})

        with open(dest_path, 'wt') as f:
            f.write(json.dumps(self._get_column_config(), indent=4))

    def _get_column_config(self) -> dict:
        """
        Returns a dictionary encapsulating the column mapping configuration
        """
        return {
            'column_mapping': self.get_source_dest_pairs(),
            'source_file': str(self.field("srcFile")),
            'is_text': bool(self.field("typeText")),
            'is_spatial': bool(self.field("typeSpatial")),
            'geom_column': self.field("geomCol") or None,
            'overwrite': bool(self.field("optOverwrite")),
            'dest_table': self.targetTab or '',
            'translators': self._get_value_translators()
        }

    def _load_column_mapping(self):
        """
        Imports the current column mapping from a JSON definition file
        """
        config = RegistryConfig()
        prev_folder = config.read(["LastImportConfigFolder"]).get("LastImportConfigFolder")
        if not prev_folder:
            prev_folder = QDir.homePath()

        source_path, _ = QFileDialog.getOpenFileName(self, self.tr("Load Configuration"),
                                                     prev_folder,
                                                     "{0} (*.json)".format(self.tr('Configuration files')))

        if not source_path:
            return

        config.write({"LastImportConfigFolder": QFileInfo(source_path).path()})

        with open(source_path, 'rt') as f:
            imported_config = json.loads(''.join(f.readlines()))
            self._restore_column_config(imported_config)

    def _restore_column_config(self, config: dict):
        """
        Restores a previously saved column configuration
        """
        column_mapping = config.get('column_mapping', {})

        # test validity -- ensure that all the referenced source and destination columns
        # from the saved file are available
        for saved_source, saved_dest in column_mapping.items():

            for source_row in range(self.lstSrcFields.count()):
                if ImportData.names_are_matching(saved_source, self.lstSrcFields.item(source_row).text()):
                    break
            else:
                self.show_error_message(self.tr('Source column {} not found in dataset'.format(saved_source)))
                return

            for destination_row in range(self.lstTargetFields.count()):
                if ImportData.names_are_matching(saved_dest, self.lstTargetFields.item(destination_row).text()):
                    break
            else:
                self.show_error_message(self.tr('Destination column {} not found in dataset'.format(saved_dest)))
                return

        self.set_source_dest_pairs(column_mapping)

        # Restore translators
        self._trans_widget_mgr.clear()
        translators = config.get('translators', {})
        self._restore_translators(translators)

    def _restore_translators(self, value_translators: dict[str, list]):
        """
        Restores the translators from a previously saved configuration.

        Args:
            value_translators (dict[str, list]): A dictionary containing translator configurations.
                The keys are translator names, and the values are lists of translator settings.
        """
        for translator_name, translators in value_translators.items():
            if len(translators) == 0:
                continue

            trans_config = ValueTranslatorConfig.translators.get(translator_name, None)

            if translator_name == "Lookup values":

                for translator in translators:
                    dest_table = translator["dest_table"]
                    dest_column= translator["dest_column"]
                    src_column = translator["src_column"]
                    reftable   = translator["referenced_table"]
                    default_value = translator["default_value"]
                    trans_type = translator["translator_type"]

                    trans_dlg = trans_config.create(
                        self,
                        self._source_columns(),
                        dest_table,
                        dest_column,
                        src_column
                    )
                    trans_dlg.set_config_key(translator_name)
                    trans_dlg.cbo_lookup.setCurrentIndex(trans_dlg.cbo_lookup.findText(reftable))
                    trans_dlg.cbo_default.setCurrentIndex(trans_dlg.cbo_default.findText(default_value))

                    self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

            if translator_name == "Related table":
                for vt in translators:
                    dest_table = vt["dest_table"] 
                    dest_column = vt["dest_column"] 
                    src_column = vt["src_column"]
                    referenced_table = vt["referenced_table"] 
                    output_ref_column = vt["output_ref_column"] 
                    input_ref_columns = vt["input_ref_columns"] 

                    trans_dlg = trans_config.create(
                        self,
                        self._source_columns(),
                        dest_table,
                        dest_column,
                        src_column
                    )
                    trans_dlg.txt_table_name.setText(dest_table)
                    trans_dlg.txt_column_name.setText(dest_column)
                    trans_dlg.cbo_source_tables.setCurrentIndex(trans_dlg.cbo_source_tables.findText(referenced_table))
                    trans_dlg.cbo_output_column.setCurrentIndex(trans_dlg.cbo_output_column.findText(output_ref_column))
                    trans_dlg.tb_source_trans_cols.clear_all()

                    for src_col, dest_col in input_ref_columns.items():
                        trans_dlg.tb_source_trans_cols.append_data_row(
                            src_col,
                            dest_col
                        )
                    self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

            if translator_name == "Supporting documents":
                for vt in translators:
                    dest_table = vt["dest_table"] 
                    dest_column = vt["dest_column"] 
                    src_column = vt["src_column"]
                    referenced_table = vt["referenced_table"] 
                    doc_type_id = vt["document_type_id"]
                    doc_type = vt["document_type"]
                    doc_source_dir = vt["source_directory"]

                    trans_dlg = trans_config.create(
                        self,
                        self._source_columns(),
                        dest_table,
                        dest_column,
                        src_column
                    )

                    trans_dlg._dest_table = dest_table
                    trans_dlg._dest_col = dest_column
                    trans_dlg._document_type_id = doc_type_id
                    trans_dlg._document_type_name = doc_type
                    trans_dlg.document_directory = doc_source_dir
                    trans_dlg.txtRootFolder.setText(doc_source_dir)

                    self._trans_widget_mgr.add_widget(dest_column, trans_dlg)

                    

    def _get_value_translators(self) -> dict[str, list]:
        trans_widgets = self._trans_widget_mgr.widgets()
        translators = {}
        for name, widget in trans_widgets.items():
            conf_key = widget.config_key()

            if conf_key not in translators:
                translators[conf_key] = []

            vt = widget.value_translator()

            translator = {}

            if conf_key == "Lookup values":
                src_col = ""
                ref_cols = vt.input_referenced_columns()
                if len(ref_cols.keys()) > 0:
                    src_col = list(ref_cols.keys())[0]

                translator = {"name": name,
                    "dest_table": vt.referencing_table(),
                    "dest_column":vt.referencing_column(),
                    "referenced_table": vt.referenced_table(),
                    "default_value": vt.default_value(),
                    "src_column" :src_col,
                    "translator_type": conf_key
                    }

            if conf_key == "Related table":
                translator = {
                    "name": name,
                    "dest_table": vt.referencing_table(),
                    "dest_column": vt.referencing_column(),
                    "referenced_table": vt.referenced_table(),
                    "output_ref_column": vt.output_referenced_column(),
                    "input_ref_columns": vt.input_referenced_columns(),
                    "src_column":widget.selected_source_column()
                }

            if conf_key == "Supporting documents":
                src_col = ""
                ref_cols = vt.input_referenced_columns()
                if len(ref_cols.keys()) > 0:
                    src_col = list(ref_cols.keys())[0]
                translator =  {
                    "name": name,
                    "dest_table": vt.referencing_table(),
                    "dest_column": vt.referencing_column(),
                    "referenced_table": vt.referenced_table(),
                    "document_type_id": vt.document_type_id(),
                    "document_type": vt.document_type(),
                    "source_directory": vt.source_directory(),
                    "src_column": src_col
                }

            if len(translator) > 0:
                translators[conf_key].append(translator)

        return translators

