"""
/***************************************************************************
Name                 : Options Dialog
Description          : Container for editing STDM settings.
Date                 : 26/May/20146
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
import logging
from collections import OrderedDict

from typing import Tuple

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QDir,
    QTimer
)
from qgis.PyQt.QtGui import (
    QIntValidator
)
from qgis.PyQt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMessageBox,
    QHeaderView,
    QTableWidgetItem,
    QComboBox,
    QPushButton,
    QLabel,
    QComboBox,
    QPushButton
    )

from qgis.gui import QgsGui

from stdm.data.config import DatabaseConfig
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.connection import DatabaseConnection
from stdm.settings import (
    current_profile,
    save_current_profile,
    get_entity_browser_record_limit,
    save_entity_browser_record_limit,
    save_log_mode,
    get_entity_sort_details
)
from stdm.settings.registryconfig import (
    composer_output_path,
    composer_template_path,
    debug_logging,
    logging_mode,
    set_debug_logging,
    source_documents_path,
    QGISRegistryConfig,
    RegistryConfig,
    COMPOSER_OUTPUT,
    COMPOSER_TEMPLATE,
    NETWORK_DOC_RESOURCE,
    CONFIG_UPDATED,
    LOG_MODE,
    set_run_template_converter_on_startup,
    run_template_converter_on_startup
)
from stdm.ui.customcontrols.validating_line_edit import INVALIDATESTYLESHEET
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.login_dlg import loginDlg
from stdm.ui.notification import NotificationBar
from stdm.utils.util import value_from_metadata

MAX_LIMIT = 100000  # Maximum records in a entity browser


def pg_profile_names():
    """/
    :return: List containing tuple of PostgreSQL database connection names
    and full path stored by QGIS.
    :rtype: list
    """
    pg_connection_path = "/PostgreSQL/connections"
    q_config = QGISRegistryConfig(pg_connection_path)

    pg_connections = q_config.group_children()

    profiles = [(conn_name, "{0}/{1}".format(pg_connection_path, conn_name))
                for conn_name in pg_connections]

    return profiles


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_options.ui'))


class OptionsDialog(WIDGET, BASE):
    """
    Dialog for editing STDM settings.
    """

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)

        QgsGui.enableAutoGeometryRestore(self)

        self.btn_composer_out_folder.setIcon(GuiUtils.get_icon('open_file.png'))
        self.btn_template_folder.setIcon(GuiUtils.get_icon('open_file.png'))
        self.btn_supporting_docs.setIcon(GuiUtils.get_icon('open_file.png'))

        self.iface = iface

        self.notif_bar = NotificationBar(self.vlNotification, 6000)
        self._apply_btn = self.buttonBox.button(QDialogButtonBox.Apply)

        self._reg_config = RegistryConfig()
        settings = self._reg_config.read(['Host', 'Database', 'Port'])
        self._db_config = DatabaseConfig(settings)

        version = value_from_metadata('version')

        # Connect signals
        self._apply_btn.clicked.connect(self.apply_settings)
        self.buttonBox.accepted.connect(self.on_accept)
        self.chk_pg_connections.toggled.connect(self._on_use_pg_connections)
        self.cbo_pg_connections.currentIndexChanged.connect(
            self._on_pg_profile_changed)
        self.btn_db_conn_clear.clicked.connect(self.clear_properties)
        self.btn_test_db_connection.clicked.connect(self._on_test_connection)
        self.btn_supporting_docs.clicked.connect(
            self._on_choose_supporting_docs_path
        )
        self.btn_template_folder.clicked.connect(
            self._on_choose_doc_designer_template_path
        )
        self.btn_composer_out_folder.clicked.connect(
            self._on_choose_doc_generator_output_path
        )

        self._config = StdmConfiguration.instance()
        self._default_style_sheet = self.txtRepoLocation.styleSheet()

        self._add_logging_modes()

        self.init_gui()

        self.profile_entity_widget = None
        self.cache = None
        self.sort_record_widget = None

        self.tabWidget.setCurrentIndex(0)
        self.btnAdd.clicked.connect(self.add_sorting_column)
        self.init_sorting_widgets(self.cbo_profiles.currentText())
        self.cbo_profiles.currentIndexChanged.connect(self.profile_changed)

        self.chk_pg_connections.setVisible(False)
        self.cbo_pg_connections.setVisible(False)


    def init_gui(self):
        # Set integer validator for the port number
        int_validator = QIntValidator(1024, 49151)
        self.txtPort.setValidator(int_validator)

        # Load profiles
        self.load_profiles()

        # Set current profile in the combobox
        curr_profile = current_profile()
        if not curr_profile is None:
            GuiUtils.set_combo_current_index_by_text(self.cbo_profiles, curr_profile.name)

        # Load current database connection properties
        self._load_db_conn_properties()

        # Load existing PostgreSQL connections
        self._load_qgis_pg_connections()

        # Load directory paths
        self._load_directory_paths()

        self.edtEntityRecords.setMaximum(MAX_LIMIT)
        self.edtEntityRecords.setValue(get_entity_browser_record_limit())

        # Debug logging
        lvl = debug_logging()
        if lvl:
            self.chk_logging.setCheckState(Qt.Checked)
        else:
            self.chk_logging.setCheckState(Qt.Unchecked)

        # Template converter
        value = run_template_converter_on_startup()
        if value:
            self.cbTempConv.setCheckState(Qt.Checked)
        else:
            self.cbTempConv.setCheckState(Qt.Unchecked)

        # Logging Mode
        log_mode =  logging_mode()
        index = self.cbLogMode.findText(log_mode)
        self.cbLogMode.setCurrentIndex(index)

    def _add_logging_modes(self):
        self.cbLogMode.addItem('STDOUT')
        self.cbLogMode.addItem('FILE')

    def profile_changed(self):
        self.init_sorting_widgets(self.cbo_profiles.currentText())

    def init_sorting_widgets(self, profile_name):
        profile = self._config.profile(profile_name)
        self.profile_entity_widget = ProfileEntityWidget(self.cbEntities, profile)
        self.cache = SortRecordCache(profile, self._reg_config)
        self.sort_record_widget = SortRecordWidget(self.twSorting, self.cache)
        self.show_cache(self.cache.profile_cache(profile_name))

    def load_profiles(self):
        """
        Load existing profiles into the combobox.
        """
        profile_names = list(self._config.profiles.keys())

        self.cbo_profiles.clear()
        self.cbo_profiles.addItem('')
        self.cbo_profiles.addItems(profile_names)

    def _load_db_conn_properties(self):
        # Load database connection properties from the registry.
        db_conn = self._db_config.read()

        if not db_conn is None:
            self.txtHost.setText(db_conn.Host)
            self.txtPort.setText(str(db_conn.Port))
            self.txtDatabase.setText(db_conn.Database)

    def _load_qgis_pg_connections(self):
        """
        Load QGIS postgres connections.
        """
        self.cbo_pg_connections.addItem('')

        profiles = pg_profile_names()
        for profile in profiles:
            self.cbo_pg_connections.addItem(profile[0], profile[1])

    def _load_directory_paths(self):
        # Load paths to various directory settings.
        comp_out_path = composer_output_path()
        comp_temp_path = composer_template_path()
        source_doc_path = source_documents_path()

        if not source_doc_path is None:
            self.txtRepoLocation.setText(source_doc_path)

        if not comp_out_path is None:
            self.txt_output_dir.setText(comp_out_path)

        if not comp_temp_path is None:
            self.txt_template_dir.setText(comp_temp_path)

    def _on_use_pg_connections(self, state):
        # Slot raised when to (not) use existing pg connections
        if not state:
            self.cbo_pg_connections.setCurrentIndex(0)
            self.cbo_pg_connections.setEnabled(False)

            # Restore current connection in registry
            self._load_db_conn_properties()

        else:
            self.cbo_pg_connections.setEnabled(True)

    def _on_pg_profile_changed(self, index):
        """
        Slot raised when the index of the pg profile changes. If the
        selection is valid then the system will attempt to extract
        the database connection properties of the selected profile
        stored in the registry.
        """
        if index == 0:
            return

        profile_path = self.cbo_pg_connections.itemData(index)

        q_config = QGISRegistryConfig(profile_path)
        db_items = q_config.read(['database', 'host', 'port'])

        if len(db_items) > 0:
            self.txtDatabase.setText(db_items['database'])
            self.txtHost.setText(db_items['host'])
            self.txtPort.setText(db_items['port'])

    def clear_properties(self):
        """
        Clears the host, database name and port number values from the
        respective controls.
        """
        self.txtDatabase.clear()
        self.txtHost.clear()
        self.txtPort.clear()

    def _on_choose_supporting_docs_path(self):
        # Slot raised to select directory for supporting documents.
        self._set_selected_directory(self.txtRepoLocation, self.tr(
            'Supporting Documents Directory')
                                     )

    def _on_choose_doc_designer_template_path(self):
        # Slot raised to select directory for document designer templates.
        self._set_selected_directory(self.txt_template_dir, self.tr(
            'Document Designer Templates Directory')
                                     )

    def _on_choose_doc_generator_output_path(self):
        # Slot raised to select directory for doc generator outputs.
        self._set_selected_directory(self.txt_output_dir, self.tr(
            'Document Generator Output Directory')
                                     )

    def _set_selected_directory(self, txt_box, title):
        def_path = txt_box.text()
        sel_doc_path = QFileDialog.getExistingDirectory(self, title, def_path)

        if sel_doc_path:
            normalized_path = QDir.fromNativeSeparators(sel_doc_path)
            txt_box.clear()
            txt_box.setText(normalized_path)

    def _validate_db_props(self):
        # Test if all properties have been specified
        status = True

        self.notif_bar.clear()

        if not self.txtHost.text():
            msg = self.tr('Please specify the database host address.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        if not self.txtPort.text():
            msg = self.tr('Please specify the port number.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        if not self.txtDatabase.text():
            msg = self.tr('Please specify the database name.')
            self.notif_bar.insertErrorNotification(msg)

            status = False

        return status

    def _database_connection(self):
        # Creates a databaase connection object from the specified args
        host = self.txtHost.text()
        port = self.txtPort.text()
        database = self.txtDatabase.text()

        # Create database connection object
        db_conn = DatabaseConnection(host, port, database)

        return db_conn

    def _on_test_connection(self):
        """
        Slot raised to test database connection.
        """
        status = self._validate_db_props()

        if not status:
            return

        login_dlg = loginDlg(self, True)
        db_conn = self._database_connection()
        login_dlg.set_database_connection(db_conn)

        res = login_dlg.exec_()
        if res == QDialog.Accepted:
            msg = self.tr("Connection to '{0}' database was "
                          "successful.".format(db_conn.Database))
            QMessageBox.information(self, self.tr('Database Connection'), msg)

    def set_current_profile(self):
        """
        Saves the given profile name as the current profile.
        """
        profile_name = self.cbo_profiles.currentText()

        if not profile_name:
            self.notif_bar.clear()

            msg = self.tr('Profile name is empty, current profile will not '
                          'be set.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        save_current_profile(profile_name)

        return True

    def save_database_properties(self):
        """
        Saves the specified database connection properties to the registry.
        :return: True if the connection properties were successfully saved.
        :rtype: bool
        """
        if not self._validate_db_props():
            return False

        # Create a database object and write it to the registry
        db_conn = self._database_connection()
        self._db_config.write(db_conn)

        return True

    def set_supporting_documents_path(self):
        """
        Set the directory of supporting documents.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txtRepoLocation.text()

        if not path:
            msg = self.tr('Please set the supporting documents directory.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        # Validate path
        if not self._check_path_exists(path, self.txtRepoLocation):
            return False

        # Commit to registry
        self._reg_config.write({NETWORK_DOC_RESOURCE: path})

        return True

    def set_document_templates_path(self):
        """
        Set the directory of document designer templates.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txt_template_dir.text()

        if not path:
            msg = self.tr('Please set the document designer templates '
                          'directory.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        # Validate path
        if not self._check_path_exists(path, self.txt_template_dir):
            return False

        # Commit to registry
        self._reg_config.write({COMPOSER_TEMPLATE: path})

        return True

    def set_document_output_path(self):
        """
        Set the directory of document generator outputs.
        :return: True if the directory was set in the registry, otherwise
        False.
        :rtype: bool
        """
        path = self.txt_output_dir.text()

        if not path:
            msg = self.tr('Please set the document generator output directory'
                          '.')
            self.notif_bar.insertErrorNotification(msg)

            return False

        # Validate path
        if not self._check_path_exists(path, self.txt_output_dir):
            return False

        # Commit to registry
        self._reg_config.write({COMPOSER_OUTPUT: path})

        return True

    def _save_log_mode(self, log_mode: str):
        self._reg_config.write({LOG_MODE: log_mode})

    def _check_path_exists(self, path, text_box):
        # Validates if the specified folder exists
        dir = QDir()

        if not dir.exists(path):
            msg = self.tr("'{0}' directory does not exist.".format(path))
            self.notif_bar.insertErrorNotification(msg)

            # Highlight textbox control
            text_box.setStyleSheet(INVALIDATESTYLESHEET)

            timer = QTimer(self)
            # Sync interval with that of the notification bar
            timer.setInterval(self.notif_bar.interval)
            timer.setSingleShot(True)

            # Remove previous connected slots (if any)
            receivers = timer.receivers(QTimer.timeout)
            if receivers > 0:
                self._timer.timeout.disconnect()

            timer.start()
            timer.timeout.connect(lambda: self._restore_stylesheet(
                text_box)
                                  )

            return False

        return True

    def _restore_stylesheet(self, textbox):
        # Slot raised to restore the original stylesheet of the textbox control
        textbox.setStyleSheet(self._default_style_sheet)

        # Get reference to timer and delete
        sender = self.sender()
        if not sender is None:
            sender.deleteLater()

    def apply_debug_logging(self):
        # Save debug logging
        logger = logging.getLogger('stdm')

        if self.chk_logging.checkState() == Qt.Checked:
            logger.setLevel(logging.DEBUG)
            set_debug_logging(True)
        else:
            logger.setLevel(logging.ERROR)
            set_debug_logging(False)

    def apply_settings(self):
        """
        Save settings.
        :return: True if the settings were successfully applied, otherwise
        False.
        :rtype: bool
        """
        # Set current profile
        if not self.set_current_profile():
            return False

        # Set db connection properties
        if not self.save_database_properties():
            return False

        # Set supporting documents directory
        if not self.set_supporting_documents_path():
            return False

        # Set document designer templates path
        if not self.set_document_templates_path():
            return False

        # Set document generator output path
        if not self.set_document_output_path():
            return False

        if self.cbTempConv.checkState() == Qt.Checked:
            set_run_template_converter_on_startup(True)
        else:
            set_run_template_converter_on_startup(False)

        self.apply_debug_logging()

        # Set Entity browser record limit
        save_entity_browser_record_limit(self.edtEntityRecords.value())

        save_log_mode(self.cbLogMode.currentText())

        self.cache.save()

        msg = self.tr('Settings successfully saved.')
        self.notif_bar.insertSuccessNotification(msg)

        return True

    def on_accept(self):
        """
        Slot raised to save the settings of the current widget and close the
        widget.
        """
        if not self.apply_settings():
            return

        self.accept()

    def add_sorting_column(self):
        sort_record = self.profile_entity_widget.make_sorting_record()
        if sort_record is not None:
            self.sort_record_widget.add_sort_record(sort_record)

    def show_cache(self, cache):
        for entity in cache:
            name = list(entity.keys())[0]
            idx = self.cbEntities.findText(name)
            self.cbEntities.setCurrentIndex(idx)
            sort_record = self.profile_entity_widget.make_sorting_record()
            if sort_record is not None:
                self.sort_record_widget.add_sort_record_cached(sort_record, entity[name])

class ProfileEntityWidget():
    """
    Class to manage entity widget that holds entities for the current profile.
    """
    def __init__(self, combo_widget, current_profile):
        """
        :param combo_widget: Combobox for entities of a given profile.
        :type combo_widget: QCombobox
        :param current_profile: Name of the current profile.
        :type current_profile: str
        """
        self._profile = current_profile
        self._entities = {}
        self._entity_combo = combo_widget
        self._entity_combo.clear()
        self._populate_entities()
        self._populate_entities_combo()

    def _populate_entities(self):
        """
        Reads and populate entities dictionary with entities
        of the current profile.
        """
        for entity in self._profile.user_entities():
            self._entities[self.fmt_short_name(entity.short_name)] = entity

    def _populate_entities_combo(self):
        """
        Reads the entities dictionary and populate the entities
        combobox.
        """
        for key, value in self._entities.items():
            self._entity_combo.addItem(key)

    def make_sorting_record(self) -> Tuple[QLabel, QComboBox, QComboBox, QPushButton]:
        """
        """
        sort_record = self._make_record(self.selected_entity_name())
        return sort_record

    def _make_record(self, entity_name: str) -> Tuple[QLabel, QComboBox, QComboBox, QPushButton]:
        """
        Creates and returns a four item tuple that represents
        a single row in the table widget. A row contains:
         - label - name of the entity
         - columns - List of columns for a given entity
         - order - Sorting order
         - remove button - button to remove the row
         :param entity_name: Name of the entity in row.
         :type entity_name: str
         
         :rtype: tuple
        """
        if entity_name == '':
            return None

        label = QLabel(entity_name)
        columns = self._make_columns_widget(entity_name)
        order = self._make_order_widget()
        action_btn = QPushButton('Remove')
        return (label, columns, order, action_btn)

    def _make_columns_widget(self, entity_name: str) -> QComboBox:
        """
        Creates and populates sorting column combobox.
        Items of the combobox are column names of a
        given entity.
        """
        entity = self.current_entity(entity_name)
        geom_column_names = [column.name for column in entity.geometry_columns()]
        cbox = QComboBox()
        for name, column in entity.columns.items():
            if name in geom_column_names:
                continue
            cbox.addItem(name)
        return cbox

    def _make_order_widget(self) -> QComboBox:
        """
        Create a combobox for sorting order.
        """
        cbox = QComboBox()
        cbox.addItem("Ascending")
        cbox.addItem("Descending")
        return cbox

    def selected_entity_name(self):
        return self._entity_combo.currentText()

    def fmt_short_name(self, short_name):
        """
        Replace spaces with underscore
        """
        name = short_name.replace(' ', "_")
        return name

    
    def current_entity(self, entity_name):
        return self._entities[entity_name]


class SortRecordCache():
    """
    Class to manage existing records from the registry. The class
    is responsible for reading, writing, updating, and deleting values
    from the registry. 
    Upon instantiation of this class, it will read any sorting records
    for a given profile from the registry and place them into a working
    cache in memory.
    """
    def __init__(self, current_profile, reg):
        """
        :param current_profile: Current profile.
        :type current_profile: Profile
        :param reg: Registry class for accessing the registry
        :type reg: RegistryConfig
        """
        self.profile = current_profile
        self.reg_config = reg
        self._cache = {}
        self.cache_name = 'Sorting/'+self.profile.name
        self.trash_bin = []
        self.fill_cache()

    def fill_cache(self):
        """
        Read and cache values from registry.
        """
        group_keys = self.reg_config.group_keys(self.cache_name)
        if group_keys is None:
            return
        if self.profile.name not in list(self._cache.keys()):
            self._cache[self.profile.name] = []
        for key in group_keys:
            value = self.reg_config.get_value(self.cache_name, key)
            values = value.split()
            entity={key:(values[0], values[1])}
            self._cache[self.profile.name].append(entity)

    def profile_cache(self, profile_name):
        """
        Returns cached values of a given profile.

        :param profile_name: Text name of a profile.
        :type profile_name: str
        """
        return self._cache[profile_name]

    def add(self, entity_name, value):
        """
        Adds an entry to the cache.

        :param entity_name: Name of an entity to cache values for.
        :type entity_name: str
        :param value: Tuple of (sort column and sort order)
        :type value: tuple
        """
        sort_column = value[0].currentText()
        sort_order = value[1].currentText()
        self._cache[self.profile.name].append({entity_name.text():(sort_column, sort_order)})

    def remove(self, entity_name):
        """
        Finds and removes an item from local cache.
        Removed entry is moved to trash bin temporarily. The items will be 
        removed from the registry permanently onces the dialog is saved.

        :param entity_name: Key to use when finding an item from the cache.
        :type entity_name: str
        """
        entity = self.find_in_cache(entity_name)
        if entity is None:
            return
        self.trash_bin.append(entity)
        self._delete_from_cache(entity_name)

    def remove_keys(self):
        """
        Removes values in trash bin permanently from
        registry then clears the bin.
        """
        for entity in self.trash_bin:
            key = list(entity.keys())[0]
            self.reg_config.remove_key(self.cache_name, key)
        self.trash_bin = []

    def save(self):
        """
        Save cached entries permanently to registry.
        But before saving, remove any deleted items.
        """
        self.remove_keys()
        self.write_cache()

    def write_cache(self):
        """
        Write cached values to registry.
        """
        for entity in self._cache[self.profile.name]:
            entity_name = list(entity.keys())[0]
            value = list(entity.values())[0]
            self.reg_config.add_value(self.cache_name, {entity_name:value})

    def _delete_from_cache(self, entity_name):
        """
        Delete an entity from the cache.

        :param entity_name: Name of the entity to remove from cache.
        :type entity_name: str
        """
        entities = self._cache[self.profile.name]
        entities[:] = [entity for entity in entities if entity_name not in entity]

    def find_in_cache(self, entity_name):
        """
        Finds and returns an entity from the cache.

        :param entity_name: Name of the entity to find.
        :type entity_name: str
        """
        entities = self._cache[self.profile.name]
        entity = [entity for entity in entities if entity_name in list(entity.keys())]
        return entity[0] if len(entity) > 0 else None

class SortRecordWidget():
    """
    A class that contains a table widget for adding sorting details.
    Sorting details includes:
    - label - Name of the entity you are setting the sorting details
    - Field - The column you are selecting for sorting
    - Order - Order of sorting the field
    - Action - Button to remove a row from the table widget
    """
    def __init__(self, table_widget, cache):
        """
        :param table_widget: Table for adding sorting details
        :type table_widget: QTableWidget

        :param cache: The class reads existing sorting details from the 
           registry, temporary stores any additions of sorting details and
           finally writting contents to registry.
        :type cache: SortRecordCache
        """
        self._table_widget = table_widget 
        self.cache = cache
        self._header_labels = ["Entity", "Field", "Order", "Action"]
        self.set_widget_header()
        self.clear_table_widget()

    def clear_table_widget(self):
        for idx in range(self._table_widget.rowCount()):
            self._table_widget.removeRow(idx)

    def set_widget_header(self):
        self._table_widget.setColumnCount(len(self._header_labels))
        self._table_widget.setHorizontalHeaderLabels(self._header_labels)
        self._table_widget.horizontalHeader().setStretchLastSection(True)
        self._table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def add_sort_record(self, sort_record):
        entity_name, entity_columns, sort_order, delete_button = sort_record
        
        entity = self.cache.find_in_cache(entity_name.text())
        if entity is not None:
            return

        entity_columns.setCurrentIndex(0)
        sort_order.setCurrentIndex(0)

        self._add_record(sort_record)

        self.cache.add(entity_name, (entity_columns, sort_order))

    def add_sort_record_cached(self, sort_record: tuple, value):
        """ 
        Method called once to add any sort details saved in the registry.
        Creates a  single row of table widget items from the values in 
        sort_record, then sets default values for comboboxes from the values 
        read from the registry
        :param sort_record: A tuple of (QLabel, QComboBox, QComboBox, QPushButton)
        :type sort_record: tuple
        :param value: A tuple of (sort_column, sort_order)
        :type value: tuple
        """
        entity_name, entity_columns, sort_order, delete_button = sort_record

        entity_columns.setCurrentIndex(0)
        sort_order.setCurrentIndex(0)

        idx = entity_columns.findText(value[0])
        if idx > -1:
            entity_columns.setCurrentIndex(idx)

        idx = sort_order.findText(value[1])
        if idx > -1:
            sort_order.setCurrentIndex(idx)

        self._add_record(sort_record)

    def _add_record(self, sort_record: Tuple[QLabel, QComboBox, QComboBox, QPushButton]):
        """
        Adds sorting widgets to a table widget
        """
        entity_name, entity_columns, sort_order, delete_button = sort_record

        entity_columns.currentIndexChanged.connect(self.change_sort_column)
        sort_order.currentIndexChanged.connect(self.change_sort_order)
        delete_button.clicked.connect(self.delete_row)

        self._table_widget.insertRow(self._table_widget.rowCount())
        row = self._table_widget.rowCount()

        self._table_widget.setCellWidget(row-1, 0, entity_name)
        self._table_widget.setCellWidget(row-1, 1, entity_columns)
        self._table_widget.setCellWidget(row-1, 2, sort_order)
        self._table_widget.setCellWidget(row-1, 3, delete_button)

    def current_row(self):
        """ 
        Returns current row from a table widget.
        :rtype: int
        """
        return self._table_widget.currentRow()

    def current_row_entity_name(self):
        """
        Returns an entity name from the first column (QLabel)
        of the current row of the table widget.
        :rtype: str
        """ 
        entity_name = ''
        curr_row = self.current_row()
        if curr_row > -1:
            widget = self._table_widget.cellWidget(curr_row, 0)
            if isinstance(widget, QLabel):
                entity_name = widget.text()
        return entity_name

    def current_row_sort_column(self):
        """
        Returns a name of the sorting field from the second column
        (QComboBox) of the current row of the table widget.
        :rtype: str
        """ 
        sort_col_name = ''
        curr_row = self.current_row()
        if curr_row > -1:
            widget = self._table_widget.cellWidget(curr_row, 1)
            if isinstance(widget, QComboBox):
                sort_col_name = widget.currentText()
        return sort_col_name

    def current_row_sort_order(self):
        """
        Returns a name of the sorting order from the third column
        (QComboBox) of the current row of the table widget.
        :rtype: str
        """
        sort_order = ''
        curr_row = self.current_row()
        if curr_row > -1:
            widget = self._table_widget.cellWidget(curr_row, 2)
            if isinstance(widget, QComboBox):
                sort_order = widget.currentText()
        return sort_order

    def entity_value(self):
        """
        Returns sorting details (sorting column and sorting order) of
        an entity from the cache.
        :rtype: tuple
        """
        entity = self.cache.find_in_cache(self.current_row_entity_name())
        return entity if entity is None else list(entity.values())[0]

    def update_entity_at_current_row(self, value):
        """
        Updates the value of the current entity in cache
        :param value: Tuple of (sorting column and sorting order).
        :type value: tuple
        """
        entity_name = self.current_row_entity_name()
        entity = self.cache.find_in_cache(entity_name)
        entity[entity_name] = value

    def change_sort_column(self):
        """
        Updates sorting column of an entity stored in the cache.
        """
        value = self.entity_value()
        if value is not None:
            sort_column = self.current_row_sort_column()
            sort_order = value[1]
            self.update_entity_at_current_row((sort_column, sort_order))

    def change_sort_order(self):
        """
        Updates sorting order (Ascending or Descending) of an
        entity stored in the cache.
        """
        value = self.entity_value()
        if value is not None:
            sort_column = value[0]
            sort_order = self.current_row_sort_order()
            self.update_entity_at_current_row((sort_column, sort_order))

    def delete_row(self):
        """
        Removes the current row from the table widget
        """
        entity_name = self.current_row_entity_name()
        if entity_name == '':
            return
        self._table_widget.removeRow(self.current_row())
        self.cache.remove(entity_name)

