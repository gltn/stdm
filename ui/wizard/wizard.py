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

import platform
import os
import sys
import logging
from datetime import date
from datetime import datetime 
import calendar

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration, 
        Profile
)
from stdm.utils.util import enable_drag_sort
from stdm.data.configuration.entity import entity_factory, Entity
from stdm.data.configuration.entity_relation import EntityRelation 
from stdm.data.configuration.columns import BaseColumn

from stdm.data.configuration.value_list import (
    ValueList,
    CodeValue,
    value_list_factory
)

from stdm.data.configuration.social_tenure import *
from stdm.data.configuration.config_updater import ConfigurationSchemaUpdater
from stdm.data.configuration.db_items import DbItem
from stdm.data.pg_utils import (
        pg_table_exists, 
        pg_table_count,
        table_column_names
       )
from stdm.settings.config_serializer import ConfigurationFileSerializer 
from stdm.settings.registryconfig import RegistryConfig 
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.license_doc import LicenseDocument
from stdm.settings import (
    current_profile,
    save_current_profile
)

from stdm.settings.registryconfig import (
        RegistryConfig,
        LOCAL_SOURCE_DOC,
        COMPOSER_OUTPUT,
        COMPOSER_TEMPLATE,
        SHOW_LICENSE
)

from custom_item_model import *

from ui_stdm_config import Ui_STDMWizard
from ui_entity import Ui_dlgEntity
from profile_editor import ProfileEditor
from create_entity import EntityEditor
from column_editor import ColumnEditor
from create_lookup import LookupEditor
from create_lookup_value import ValueEditor
from entity_depend import EntityDepend
from column_depend import ColumnDepend

# create logger
LOGGER = logging.getLogger('stdm')
LOGGER.setLevel(logging.DEBUG)

CHECKBOX_VALUES = [False, None, True]
CHECK_STATE = {True:Qt.Checked, False:Qt.Unchecked}

ORIG_CONFIG_FILE = QDir.home().path()+ '/.stdm/orig_configuration.stc'
CONFIG_FILE = QDir.home().path()+ '/.stdm/configuration.stc'
CONFIG_BACKUP_FILE = QDir.home().path()+ '/.stdm/configuration_bak.stc'

EXCL_ENTITIES = ['SUPPORTING_DOCUMENT', 'SOCIAL_TENURE',
                 'ADMINISTRATIVE_SPATIAL_UNIT', 'ENTITY_SUPPORTING_DOCUMENT',
                 'VALUE_LIST', 'ASSOCIATION_ENTITY']

class ConfigWizard(QWizard, Ui_STDMWizard):
    wizardFinished = pyqtSignal(object)
    """
    STDM configuration wizard editor
    """
    def __init__(self, parent):
        QWizard.__init__(self, parent)
        self.setupUi(self)
        self.register_fields()

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
        self.cboSPUnit.setModel(self.STR_spunit_model)

        self.init_entity_item_model()

        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)

        # STR view model
        self.party_item_model = STRColumnEntitiesModel()
        self.spunit_item_model = STRColumnEntitiesModel()

        #cboParty & cboSPUnit
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

        self.stdm_config = None
        self.new_profiles = []
        self.orig_assets_count = 0  # count of items in StdmConfiguration instance
        self.load_stdm_config()

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.splitter_3.setStretchFactor(0, 11)
        self.splitter_3.setStretchFactor(1, 0)
        self.splitter.isCollapsible(False)
        self.splitter_2.isCollapsible(False)
        self.splitter_3.isCollapsible(False)
        self.splitter_3.setSizes([330, 150])

        self.cboProfile.currentIndexChanged.connect(self.profile_changed)
        self.set_current_profile()

    def reject(self):
        """
        Event handler for the cancel button.
        If configuration has been edited, warn user before exiting.
        """
        cnt = len(self.stdm_config)
        if cnt <> self.orig_assets_count:
            msg0 = self.tr("All changes you've made on the configuration will be lost.\n")
            msg1 = self.tr("Are you sure you want to cancel?")
            if self.query_box(msg0+msg1) == QMessageBox.Cancel:
                return
        self.done(0)

    def load_stdm_config(self):
        """
        Read and load configuration from file 
        """
        try:
            config_file = self.healthy_config_file()
        except(ConfigurationException, IOError) as e:
            self.show_message(self.tr(unicode(e) ))

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
        bak_config_file  = self.healthy_file(CONFIG_BACKUP_FILE)
        orig_config_file = self.healthy_file(ORIG_CONFIG_FILE)

        if main_config_file and not bak_config_file:
            return CONFIG_FILE

        if main_config_file and bak_config_file:
            return self.user_choose_config()

        # this scenario is taken care of when you attempt to
        # run the wizard, we can safely remove it
        #====>START_REMOVE
        if not main_config_file and bak_config_file:
            return self.system_choose_backup_config()

        if not main_config_file and not bak_config_file:
            if orig_config_file:
                config_file = self.system_choose_orig_config()
            else:
                config_file = ''
        #<======END_REMOVE

        if config_file == '':
            raise IOError('No configuration file to load')

        return config_file

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
                "backup file " )
        self.show_message(msg)
        return CONFIG_BACKUP_FILE

    def system_choose_orig_config(self):
        msg = self.tr("Your configuration files seems to be corrupt!\n "
                " The system will revert to the original system configuration file.")
        self.show_message(msg)
        return ORIG_CONFIG_FILE

    def user_choose_config(self):
        """
        Function assumes both configuration file and backup configuration
        file exist. Returns either the configuration file or the backup 
        configuration file depending on what the users selects to use.
        :rtype: str
        """
        msg = self.tr("Please note that your previous configuration wizard did "
                "not complete successfully!\n However a backup of work done on "
                "that session is available.\n Would you like to restore that backup session?\n "
                "If you choose the NO button, you will lose all your latest changes, \n "
                "and there could be a mismatch between the database and the "
                "configuration.")

        if self.query_box_yesno(msg, QMessageBox.Critical) == QMessageBox.Yes:
            return CONFIG_BACKUP_FILE
        else:
            return CONFIG_FILE


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
        #self.cboProfile.currentIndexChanged.connect(self.profile_changed)
        self.btnNewP.clicked.connect(self.new_profile)
        self.btnPDelete.clicked.connect(self.delete_profile)

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
        self.cboParty.setModel(entity_model)
        #self.cboSPUnit.setModel(entity_model)

    def init_STR_ctrls_event_handlers(self):
        """
        Attach onChange event handlers for the STR combobox 
        """
        pass
        #self.cboParty.currentIndexChanged.connect(self.party_changed)
        #self.cboSPUnit.currentIndexChanged.connect(self.spatial_unit_changed)

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
        self.lblDesc.setText("")

        self.pftableView.setColumnWidth(0, 250)
        
        # Attach multi party checkbox state change event handler
        self.cbMultiParty.stateChanged.connect(self.multi_party_state_change)

        # disable editing of view widgets
        self.pftableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tbvColumns.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lvEntities.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lvLookups.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lvLookupValues.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        self.lvLookups.setCurrentIndex(self.lvLookups.model().index(0,0))

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
                unicode(io_err)
            )

            return False

        except ConfigurationException as c_ex:
            QMessageBox.critical(
                self.iface.mainWindow(),
                self.tr('Load Configuration Error'),
                unicode(c_ex)
            )

            return False

        return True

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        profiles = []
        for profile in self.stdm_config.profiles.values():
            for entity in profile.entities.values():
                self.connect_column_signals(entity)
            self.connect_entity_signals(profile)
            profiles.append(profile.name)
        self.cbo_add_profiles(profiles)

        self.lvLookups.setCurrentIndex(self.lvLookups.model().index(0,0))
        self.lvEntities.setCurrentIndex(self.lvEntities.model().index(0,0))

    def connect_column_signals(self, entity):
        """
        Connect signals triggered when column is added or deleted from an entity
        """
        entity.column_added.connect(self.add_column_item)
        entity.column_removed.connect(self.delete_column_item)
        
    def validate_STR(self):
        """
        Validate both Party & Spatial Unit entities for STR are properly set. 
        Returns a tuple indicating the setting status and a status message.
        :rtype: tuple (boolean, str)
        """
        # check if any entities exist,
        if self.entity_model.rowCount() == 0:
            return False, self.tr("No entities for creating Social Tenure Relationship")

        # check that party and spatial unit entities are not the same
        if self.cboParty.currentText() == self.cboSPUnit.currentText():
            return False, self.tr("Party and Spatial Unit entities cannot be the same!")

        profile = self.current_profile()
        spatial_unit = profile.entity(unicode(self.cboSPUnit.currentText()))

        if spatial_unit is None:
            return False, self.tr('No spatial unit entity found for '
            'creating Social Tenure Relationship!')

        # check if the spatial unit entity has a geometry column
        if not spatial_unit.has_geometry_column():
            return False, self.tr("%s entity should have a geometry column!")\
                    % spatial_unit.short_name

        return True, self.tr("Ok")

    def index_party_table(self):
        """
        Returns an index of the selected party unit
        """
        for index, entity in enumerate(self.entity_model.entities().values()):
            if entity.has_geometry_column():
                continue
            else:
                return index
        return 0


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

    def check_empty_entities(self):
        """
        """
        is_empty = True

        profile = self.current_profile()
        for entity in profile.entities.values():
            col_count = 0
            for column in entity.columns.values():
                if column.action <> DbItem.DROP:
                    col_count += 1
                    break
            if col_count == 0:
                self.show_message(self.tr("Entity '%s' has no columns!") % entity.short_name)
                is_empty = False 

        return is_empty


    def check_empty_lookups(self):
        """
        Verifies that all lookups in the current profile
        have values. Returns true if all have values else false
        :rtype: bool
        """
        valid = True
        profile  = self.current_profile()
        if not profile:
            return valid
        for vl in profile.value_lists():
            # don't check deleted entities
            if vl.action == DbItem.DROP:
                continue
            if vl.is_empty():
                valid = False
                self.show_message(self.tr("Lookup %s has no values") % vl.short_name)
                break
        return valid

    def fmt_path_str(self, path):
        """
        Returns a directory path string formatted in a unix format
        :param path: string representing the windows path
        :type path: str
        :rtype: str
        """
        rpath = r''.join(unicode(path))
        return rpath.replace("\\", "/")

    def read_settings_path(self, reg_keys, os_path):
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
        except:
            reg_doc_path = None

        if reg_doc_path is not None:
            doc_path = self.verify_path(reg_doc_path)
        else:
            path = QDir.home().path() + os_path
            doc_path = self.verify_path(path)

        return doc_path

    def verify_path(self, path):
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

    def make_os_path(self, path):
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

    def initializePage(self, int):
        if self.currentId() == 0:
            self.show_license()

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

    def set_str_controls(self, str_table):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        :param str_table: Social Tenure Relationship table
        :type str_table: str
        """
        self.enable_str_setup()
        if pg_table_exists(str_table) and pg_table_count(str_table) > 0:
            self.disable_str_setup()
            
    def enable_str_setup(self):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        """
        self.cboParty.setEnabled(True)
        self.cboSPUnit.setEnabled(True)

    def disable_str_setup(self):
        """
        Disable STR UI widgets if Social Tenure Relationship has
        been set and saved in the database
        """
        self.cboParty.setEnabled(False)
        self.cboSPUnit.setEnabled(False)

    def validateCurrentPage(self):
        validPage = True

        if self.nextId() == 2:
            validPage, msg = self.validate_path_settings()
            if not validPage:
                self.show_message(msg)
                return validPage

        if self.currentId() == 3:
            self.party_changed(0)

            curr_profile = self.current_profile()

            idx1 = self.index_party_table()
            self.cboParty.setCurrentIndex(idx1)

            idx = self.index_spatial_unit_table(
                    curr_profile, self.STR_spunit_model)
            self.cboSPUnit.setCurrentIndex(idx)
            #self.spatial_unit_changed(idx)

            self.set_multi_party_checkbox(curr_profile)

            # verify that lookup entities have values
            validPage = self.check_empty_lookups()

            # check if social tenure relationship has been setup
            str_table = curr_profile.prefix +"_social_tenure_relationship"
            self.set_str_controls(str_table)

        if self.currentId() == 4:
            validPage, msg = self.validate_STR()

            if validPage:
                profile = self.current_profile()

                #party
                party = profile.entity(unicode(self.cboParty.currentText()))
                spatial_unit = profile.entity(unicode(self.cboSPUnit.currentText()))

                profile.set_social_tenure_attr(SocialTenure.PARTY, party)
                profile.set_social_tenure_attr(SocialTenure.SPATIAL_UNIT, spatial_unit)
            else:
                self.show_message(self.tr(msg))

        if self.currentId() == 5: # FINAL_PAGE:
            # last page

            # before any updates, backup your current working profile
            self.backup_config_file()

            #* commit config to DB
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
                    { LOCAL_SOURCE_DOC:self.edtDocPath.text(),
                      COMPOSER_OUTPUT:self.edtOutputPath.text(),
                      COMPOSER_TEMPLATE:self.edtTemplatePath.text()
                     })

            # compute a new asset count
            self.orig_assets_count = len(self.stdm_config)

            #pause, allow user to read post saving messages
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
        info_file.write(time_stamp+'\n')
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
        logs_folder = self.get_folder(QDir.home().path()+'/.stdm/logs')
        file_name = logs_folder+'/configuration_update_'+fmt_date+'.log'
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
        time_stamp = week_day+' '+fmt_date
        return time_stamp

    def _updater_thread_started(self):
        """
        Slot for initiating the schema updating process.
        """
        self.config_updater.exec_()

    def config_update_started(self):
        self.button(QWizard.FinishButton).setEnabled(False)
        self.button(QWizard.CancelButton).setEnabled(False)
        QCoreApplication.processEvents()

        self.txtHtml.setFontWeight(75)
        self.txtHtml.append(QApplication.translate("Configuration Wizard",
                               "Configuration update started...")
        )
        self.txtHtml.setFontWeight(50)

    def config_update_progress(self, info_id, msg):
        if info_id == 0: # information
            self.txtHtml.setTextColor(QColor('black'))

        if info_id == 1: # Warning
            self.txtHtml.setTextColor(QColor(255, 170, 0))

        if info_id == 2: # Error
            self.txtHtml.setTextColor(QColor('red'))

        self.txtHtml.append(msg)

    def config_update_completed(self, status):
        self.button(QWizard.CancelButton).setEnabled(True)
        if status:
            self.txtHtml.setTextColor(QColor(51, 182, 45))
            self.txtHtml.setFontWeight(75)
            msg = QApplication.translate('Configuration Wizard',
                                         'The configuration has been '
                                         'successfully updated.')
            self.txtHtml.append(msg)
            self.is_config_done = True

            #Write config to a file
            cfs = ConfigurationFileSerializer(CONFIG_FILE)

            # flag wizard has been run
            self.reg_config.write({'WizardRun':1})

            try:
                cfs.save()
                #Save current profile to the registry
                profile_name = unicode(self.cboProfile.currentText())
                save_current_profile(profile_name)

                # delete config backup file
                self.delete_config_backup_file()

            except(ConfigurationException, IOError) as e:
                self.show_message(self.tr(unicode(e) ))

        else:
            self.txtHtml.append(self.tr("Failed to update configuration. "
                                "Check error logs."))
            self.is_config_done = False

        self.save_update_info(self.txtHtml.toPlainText(), self.new_update_file)

        #Exit thread
        self.updater_thread.quit()
        self.wizardFinished.emit(self.cboProfile.currentText())

    def backup_config_file(self):
        """
        """
        cfs = ConfigurationFileSerializer(CONFIG_BACKUP_FILE)
        
        try:
            cfs.save()
        except(ConfigurationException, IOError) as e:
            self.show_message(self.tr(unicode(e) ))

    def delete_config_backup_file(self):
        QFile.remove(CONFIG_BACKUP_FILE)

    def register_fields(self):
        self.setOption(self.HaveHelpButton, True)  
        page_count = self.page(1)
        page_count.registerField(self.tr("Accept"), self.rbAccpt)
        page_count.registerField(self.tr("Reject"), self.rbReject)

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
        except:
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
        except:
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
        except:
            LOGGER.debug("Error setting support document path!")

    def open_dir_chooser(self, message, dir=None):
        """
        Returns a selected folder from the QFileDialog
        :param message:message to show on the file selector
        :type message: str
        """
        sel_dir = str(QtGui.QFileDialog.getExistingDirectory(
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

    def delete_str_spunit_item(self, name):
        """
        Removes an entity from a model
        param name: Name of entity to delete
        type name: str
        """
        items = self.STR_spunit_model.findItems(name)
        if len(items) > 0:
            self.STR_spunit_model.removeRow(items[0].row())

        self.STR_spunit_model.delete_entity_byname(name)


    def cbo_add_profile(self, profile):
        """
        param profile: List of profile to add in a combobox
        type profile: list
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

    def set_current_profile(self):
        # Set current profile on the profile combobox.
        cp = current_profile()
        if not cp is None:
            index = self.cboProfile.findText(cp.name, Qt.MatchFixedString)
            if index >= 0:
                self.cboProfile.setCurrentIndex(index)
        else:
            if self.cboProfile.count() > 0:
                self.cboProfile.setCurrentIndex(0)


    #PROFILE
    def new_profile(self):
        """
        Event handler for creating a new profiled
        """
        editor = ProfileEditor(self)
        result = editor.exec_()
        if result == 1:
            profile = self.stdm_config.create_profile(editor.profile_name)

            self.new_profiles.append(editor.profile_name)
            profile.description = editor.desc
            self.connect_entity_signals(profile)
            self.stdm_config.add_profile(profile)
            #self.switch_profile(self.cboProfile.currentText())

    def connect_entity_signals(self, profile):
        """
        Connects signals to emit when an entity is added or removed from a
        profile
        :param profile: Profile that emits the signals
        :type profile: Profile
        """
        profile.entity_added.connect(self.add_entity_item)
        profile.entity_removed.connect(self.delete_entity_item)

    def current_profile(self):
        """
        Returns an instance of the selected profile in the 
        profile combobox
        rtype: Profile
        """
        profile = None
        prof_name = self.cboProfile.currentText()
        if len(prof_name) > 0:
            profile = self.stdm_config.profile(unicode(prof_name))
        return profile

    def delete_profile(self):
        """
        Delete the current selected profile, but not the last one.
        """
        if self.cboProfile.count() == 1:
            msg0 = self.tr("This is the last profile in your wizard. ")
            msg1 = self.tr("STDM requirement is to have atleast one profile in your database.")
            msg2 = self.tr(" Delete is prohibited.")
            self.show_message(QApplication.translate("Configuration Wizard", \
                    msg0+msg1+msg2), QMessageBox.Information)
            return

        msg0 = self.tr("You will loose all items related to this profile i.e \n")
        msg1 = self.tr("entities, lookups and Social Tenure Relationships.\n")
        msg2 = self.tr("Are you sure you want to delete this profile?")
        if self.query_box(msg0+msg1+msg2) == QMessageBox.Cancel:
            return

        profile_name = unicode(self.cboProfile.currentText())
        if not self.stdm_config.remove_profile(profile_name):
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Unable to delete profile!"))
            return
        self.load_profile_cbo()

    def get_profiles(self):
        """
        Returns a list of profiles from the StdmConfiguration instance.
        :rtype: list
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
            params['parent']  = self
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
        if len(self.pftableView.selectedIndexes())==0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No entity selected for edit!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.pftableView)

        if model_item:
            profile = self.current_profile()
            in_db = pg_table_exists(entity.name)

            tmp_short_name = entity.short_name

            params = {}
            params['parent']  = self
            params['profile'] = profile
            params['entity']  = entity
            params['in_db']   = in_db

            editor = EntityEditor(**params)
            result = editor.exec_()

            if result == 1:
                model_index_name = model_item.index(row_id, 0)
                model_index_desc = model_item.index(row_id, 1)

                model_item.setData(model_index_name, editor.entity.short_name) 
                model_item.setData(model_index_desc, editor.entity.description) 


    def delete_entity(self):
        """
        Delete selected entity
        """
        if len(self.pftableView.selectedIndexes())==0:
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
        if column.name in cols:
            return True
        else:
            return False

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
        self.lvEntities.setModel(view_model)
        self.cboParty.setModel(view_model)
        #self.cboSPUnit.setModel(view_model)

    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
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

        self.cboParty.currentIndexChanged.emit(self.cboParty.currentIndex())
        self.cboSPUnit.currentIndexChanged.emit(self.cboSPUnit.currentIndex())

    def switch_profile(self, name):
        """
        Used to refresh all QStandardItemModel's attached to various
        view widgets in the wizard.
        :param name: name of the new profile to show
        :type name: str
        """
        if not name:
            return

        profile = self.stdm_config.profile(unicode(name))
        if profile is not None:
            self.lblDesc.setText(profile.description)
        else:
            return
        # clear view models
        self.clear_view_model(self.entity_model)
        self.clear_view_model(self.col_view_model)
        self.clear_view_model(self.lookup_view_model)
        self.clear_view_model(self.lookup_value_view_model)
        self.clear_view_model(self.party_item_model)
        #self.clear_view_model(self.spunit_item_model)
        self.clear_view_model(self.STR_spunit_model)

        self.entity_model = EntitiesModel()
        self.set_view_model(self.entity_model)
        self.cboSPUnit.setModel(self.STR_spunit_model)

        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)

        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)
        self.lvLookupValues.setModel(self.lookup_value_view_model)

        # from profile entities to view_model
        self.populate_view_models(profile)
        self.populate_spunit_model(profile)

        self.connect_signals()
        self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0,0))

        # Enable drag and drop for new profiles only
        if name in self.new_profiles:
            enable_drag_sort(self.tbvColumns)
            enable_drag_sort(self.lvLookupValues)
            enable_drag_sort(self.pftableView)
        else:
            self.tbvColumns.setDragEnabled(False)
            self.lvLookupValues.setDragEnabled(False)
            self.pftableView.setDragEnabled(False)

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
        self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0,0))

    def refresh_columns_view(self, entity):
        """
        Clears columns in the column view model associated
        with the columns Table View then re-inserts columns from
        the entity
        """
        self.clear_view_model(self.col_view_model)
        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)
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
        model_item = view.currentIndex().model()
        if model_item:
            sel_id = view.currentIndex().row()
            entity = model_item.entities().items()[sel_id][1]
        return (model_item, entity, sel_id)
		
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

        if row_id > -1:
            view_model = self.entity_item_model.currentIndex().model()
            self.col_view_model.clear()
            self.col_view_model = ColumnEntitiesModel()

            columns = view_model.entity_byId(row_id).columns.values()
            self.addColumns(self.col_view_model, columns)

            self.tbvColumns.setModel(self.col_view_model)

    def party_changed(self, row_id):
        """
        Event handler for STR party combobox - event currentIndexChanged.
        """
        cbo_model = self.cboParty.model()
        try:
            columns = cbo_model.entity_byId(row_id).columns.values()
            self.party_item_model.clear()
            self.party_item_model = STRColumnEntitiesModel()
            self.addColumns(self.party_item_model, columns)
        except:
            pass

    def spatial_unit_changed(self, row_id):
        """
        Event handler for STR spatial unit combobox - event currentIndexChanged.
        :param row_id: index of the selected item in the combobox
        :type row_id: int
        """
        cbo_model = self.cboSPUnit.model()
        try:
            columns = cbo_model.entity_byId(row_id).columns.values()
            self.spunit_item_model.clear()
            self.spunit_item_model = STRColumnEntitiesModel()
            self.addColumns(self.spunit_item_model, columns)
        except:
            pass

    def new_column(self):
        """
        On click event handler for adding a new column
        """
        if len(self.lvEntities.selectedIndexes())==0:
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

            editor = ColumnEditor(**params)
            result = editor.exec_()

            if result == 1:
                if editor.type_info == 'LOOKUP':
                    self.clear_lookup_view()
                    self.populate_lookup_view(profile)
                    self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0,0))

                # add this entity to STR spatial unit list of selection.
                if editor.type_info == 'GEOMETRY':
                    self.STR_spunit_model.add_entity(entity)
                    print 'hello'

    def edit_column(self):
        """
        Event handler for editing a column.
        """

        rid, column, model_item = self._get_model(self.tbvColumns)
        
        if column and column.action == DbItem.CREATE:
            row_id, entity = self._get_entity(self.lvEntities)

            profile = self.current_profile()
            params = {}
            params['parent'] = self
            params['column'] = column
            params['entity'] = entity
            params['profile'] = profile
            params['in_db'] = self.column_exist_in_entity(entity, column)

            params['is_new'] = False

            tmp_column = column #model_item.entity(column.name)

            editor = ColumnEditor(**params)
            result = editor.exec_()

            if result == 1: # after successfully editing

                model_index_name  = model_item.index(rid, 0)
                model_index_dtype = model_item.index(rid, 1)
                model_index_desc  = model_item.index(rid, 2)

                model_item.setData(model_index_name, editor.column.name)
                model_item.setData(model_index_dtype, editor.column.TYPE_INFO.capitalize())
                model_item.setData(model_index_desc, editor.column.description)

                model_item.edit_entity(tmp_column, editor.column)

                tmp_column.copy_attrs(editor.column)

                # Replace the current entity with a new one
                # Apperently, ordered dict key replacement will cause change in 
                # key positions.
                entity.columns[tmp_column.name] = editor.column
                entity.columns[editor.column.name] = \
                        entity.columns.pop(tmp_column.name)
                
                self.refresh_columns_view(entity)

                self.clear_view_model(self.STR_spunit_model)
                self.populate_spunit_model(profile)
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No column selected for edit!"))

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
            entity_item = model_item.entities().values()[row_id]
        return row_id, entity_item

    def _get_model(self, view):
        row_id = -1
        model_item, entity, row_id = self.get_model_entity(view)
        column = None
        if model_item:
            column = model_item.entities().values()[row_id]
        return row_id, column, model_item

    def _get_entity(self, view):
        model_item, entity, row_id = self.get_model_entity(view)
        if entity:
            return row_id, entity

    def delete_column(self):
        """
        Delete selected column, show warning dialog if a column has dependencies.
        """
        row_id, column, model_item = self._get_model(self.tbvColumns)
        if not column:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No column selected for deletion!"))
            return

        if self.check_column_dependencies(column):
            ent_id, entity = self._get_entity(self.lvEntities)

            # delete from the entity
            entity.remove_column(column.name)

            if not entity.has_geometry_column():
                self.delete_str_spunit_item(entity.short_name)


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
            # 0 - user choose not to delete column
            if result == 0:
                ok_delete =  False

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
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No profile selected to add lookup!"))

    def edit_lookup(self):
        """
        Event handler for editing a lookup. Editing is only allowed to lookups 
        that have not yet been saved in the database.
        """
        profile = self.current_profile()

        if profile:
            if len(self.lvLookups.selectedIndexes()) == 0:
                self.show_message(self.tr("No lookup selected for edit!"))
                return

            row_id, lookup, model_item = self._get_model(self.lvLookups)

            tmp_lookup = lookup # model_item.entity(lookup.short_name)

            editor = LookupEditor(self, profile, lookup)
            result = editor.exec_()

            if result == 1:
                model_index_name  = model_item.index(row_id, 0)
                model_item.setData(model_index_name, editor.lookup.short_name)

                model_item.edit_entity(tmp_lookup, editor.lookup)

                profile.entities[tmp_lookup.short_name] = editor.lookup
                profile.entities[editor.lookup.short_name] = \
                        profile.entities.pop(tmp_lookup.short_name)

                self.refresh_lookup_view()

        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Nothing to edit!"))


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

        row_id, lookup = self._get_entity_item(self.lvLookups)
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

    def all_column_dependencies(self, profile):
        """
        Returns a list of all column dependencies, for all
        enitites in the current profile
        :param profile: current selected profile
        :type profile: Profile 
        :rtype: list
        """
        depends = []
        #for profile in profiles:
        for entity in profile.entities.values():
            if entity.action <> DbItem.DROP:
                for column in entity.columns.values():
                    if column.action <> DbItem.DROP:
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
        for v in entity.values:
            cv = entity.code_value(v)
            if cv.updated_value == '':
                txt = cv.value
            else:
                txt = cv.updated_value

            val = QStandardItem(txt)
            self.lookup_value_view_model.appendRow(val)

    def add_values(self, values):
        """
        Populate lookup values model.
        :param values: list of lookup values
        :type values: list 
        """
        self.lookup_value_view_model.clear()
        for v in values:
            val = QStandardItem(v.value)
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

    def add_lookup_value(self):
        """
        On click event handler for the lookup values `Add` button
        """
        if len(self.lvLookups.selectedIndexes()) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No lookup selected to add value!"))
            return

        row_id, lookup = self._get_entity_item(self.lvLookups)
        if lookup:
            value_editor = ValueEditor(self, lookup)
            result = value_editor.exec_()
            if result == 1:
                self.add_values(value_editor.lookup.values.values())
                self.lvLookupValues.setModel(self.lookup_value_view_model)

    def edit_lookup_value(self):
        """
        On click event handler for the lookup values `Edit` button
        """
        if len(self.lvLookupValues.selectedIndexes() ) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No value selected for edit!"))
            return

        self.lookup_item_model.currentIndex()
        # get selected lookup value
        model_index = self.lvLookupValues.selectedIndexes()[0]
        value_text = self.lookup_value_view_model.itemFromIndex(model_index).text()

        # get selected lookup
        row_id, lookup = self._get_entity_item(self.lvLookups)
        lookup_view_model = self.lookup_item_model.currentIndex().model().entity_byId(row_id)
        code_value = lookup_view_model.values[unicode(value_text)]

        value_editor = ValueEditor(self, lookup, code_value)
        result = value_editor.exec_()
        if result == 1:
            self.add_values(value_editor.lookup.values.values())

    def delete_lookup_value(self):
        """
        On click event handler for the lookup values `Delete` button
        """
        if len(self.lvLookupValues.selectedIndexes() ) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Select value to delete"))
            return

        row_id, lookup = self._get_entity_item(self.lvLookups)
        model_index = self.lvLookupValues.selectedIndexes()[0]
        value_text = self.lookup_value_view_model.itemFromIndex(model_index).text()
        lookup.remove_value(unicode(value_text))
        self.add_values(lookup.values.values())

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
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard",message))
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
        msgbox.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msgbox.setText(msg)
        msgbox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok);
        msgbox.setDefaultButton(QMessageBox.Cancel);
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
        msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No);
        msgbox.setDefaultButton(QMessageBox.Yes);
        result = msgbox.exec_()
        return result

