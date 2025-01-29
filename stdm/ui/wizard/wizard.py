"""
/***************************************************************************
Name                 : wizard
Description          : STDM profile configuration wizard
Date                 : 06/January/2016
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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

import calendar
import copy
import os
from datetime import date
from datetime import datetime

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    Qt,
    QDir,
    pyqtSignal,
    QDate,
    QFile,
    QThread,
    QCoreApplication,
    QEvent,
    QIODevice,
    QPointF,
    QSizeF,
    QItemSelectionModel,
    QModelIndex,
    QSortFilterProxyModel
)
from qgis.PyQt.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QColor,
    QFont
)
from qgis.PyQt.QtWidgets import (
    QWizard,
    QMessageBox,
    QAbstractItemView,
    QDialog,
    QApplication,
    QMenu,
    QFileDialog,
    QTableView
)
from qgis.PyQt.QtXml import QDomDocument

from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsPrintLayout,
    QgsReadWriteContext
)

from stdm.data.configuration.columns import (
    AdministrativeSpatialUnitColumn,
    MultipleSelectColumn
)
from stdm.exceptions import DummyException
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.db_items import DbItem
from stdm.data.configuration.social_tenure import *
from stdm.data.configuration.stdm_configuration import (
    StdmConfiguration
)

from stdm.data.configuration.profile import Profile

from stdm.data.license_doc import LicenseDocument
from stdm.data.pg_utils import (
    pg_table_exists,
    table_column_names,
    pg_table_record_count,
    mandatory_columns,
    unique_columns
)

from stdm.security.privilege_provider import MultiPrivilegeProvider
from stdm.settings import (
    current_profile,
    save_current_profile
)
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings.registryconfig import (
    RegistryConfig,
    LOCAL_SOURCE_DOC,
    COMPOSER_OUTPUT,
    COMPOSER_TEMPLATE
)

from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar
from stdm.ui.wizard.column_depend import ColumnDepend
from stdm.ui.wizard.column_editor import ColumnEditor
from stdm.ui.wizard.copy_editor import CopyProfileEditor
from stdm.ui.wizard.create_entity import EntityEditor
from stdm.ui.wizard.create_lookup import LookupEditor
from stdm.ui.wizard.create_lookup_value import ValueEditor
from stdm.ui.wizard.custom_item_model import (
    EntitiesModel,
    ColumnEntitiesModel,
    STRColumnEntitiesModel,
    LookupEntitiesModel
)

from stdm.ui.wizard.entity_attributes_editor import (
    TenureCustomAttributesEditor
)
from stdm.ui.wizard.entity_depend import EntityDepend
from stdm.ui.wizard.profile_editor import ProfileEditor
from stdm.ui.wizard.spatial_tenure_types_dialog import (
    SpatialUnitTenureTypeDialog
)
from stdm.utils.util import enable_drag_sort

# ---- Testing Layout converter ------- #
from stdm.composer.converter import (
    get_templates
)

from stdm.composer.template_converter import (
        TemplateConverter
 )

from stdm.composer.custom_items.label import (
    STDM_DATA_LABEL_ITEM_TYPE
)
from stdm.composer.custom_items.photo import (
    STDM_PHOTO_ITEM_TYPE
)
from stdm.composer.custom_items.table import (
    STDM_DATA_TABLE_ITEM_TYPE
)
from stdm.composer.custom_items.qrcode import (
   STDM_QR_ITEM_TYPE
)

from stdm.composer.layout_utils import LayoutUtils

from qgis.core import (
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsUnitTypes,
    QgsLayoutItemPicture,
    QgsLayoutFrame
)
# ---- Testing Layout converter ------- #

# create logger
LOGGER = logging.getLogger('stdm')
LOGGER.setLevel(logging.DEBUG)

CHECKBOX_VALUES = [False, None, True]
CHECK_STATE = {True: Qt.Checked, False: Qt.Unchecked}

ORIG_CONFIG_FILE = QDir.home().path() + '/.stdm/orig_configuration.stc'
CONFIG_FILE = QDir.home().path() + '/.stdm/configuration.stc'
CONFIG_BACKUP_FILE = QDir.home().path() + '/.stdm/configuration_bak.stc'
DRAFT_CONFIG_FILE = QDir.home().path() + '/.stdm/configuration_draft.stc'

EXCL_ENTITIES = ['SUPPORTING_DOCUMENT', 'SOCIAL_TENURE',
                 'ADMINISTRATIVE_SPATIAL_UNIT', 'ENTITY_SUPPORTING_DOCUMENT',
                 'VALUE_LIST', 'ASSOCIATION_ENTITY']

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('wizard/ui_stdm_config.ui'))

class ConfigWizard(WIDGET, BASE):
    """
    STDM configuration wizard editor
    """
    wizardFinished = pyqtSignal(object, bool)

    def __init__(self, parent):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self.btnTemplates.setIcon(GuiUtils.get_icon('open_file.png'))
        self.btnDocOutput.setIcon(GuiUtils.get_icon('open_file.png'))
        self.btnDocPath.setIcon(GuiUtils.get_icon('open_file.png'))
        self.btnCopy.setIcon(GuiUtils.get_icon('composer_table.png'))
        self.btnPDelete.setIcon(GuiUtils.get_icon('remove.png'))
        self.btnNewP.setIcon(GuiUtils.get_icon('add.png'))

        self.btnNewEntity.setIcon(GuiUtils.get_icon('add.png'))
        self.btnEditEntity.setIcon(GuiUtils.get_icon('edit.png'))
        self.btnDeleteEntity.setIcon(GuiUtils.get_icon('delete.png'))

        self.btnAddColumn.setIcon(GuiUtils.get_icon('add.png'))
        self.btnEditColumn.setIcon(GuiUtils.get_icon('edit.png'))
        self.btnDeleteColumn.setIcon(GuiUtils.get_icon('delete.png'))
        self.btnExport.setIcon(GuiUtils.get_icon('export.png'))

        self.btnAddLookup.setIcon(GuiUtils.get_icon('add.png'))
        self.btnEditLookup.setIcon(GuiUtils.get_icon('edit.png'))
        self.btnDeleteLookup.setIcon(GuiUtils.get_icon('delete.png'))

        self.btnAddLkupValue.setIcon(GuiUtils.get_icon('add.png'))
        self.btnEditLkupValue.setIcon(GuiUtils.get_icon('edit.png'))
        self.btnDeleteLkupValue.setIcon(GuiUtils.get_icon('delete.png'))

        self.btn_sp_units_tenure.setIcon(GuiUtils.get_icon('social_tenure.png'))
        self.btn_custom_attrs.setIcon(GuiUtils.get_icon('column.png'))

        self.register_fields()

        # Add maximize buttons
        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowSystemMenuHint |
            Qt.WindowMaximizeButtonHint
        )
        # Initialize notification bars
        self._notif_bar_str = NotificationBar(self.vl_notification_str)

        # transfer state between wizard and column editor
        self.editor_cache = {}
        self.editor_cache['prop_set'] = None

        # directory path settings
        self.init_path_ctrls_event_handlers()

        # profile
        self.init_profile_ctrls_event_handlers()

        # register enitity model to different view controllers
        self.entity_model = EntitiesModel()
        self.set_views_entity_model(self.entity_model)

        self.STR_spunit_model = EntitiesModel()

        self.init_entity_item_model()

        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)

        # STR view model
        self.party_item_model = STRColumnEntitiesModel()
        self.spunit_item_model = STRColumnEntitiesModel()

        # cboParty & cboSPUnit
        self.init_STR_ctrls_event_handlers()

        # profile page : Add entities
        self.init_entity_ctrls_event_handlers()

        # Entity customization page
        self.init_column_ctrls_event_handlers()

        # lookup
        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)

        self.init_lookup_ctrls_event_handlers()

        self.lookup_item_model = self.lvLookups.selectionModel()
        self.lookup_item_model.selectionChanged.connect(self.lookup_changed)

        # lookup values
        self.lookup_value_view_model = QStandardItemModel(self.lvLookupValues)
        self.init_lkvalues_event_handlers()

        self.init_ui_ctrls()

        self.reg_config = RegistryConfig()

        self.load_directory_path_settings()

        self.setStartId(1)

        self.draft_config = False
        self.stdm_config = None
        self.new_profiles = []

        self.privileges = {}

        # self._str_table_exists = False
        self._sp_t_mapping = {}
        self._custom_attr_entities = {}
        self.orig_assets_count = 0  # count of items in StdmConfiguration instance
        config_file = self.get_config_file()
        self.load_stdm_config(config_file)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter_3.setStretchFactor(0, 11)
        self.splitter_3.setStretchFactor(1, 1)
        self.splitter.isCollapsible(False)
        self.splitter_2.isCollapsible(False)
        self.splitter_3.isCollapsible(False)
        self.splitter_3.setSizes([330, 300])

        cp = current_profile()
        if not cp is None:
            self.set_current_profile(cp.name)
        else:
            self.set_current_profile('')

        self._init_str_ctrls()

        self.save_draft_action = None
        self.discard_draft_action = None
        self.tmp_title = self.windowTitle()
        self.configure_custom_button1()
        self.set_window_title()

        self.pftableView.installEventFilter(self)
        self.tbvColumns.installEventFilter(self)

        self.selected_index = None

        tables = self.get_tables(current_profile())
        self.mandt_cols =  mandatory_columns(tables)
        self.unique_cols  =  unique_columns(tables)



    def get_tables(self, profile: Profile):
        """
        Get the tables of the profile
        """
        tables = []
        for entity in profile.entities.values():
            tables.append(entity.name)
        return tables

    def set_window_title(self):
        if self.draft_config:
            self.setWindowTitle('')
            draft = self.tr(' - [ DRAFT ]')
            self.setWindowTitle('{}{}'.format(self.tmp_title, draft))
        else:
            self.setWindowTitle(self.tmp_title)

    def _init_str_ctrls(self):
        # Collapse STR date range group boxes
        self.gb_start_dates.setCollapsed(False)
        self.gb_end_dates.setCollapsed(False)

        # Set default dates
        current_date = QDate.currentDate()
        self.dt_start_minimum.setDate(current_date)
        self.dt_start_maximum.setDate(current_date)
        self.dt_end_minimum.setDate(current_date)
        self.dt_end_maximum.setDate(current_date)

        # Connect signals
        self.dt_start_minimum.dateChanged.connect(
            self._on_str_start_min_date_changed
        )
        self.dt_start_maximum.dateChanged.connect(
            self._on_str_start_max_date_changed
        )
        self.dt_end_minimum.dateChanged.connect(
            self._on_str_end_min_date_changed
        )
        self.dt_end_maximum.dateChanged.connect(
            self._on_str_end_max_date_changed
        )

    def _on_str_start_min_date_changed(self, date):
        # Adjust limit of complementary control
        if date > self.dt_start_maximum.date():
            msg = self.tr(
                'Minimum start date is greater than maximum start '
                'date.'
            )
            self._notif_bar_str.clear()
            self._notif_bar_str.insertWarningNotification(msg)

    def _on_str_start_max_date_changed(self, date):
        # Adjust limit of complementary control
        if date < self.dt_start_minimum.date():
            msg = self.tr(
                'Maximum start date is less than minimum start '
                'date.'
            )
            self._notif_bar_str.clear()
            self._notif_bar_str.insertWarningNotification(msg)

    def _on_str_end_min_date_changed(self, date):
        # Adjust limit of complementary control
        if date > self.dt_end_maximum.date():
            msg = self.tr(
                'Minimum end date is greater than maximum end '
                'date.'
            )
            self._notif_bar_str.clear()
            self._notif_bar_str.insertWarningNotification(msg)

    def _on_str_end_max_date_changed(self, date):
        # Adjust limit of complementary control
        if date < self.dt_end_minimum.date():
            msg = self.tr(
                'Maximum end date is less than minimum end '
                'date.'
            )
            self._notif_bar_str.clear()
            self._notif_bar_str.insertWarningNotification(msg)

    def configuration_is_dirty(self):
        '''
        checks if anything has been added to the configuration
        :rtype:boolean
        '''
        config_is_dirty = False
        cnt = len(self.stdm_config)
        if cnt != self.orig_assets_count:
            config_is_dirty = True
        return config_is_dirty

    def reject(self):
        """
        Event handler for the cancel button.
        If configuration has been edited, warn user before exiting.
        """
        self.pftableView.removeEventFilter(self)
        self.tbvColumns.removeEventFilter(self)

        if self.draft_config:
            self.save_current_configuration(DRAFT_CONFIG_FILE)
        else:
            if self.config_is_dirty():
                warn_result = self.dirty_config_warning()
                if warn_result == QMessageBox.Cancel:
                    return
                if warn_result == QMessageBox.Yes:
                    self.save_current_configuration(DRAFT_CONFIG_FILE)

        self.done(0)

    def config_is_dirty(self):
        cnt = len(self.stdm_config)
        if cnt != self.orig_assets_count:
            return True
        else:
            return False

    def dirty_config_warning(self):
        msg0 = self.tr("You have made some changes to your current "
                       "configuration file, but you have not saved them in the "
                       "database permanently.\n Would you like to save your "
                       "changes as draft and continue next time? ")
        return self.query_box_save_cancel(msg0)

    def get_config_file(self):
        config_file = None
        try:
            config_file = self.healthy_config_file()
        except(ConfigurationException, IOError) as e:
            self.show_message(self.tr(str(e)))
        return config_file

    def load_stdm_config(self, config_file):
        """
        Read and load configuration from file
        """
        if config_file is None:
            return

        self.load_configuration_from_file(config_file)

        self.stdm_config = StdmConfiguration.instance()
        self.orig_assets_count = len(self.stdm_config)

        self.load_profiles()
        self.is_config_done = False
        self.stdm_config.profile_added.connect(self.cbo_add_profile)

    def healthy_config_file(self):
        """
        look for a healthy configuration file to load
        """
        main_config_file = self.healthy_file(CONFIG_FILE)
        bak_config_file = self.healthy_file(CONFIG_BACKUP_FILE)
        draft_config_file = self.healthy_file(DRAFT_CONFIG_FILE)
        orig_config_file = self.healthy_file(ORIG_CONFIG_FILE)

        if main_config_file and not bak_config_file and \
                draft_config_file == False:
            return CONFIG_FILE

        if bak_config_file:
            return self.user_choose_config()

        if draft_config_file:
            self.draft_config = True
            return DRAFT_CONFIG_FILE

    def healthy_file(self, config_file):
        is_healthy = False
        if QFile.exists(config_file):
            qf = QFile(config_file)
            if qf.size() > 0:
                is_healthy = True
        return is_healthy

    def system_choose_backup(self):
        msg = self.tr("Your main configuration file seems to be corrupt!\n" +
                      "The system will revert to the latest configuration " +
                      "backup file ")
        self.show_message(msg)
        return CONFIG_BACKUP_FILE

    def system_choose_orig_config(self):
        msg = self.tr("Your configuration files seems to be corrupt!\n "
                      " The system will revert to the original system configuration file.")
        self.show_message(msg)
        return ORIG_CONFIG_FILE

    def user_choose_config(self):
        """
        The function assumes both configuration (configuration.stc) and
        backup configuration (configuration_bak.stc) files exist.
        If a user chooses 'YES', the backup file is returned else the main configuration.
        :rtype: str
        """
        msg = self.tr("Your previous configuration wizard did "
                      "not complete successfully!\n Would you like to recover that session?")

        if self.query_box_yesno(msg, QMessageBox.Critical) == QMessageBox.Yes:
            return CONFIG_BACKUP_FILE
        else:
            self.rename_config_backup_file(CONFIG_BACKUP_FILE)
            return CONFIG_FILE

    def rename_config_backup_file(self, config_backup_file):
        h = str(datetime.now().hour)
        m = str(datetime.now().minute)
        s = str(datetime.now().second)
        patch = h + m + s
        new_name = config_backup_file.replace('_bak', '_bak' + patch)
        old_backup_config_file = QFile(config_backup_file)
        old_backup_config_file.rename(new_name)

    def init_path_ctrls_event_handlers(self):
        """
        Attach OnClick event handlers for the document path buttons
        """
        self.btnDocPath.clicked.connect(self.set_support_doc_path)
        self.btnDocOutput.clicked.connect(self.set_output_path)
        self.btnTemplates.clicked.connect(self.set_template_path)

    def init_profile_ctrls_event_handlers(self):
        """
        Attach event handlers for the profile toolbar
        """
        self.cboProfile.currentIndexChanged.connect(self.profile_changed)
        self.btnNewP.clicked.connect(self.new_profile)
        self.btnPDelete.clicked.connect(self.delete_profile)
        self.btnCopy.clicked.connect(self.copy_profile)

    def init_entity_item_model(self):
        """
        Attach a selection change event handler for the custom
        QStandardItemModel - entity_item_model
        """
        self.entity_item_model = self.lvEntities.selectionModel()
        self.entity_item_model.selectionChanged.connect(self.entity_changed)

    def set_views_entity_model(self, entity_model):
        """
        Attach custom item model to hold data for the view controls
        :param entity_model: Custom QStardardItemModel
        :type entity_model: EntitiesModel
        """
        self.pftableView.setModel(entity_model)
        self.lvEntities.setModel(entity_model)

    def init_STR_ctrls_event_handlers(self):
        """
        Attach onChange event handlers for the STR combobox.
        """
        # Connect party (de)selection
        self.lst_parties.party_selected.connect(
            self._on_party_selected
        )
        self.lst_parties.party_deselected.connect(
            self._on_party_deselected
        )

        # Connect spatial unit view signals
        self.lst_spatial_units.spatial_unit_selected.connect(
            self._on_spatial_unit_selected
        )
        self.lst_spatial_units.spatial_unit_deselected.connect(
            self._on_spatial_unit_deselected
        )

        # Connect button for showing mapping of tenure types
        self.btn_sp_units_tenure.clicked.connect(self.on_show_sp_units_tenure)

        # Connect button for showing dialog for editing tenure attributes
        self.btn_custom_attrs.clicked.connect(
            self.on_show_custom_attributes_editor
        )

    def init_entity_ctrls_event_handlers(self):
        """
        Attach OnClick event handlers for the entity toolbar buttons
        """
        self.btnNewEntity.clicked.connect(self.new_entity)
        self.btnEditEntity.clicked.connect(self.edit_entity)
        self.btnDeleteEntity.clicked.connect(self.delete_entity)

    def init_column_ctrls_event_handlers(self):
        """
        Attach OnClick event handlers for the columns toolbar buttons
        """
        self.btnAddColumn.clicked.connect(self.new_column)
        self.btnEditColumn.clicked.connect(self.edit_column)
        self.btnDeleteColumn.clicked.connect(self.delete_column)
        self.btnExport.clicked.connect(self.export_columns)

    def init_lookup_ctrls_event_handlers(self):
        """
        Attach OnClick event handlers for the lookup toolbar buttons
        """
        self.btnAddLookup.clicked.connect(self.new_lookup)
        self.btnEditLookup.clicked.connect(self.edit_lookup)
        self.btnDeleteLookup.clicked.connect(self.delete_lookup)

    def init_lkvalues_event_handlers(self):
        """
        Attach OnClick event handlers for the lookup values toolbar buttons
        """
        self.btnAddLkupValue.clicked.connect(self.add_lookup_value)
        self.btnEditLkupValue.clicked.connect(self.edit_lookup_value)
        self.btnDeleteLkupValue.clicked.connect(self.delete_lookup_value)

    def init_ui_ctrls(self):
        """
        Set default state for UI controls
        """
        self.edtDocPath.setFocus()
        self.rbReject.setChecked(True)
        self.edtDesc.setText("")

        self.pftableView.setColumnWidth(0, 250)
        self.pftableView.setColumnWidth(1, 260)
        self.pftableView.doubleClicked.connect(self.edit_entity)
        # disable editing of view widgets
        self.pftableView.setEditTriggers(QAbstractItemView.NoEditTriggers)


        # Attach multi party checkbox state change event handler
        self.cbMultiParty.stateChanged.connect(self.multi_party_state_change)

        self.tbvColumns.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbvColumns.doubleClicked.connect(self.edit_column)
        self.tbvColumns.clicked.connect(self.column_clicked)

        self.columns_proxy_model = QSortFilterProxyModel(self.col_view_model)
        self.columns_proxy_model.setSourceModel(self.col_view_model)
        self.columns_proxy_model.setFilterKeyColumn(0)
        self.tbvColumns.setModel(self.columns_proxy_model)
        self.tbvColumns.setSortingEnabled(True)

        self.lvEntities.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lvEntities.clicked.connect(self.entity_clicked)

        self.lvLookups.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lvLookups.setCurrentIndex(self.lvLookups.model().index(0, 0))
        self.lvLookups.doubleClicked.connect(self.edit_lookup)
        self.lvLookups.clicked.connect(self.lookup_clicked)

        self.lvLookupValues.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lvLookupValues.doubleClicked.connect(self.edit_lookup_value)


    def _on_party_selected(self, item):
        # Handle selection of a party entity.
        # Check if the party has also been set as the spatial unit.
        party_name = item.text()
        sp_units = self.lst_spatial_units.spatial_units()
        if party_name in sp_units:
            self._notif_bar_str.clear()
            msg = self.tr(
                "The selected entity has already been specified as a spatial "
                "unit in the profile's social tenure relationship."
            )
            self._notif_bar_str.insertWarningNotification(msg)
            item.setCheckState(Qt.Unchecked)

            return

        # Add party item to view
        p = self.current_profile()
        if not p is None:
            party_entity = p.entity(party_name)
            p.social_tenure.add_party(party_entity)
            self.dg_tenure.add_party_entity(party_entity)

    def _on_party_deselected(self, item):
        # Handle deselection of a party entity
        # Remove party graphic item from the view
        party_name = item.text()

        p = self.current_profile()
        if not p is None:
            # Remove party from the profile
            res = p.social_tenure.remove_party(party_name)
            if res:
                self.dg_tenure.remove_party(party_name)

    def _on_spatial_unit_selected(self, item):
        # Check if the spatial unit has also been selected as a party
        sp_unit_name = item.text()
        parties = self.lst_parties.parties()
        if sp_unit_name in parties:
            self._notif_bar_str.clear()
            msg = self.tr(
                "The selected entity has already been specified as a party "
                "in the profile's social tenure relationship."
            )
            self._notif_bar_str.insertWarningNotification(msg)
            item.setCheckState(Qt.Unchecked)

            return

        # Add spatial unit item to view
        p = self.current_profile()
        if not p is None:
            sp_unit_entity = p.entity(sp_unit_name)
            self.dg_tenure.add_spatial_unit_entity(sp_unit_entity)

            t_type = self._sp_t_mapping.get(sp_unit_name, None)
            if t_type is None:
                # Set primary tenure type for the selected spatial unit
                p_tenure_vl = p.social_tenure.tenure_type_collection
                self._sp_t_mapping[sp_unit_name] = p_tenure_vl.short_name

    def _on_spatial_unit_deselected(self, item):
        # Handle deselection of a spatial unit entity
        # Remove spatial unit graphic item from the view
        sp_unit_name = item.text()
        self.dg_tenure.remove_spatial_unit(sp_unit_name)

        # Remove spatial unit from tenure mapping collection
        if sp_unit_name in self._sp_t_mapping:
            del self._sp_t_mapping[sp_unit_name]

    def load_configuration_from_file(self, file_name):
        """
        Load configuration object from the file.
        :return: True if the file was successfully
        loaded. Otherwise, False.
        :rtype: bool
        """
        config_serializer = ConfigurationFileSerializer(file_name)

        try:
            config_serializer.load()

        except IOError as io_err:
            QMessageBox.critical(self.iface.mainWindow(),
                                 self.tr('Load Configuration Error'),
                                 str(io_err)
                                 )

            return False

        except ConfigurationException as c_ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr('Load Configuration Error'),
                str(c_ex)
            )

            return False

        return True

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        profiles = []
        self.cboProfile.clear()
        for profile in self.stdm_config.profiles.values():
            for entity in profile.entities.values():
                self.connect_column_signals(entity)
            self.connect_entity_signals(profile)
            profiles.append(profile.name)
        self.cbo_add_profiles(profiles)

        self.lvLookups.setCurrentIndex(self.lvLookups.model().index(0, 0))
        self.lvEntities.setCurrentIndex(self.lvEntities.model().index(0, 0))

    def connect_column_signals(self, entity):
        """
        Connect signals triggered when column is added or deleted from an entity
        """
        entity.column_added.connect(self.add_column_item)
        entity.column_removed.connect(self.delete_column_item)

    def on_show_sp_units_tenure(self):
        """
        Shows dialog for specifying spatial unit tenure types.
        """
        self._notif_bar_str.clear()

        p = self.current_profile()
        can_edit = not p.str_table_exists
        sp_unit_tenure_dlg = SpatialUnitTenureTypeDialog(
            self,
            editable=can_edit
        )

        # Get the currently selected spatial units
        sel_sp_units = self.lst_spatial_units.spatial_units()

        # If there are no spatial units specified then inform user
        c = len(sel_sp_units)
        if c == 0:
            self._notif_bar_str.clear()
            msg = self.tr(
                "Please select at least one spatial unit in order to "
                "be able to specify the tenure type."
            )
            self._notif_bar_str.insertWarningNotification(msg)

            return

        p = self.current_profile()

        vl_names = [vl.short_name for vl in p.value_lists()]

        # Set applicable spatial units and tenure types in the dialog
        sp_unit_tenure_dlg.init([sel_sp_units, vl_names])

        social_tenure = self.current_profile().social_tenure

        # Get corresponding tenure types and assign default if not set
        for i, sp in enumerate(sel_sp_units):
            # Check from the initialized collection if the tenure had been set
            t_type = self._sp_t_mapping.get(sp, None)

            # Assign default tenure lookup if None
            if t_type is None:
                t_type = social_tenure.tenure_type_collection.short_name

            # Set spatial unit tenure type
            sp_unit_tenure_dlg.set_spatial_unit_tenure_type(
                sp,
                t_type
            )

            sp_unit_tenure_dlg.sp_tenure_view.openPersistentEditor(
                sp_unit_tenure_dlg.sp_tenure_view.model().index(i, 1)
            )

        if sp_unit_tenure_dlg.exec_() == QDialog.Accepted:
            self._sp_t_mapping = sp_unit_tenure_dlg.tenure_mapping()

    def _sync_custom_tenure_entities(self):
        # Synchronize list of custom attribute entities with selected
        # tenure types.

        p = self.current_profile()

        for tt in self._sp_t_mapping.values():
            if not tt in self._custom_attr_entities:
                c_ent = p.social_tenure.initialize_custom_attributes_entity(
                    tt
                )
                self._custom_attr_entities[tt] = c_ent

        # Remove tenure types not applicable in the list
        tt_names = self._sp_t_mapping.values()
        for tt_name in self._custom_attr_entities.keys():
            if tt_name not in tt_names:
                del self._custom_attr_entities[tt_name]

    def on_show_custom_attributes_editor(self):
        """
        Slot raised to show the dialog for editing custom tenure attributes.
        """
        # Sync tenure types
        custom_tenure_valid = self.check_spatial_unit_tenure_mapping()
        profile = self.current_profile()
        if not custom_tenure_valid:
            return False

        can_edit = not profile.str_table_exists

        # Initialize entity attribute editor
        custom_attr_editor = TenureCustomAttributesEditor(
            profile,
            self._custom_attr_entities,
            self,
            editable=can_edit,
            exclude_columns=[
                'id',
                'social_tenure_relationship_id',
                SocialTenure.CUSTOM_TENURE_DUMMY_COLUMN
            ]
        )
        custom_attr_editor.setWindowTitle(
            self.tr('Custom Tenure Attributes Editor')
        )

        if custom_attr_editor.exec_() == QDialog.Accepted:
            # Append columns to the custom attribute entities
            t_attrs = custom_attr_editor.custom_tenure_attributes
            for tt, attrs in t_attrs.items():
                ent = self._custom_attr_entities[tt]
                for attr in attrs:
                    ent.add_column(attr)

    def validate_STR(self):
        """
        Validate both Party & Spatial Unit entities for STR are properly set.
        Returns a tuple indicating the setting status and a status message.
        :rtype: tuple (boolean, str)
        """
        # check if any entities exist,
        if self.entity_model.rowCount() == 0:
            return False, self.tr(
                'No entities for creating social tenure relationship.'
            )

        # Validate parties
        if len(self.lst_parties.parties()) == 0:
            return False, self.tr(
                'Please select at least one party from the list of applicable '
                'party entities.'
            )

        # Validate spatial units
        if len(self.lst_spatial_units.spatial_units()) == 0:
            return False, self.tr(
                'Please select at least one spatial unit from the list of '
                'applicable spatial unit entities.'
            )

        # Validate date ranges
        if self.gb_start_dates.isChecked():
            if self.dt_start_minimum.date() > self.dt_start_maximum.date():
                msg = self.tr(
                    'Minimum start date is greater than maximum start date.'
                )
                return False, msg

        if self.gb_end_dates.isChecked():
            if self.dt_end_minimum.date() > self.dt_end_maximum.date():
                msg = self.tr(
                    'Minimum end date is greater than maximum end date.'
                )
                return False, msg

        if self.gb_start_dates.isChecked() and self.gb_end_dates.isChecked():
            if self.dt_start_minimum.date() >= self.dt_end_maximum.date():
                msg = self.tr(
                    'Minimum start date should be less than maximum end date.'
                )
                return False, msg

        return True, self.tr("Ok")

    def index_party_table(self, profile, model):
        """
        Returns an index of the selected party unit in STR
        :param profile: current selected profile
        :type profile: Profile
        :param model: custom entities model for views
        :type model: EntitiesModel
        """
        index = 0
        # first look if STR has been set for current profile, return
        # index of the set party
        if not profile.social_tenure.party is None:
            party_name = profile.social_tenure.party.short_name
            items = model.findItems(party_name)
            if len(items) > 0:
                index = items[0].row()
        else:
            for idx, entity in enumerate(self.entity_model.entities().values()):
                if entity.has_geometry_column():
                    continue
                else:
                    index = idx
                    break
        return index

    def index_spatial_unit_table(self, profile, model):
        """
        Returns an index of the selected spatial unit
        """
        index = 0
        # first look if STR has been set for current profile, return
        # that index
        if not profile.social_tenure.spatial_unit is None:
            spunit_name = profile.social_tenure.spatial_unit.short_name
            items = model.findItems(spunit_name)
            if len(items) > 0:
                index = items[0].row()
        else:
            for idx, entity in enumerate(model.entities().values()):
                if entity.has_geometry_column():
                    index = idx
                    break

        return index

    def find_empty_lookups(self):
        """
        Verifies that all lookups in the current profile
        have values. Returns true if all have values else false
        :rtype: bool
        """
        found_empty = False
        profile = self.current_profile()
        for vl in profile.value_lists():
            # don't bother with enities destined for deletion
            if vl.action == DbItem.DROP:
                continue
            if vl.is_empty():
                found_empty = True
                self.show_message(self.tr("Lookup %s has no values") % vl.short_name)
                break
        return found_empty

    def check_spatial_unit_tenure_mapping(self):
        """
        Checks if spatial unit is linked to tenure lookup.
        :return: The status of validity
        :rtype: Boolean
        """
        self._sync_custom_tenure_entities()
        profile = self.current_profile()
        social_tenure = profile.social_tenure
        spatial_units_tenure = profile.social_tenure.spatial_units_tenure
        custom_tenure_valid = True
        for spatial_unit in social_tenure.spatial_units:
            if spatial_unit.short_name not in spatial_units_tenure.keys():
                self._notif_bar_str.clear()
                msg = self.tr(
                    'No tenure types have been specified in the profile\'s social '
                    'tenure relationship.'
                )
                self._notif_bar_str.insertWarningNotification(msg)
                custom_tenure_valid = False
        return custom_tenure_valid

    def fmt_path_str(self, path):
        """
        Returns a directory path string formatted in a unix format
        :param path: string representing the windows path
        :type path: str
        :rtype: str
        """
        rpath = r''.join(str(path))
        return rpath.replace("\\", "/")

    def read_settings_path(self, reg_keys: list[str], os_path: str) ->str:
        """
        Returns path settings from the registry or an os folder path
        :param reg_key: list of registry keys to read the path setting
        :type reg_keys: list
        :param os_path: os directory to use if the reg_key is not set
        :type os_path: str
        :rtype: str
        """
        try:
            # returns a dict {reg_key:reg_value}
            key = self.reg_config.read(reg_keys)
            if len(key) > 0:
                reg_doc_path = key[reg_keys[0]]
            else:
                reg_doc_path = None
        except DummyException:
            reg_doc_path = None

        if reg_doc_path is not None:
            doc_path = self.verify_path(reg_doc_path)
        else:
            path = QDir.home().path() + os_path
            doc_path = self.verify_path(path)

        return doc_path

    def verify_path(self, path: str) ->str:
        """
        Returns a path after verifying that it exists in the os.
        The path is created if it does not exist.
        :param path: path from registry to verify
        :type path: str
        :rtype: str
        """
        qdir = QDir()
        if not qdir.exists(path):
            doc_path = self.make_os_path(path)
        else:
            doc_path = path
        return doc_path

    def make_os_path(self, path: str) ->str:
        """
        Creates and returns an os path
        :param path: path to create
        :type path: str
        :rtype: str
        """
        qdir = QDir()
        if not qdir.mkpath(path):
            path = ''
        return path

    def show_license(self):
        """
        Show STDM license file
        """
        self.txtLicense.clear()
        license = LicenseDocument()
        self.txtLicense.setText(license.read_license_info())

    def load_directory_path_settings(self):
        """
        Read and display default directory path settings
        """
        self.load_doc_path()
        self.load_output_path()
        self.load_template_path()

    def load_doc_path(self):
        """
        Read and display default document path
        """
        doc_path = self.read_settings_path([LOCAL_SOURCE_DOC],
                                           '/.stdm/documents/')
        self.edtDocPath.setText(doc_path)

    def load_output_path(self):
        """
        Read and display default report output path
        """
        output_path = self.read_settings_path([COMPOSER_OUTPUT],
                                              '/.stdm/reports/outputs')
        self.edtOutputPath.setText(output_path)

    def load_template_path(self):
        """
        Read and display default template path
        """
        templates_path = self.read_settings_path([COMPOSER_TEMPLATE],
                                                 '/.stdm/reports/templates')
        self.edtTemplatePath.setText(templates_path)

    def initializePage(self, id):
        if self.currentId() == 0:
            self.show_license()

        # STR page
        if id == 4:
            c_profile = self.current_profile()

            # Set profile in the corresponding controls in the STR page
            self.lst_parties.profile = c_profile
            self.lst_parties.social_tenure = c_profile.social_tenure
            self.lst_spatial_units.profile = c_profile
            self.lst_spatial_units.social_tenure = c_profile.social_tenure
            self.dg_tenure.profile = c_profile

            # Set spatial unit tenure mapping
            for sp, t in c_profile.social_tenure.spatial_units_tenure.items():
                self._sp_t_mapping[sp] = t.short_name

            # Set tenure custom attribute entities
            for tt, ent in c_profile.social_tenure.custom_attribute_entities.items():
                self._custom_attr_entities[tt] = ent

            # check if social tenure relationship has been setup
            if len(self.lst_parties.social_tenure.parties) > 0:
                entity = self.lst_parties.social_tenure.parties[0]
                self.set_str_controls(entity.name)
            else:
                self.enable_str_setup()

            # Set validity date ranges
            self._set_str_validity_ranges()

    def _set_str_validity_ranges(self):
        # Set the start/end validity dates if specified
        social_tenure = self.current_profile().social_tenure
        validity_start_col = social_tenure.validity_start_column
        validity_end_col = social_tenure.validity_end_column

        # Start range
        if validity_start_col.minimum > validity_start_col.SQL_MIN and \
                validity_start_col.maximum < validity_start_col.SQL_MAX:
            self.gb_start_dates.setChecked(True)
            self.dt_start_maximum.setDate(validity_start_col.maximum)
            self.dt_start_minimum.setDate(validity_start_col.minimum)

        # End range
        if validity_end_col.minimum > validity_end_col.SQL_MIN and \
                validity_end_col.maximum < validity_end_col.SQL_MAX:
            self.gb_end_dates.setChecked(True)
            self.dt_end_maximum.setDate(validity_end_col.maximum)
            self.dt_end_minimum.setDate(validity_end_col.minimum)

        # Suppress warning notifications
        self._notif_bar_str.clear()

    def bool_to_check(self, state):
        """
        Given a boolean returns a Qt checkstate.
        :param state: True/False
        :type state: boolean
        :rtype: Qt.CheckState
        """
        return CHECK_STATE[state]

    def multi_party_state_change(self):
        """
        Event handler for the multi party checkbox state change event.
        """
        profile = self.current_profile()
        profile.social_tenure.multi_party = \
            CHECKBOX_VALUES[self.cbMultiParty.checkState()]

    def set_multi_party_checkbox(self, profile):
        """
        Set the state of multi party checkbox from the current
        profile 'social_tenure.multi_party' attribute.
        :param profile: profile to extract multi party value
        :type profile: Profile
        """
        self.cbMultiParty.setCheckState(self.bool_to_check(
            profile.social_tenure.multi_party))

    def empty_text(self, text):
        """
        Validates if a unicode text is empty
        :rtype: boolean
        """
        if text.strip() == '':
            return True
        else:
            return False

    def validate_path_settings(self):
        """
        Validate for empty path settings, if path is empty
        returns a tuple of boolean and message
        :rtype: tuple (boolean, str)
        """
        error_msg = "Please enter {0} !"
        if self.empty_text(self.edtDocPath.text()):
            return False, self.tr(error_msg.format("'supporting documents path'"))

        if self.empty_text(self.edtOutputPath.text()):
            return False, self.tr(error_msg.format("'documents output path'"))

        if self.empty_text(self.edtTemplatePath.text()):
            return False, self.tr(error_msg.format("'documents template path'"))

        return True, "Ok."

    def set_str_controls(self, str_table: str):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        :param str_table: Social Tenure Relationship table
        :type str_table: str
        """
        self.enable_str_setup()
        if pg_table_exists(str_table):
            curr_profile = self.current_profile()
            curr_profile.str_table_exists = True
            self.disable_str_setup()

    def enable_str_setup(self):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        """
        self._enable_disable_str_ctrls(True)

    def disable_str_setup(self):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        """
        self._enable_disable_str_ctrls(False)

    def _enable_disable_str_ctrls(self, state):
        self.lst_parties.setEnabled(state)
        self.lst_spatial_units.setEnabled(state)
        self.gb_start_dates.setEnabled(state)
        self.gb_end_dates.setEnabled(state)
        self.dt_start_minimum.setEnabled(state)
        self.dt_start_maximum.setEnabled(state)
        self.dt_end_minimum.setEnabled(state)
        self.dt_end_maximum.setEnabled(state)

    def validateCurrentPage(self):
        validPage = True

        if self.nextId() == 2:
            validPage, msg = self.validate_path_settings()
            if not validPage:
                self.show_message(msg)
                return validPage

        if self.currentId() == 3:
            curr_profile = self.current_profile()

            idx1 = self.index_party_table(curr_profile, self.entity_model)

            self.set_multi_party_checkbox(curr_profile)

            # verify that lookup entities have values
            if self.find_empty_lookups():
                validPage = False

        if self.currentId() == 4:
            validPage, msg = self.validate_STR()

            if validPage:
                sp_tenure_status = self.check_spatial_unit_tenure_mapping()

                if not sp_tenure_status:
                    return
                profile = self.current_profile()
                st = profile.social_tenure

                # Set STR entities
                parties = self.lst_parties.parties()
                spatial_units = self.lst_spatial_units.spatial_units()

                profile.set_social_tenure_attr(SocialTenure.PARTY, parties)
                profile.set_social_tenure_attr(SocialTenure.SPATIAL_UNIT, spatial_units)

                # Date ranges
                if self.gb_start_dates.isChecked():
                    min_start_date = self.dt_start_minimum.date().toPyDate()
                    max_start_date = self.dt_start_maximum.date().toPyDate()

                    profile.set_social_tenure_attr(
                        SocialTenure.START_DATE,
                        (min_start_date, max_start_date)
                    )

                if self.gb_end_dates.isChecked():
                    min_end_date = self.dt_end_minimum.date().toPyDate()
                    max_end_date = self.dt_end_maximum.date().toPyDate()

                    profile.set_social_tenure_attr(
                        SocialTenure.END_DATE,
                        (min_end_date, max_end_date)
                    )

                # Set spatial units' tenure types
                for spu, tt in self._sp_t_mapping.items():
                    st.add_spatial_tenure_mapping(spu, tt)

                # Set custom attributes entity
                for tt, ent in self._custom_attr_entities.items():
                    # Check if the attributes entity exists in the profile
                    status = profile.has_entity(ent)
                    if not status:
                        profile.add_entity(ent, True)

                    st.add_tenure_attr_custom_entity(tt, ent)

            else:
                self.show_message(self.tr(msg))

        if self.currentId() == 5:  # FINAL_PAGE:
            # last page
            profile = self.current_profile()
            profile.description = self.edtDesc.text()

            # before any updates, backup your current working profile
            self.backup_config_file()

            # * commit config to DB
            self.config_updater = ConfigurationSchemaUpdater()

            ##*Thread to handle schema updating
            self.updater_thread = QThread(self)
            self.config_updater.moveToThread(self.updater_thread)

            ##*Connect schema updater slots
            self.config_updater.update_started.connect(self.config_update_started)
            self.config_updater.update_progress.connect(self.config_update_progress)
            self.config_updater.update_completed.connect(self.config_update_completed)

            ##*Connect thread signals
            self.updater_thread.started.connect(self._updater_thread_started)
            self.updater_thread.finished.connect(self.updater_thread.deleteLater)

            self.txtHtml.append(self.tr("Preparing configuration, please wait..."))

            ##*Start the process
            self.updater_thread.start()

            # write document paths to registry
            self.reg_config.write(
                {LOCAL_SOURCE_DOC: self.edtDocPath.text(),
                 COMPOSER_OUTPUT: self.edtOutputPath.text(),
                 COMPOSER_TEMPLATE: self.edtTemplatePath.text()
                 })

            # compute a new asset count
            self.orig_assets_count = len(self.stdm_config)

            # pause, allow user to read post-save messages
            self.pause_wizard_dialog()
            validPage = False

        return validPage

    def pause_wizard_dialog(self):
        """
        Pause the wizard before closing to allow user to
        read the message on the TextEdit widget
        """
        self.button(QWizard.BackButton).setEnabled(False)
        self.button(QWizard.CancelButton).setText(self.tr("Close"))

    def save_update_info(self, info, write_method):
        """
        Call `method` to save update information displayed on the TextEdit widget
        to file
        :param info: update information to save to file
        :type info: str
        :param write_method: function used to write the udpate info to file
        :type write_method:function
        """
        write_method(info)

    def append_update_file(self, info):
        """
        Append info to a single file
        :param info: update iformation to save to file
        :type info: str
        """
        file_name = os.path.expanduser('~') + '/.stdm/logs/configuration_update.log'
        info_file = open(file_name, "a")
        time_stamp = self.get_time_stamp()
        info_file.write('\n')
        info_file.write(time_stamp + '\n')
        info_file.write('\n')
        info_file.write(info)
        info_file.write('\n')
        info_file.close()

    def new_update_file(self, info):
        """
        Create an new file for each update
        :param info: update info to write to file
        :type info: str
        """
        fmt_date = datetime.now().strftime('%d%m%Y_%H.%M')
        logs_folder = self.get_folder(QDir.home().path() + '/.stdm/logs')
        file_name = logs_folder + '/configuration_update_' + fmt_date + '.log'
        info_file = open(file_name, "w")
        info_file.write(info)
        info_file.close()

    def get_folder(self, folder):
        qdir = QDir()
        if not qdir.exists(folder):
            qdir.mkpath(folder)
        return folder

    def get_time_stamp(self):
        """
        Return a formatted day of week and date/time
        """
        cdate = date.today()
        week_day = calendar.day_name[cdate.weekday()][:3]
        fmt_date = datetime.now().strftime('%d-%m-%Y %H:%M')
        time_stamp = week_day + ' ' + fmt_date
        return time_stamp

    def _updater_thread_started(self):
        """
        Slot for initiating the schema updating process.
        """
        self.config_updater.exec_()

    def config_update_started(self):
        self.button(QWizard.FinishButton).setEnabled(False)
        self.button(QWizard.CancelButton).setEnabled(False)
        self.button(QWizard.CustomButton1).setEnabled(False)

        QCoreApplication.processEvents()

        self.txtHtml.setFontWeight(75)
        self.txtHtml.append(QApplication.translate("Configuration Wizard",
                                                   "Configuration update started...")
                            )
        self.txtHtml.setFontWeight(50)

    def config_update_progress(self, info_id, msg):
        if info_id == 0:  # information
            self.txtHtml.setTextColor(QColor('black'))

        if info_id == 1:  # Warning
            self.txtHtml.setTextColor(QColor(255, 170, 0))

        if info_id == 2:  # Error
            self.txtHtml.setTextColor(QColor('red'))

        self.txtHtml.append(msg)

    def config_update_completed(self, status):
        self.button(QWizard.CancelButton).setEnabled(True)
        self.button(QWizard.CustomButton1).setEnabled(True)
        if status:
            self.txtHtml.setTextColor(QColor(51, 182, 45))
            self.txtHtml.setFontWeight(75)
            msg = QApplication.translate('Configuration Wizard',
                                         'The configuration has been '
                                         'successfully updated.')
            self.txtHtml.append(msg)
            self.is_config_done = True

            # Write config to a file
            cfs = ConfigurationFileSerializer(CONFIG_FILE)

            try:
                cfs.save()

                # Save current profile to the registry
                profile_name = str(self.cboProfile.currentText())
                save_current_profile(profile_name)

                # delete config backup file
                self.delete_config_backup_file()

                # delete draft config file
                self.delete_draft_config_file()

                self.draft_config = False

            except(ConfigurationException, IOError) as e:
                self.show_message(self.tr(str(e)))

        else:
            self.txtHtml.append(self.tr("Failed to update configuration. "
                                        "Check error logs."))
            self.is_config_done = False

        self.save_update_info(self.txtHtml.toPlainText(), self.new_update_file)

        # flag wizard has been run
        self.reg_config.write({'WizardRun': 1})

        # Exit thread
        self.updater_thread.quit()
        if status:
            self.wizardFinished.emit(self.cboProfile.currentText(), False)
        else:
            self.wizardFinished.emit(self.cboProfile.currentText(), True)
            self.orig_assets_count = len(self.stdm_config)

    def backup_config_file(self):
        """
        """
        cfs = ConfigurationFileSerializer(CONFIG_BACKUP_FILE)

        try:
            cfs.save()
        except(ConfigurationException, IOError) as e:
            self.show_message(self.tr(str(e)))

    def save_current_configuration(self, filename):
        """
        Write current configuration to a file
        :param filename: file to write too
        :type filename: str
        """
        cfs = ConfigurationFileSerializer(filename)

        try:
            cfs.save()
        except(ConfigurationException, IOError) as e:
            self.show_message(self.tr(str(e)))

    def delete_config_backup_file(self):
        QFile.remove(CONFIG_BACKUP_FILE)

    def delete_draft_config_file(self):
        QFile.remove(DRAFT_CONFIG_FILE)

    def register_fields(self):
        self.setOption(self.HaveHelpButton, True)
        page_count = self.page(1)
        page_count.registerField(self.tr("Accept"), self.rbAccpt)
        page_count.registerField(self.tr("Reject"), self.rbReject)

    def configure_custom_button1(self):
        self.setButtonText(QWizard.CustomButton1, self.tr('Options'))
        menu = QMenu()
        self.save_draft_action = menu.addAction('Save draft', self.save_draft)
        self.discard_draft_action = menu.addAction('Discard draft', self.discard_draft)
        self.button(QWizard.CustomButton1).setMenu(menu)

        self.button(QWizard.CustomButton1).pressed.connect(self.custom_button_clicked)

    def custom_button_clicked(self):
        # self.save_draft_action.setEnabled(self.configuration_is_dirty())
        self.discard_draft_action.setEnabled(self.draft_config)

    def save_draft(self):
        '''
        Save a draft configuration
        '''
        self.save_current_configuration(DRAFT_CONFIG_FILE)
        current_profile_name = self.cboProfile.currentText()
        self.load_stdm_config(DRAFT_CONFIG_FILE)
        self.refresh_config(current_profile_name)

    def refresh_config(self, profile_name):
        # config_file = self.get_config_file()
        # self.load_stdm_config(config_file)
        self.switch_profile(profile_name)
        self.set_current_profile(profile_name)
        self.set_window_title()

    def discard_draft(self):
        '''
        Delete draft configuration
        '''
        msg = self.tr('Are you sure you want to discard the draft profile?')
        if self.query_box_yesno(msg) == QMessageBox.Yes:
            self.delete_draft_config_file()
            self.draft_config = False
            config_file = self.get_config_file()
            self.load_stdm_config(config_file)
            self.set_window_title()

    def set_support_doc_path(self):
        """
        OnClick event handler for the supporting document path selection button
        """
        try:
            dir_name = self.open_dir_chooser( \
                self.tr("Select a directory for supporting documents"),
                str(self.edtDocPath.text()))

            if len(dir_name.strip()) > 0:
                self.edtDocPath.setText(dir_name)
        except DummyException:
            LOGGER.debug("Error setting support document path!")
            raise

    def set_output_path(self):
        """
        OnClick event handler for the document output path selection button
        """
        try:
            dir_name = self.open_dir_chooser(QApplication.translate( \
                "STDM Configuration",
                "Select a directory for outputting generated documents"),
                str(self.edtOutputPath.text()))

            if len(dir_name.strip()) > 0:
                self.edtOutputPath.setText(dir_name)
        except DummyException:
            LOGGER.debug("Error setting support document path!")

    def set_template_path(self):
        """
        OnClick event handler for the documents template path selection button
        """
        try:
            dir_name = self.open_dir_chooser(QApplication.translate( \
                "STDM Configuration",
                "Select a directory for document templates"),
                str(self.edtTemplatePath.text()))

            if len(dir_name.strip()) > 0:
                self.edtTemplatePath.setText(dir_name)
        except DummyException:
            LOGGER.debug("Error setting support document path!")

    def open_dir_chooser(self, message, dir=None):
        """
        Returns a selected folder from the QFileDialog
        :param message:message to show on the file selector
        :type message: str
        """
        sel_dir = str(QFileDialog.getExistingDirectory(
            self, self.tr("Select Folder"), ""))
        return sel_dir

    def add_entity_item(self, entity):
        """
        param entity: Instance of a new entity
        type entity: BaseColumn
        """
        if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                                    'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                                    'ENTITY_SUPPORTING_DOCUMENT', 'VALUE_LIST', 'ASSOCIATION_ENTITY']:
            self.entity_model.add_entity(entity)

        # if entity is a supporting document, add it to the Valuelist view model
        if entity.TYPE_INFO == 'VALUE_LIST' and entity.action != DbItem.DROP:
            self.lookup_view_model.add_entity(entity)

    def delete_entity_item(self, name):
        """
        Removes an entity from a model
        param name: Name of entity to delete
        type name: str
        """
        items = self.entity_model.findItems(name)
        if len(items) > 0:
            self.entity_model.removeRow(items[0].row())

    def populate_spunit_model(self, profile):
        self.STR_spunit_model.entities().clear()
        for entity in profile.entities.values():
            if entity.action == DbItem.DROP:
                continue

            if entity.TYPE_INFO not in EXCL_ENTITIES and \
                    entity.has_geometry_column():
                self.STR_spunit_model.add_entity(entity)

    def delete_entity_from_spatial_unit_model(self, entity):
        """
        Removes an entity with NO geometry column from a
        spatial unit model.
        param name: Name of entity to delete
        type name: str
        """
        if not entity.has_geometry_column():
            items = self.STR_spunit_model.findItems(entity.short_name)
            if len(items) > 0:
                self.STR_spunit_model.removeRow(items[0].row())

            self.STR_spunit_model.delete_entity_byname(entity.short_name)

    def cbo_add_profile(self, profile):
        """
        param profile: List of profile to add in a combobox
        """
        profiles = []
        profiles.append(profile.name)
        self.cboProfile.insertItems(0, profiles)
        self.cboProfile.setCurrentIndex(0)

    def cbo_add_profiles(self, profiles):
        """
        param profiles: list of profiles to add in the profile combobox
        type profiles: list
        """
        self.cboProfile.insertItems(0, profiles)

    def set_current_profile(self, name):
        if name != '':
            index = self.cboProfile.findText(name, Qt.MatchFixedString)
            if index >= 0:
                self.cboProfile.setCurrentIndex(index)
        else:
            if self.cboProfile.count() > 0:
                self.cboProfile.setCurrentIndex(0)

    # PROFILE
    def new_profile(self):
        """
        Event handler for creating a new profiled
        """
        # self.pftableView.removeEventFilter(self)
        # self.tbvColumns.removeEventFilter(self)

        editor = ProfileEditor(self)
        result = editor.exec_()
        if result == 1:
            profile = self.stdm_config.create_profile(editor.profile_name)

            self.new_profiles.append(editor.profile_name)
            profile.description = editor.desc
            self.connect_entity_signals(profile)
            self.stdm_config.add_profile(profile)

        # self.pftableView.installEventFilter(self)
        # self.tbvColumns.installEventFilter(self)
        # self.switch_profile(self.cboProfile.currentText())

    def connect_entity_signals(self, profile):
        """
        Connects signals to emit when an entity is added or removed from a
        profile
        :param profile: Profile that emits the signals
        :type profile: Profile
        """
        profile.entity_added.connect(self.add_entity_item)
        profile.entity_removed.connect(self.delete_entity_item)

    def current_profile(self) -> Profile:
        """
        Returns an instance of the selected profile in the
        profile combobox
        """
        profile = None
        prof_name = self.cboProfile.currentText()
        if len(prof_name) > 0:
            profile = self.stdm_config.profile(str(prof_name))
        return profile

    def delete_profile(self):
        """
        Delete the current selected profile, but not the last one.
        """
        profile_name = str(self.cboProfile.currentText())

        if self.cboProfile.count() == 1:
            msg = self.tr('{0} profile cannot be deleted. At least one '
                          'profile is required to exist in the '
                          'STDM configuration. ').format(profile_name)

            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     msg), QMessageBox.Warning)
            return

        msg = self.tr('You will loose all items related to this profile i.e \n'
                      'entities, lookups and Social Tenure Relationships.\n'
                      'Are you sure you want to delete this profile?')
        if self.query_box(msg) == QMessageBox.Cancel:
            return

        if not self.stdm_config.remove_profile(profile_name):
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "Unable to delete profile!"))
            return

        self.load_profile_cbo()

    def copy_profile(self):
        '''
        Create a copy of the current profile
        '''
        current_profile_name = self.cboProfile.currentText()
        orig_description = self.edtDesc.text()

        profile_names = self.profile_names()
        editor = CopyProfileEditor(self, current_profile_name, orig_description, profile_names)
        result = editor.exec_()

        if result == 1:
            if not self.draft_config:
                self.save_current_configuration(DRAFT_CONFIG_FILE)
                self.draft_config = True

            copy_profile_name = editor.copy_name
            copy_profile_desc = editor.copy_desc

            self.make_profile_copy(current_profile_name,
                                   copy_profile_name, DRAFT_CONFIG_FILE)

            self.load_stdm_config(DRAFT_CONFIG_FILE)
            self.refresh_config(copy_profile_name)

            copied_profile = self.current_profile()
            copied_profile.description = copy_profile_desc
            self.edtDesc.setText(copy_profile_desc)
            new_prefix = self.stdm_config.prefix_from_profile_name(copy_profile_name)

            copied_profile.set_prefix(new_prefix)
            copied_profile.str_table_exists = False

    def profile_names(self):
        '''
        Returns names of profiles in the profiles combobox
        :rtype: list - of string
        '''
        names = []
        for index in range(self.cboProfile.count()):
            names.append(self.cboProfile.itemText(index))
        return names

    def get_profiles(self):
        """
        Returns a list of profiles from the StdmConfiguration instance.
        :rtype: list - of Profile
        """
        profiles = []
        for profile in self.stdm_config.profiles.items():
            profiles.append(profile[0])

        return profiles

    def load_profile_cbo(self):
        """
        Populate profile combobox with list of profiles.
        """
        profiles = self.get_profiles()
        self.cboProfile.clear()
        self.cboProfile.insertItems(0, profiles)
        self.cboProfile.setCurrentIndex(0)

    def add_column_item(self, column):
        """
        Event handler to add new column to various view models
        :param column: instance of BaseColumn to add
        :type column: BaseColumn
        """
        self.col_view_model.add_entity(column)
        self.party_item_model.add_entity(column)
        self.spunit_item_model.add_entity(column)

    def delete_column_item(self):
        """
        Event handler for removing column item from various view models
        """
        model_item, column, row_id = self.get_model_entity(self.tbvColumns)
        if column is None:
            return
        self.col_view_model.delete_entity(column)
        self.col_view_model.removeRow(row_id)
        self.party_item_model.removeRow(row_id)
        self.spunit_item_model.removeRow(row_id)

    def new_entity(self):
        """
        Creates a new entity and adds it to the current profile
        """
        profile = self.current_profile()
        if profile:
            params = {}
            params['parent'] = self
            params['profile'] = profile
            editor = EntityEditor(**params)
            editor.exec_()
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No profile selected to add entity!"))

    def edit_entity(self):
        """
        Event handler for editing an entity
        """
        if len(self.pftableView.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "Please select an entity to edit!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.pftableView)

        if model_item:
            profile = self.current_profile()
            in_db = pg_table_exists(entity.name)

            tmp_short_name = copy.deepcopy(entity.short_name)

            params = {}
            params['parent'] = self
            params['profile'] = profile
            params['entity'] = entity
            params['in_db'] = in_db

            editor = EntityEditor(**params)
            result = editor.exec_()

            if result == 1:
                model_index_name = model_item.index(row_id, 0)
                model_index_sd = model_item.index(row_id, 1)
                model_index_desc = model_item.index(row_id, 2)

                model_item.setData(model_index_name, editor.entity.short_name)
                model_item.setData(model_index_sd, 
                                   self._bool_to_yesno(editor.entity.supports_documents))
                model_item.setData(model_index_desc, editor.entity.description)

                model_item.edit_entity(tmp_short_name, editor.entity)

                self.clear_view_model(self.STR_spunit_model)
                self.populate_spunit_model(profile)

                self.refresh_lookup_view()

    def delete_entity(self):
        """
        Delete selected entity
        """
        if len(self.pftableView.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No entity selected for deletion!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.pftableView)

        if model_item:
            dependencies = entity.dependencies()
            if len(dependencies['entities']) > 0 or len(dependencies['views']) > 0:
                entity_depend = EntityDepend(self, entity, dependencies)
                result = entity_depend.exec_()
                if result == 0:
                    return

            self.entity_item_model.selectionChanged.disconnect()
            model_item.delete_entity(entity)
            # delete entity from selected profile
            profile = self.current_profile()
            profile.remove_entity(entity.short_name)

            self.init_entity_item_model()
            self.entity_item_model.selectionChanged.connect(self.entity_changed)
            self.trigger_entity_change()

            self.clear_view_model(self.STR_spunit_model)
            self.populate_spunit_model(profile)

    def column_exist_in_entity(self, entity, column):
        """
        Returns True if a column exists in a given entity in DB
        :param entity: Entity instance to check if column exist
        :type entity: Entity
        :param column: Column instance to check its existance
        :type entity: BaseColumn
        :rtype: boolean
        """
        cols = table_column_names(entity.name)
        return True if column.name in cols else False

    def entity_has_records(self, entity):
        """
        Returns True if entity has records in the database else False.
        :param entity: Entity instance
        :type entity: Entity
        :rtype: boolean
        """
        if not pg_table_exists(entity.name):
            return False

        record_count = pg_table_record_count(entity.name)
        return True if record_count > 0 else False

    def clear_view_model(self, view_model):
        rows = view_model.rowCount()
        for i in range(rows):
            view_model.removeRow(i)
        view_model.clear()

    def set_view_model(self, view_model):
        """
        Attach model to table views, list views and combobox widgets
        :param view_model: custom EntitiesModel
        :type view_model: EntitiesModel
        """
        self.pftableView.setModel(view_model)
        self.pftableView.setColumnWidth(0, 200)
        self.pftableView.setColumnWidth(1, 260)
        self.lvEntities.setModel(view_model)


    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
                continue

            if hasattr(entity, 'user_editable') and entity.TYPE_INFO != 'VALUE_LIST':
                if entity.user_editable == False:
                    continue

            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                                        'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                                        'ENTITY_SUPPORTING_DOCUMENT', 'ASSOCIATION_ENTITY']:

                if entity.TYPE_INFO == 'VALUE_LIST':
                    self.lookup_view_model.add_entity(entity)
                    self.addValues_byEntity(entity)
                else:
                    self.entity_model.add_entity(entity)

    def connect_signals(self):
        self.init_entity_item_model()

        self.lookup_item_model = self.lvLookups.selectionModel()
        self.lookup_item_model.selectionChanged.connect(self.lookup_changed)

    def drop_entity_event(self, event):
        tv = self.pftableView
        profile = self.current_profile()
        if profile is None:
            return False
        for i in range(tv.model().rowCount()):
            midx = tv.model().index(i, 0)
            name = tv.model().data(midx)
            row = midx.row()
            profile.update_entity_row_index(name, row)
        profile.sort_entities()
        return True

    def drop_column_event(self, event):
        ev = self.lvEntities
        cv = self.tbvColumns

        model_item, entity, row_id = self.get_model_entity(ev)

        if entity is None:
            return False

        for i in range(cv.model().rowCount()):
            midx = cv.model().index(i, 0)
            col_name = cv.model().data(midx)
            row = midx.row()
            entity.update_column_row_index(col_name, row)
        entity.sort_columns()
        return True

    def eventFilter(self, object, event):
        if object is self.pftableView:
            if event.type() == QEvent.ChildRemoved:
                self.drop_entity_event(event)
                event.accept()
                return True

        if object is self.tbvColumns:
            if event.type() == QEvent.ChildRemoved:
                self.drop_column_event(event)
                event.accept()
                return True
        return False

    def switch_profile(self, name):
        """
        Used to refresh all QStandardItemModel's attached to various
        view widgets in the wizard.
        :param name: name of the new profile to show
        :type name: str
        """
        if not name:
            return

        profile = self.stdm_config.profile(str(name))
        if profile is None:
            return
        self.edtDesc.setText(profile.description)
        # clear view models
        self.clear_view_model(self.entity_model)
        self.clear_view_model(self.col_view_model)
        self.clear_view_model(self.lookup_view_model)
        self.clear_view_model(self.lookup_value_view_model)
        self.clear_view_model(self.party_item_model)
        # self.clear_view_model(self.spunit_item_model)
        self.clear_view_model(self.STR_spunit_model)

        self.entity_model = EntitiesModel()
        self.set_view_model(self.entity_model)

        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)

        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)
        self.lvLookupValues.setModel(self.lookup_value_view_model)

        # from profile entities to view_model
        self.populate_view_models(profile)
        self.populate_spunit_model(profile)

        self.connect_signals()
        self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0, 0))

        enable_drag_sort(self.tbvColumns)
        enable_drag_sort(self.lvLookupValues)
        enable_drag_sort(self.pftableView)

        self.pftableView.setDropIndicatorShown(True)
        self.pftableView.setDragEnabled(True)
        self.pftableView.setAcceptDrops(True)
        self.pftableView.setDragDropMode(QTableView.DragDrop)
        self.pftableView.setDefaultDropAction(Qt.MoveAction)

        self._custom_attr_entities = {}

    def refresh_entity_view(self):
        self.clear_view_model(self.entity_model)
        self.entity_model = EntitiesModel()
        self.set_view_model(self.entity_model)
        self.populate_view_models(self.current_profile())

    def refresh_lookup_view(self):
        """
        Reloads the lookups after editing an entity.
        """
        self.clear_view_model(self.lookup_view_model)

        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)

        profile = self.current_profile()
        self.populate_lookup_view(profile)

        self.lookup_item_model = self.lvLookups.selectionModel()
        self.lookup_item_model.selectionChanged.connect(self.lookup_changed)
        self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0, 0))

    def refresh_columns_view(self, entity):
        """
        Clears columns in the column view model associated
        with the columns Table View then re-inserts columns from
        the entity
        """
        self.clear_view_model(self.col_view_model)
        self.col_view_model = ColumnEntitiesModel()
        #self.tbvColumns.setModel(self.col_view_model)
        self.tbvColumns.setModel(self.columns_proxy_model)
        self.populate_columns_view(entity)

    def profile_changed(self, row_id):
        """
        Event handler for the profile combobox current index changed.
        """
        self.switch_profile(self.cboProfile.currentText())

    def get_model_entity(self, view):
        """
        Extracts and returns an entitymodel, entity and the
        current selected item ID from QAbstractItemView of a
        given view widget
        param view: Widget that inherits QAbstractItemView
        type view: QAbstractitemView
        rtype: tuple - (QStandardItemModel, Entity, int)
        """
        sel_id = -1
        entity = None
        model_indexes = view.selectedIndexes()
        if len(model_indexes) == 0:
            return (None, None, None)
        model_index = model_indexes[0]
        model_item = model_index.model()
        name = model_item.data(model_index)
        entity = model_item.entity(name)
        row = model_index.row()

        return (model_item, entity, row)

    def addColumns(self, v_model, columns):
        """
        Add columns to a view model
        param v_model: Instance of EntitiesModel
        type v_model: EntitiesModel
        param columns: List of column names to insert in v_model
        type columns: list
        """
        for column in columns:
            if column.user_editable():
                v_model.add_entity(column)

    def entity_changed(self, selected, diselected):
        """
        triggered when you select an entity, clears an existing column entity
        model and create a new one.
        Get the columns of the selected entity, add them to the newly created
        column entity model
        """
        self.trigger_entity_change()

    def trigger_entity_change(self):
        row_id = self.entity_item_model.currentIndex().row()
        view_model = self.entity_item_model.currentIndex().model()
        self.col_view_model.clear()
        self.col_view_model = ColumnEntitiesModel()

        if row_id > -1:
            # columns = view_model.entity_byId(row_id).columns.values()
            ent_name = view_model.data(view_model.index(row_id, 0))

            entity = view_model.entity(ent_name)
            if entity is None:
                return
            columns = list(view_model.entity(ent_name).columns.values())
            self.addColumns(self.col_view_model, columns)

            self.tbvColumns.setModel(self.col_view_model)
        self.size_columns_viewer()

    def entity_clicked(self, model_index: QModelIndex):
        _ ,entity, _ = self.get_selected_item_data(self.lvEntities)
        if entity is None:
            return
        profile = current_profile()
        if profile is None:
            return
        entity_name = entity.name.replace(f'{profile.prefix}_', '')
        s_doc = f'check_{entity_name}_document_type'
        self.highlight_lookup(s_doc)

    def highlight_lookup(self, lookup_name: str = ''):
        if lookup_name == '':
            return

        self.lvLookups.clearSelection()
        start_index = self.lvLookups.model().index(0, 0)
        matches = self.lvLookups.model().match(
            start_index,
            Qt.DisplayRole,
            lookup_name,
            hits=1,
            flags=Qt.MatchContains
        )
        if matches:
            current_index = matches[0]
            self.lvLookups.selectionModel().select(
                current_index, QItemSelectionModel.Select
            )
            self.lookup_item_model.setCurrentIndex(current_index, QItemSelectionModel.Select)
            self.lvLookups.clicked.emit(current_index)

            self.clear_previous_selection()
            font = QFont()
            font.setBold(True)
            self.lvLookups.selectionModel().model().setData(
                current_index,
                font, 
                Qt.FontRole
            )
            self.selected_index = current_index

    def size_columns_viewer(self):
        NAME = 0
        TYPE = 1
        DESC = 2

        self.tbvColumns.setColumnWidth(NAME, 200)
        self.tbvColumns.setColumnWidth(TYPE, 180)
        self.tbvColumns.setColumnWidth(DESC, 200)

    def spatial_unit_changed(self, row_id):
        """
        Event handler for STR spatial unit combobox - event currentIndexChanged.
        :param row_id: index of the selected item in the combobox
        :type row_id: int
        """
        cbo_model = self.cboSPUnit.model()
        try:
            columns = list(cbo_model.entity_byId(row_id).columns.values())
            self.spunit_item_model.clear()
            self.spunit_item_model = STRColumnEntitiesModel()
            self.addColumns(self.spunit_item_model, columns)
        except DummyException:
            pass

    def new_column(self):
        """
        On click event handler for adding a new column
        """
        if len(self.lvEntities.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No entity selected to add column!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.lvEntities)

        if model_item:
            profile = self.current_profile()
            params = {}
            params['parent'] = self
            params['entity'] = entity
            params['profile'] = profile
            params['is_new'] = True
            params['entity_has_records'] = self.entity_has_records(entity)

            editor = ColumnEditor(**params)
            result = editor.exec_()

            if result == 1:
                entity.add_column(editor.column)

                if editor.type_info == 'LOOKUP':
                    self.clear_lookup_view()
                    self.populate_lookup_view(profile)
                    self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0, 0))

                # add this entity to STR spatial unit list of selection.
                if editor.type_info == 'GEOMETRY':
                    self.STR_spunit_model.add_entity(entity)

                row = self.tbvColumns.model().rowCount() - 1
                self.tbvColumns.selectRow(row)
                self.tbvColumns.scrollToBottom()

                midx = self.tbvColumns.model().index(row, 0)
                profile.update_entity_row_index(editor.column.name, midx.row())

                # Update privileges for entities that already exists in the database.
                if pg_table_exists(entity.name):
                    self.process_privilege(entity, editor.column)

    def clear_previous_selection(self):
        if self.selected_index == None:
            return
        font = QFont()
        font.setBold(False)
        self.lvLookups.selectionModel().model().setData(
            self.selected_index,
            font,
            Qt.FontRole
        )

    def column_clicked(self, model_index: QModelIndex):
        _ ,column, _ = self.get_selected_item_data(self.tbvColumns)
        lookup_name = ''
        if column.TYPE_INFO == 'LOOKUP': 
            lookup_name = column.parent.short_name

        if column.TYPE_INFO == 'MULTIPLE_SELECT':
            lookup_name = column.value_list.short_name

        self.highlight_lookup(lookup_name)

    def edit_column(self):
        """
        Event handler for editing a column.
        """
        CHECK_STATE = {True: 'Yes', False: 'No'}

        if len(self.tbvColumns.selectedIndexes()) == 0:
            self.show_message(self.tr("Please select a column to edit"))
            return

        rid, column, model_item = self.get_selected_item_data(self.tbvColumns)
        if rid == -1:
            return


        #if column and column.action == DbItem.CREATE:

        _, entity = self._get_entity(self.lvEntities)

        profile = self.current_profile()
        params = {}
        params['parent'] = self
        params['column'] = column
        params['entity'] = entity
        params['profile'] = profile
        params['in_db'] = self.column_exist_in_entity(entity, column)
        params['entity_has_records'] = self.entity_has_records(entity)

        params['is_new'] = False

        original_column = column  # model_item.entity(column.name)

        editor = ColumnEditor(**params)
        result = editor.exec_()

        if result == 1:

            editor.column.action = DbItem.ALTER
            entity.action = DbItem.ALTER

            model_index_name = model_item.index(rid, 0)
            model_index_dtype = model_item.index(rid, 1)
            model_index_mandt = model_item.index(rid, 2)
            model_index_unique = model_item.index(rid, 3)
            model_index_desc = model_item.index(rid, 4)

            data_type_name = editor.column.display_name()
            if editor.column.TYPE_INFO == 'VARCHAR':
                data_type_name = f'{data_type_name} ({editor.column.maximum})'

            model_item.setData(model_index_name, editor.column.name)
            model_item.setData(model_index_dtype, data_type_name)
            model_item.setData(model_index_mandt, CHECK_STATE[editor.column.mandatory] )
            model_item.setData(model_index_unique, CHECK_STATE[editor.column.unique])
            model_item.setData(model_index_desc, editor.column.description)

            model_item.edit_entity(original_column, editor.column)

            entity.columns[original_column.name] = editor.column
            entity.rename_column(original_column.name, editor.column.name)

            editor.column.mandatory_in_db = editor.column.name in self.mandt_cols
            unique_name = f'unq_{editor.column.entity.name}_{editor.column.name}'
            editor.column.unique_in_db = unique_name in self.unique_cols

            StdmConfiguration.instance().profile(profile.name).entities[entity.short_name].append_updated_column(editor.column)

            self.populate_spunit_model(profile)

            if pg_table_exists(entity.name):
                self.process_privilege(entity, editor.column)

        # else:
        #     self.show_message(QApplication.translate("Configuration Wizard", \
        #                                              "No column selected for edit!"))

    def process_privilege(self, entity, column):
        # if a new column is lookup, then assign privileges to that lookup
        new_content = None
        if self.column_has_entity_relation(column):
            new_content = column.entity_relation.parent.name
        if isinstance(column, MultipleSelectColumn):
            new_content = column.association.first_parent.name

        if new_content is None: return
        self.update_privilege_cache(entity, column, new_content)

    def column_has_entity_relation(self, column):
        answer = False
        if (isinstance(column, ForeignKeyColumn) or
                isinstance(column, AdministrativeSpatialUnitColumn)):
            answer = True
        return answer

    def update_privilege_cache(self, entity, column, new_content):
        if entity.short_name not in self.privileges:
            mpp = MultiPrivilegeProvider(entity.short_name)
            mpp.add_related_content(column.name, new_content)
            self.privileges[entity.short_name] = mpp
        else:
            self.privileges[entity.short_name].add_related_content(
                column.name, new_content)

    def delete_privilege_cache(self, entity_name, column_name):
        if entity_name in self.privileges:
            self.privileges[entity_name].related_contents.pop(column_name, None)

    def grant_privileges(self):
        # mpp - MultiPrivilegeProvider
        for mpp in self.privileges.values():
            mpp.grant_privilege()

    def find_updated_value(self, lookup, text):
        cv = None
        for code_value in lookup.values.values():
            if code_value.updated_value == text:
                cv = code_value
                break
        return cv

    def clear_lookup_view(self):
        """
        Clears items from the model attached to the lookup view
        """
        self.clear_view_model(self.lookup_view_model)
        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)
        self.lookup_item_model = self.lvLookups.selectionModel()
        self.lookup_item_model.selectionChanged.connect(self.lookup_changed)

    def populate_lookup_view(self, profile):
        """
        Fills the lookup view model with lookup entites from a
        given profile.
        :param profile: profile to extract lookups
        :type profile: Profile
        """
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
                continue
            if entity.TYPE_INFO == 'VALUE_LIST':
                self.lookup_view_model.add_entity(entity)
                self.addValues_byEntity(entity)

    def populate_columns_view(self, entity):
        for column in entity.columns.values():
            if column.action == DbItem.DROP:
                continue
            if column.TYPE_INFO == 'SERIAL':
                continue
            self.col_view_model.add_entity(column)

    def _get_entity_item(self, view):
        """
        Helper function to extract item model from a listview
        :param view: Listview to extract a model
        :type view: QListView
        :rtype: tuple (int, EntitiesModel)
        """
        model_item, entity, row_id = self.get_model_entity(view)
        entity_item = None
        if model_item:
            entity_item = list(model_item.entities().values())[row_id]
        return row_id, entity_item, model_item

    def _get_entity(self, view):
        model_item, entity, row_id = self.get_model_entity(view)
        if entity:
            return row_id, entity

    def get_selected_item_data(self, view: QTableView) -> tuple[int, 'Column', 'QAbstractItemModel']:
        if len(view.selectedIndexes()) == 0:
            return -1, None, None
        model_item = view.model()
        row_id = view.selectedIndexes()[0].row()
        col_name = view.model().data(
            view.model().index(row_id, 0))
        column = model_item.entities()[str(col_name)]
        return row_id, column, model_item

    def delete_column(self):
        """
        Delete selected column but show warning dialog if a
        column has dependencies.
        """
        _, column, model_item = self.get_selected_item_data(self.tbvColumns)
        if column is None:
            return
        if not column:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No column selected for deletion!"))
            return

        if self.column_has_entity_relation(column):
            results = self.check_column_dependencies(column)
            if results == False:
                return

        ent_id, entity = self._get_entity(self.lvEntities)

        # delete column from the entity
        entity.remove_column(column.name)

        model_item.delete_entity(column)

        self.delete_entity_from_spatial_unit_model(entity)

        if self.column_has_entity_relation(column):
            self.delete_privilege_cache(entity.short_name, column.name)

    def export_columns(self):
        if len(self.lvEntities.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No entity selected to export columns!"))
            return
        model_item, entity, row_id = self.get_model_entity(self.lvEntities)
        entity_item_model = self.lvEntities.selectionModel()
        view_model = entity_item_model.currentIndex().model()
        ent_name = view_model.data(view_model.index(row_id, 0))
        columns = list(view_model.entity(ent_name).columns.values())
        if len(columns) == 0:
            return
        
        dest_path, _ = QFileDialog.getSaveFileName(self, self.tr("Configuration"),
                                                   ent_name,
                                                   "{0} (*.csv)".format(self.tr('Export files')))
                                                
        if not dest_path:
            return
        
        with open(dest_path, 'w') as f:
            for column in columns:
                if column.user_editable():
                    data_type_name = column.TYPE_INFO
                    if column.TYPE_INFO == 'VARCHAR':
                        data_type_name = f'{data_type_name} ({column.maximum})'
                    row = f"{column.name},{data_type_name}\n"
                    f.write(row)
        self.show_message("Export done.")

    def check_column_dependencies(self, column):
        """
        Checks if a columns has dependencies,
        :param column: column to check for dependencies.
        :type column: BaseColumn
        :rtype: boolean
        """
        ok_delete = True
        dependencies = column.dependencies()
        if len(dependencies['entities']) > 0 or len(dependencies['views']) > 0:
            # show dependencies dialog
            column_depend = ColumnDepend(self, column, dependencies)
            result = column_depend.exec_()
            # 0 - user chose not to delete column
            if result == 0:
                ok_delete = False

        return ok_delete

    def new_lookup(self):
        """
        Event handler for adding a new lookup to the current profile
        """
        profile = self.current_profile()
        if profile:
            editor = LookupEditor(self, profile)
            result = editor.exec_()

            if result == 1:
                self.lookup_view_model.add_entity(editor.lookup)
                self.refresh_lookup_view()
                qm = self.lvLookups.model().index(
                    self.lvLookups.model().rowCount() - 1, 0)
                self.lvLookups.setCurrentIndex(qm)
                self.lvLookups.setFocus()

        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No profile selected to add lookup!"))

    def lookup_selection_changed(self, current_index: QModelIndex, prev_index: QModelIndex):
        font = QFont()
        font.setBold(False)
        self.lvLookups.selectionModel().model().setData(
            prev_index,
            font,
            Qt.FontRole
        )

    def lookup_clicked(self, model_index: QModelIndex):
        self.clear_previous_selection()
        self.lookup_changed(None, None)

    def edit_lookup(self):
        """
        Event handler for editing a lookup. Editing is only allowed to lookups
        that have not yet been saved in the database.
        """
        profile = self.current_profile()

        if profile is None:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "Nothing to edit!"))
            return

        if len(self.lvLookups.selectedIndexes()) == 0:
            self.show_message(self.tr("Please select a lookup to edit!"))
            return

        row_id, lookup, model_item = self.get_selected_item_data(self.lvLookups)
        if row_id == -1:
            return
        tmp_short_name = copy.deepcopy(lookup.short_name)
        lookup.entity_in_database = False  # pg_table_exists(lookup.name)

        editor = LookupEditor(self, profile, lookup)
        result = editor.exec_()

        if result == 1:
            model_index_name = model_item.index(row_id, 0)
            model_item.setData(model_index_name, editor.lookup.short_name)
            model_item.edit_entity(tmp_short_name, editor.lookup)

            profile.entities[tmp_short_name] = editor.lookup
            profile.entities[editor.lookup.short_name] = \
                profile.entities.pop(tmp_short_name)

            profile.remove_entity(tmp_short_name)

        self.lvLookups.setFocus()

    def scroll_to_bottom(self, table_view, scroll_position):
        table_view.selectRow(table_view.model().rowCount() - 1)
        table_view.verticalScrollBar().setValue(scroll_position)

    def show_lookups(self, profile):
        for vl in profile.value_lists():
            self.show_message(vl.short_name)

    def delete_lookup(self):
        """
        Event handler for deleting a selected lookup. Does NOT allow
        deleting of 'tenure_type' lookup.
        """
        profile = self.current_profile()

        if profile is None:
            self.show_message(self.tr("Nothing to delete!"))

        if len(self.lvLookups.selectedIndexes()) == 0:
            self.show_message(self.tr("Select a lookup to delete!"))
            return

        row_id, lookup, model_item = self._get_entity_item(self.lvLookups)
        # get dependencies for all the columns in all entities for
        # the current profile
        dependencies = self.all_column_dependencies(profile)

        if self.find_lookup(lookup.name, dependencies):
            self.show_message(self.tr("Cannot delete '{0}' lookup!\n "
                                      "Lookup is been used by existing columns."
                                      "".format(lookup.name, lookup.name)))
            return

        # dont delete `tenure_type` lookup
        if lookup.short_name == 'check_tenure_type':
            self.show_message(self.tr("Cannot delete tenure "
                                      "type lookup table!"))
            return

        msg = self.tr('Delete selected lookup?')
        if self.query_box_yesno(msg) == QMessageBox.Yes:
            profile.entities[lookup.short_name].action = DbItem.DROP
            profile.remove_entity(lookup.short_name)
            self.lookup_view_model.removeRow(row_id)
            self.refresh_lookup_view()

    def all_column_dependencies(self, profile):
        """
        Returns a list of all column dependencies, for all
        enitites in the current profile
        :param profile: current selected profile
        :type profile: Profile
        :rtype: list
        """
        depends = []
        # for profile in profiles:
        for entity in profile.entities.values():
            if entity.action == DbItem.DROP:
                continue
            for column in entity.columns.values():
                if column.action == DbItem.DROP:
                    continue
                if self.column_has_entity_relation(column):
                    depends.append(column.dependencies())
        return depends

    def find_lookup(self, name, dependencies):
        """
        Returns True if name is in the list of dependencies
        else False
        :param name: name to search in the list
        :type name: str
        :param dependencies: list to search
        :type dependencies: list
        :rtype: boolean
        """
        for depend in dependencies:
            if name in depend['entities']:
                return True
        return False

    def addValues_byEntity(self, entity):
        """
        Populate lookup values model with values extracted from entity.
        :param entity: ValueList(a.k.a Lookup)
        :type entity: Entity of TYPE_INFO - VALUE_LIST
        """
        for cv in entity.values.values():
            if cv.updated_value == '':
                txt = cv.value
            else:
                txt = cv.updated_value
            val = QStandardItem(txt)
            val.setData(GuiUtils.get_icon_pixmap("text_sm.png"), Qt.DecorationRole)
            self.lookup_value_view_model.appendRow(val)

    def add_values(self, values):
        """
        Populate lookup values model.
        :param values: list of lookup values
        :type values: list
        """
        self.lookup_value_view_model.clear()
        for v in values:
            if v.updated_value != "":
                v.value = v.updated_value

            val = QStandardItem(v.value)
            val.setData(GuiUtils.get_icon_pixmap("text_sm.png"), Qt.DecorationRole)
            self.lookup_value_view_model.appendRow(val)

    def lookup_changed(self, selected, diselected):
        """
        On selection changed event handler for the lookup model.
        Attached to "lookup_item_model"
        :param selected: the selected item
        :type selected: QItemSelection
        :param diselected: previous selected item
        :type diselected: QItemSelection
        """
        row_id = self.lookup_item_model.currentIndex().row()
        if row_id == -1:
            return
        view_model = self.lookup_item_model.currentIndex().model()
        self.lookup_value_view_model.clear()
        self.addValues_byEntity(view_model.entity_byId(row_id))
        self.lvLookupValues.setModel(self.lookup_value_view_model)

        lookup_entity = list(view_model.entities().values())[row_id]
        
        self.toggle_lookup_toolbuttons(lookup_entity.name)

    def toggle_lookup_toolbuttons(self, lookup_name: str):
        """"
        Disable edit and delete buttons if the lookup is used by
        a column in any of the entities in the current profile,  
        and the lookup is already saved in database.
        """
        profile_dependencies = self.all_column_dependencies(self.current_profile())
        is_found = self.find_lookup(lookup_name, profile_dependencies)
        in_database = pg_table_exists(lookup_name)

        self.btnEditLookup.setEnabled(not (is_found and in_database))
        self.btnDeleteLookup.setEnabled(not (is_found and in_database))

    def add_lookup_value(self):
        """
        On click event handler for the lookup values `Add` button
        """
        if len(self.lvLookups.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "No lookup selected to add value!"))
            return

        row_id, lookup, model_items = self._get_entity_item(self.lvLookups)
        if lookup:
            value_editor = ValueEditor(self, lookup)
            result = value_editor.exec_()
            if result == 1:
                model_items.model_item(row_id).set_default_bg_color()
                self.add_values(list(value_editor.lookup.values.values()))
                self.lvLookupValues.setModel(self.lookup_value_view_model)

    def edit_lookup_value(self):
        """
        On click event handler for the lookup values `Edit` button
        """
        if len(self.lvLookupValues.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "Please select a lookup value to edit!"))
            return

        self.lookup_item_model.currentIndex()
        # get selected value text
        model_index = self.lvLookupValues.selectedIndexes()[0]
        value_text = self.lookup_value_view_model.itemFromIndex(model_index).text()

        # get selected lookup
        row_id, lookup, model_item = self._get_entity_item(self.lvLookups)
        lookup = self.lookup_item_model.currentIndex().model().entity_byId(row_id)

        # Hack to rename a lookup value
        vt = str(value_text)
        # As the lookup value dictionary is converted to md5, convert this value
        hashed_vt = lookup.value_hash(vt)
        try:
            code_value = lookup.values[hashed_vt]
        except DummyException:
            code_value = self.find_updated_value(lookup, vt)

        ####

        value_editor = ValueEditor(self, lookup, code_value)
        result = value_editor.exec_()
        if result == 1:
            model_item_name = self.lookup_value_view_model.index(model_index.row(), 0)
            self.lookup_value_view_model.setData(
                model_item_name, value_editor.edtValue.text()
            )
            # self.add_values(value_editor.lookup.values.values(), test=True)

    def delete_lookup_value(self):
        """
        On click event handler for the lookup values `Delete` button
        """
        if len(self.lvLookupValues.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                                                     "Select value to delete"))
            return

        row_id, lookup, model_items = self._get_entity_item(self.lvLookups)
        model_index = self.lvLookupValues.selectedIndexes()[0]
        value_text = self.lookup_value_view_model.itemFromIndex(model_index).text()
        lookup.remove_value(str(value_text))

        if lookup.is_empty():
            model_items.model_item(row_id).indicate_as_empty()
        
        self.add_values(list(lookup.values.values()))

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        """
        Show a message dialog message
        :param message: Message to show
        :type message: str
        :param msg_icon:Icon to show on the message box
        :type msg_icon: QMessage.Icon
        """
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard", "STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard", message))
        msg.exec_()

    def query_box(self, msg):
        """
        Show 'OK/Cancel' query message box
        :param msg: message to show on the box
        :type msg: str
        :rtype: QMessageBox.StandardButton

        """
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Warning)
        msgbox.setWindowTitle(QApplication.translate("STDM Configuration Wizard", "STDM"))
        msgbox.setText(msg)
        msgbox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msgbox.setDefaultButton(QMessageBox.Cancel)
        result = msgbox.exec_()
        return result

    def query_box_yesno(self, msg, msg_icon=QMessageBox.Warning):
        """
        Show 'Yes/No' query message box
        :param msg: message to show on the box
        :type msg: str
        :rtype: QMessageBox.StandardButton
        """
        msgbox = QMessageBox(self)
        msgbox.setIcon(msg_icon)
        msgbox.setWindowTitle(self.tr("STDM Configuration Wizard"))
        msgbox.setText(msg)
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msgbox.setDefaultButton(QMessageBox.Yes)
        result = msgbox.exec_()
        return result

    def query_box_save_cancel(self, msg, msg_icon=QMessageBox.Warning):
        """
        Show 'Yes/No' query message box
        :param msg: message to show on the box
        :type msg: str
        :rtype: QMessageBox.StandardButton
        """
        msgbox = QMessageBox(self)
        msgbox.setIcon(msg_icon)
        msgbox.setWindowTitle(self.tr("STDM Configuration Wizard"))
        msgbox.setText(msg)
        msgbox.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        btnY = msgbox.button(QMessageBox.Yes)
        btnY.setText(self.tr('Save'))
        btnN = msgbox.button(QMessageBox.No)
        btnN.setText(self.tr("Don't Save"))
        btnC = msgbox.button(QMessageBox.Cancel)
        btnC.setText(self.tr("Cancel"))
        msgbox.setDefaultButton(QMessageBox.Yes)
        result = msgbox.exec_()
        return result

    def make_profile_copy(self, orig_profile_name, copy_profile_name,
                          config_file_name):
        '''
        Makes a copy of a profile Dom Element and appends it to the
        draft configuration file.
        :param profile_name: Name of the profile dom element to copy.
        :type profile_name: str
        :param copy_profile_name: Name of the copied profile dom element.
        :type copy_profile_name: str
        :param config_file_name: Name of the configuration.stc file to insert
        the new dom element.
        :type config_file_name: str
        '''
        is_file_healthy = self.healthy_file(config_file_name)

        if is_file_healthy:
            orig_dom_doc = ConfigurationDomDocument(config_file_name)
            copy_dom_doc = ConfigurationDomDocument(config_file_name)

            config_file = QFile(config_file_name)

            open_file = config_file.open(QIODevice.ReadWrite | QIODevice.Truncate)

            if open_file:
                orig_dom_elem = orig_dom_doc.find_dom_element('Profile', orig_profile_name)
                if orig_dom_elem:
                    copy_dom_elem = copy_dom_doc.find_dom_element('Profile', orig_profile_name)

                    copy_dom_doc.rename_element(copy_dom_elem, copy_profile_name)
                    orig_dom_doc.documentElement().insertAfter(copy_dom_elem, orig_dom_elem)
                    config_file.write(orig_dom_doc.toByteArray())

                config_file.close()

    def _bool_to_yesno(self, state: bool) -> str:
        CHECK_STATE = {True: 'Yes', False: 'No'}
        return CHECK_STATE[state]


class ConfigurationDomDocument(QDomDocument):
    def __init__(self, dom_file_name):
        super(ConfigurationDomDocument, self).__init__()
        self.dom_file_name = dom_file_name
        self.set_content()

    def set_content(self):
        file_handle = QFile(self.dom_file_name)
        status, msg, line, col = self.setContent(file_handle)
        if not status:
            error_message = 'Configuration file cannot be loaded: {0}'. \
                format(msg)
            raise ConfigurationException(error_message)

    def find_dom_element(self, elem_name, attr_value):
        found_elem = None
        child_nodes = self.documentElement().childNodes()
        for i in range(child_nodes.count()):
            child_elem = child_nodes.item(i).toElement()
            if child_elem.tagName() == elem_name:
                if child_elem.attribute('name') == attr_value:
                    found_elem = child_nodes.item(i).toElement()
                    break
        return found_elem

    def rename_element(self, dom_elem, new_name):
        dom_elem.setAttribute('name', new_name)

