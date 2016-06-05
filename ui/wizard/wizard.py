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

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration, 
        Profile
)

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
        DOCUMENTS_KEY,
        TEMPLATES_KEY,
        OUTPUTS_KEY
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

# create logger
LOGGER = logging.getLogger('stdm')
LOGGER.setLevel(logging.DEBUG)

class ConfigWizard(QWizard, Ui_STDMWizard):
    """
    STDM configuration wizard editor
    """
    def __init__(self, parent):
        QWizard.__init__(self, parent)
        self.setupUi(self)
        self.register_fields()

        # directory path settings
        self.init_path_ctrls_event_handlers()

        # profile
        self.init_profile_ctrls_event_handlers()
        
        # register enitity model to different view controllers
        self.entity_model = EntitiesModel()
        self.set_views_entity_model(self.entity_model)

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

        self.is_config_done = False
        self.stdm_config = StdmConfiguration.instance()  
        self.stdm_config.profile_added.connect(self.cbo_add_profile)

        # if StdmConfiguration profiles instance is not empty, 
        # load earlier profiles and go straight to profile config page
        if len(self.stdm_config.profiles) > 0:
            self.reload_profiles()
            self.load_path()
            self.setStartId(1)
        else:
            # wizard start at page 0 - license
            self.setStartId(0)

    def init_path_ctrls_event_handlers(self):
        self.btnDocPath.clicked.connect(self.set_support_doc_path)
        self.btnDocOutput.clicked.connect(self.set_output_path)
        self.btnTemplates.clicked.connect(self.set_template_path)

    def init_profile_ctrls_event_handlers(self):
        self.cboProfile.currentIndexChanged.connect(self.profile_changed)
        self.btnNewP.clicked.connect(self.new_profile)
        self.btnPDelete.clicked.connect(self.delete_profile)

    def init_entity_item_model(self):
        self.entity_item_model = self.lvEntities.selectionModel()
        self.entity_item_model.selectionChanged.connect(self.entity_changed)

    def set_views_entity_model(self, entity_model):
        self.pftableView.setModel(entity_model)
        self.lvEntities.setModel(entity_model)	
        self.cboParty.setModel(entity_model)
        self.cboSPUnit.setModel(entity_model)

    def init_STR_ctrls_event_handlers(self):
        self.cboParty.currentIndexChanged.connect(self.party_changed)
        self.cboSPUnit.currentIndexChanged.connect(self.spatial_unit_changed)

    def init_entity_ctrls_event_handlers(self):
        self.btnNewEntity.clicked.connect(self.new_entity)
        self.btnEditEntity.clicked.connect(self.edit_entity)
        self.btnDeleteEntity.clicked.connect(self.delete_entity)

    def init_column_ctrls_event_handlers(self):
        self.btnAddColumn.clicked.connect(self.new_column)
        self.btnEditColumn.clicked.connect(self.edit_column)
        self.btnDeleteColumn.clicked.connect(self.delete_column)

    def init_lookup_ctrls_event_handlers(self):
        self.btnAddLookup.clicked.connect(self.new_lookup)
        self.btnEditLookup.clicked.connect(self.edit_lookup)
        self.btnDeleteLookup.clicked.connect(self.delete_lookup)

    def init_lkvalues_event_handlers(self):
        self.btnAddLkupValue.clicked.connect(self.add_lookup_value)
        self.btnEditLkupValue.clicked.connect(self.edit_lookup_value)
        self.btnDeleteLkupValue.clicked.connect(self.delete_lookup_value)

    def init_ui_ctrls(self):
        self.edtDocPath.setFocus()
        self.rbReject.setChecked(True)
        self.pftableView.setColumnWidth(0, 250)
        self.lblDesc.setText("")

    def reload_profiles(self):
        """
        Read and load the profiles from StdmConfiguration instance
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
        Returns a tuple (True, 'OK') if all properties for 
        Social Tenure Relationship are set, else (False, 'message').
        Check if any entities exist,
        Check that party and spatial unit entities are not the same
        Check if spatial unit has a geometry column
        :rtype: tuple
        """
        if self.entity_model.rowCount() == 0:
            return False, "No entities for creating Social Tenure Relationship"

        if self.cboParty.currentIndex() == self.cboSPUnit.currentIndex():
            return False, "Party and Spatial Unit entities cannot be the same!"

        profile = self.current_profile()
        spatial_unit = profile.entity(unicode(self.cboSPUnit.currentText()))

        if not spatial_unit.has_geometry_column():
            return False, "%s entity should have a geometry column!"\
                    % spatial_unit.short_name

        return True, "Ok"


    def index_spatial_unit_table(self):
        for index, entity in enumerate(self.entity_model.entities().values()):
            if entity.has_geometry_column():
                return index
        return 0

    def validate_empty_lookups(self):
        """
        Verifys that all lookups in the current profile
        have values. Returns true if all have values else false
        rtype: bool
        """
        valid = True
        profile  = self.current_profile()
        if not profile:
            return valid
        for vl in profile.value_lists():
            if vl.is_empty():
                valid = False
                self.show_message("Lookup %s has no values" % vl.short_name)
                break
        return valid

    def fmt_path_str(self, path):
        """
        param path: string representing the windows path
        type path: str
        Returns a directory path string formatted in a unix format
        rtype: str
        """
        rpath = r''.join(unicode(path))
        return rpath.replace("\\", "/")

    def read_settings_path(self, reg_keys, os_path):
        """
        param reg_key: list of registry keys to read the path setting
        type reg_keys: list
        param os_path: os directory to use if the reg_key is not set
        type os_path: str
        Returns path settings from the registry or an os folder
        rtype: str
        """
        reg_config = RegistryConfig()
        try:
            # returns a dict {reg_key:reg_value}
            key = reg_config.read(reg_keys)
            if len(key) > 0:
                reg_doc_path = key[reg_keys[0]]
            else:
                reg_doc_path = None
        except:
            reg_doc_path = None

        if reg_doc_path is not None:
            return reg_doc_path
        else:
            doc_path = os.path.expanduser('~')+os_path
            if not os.path.exists(doc_path):
                os.makedirs(doc_path) 
            return self.fmt_path_str(doc_path)

    def show_license(self):
        self.txtLicense.clear()
        license = LicenseDocument()
        self.txtLicense.setText(license.read_license_info())

    def load_path(self):
        self.load_doc_path()
        self.load_output_path()
        self.load_template_path()

    def load_doc_path(self):
        doc_path = self.read_settings_path(['documents'], '/.stdm/documents/')
        self.edtDocPath.setText(doc_path)

    def load_output_path(self):
        output_path = self.read_settings_path(['outputs'], 
                '/.stdm/reports/outputs')
        self.edtOutputPath.setText(output_path)

    def load_template_path(self):
        templates_path = self.read_settings_path(['templates'],
                '/.stdm/reports/templates')
        self.edtTemplatePath.setText(templates_path)

    def initializePage(self, int):
        if self.currentId() == 0:
            self.show_license()

    def validateCurrentPage(self):
        validPage = True

        if self.currentId() == 0:
            self.load_path()

            if self.rbReject.isChecked():
                message1 = "To continue with the wizard please comply with "
                message2 = "disclaimer policy by selecting the option 'I Agree'"
                self.show_message(message1+message2)
                validPage = False

        if self.currentId() == 3:
            self.party_changed(0)
            # get an entity with a geometry column
            idx = self.index_spatial_unit_table()
            self.cboSPUnit.setCurrentIndex(idx)
            self.spatial_unit_changed(idx)
            # verify that lookup entities have values
            validPage = self.validate_empty_lookups()

        if self.currentId() == 4:
            validPage, msg = self.validate_STR()

            if validPage:
                profile = self.current_profile()
                party = profile.entity(unicode(self.cboParty.currentText()))
                spatial_unit = profile.entity(unicode(self.cboSPUnit.currentText()))

                profile.set_social_tenure_attr(SocialTenure.PARTY, party)
                profile.set_social_tenure_attr(SocialTenure.SPATIAL_UNIT, spatial_unit)
            else:
                self.show_message(QApplication.translate("Configuration Wizard", msg))

        if self.currentId() == 5: # FINAL_PAGE:
            # last page
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

            ##*Start the process
            self.updater_thread.start()

            # write document paths to registry
            reg_config = RegistryConfig()
            reg_config.write(
                    { DOCUMENTS_KEY:self.edtDocPath.text(),
                      OUTPUTS_KEY:self.edtOutputPath.text(),
                      TEMPLATES_KEY:self.edtTemplatePath.text()
                     })
                    
            #pause, allow user to read post saving messages
            self.pause_wizard_dialog()
            validPage = False

        return validPage

    def pause_wizard_dialog(self):
            self.button(QWizard.BackButton).setEnabled(False)
            self.button(QWizard.FinishButton).setEnabled(False)
            self.button(QWizard.CancelButton).setText(\
                    QApplication.translate("Configuration Wizard","Close"))


    def _updater_thread_started(self):
        """
        Slot for initiating the schema updating process.
        """
        self.config_updater.exec_()

    def config_update_started(self):
        self.txtHtml.append(QApplication.translate("Configuration Wizard",
                               "Configuration update started ...")
        )

    def config_update_progress(self, info_id, msg):
        if info_id == 0: # information
            self.txtHtml.setTextColor(QColor('black'))

        if info_id == 1: # Warning
            self.txtHtml.setTextColor(QColor(255, 170, 0))

        if info_id == 2: # Error
            self.txtHtml.setTextColor(QColor('red'))

        self.txtHtml.append(msg)

    def config_update_completed(self, status):
        if status:
            self.txtHtml.append("The configuration successfully updated.")
            self.is_config_done = True

            #Write config to a file
            config_path = os.path.expanduser('~') + '/.stdm/configuration.stc'
            cfs = ConfigurationFileSerializer(config_path)

            try:
                cfs.save()

                #Save current profile to the registry
                profile_name = unicode(self.cboProfile.currentText())
                save_current_profile(profile_name)

            except(ConfigurationException, IOError) as e:
                self.show_message(QApplication.translate("Configuration Wizard", \
                        unicode(e)))

        else:
            self.txtHtml.append("Failed to update configuration. "
                                "Check error logs.")
            self.is_config_done = False

        #Exit thread
        self.updater_thread.quit()

    def register_fields(self):
        self.setOption(self.HaveHelpButton, True)  
        page_count = self.page(1)
        page_count.registerField("Accept", self.rbAccpt)
        page_count.registerField("Reject", self.rbReject)

    def set_support_doc_path(self):
        try:
            dir_name = self.open_dir_chooser(QApplication.translate( \
                    "STDM Configuration", 
                    "Select a directory for supporting documents"), 
                    str(self.edtDocPath.text()))

            if len(dir_name.strip()) > 0:
                self.edtDocPath.setText(dir_name)
        except:
            LOGGER.debug("Error setting support document path!")
            raise

    def set_output_path(self):
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
        sel_dir = str(QtGui.QFileDialog.getExistingDirectory(
                self, "Select Folder", ""))
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

    def delete_entity_item(self, name):
        """
        Triggered when an entity is removed from profile
        param name: Name of entity to delete
        type name: str
        """
        items = self.entity_model.findItems(name)
        if len(items) > 0:
            self.entity_model.removeRow(items[0].row())

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
        self.cboProfile.setCurrentIndex(0)

    #PROFILE
    def new_profile(self):
        """
        Creates a new instance of a profile and adds it to the
        StdmConfiguration singleton
        """
        editor = ProfileEditor(self)
        result = editor.exec_()
        if result == 1:
            profile = self.stdm_config.create_profile(editor.profile_name)
            profile.description = editor.desc
            self.connect_entity_signals(profile)
            self.stdm_config.add_profile(profile)

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
        Delete the current selected profile
        """
        if self.cboProfile.count() == 1:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Cannot delete last profile!"))
            return

        msg = "Are you sure you want to delete the profile?"
        if self.query_box(msg) == QMessageBox.Cancel:
            return

        profile_name = unicode(self.cboProfile.currentText())
        if not self.stdm_config.remove_profile(profile_name):
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Unable to delete profile!"))
            return
        self.load_profile_cbo()

    def get_profiles(self):
        profiles = []
        for profile in self.stdm_config.profiles.items():
                profiles.append(profile[0])

        return profiles

    def load_profile_cbo(self):
        profiles = self.get_profiles()
        self.cboProfile.clear()
        self.cboProfile.insertItems(0, profiles)
        self.cboProfile.setCurrentIndex(0)

    def add_column_item(self, column):
        self.col_view_model.add_entity(column)
        self.party_item_model.add_entity(column)
        self.spunit_item_model.add_entity(column)

    def delete_column_item(self, name):
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
            editor = EntityEditor(self, profile)
            editor.exec_()
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No profile selected to add entity!"))

    def edit_entity(self):
        """
        Edit selected entity
        """
        if len(self.pftableView.selectedIndexes())==0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No entity selected for edit!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.pftableView)

        # don't edit entities that already exist in the database
        if pg_table_exists(entity.name):
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Editing entity that exist in database is not allowed!"))
            return

        if model_item:
            profile = self.current_profile()
            editor = EntityEditor(self, profile, entity)
            result = editor.exec_()
            if result == 1:
                self.entity_model.delete_entity(entity)
                self.entity_model.add_entity(editor.entity)


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
        self.cboSPUnit.setModel(view_model)

    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
                continue

            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                    'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                    'ENTITY_SUPPORTING_DOCUMENT']:

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
        #Exit if the name is empty
        if not name:
            return

        profile = self.stdm_config.profile(unicode(name))
        self.lblDesc.setText(profile.description)

        # clear view models
        self.clear_view_model(self.entity_model)
        self.clear_view_model(self.col_view_model)
        self.clear_view_model(self.lookup_view_model)
        self.clear_view_model(self.lookup_value_view_model)
        self.clear_view_model(self.party_item_model)
        self.clear_view_model(self.spunit_item_model)

        self.entity_model = EntitiesModel()
        self.set_view_model(self.entity_model)

        self.col_view_model = ColumnEntitiesModel()
        self.tbvColumns.setModel(self.col_view_model)

        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)
        self.lvLookupValues.setModel(self.lookup_value_view_model)

        # from profile entities to view_model
        self.populate_view_models(profile)

        self.connect_signals()

    def profile_changed(self, row_id):
        self.switch_profile(self.cboProfile.currentText())
		
    def _create_ent(self, profile, entity_name):
        entity = profile.create_entity(entity_name, entity_factory)
        self.connect_column_signals(entity)
        profile.add_entity(entity)

    def get_model_entity(self, view):
        """
        Extracts and returns an entitymodel, entity and selected item ID
        from QAbstractItemView of a view widget
        param view: Widget that inherits QAbstractItemView
        type view: QAbstractitemView
        rtype: tuple
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
        cbo_model = self.cboParty.model()
        try:
            columns = cbo_model.entity_byId(row_id).columns.values()
            self.party_item_model.clear()
            self.party_item_model = STRColumnEntitiesModel()
            self.addColumns(self.party_item_model, columns)
            #self.lvParty.setModel(self.party_item_model)
        except:
            pass

    def spatial_unit_changed(self, row_id):
        cbo_model = self.cboSPUnit.model()
        try:
            columns = cbo_model.entity_byId(row_id).columns.values()
            self.spunit_item_model.clear()
            self.spunit_item_model = STRColumnEntitiesModel()
            self.addColumns(self.spunit_item_model, columns)
            #self.lvSpatialUnit.setModel(self.spunit_item_model)
        except:
            pass

    def _make_column(self, id, col_name, entity):
        '''
        Helper function
        '''
        col = BaseColumn.registered_types.values()[id](col_name, entity)
        return col

    def new_column(self):
        if len(self.lvEntities.selectedIndexes())==0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No entity selected to add column!"))
            return

        model_item, entity, row_id = self.get_model_entity(self.lvEntities)

        if model_item:
            profile = self.current_profile()
            params = {}
            params['entity'] = entity
            params['profile'] = profile

            editor = ColumnEditor(self, **params)
            result = editor.exec_()

            if result == 1:
                if editor.type_info == 'LOOKUP':
                    self.clear_lookup_view()
                    self.populate_lookup_view(profile)
                    self.lvLookups.setCurrentIndex(self.lookup_view_model.index(0,0))

    def edit_column(self):
        """
        Edit selected column.
        Only allow editting of columns that have not yet being persisted to the
        database
        """
        rid, column = self._get_column(self.tbvColumns)
        
        if column and column.action == DbItem.CREATE:
            row_id, entity = self._get_entity(self.lvEntities)

            # Don't edit if a column exist in database
            if self.column_exist_in_entity(entity, column):
                self.show_message(QApplication.translate("Configuration Wizard", \
                        "Editing columns that exist in database is not allowed!"))
                return

            params = {}
            params['column'] = column
            params['entity'] = entity
            params['profile'] = self.current_profile()
            
            editor = ColumnEditor(self, **params)
            result = editor.exec_()
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No column selected for edit!"))

    def clear_lookup_view(self):
        self.clear_view_model(self.lookup_view_model)
        self.lookup_view_model = LookupEntitiesModel()
        self.lvLookups.setModel(self.lookup_view_model)
        self.lookup_item_model = self.lvLookups.selectionModel()
        self.lookup_item_model.selectionChanged.connect(self.lookup_changed)
        
    def populate_lookup_view(self, profile):
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
                continue
            if entity.TYPE_INFO == 'VALUE_LIST':
                self.lookup_view_model.add_entity(entity)
                self.addValues_byEntity(entity)

    def _get_entity_item(self, view):
        model_item, entity, row_id = self.get_model_entity(view)
        entity_item = None
        if model_item:
            entity_item = model_item.entities().values()[row_id]
        return row_id, entity_item

    def _get_column(self, view):
        row_id = -1
        model_item, entity, row_id = self.get_model_entity(view)
        column = None
        if model_item:
            column = model_item.entities().values()[row_id]
        return row_id, column

    def _get_entity(self, view):
        model_item, entity, row_id = self.get_model_entity(view)
        if entity:
            return row_id, entity

    def delete_column(self):
        row_id, column = self._get_column(self.tbvColumns)
        if column:
            ent_id, entity = self._get_entity(self.lvEntities)
            # delete from the entity
            entity.remove_column(column.name)
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No column selected for deletion!"))
	
    def new_lookup(self):
        profile = self.current_profile()
        if profile:
            editor = LookupEditor(self, profile)
            result = editor.exec_()
            if result == 1:
                self.lookup_view_model.add_entity(editor.lookup)
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No profile selected to add lookup!"))

    def edit_lookup(self):
        profile = self.current_profile()
        if profile:
            if len(self.lvLookups.selectedIndexes()) == 0:
                self.show_message(QApplication.translate("Configuration Wizard", \
                        "No lookup selected for edit!"))
                return

            row_id, lookup = self._get_entity_item(self.lvLookups)
            # don't edit entities that already exist in the database
            if pg_table_exists(lookup.name):
                self.show_message(QApplication.translate("Configuration Wizard", \
                        "Editing lookup that exist in database is not allowed!"))
                return
            editor = LookupEditor(self, profile, lookup)
            result = editor.exec_()
            if result == 1:
                self.lookup_view_model.delete_entity(lookup)
                self.lookup_view_model.removeRow(row_id)
                self.lookup_view_model.add_entity(editor.lookup)
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Nothing to edit!"))

    def delete_lookup(self):
        profile = self.current_profile()
        if profile:
            if len(self.lvLookups.selectedIndexes()) > 0:
                row_id, lookup = self._get_entity_item(self.lvLookups)
                # dont delete `tenure_type` lookup
                if lookup.short_name == 'check_tenure_type':
                    self.show_message(QApplication.translate("Configuration Wizard",
                        "Cannot delete tenure type lookup table!"))
                    return
                profile.remove_entity(lookup.short_name)
                self.lookup_view_model.removeRow(row_id)
            else:
                self.show_message(QApplication.translate("Configuration Wizard", \
                        "No lookup selected for deletion!"))
        else:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Nothing to delete!"))

    def addValues_byEntity(self, entity):
        for v in entity.values:
            cv = entity.code_value(v)
            if cv.updated_value == '':
                txt = cv.value
            else:
                txt = cv.updated_value

            val = QStandardItem(txt)
            self.lookup_value_view_model.appendRow(val)

    def add_values(self, values):
        self.lookup_value_view_model.clear()
        for v in values:
            val = QStandardItem(v.value)
            self.lookup_value_view_model.appendRow(val)

    def lookup_changed(self, selected, diselected):
        row_id = self.lookup_item_model.currentIndex().row()
        if row_id == -1:
            return
        view_model = self.lookup_item_model.currentIndex().model()
        self.lookup_value_view_model.clear()
        self.addValues_byEntity(view_model.entity_byId(row_id))
        self.lvLookupValues.setModel(self.lookup_value_view_model)

    def add_lookup_value(self):
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
        if len(self.lvLookupValues.selectedIndexes() ) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "No value selected for edit!"))
            return
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
        if len(self.lvLookupValues.selectedIndexes() ) == 0:
            self.show_message(QApplication.translate("Configuration Wizard", \
                    "Select value to delete"))
            return

        row_id, lookup = self._get_entity_item(self.lvLookups)
        model_index = self.lvLookupValues.selectedIndexes()[0]
        value_text = self.lookup_value_view_model.itemFromIndex(model_index).text()
        lookup.remove_value(unicode(value_text))
        self.add_values(lookup.values.values())

    def get_str_columns(self, item_model):
        return [item_model.item(row) for row in range(item_model.rowCount()) \
                if item_model.item(row).checkState()==Qt.Checked]

    def show_message(self, message, msg_icon=QMessageBox.Critical):
        msg = QMessageBox(self)
        msg.setIcon(msg_icon)
        msg.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msg.setText(QApplication.translate("STDM Configuration Wizard",message))
        msg.exec_()

    def query_box(self, msg):
        msgbox = QMessageBox(self)
        msgbox.setIcon(QMessageBox.Question)
        msgbox.setWindowTitle(QApplication.translate("STDM Configuration Wizard","STDM"))
        msgbox.setInformativeText(QApplication.translate("STDM Configuration Wizard", msg))
        msgbox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok);
        msgbox.setDefaultButton(QMessageBox.Cancel);
        result = msgbox.exec_()
        return result


