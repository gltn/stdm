"""
/***************************************************************************
Name                 : XFormInstanceManager
Description          : A class to read and enumerate collected data from mobile phones

Date                 : 16/June/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
import os
import shutil
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import (
    QDialog,
    QMessageBox,
    QListWidgetItem,
    QFileDialog,
    QIcon,
    QDialogButtonBox
)
from PyQt4.Qt import QDirIterator
from PyQt4.QtCore import (
    QDir,
    QFile,
    QDateTime
)
from PyQt4.Qt import QApplication

from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration,
        Profile
)
import datetime

from stdm.ui.notification import NotificationBar
from stdm.settings import current_profile
from stdm.utils.util import setComboCurrentIndexWithText
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.geoodk.importer.uuid_extractor import InstanceUUIDExtractor
from stdm.ui.wizard.custom_item_model import EntitiesModel
from stdm.geoodk.importer import EntityImporter
from stdm.settings.projectionSelector import ProjectionSelector
from stdm.geoodk.importer import ImportLogger
from stdm.geoodk.importer import Save2DB

from stdm.third_party.sqlalchemy.exc import SQLAlchemyError
from stdm import resources_rc
#from stdm.geoodk.importer.geoodkserver import JSONEXTRACTOR


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_import.ui'))

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/geoodk/'
MSG = 'Error creating log'
GEOODK_FORM_HOME = CONFIG_FILE+'instances'

class ProfileInstanceRecords(QDialog, FORM_CLASS):
    """
    class constructor
    The class handles all the instances that the user has collected
    and saved in the folder and saved in a computer. The class will
    construct the path to the folder and enumerate all available instances
    and return the count. It will also rename all the file based on instance
    unique GUUID for easier management and future updates.
    """
    def __init__(self, parent=None):
        """
        initailize class variables here
        """
        super(ProfileInstanceRecords, self).__init__(parent)
        self.setupUi(self)

        self.path = None
        self.instance_list = []
        self.relations = {}
        self.parent_ids = {}
        self.importlogger = ImportLogger()
        self._notif_bar_str = NotificationBar(self.vlnotification)

        self.chk_all.setCheckState(Qt.Checked)
        self.entity_model = EntitiesModel()
        self.uuid_extractor = InstanceUUIDExtractor(self.path)
        self.btn_chang_dir.setIcon(QIcon(":/plugins/stdm/images/icons/open_file.png"))
        self.btn_refresh.setIcon(QIcon(":/plugins/stdm/images/icons/update.png"))
        self.btn_srid.setIcon(QIcon(":/plugins/stdm/images/icons/edit24.png"))

        self.chk_all.stateChanged.connect(self.check_state_on)
        #self.cbo_profile.currentIndexChanged.connect(self.current_profile_changed)
        self.btn_chang_dir.clicked.connect(self.on_directory_search)
        self.lst_widget.itemClicked.connect(self.user_selected_entities)
        self.btn_srid.clicked.connect(self.projection_settings)
        self.btn_refresh.clicked.connect(self.update_files_with_custom_filter)

        #self.load_config()
        self.on_filepath()
        self.current_profile_changed()
        self.check_state_on()
        self.instance_dir()

    def load_config(self):
        """
        Load STDM configuration
        :return:
        """
        stdm_config = None
        if QFile.exists(HOME+"/stdm/configuration.stc"):
            stdm_config = QFile(CONFIG_FILE)
        ConfigurationFileSerializer(stdm_config)
        profiles = StdmConfiguration.instance().profiles
        return profiles

    def check_state_on(self):
        """
        Ensure all the items in the list are checked
        :return:
        """
        count = self.lst_widget.count()
        if count > 0:
            for i in range(count):
                item = self.lst_widget.item(i)
                if self.chk_all.isChecked():
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

    def profiles(self):
        """
        Get all profiles
        :return:
        """
        return self.load_config().values()

    def current_profile_changed(self):
        """
        Get the current profile so that it is the one selected at the combo box
        :return:
        """
        self.instance_list = []
        self.active_profile()
        self.on_filepath()
        self.available_records()
        self.on_dir_path()
        self.profile_instance_entities()

    def active_profile(self):
        """
        get the user selected profile
        :return:p
        """
        self.profile = current_profile().name
        return self.profile

    def instance_dir(self):
        """
        Create a path where imported instance will be kept
        :return:
        """
        self.inst_path = CONFIG_FILE+"imported"
        if not os.access(self.inst_path, os.F_OK):
            os.makedirs(unicode(self.inst_path))
        else:
            return self.inst_path

    def imported_instance_path(self):
        """
        :return:
        """
        self.instance_dir()
        return self.inst_path

    def on_filepath(self):
        """
        Access the file directory with geoodk files by constructing the full path
        :return: path
        :rtype: string
        """
        if self.txt_directory.text() != '':
            self.path = self.txt_directory.text()
        else:
            self.path = GEOODK_FORM_HOME
            if not os.access(self.path, os.F_OK):
                os.makedirs(unicode(self.path))
            self.txt_directory.setText(self.path)
        return self.path

    def xform_xpaths(self):
        """
        Return the full path to the default config path and filter geoodk
        instance that matches the current profile path
        :return: directories
        :rtype: list
        """
        return [os.path.join(self.path, name) for name in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, name))
                if name.startswith(self.profile_formater())]


    def on_dir_path(self):
        """
        Extract the specific folder information and rename the file
        :return:
        """
        self.uuid_extractor.new_list = []
        if self.record_count() > 0:
            directories = self.xform_xpaths()
            for directory in directories:
                self.extract_guuid_and_rename_file(directory)

    def extract_guuid_and_rename_file(self, path):
        """
        Extract teh unique Guuid and rename the file
        so that we can uniquely identify each file
        :return:
        """
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and f.endswith('.xml'):
                file_instance = os.path.join(path, f)
                self.rename_file_to_UUID(file_instance)

    def rename_file_to_UUID(self, file):
        """
        Extract the UUID from each folder and file
        :return:
        """
        self.uuid_extractor.set_file_path(file)
        self.uuid_extractor.on_file_passed()
        self.instance_list = self.uuid_extractor.new_list

    def move_imported_file(self, file):
        """
        Moves the imported files to avoid repetition
        :return:
        """
        instance_path = self.imported_instance_path()
        try:
            basename = os.path.basename(os.path.dirname(file))
            if not os.path.isdir(os.path.join(self.imported_instance_path(), basename)):
               shutil.move(os.path.dirname(file), instance_path)
            else:
                pass

        except Exception as ex:
            return ex

    def profile_instance_entities(self):
        """
        Add the user entities that are in the instance file
        into a list view widget
        :return: model
        """
        self.lst_widget.clear()
        entity_list = self.instance_entities()
        if entity_list is not None and len(entity_list) > 0:
            for entity in entity_list:
                list_widget = QListWidgetItem(
                    current_profile().entity_by_name(entity).short_name, self.lst_widget)
                list_widget.setCheckState(Qt.Checked)
        else:
            return

    def user_selected_entities(self):
        """

        :return:
        """
        user_list= []
        count = self.lst_widget.count()
        if count > 0:
            for i in range(count):
                item = self.lst_widget.item(i)
                if item.checkState() == Qt.Checked:
                    user_list.append(current_profile().entity(item.text()).name)
            return user_list
        else:
            return None

    def instance_entities(self):
        """
        Enumerate the entities that are in the current profile
         and also that are captured in the form so that we are only importing relevant entities to database
        :return: entities
        """
        dirs = self.xform_xpaths()
        current_etities = []
        if len(dirs) > 0:
            dir_f = dirs[0]
            instance_file = [f for f in os.listdir(dir_f) if f.endswith('.xml')]
            if len(instance_file) > 0:
                self.uuid_extractor.set_file_path(os.path.join(dir_f, instance_file[0]))
                entity_list = self.check_profile_with_custom_name()
                for entity_name in entity_list:
                    if current_profile().entity_by_name(entity_name) is not None:
                        if entity_name not in current_etities:
                            current_etities.append(entity_name)
                if len(current_etities) > 0:
                    return current_etities

    def check_profile_with_custom_name(self):
        """
        Try extract mobile instance with custom filter name.
        Assumption is that there is a profile that bears that name
        :return:
        """
        mismatch_profile = 'Nothing found to import. \n' \
                           ' Ensure the current filter text or profile is correct'
        entity_attr = []
        if self.txt_filter.text()!= '':
            for obj in self.profiles():
                if obj.name.startswith(self.txt_filter.text()):
                    if obj.name != current_profile().name:
                        self._notif_bar_str.insertErrorNotification(mismatch_profile)
                        return
        return self.uuid_extractor.document_entities(self.profile)

    def user_table_filter(self):
        """
        Enumerate all user tables in the profile
        :return:
        """
        user_entities = []
        enit = current_profile().user_entities()
        for en in enit:
            user_entities.append(en.name)
        return user_entities

    def has_foreign_keys_parent(self, select_entities):
        """
        Ensure we check that the table is not parent else
        import parent table first
        :return:
        """
        self.relations = {}
        str_tables = current_profile().social_tenure
        party_tbl = str_tables.parties[0].name
        sp_tbl = str_tables.spatial_units[0].name
        has_relations = False
        for table in select_entities:
            table_object = current_profile().entity_by_name(table)
            cols = table_object.columns.values()
            for col in cols:
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    parent_object = table_object.columns[col.name]
                    if parent_object.parent:
                        self.relations[parent_object.parent.name] = [table,col.name]
                        has_relations = True
                    else:
                        self.feedback_message('unable to read foreign key properties for "{0}"'
                                              .format(parent_object.name))
                        return
        has_str_defined = self.uuid_extractor.has_str_captured_in_instance()

        if has_str_defined:

            if party_tbl not in self.relations.keys():
                self.relations[party_tbl] = ['social_tenure_relationship',
                                             str_tables.parties[0].short_name.lower()+'_id']
            if sp_tbl not in self.relations.keys():
                self.relations[sp_tbl] = ['social_tenure_relationship',
                                          str_tables.spatial_units[0].short_name.lower() + '_id']
        else:

            return has_relations

    def parent_table_isselected(self):
        """
        Take note that the user selected tables may or may not be imported
        based on parent child table relationship.
        Add those table silently so that we can show them to the user
        :return:
        """
        try:
            silent_list = []
            if self.user_selected_entities() > 0:
                for table in self.relations.keys():
                    if table not in self.user_selected_entities():
                        silent_list.append(table)
            return silent_list
        except Exception as ex:
            self._notif_bar_str.insertErrorNotification(ex.message)

    def archive_this_import_file(self, counter, instance):
        """
        Ensure that only import are done once
        :return:
        """
        try:
            self.importlogger.logger_sections()
            file_info = 'File instance ' + str(counter)+ ' : \n' + instance
            self.importlogger.onlogger_action(file_info)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": "+io.message)
            pass

    def log_table_entry(self, instance):
        """
        Ensure that only import are done once
        :return:
        """
        try:
            current_time = QDateTime()
            import_time = current_time.currentDateTime()
            log_entry = instance + ' '+ str(import_time.toPyDateTime())
            self.importlogger.onlogger_action(log_entry)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": "+io.message)
            pass

    def check_previous_import(self):
        """
        Ensure we are importing files once
        :return:
        """
        try:
            self.importlogger.add_log_info()
            for files in self.instance_list:
                current_dir = os.path.basename(files)
                exist = self.importlogger.check_file_exist(current_dir)
                if exist:
                    self.instance_list.remove(files)
            self.txt_count.setText(str(len(self.instance_list)))
            if self.record_count() != len(self.instance_list):
                msg = 'Some files have been already imported and therefore ' \
                   'not enumerated'
                self._notif_bar_str.insertErrorNotification(msg)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": "+io.message)
            pass

    def available_records(self):
        """
        Let the user know how many records have been collected and are available
         for inport process
        :return:
        """
        self.txt_count.setText(unicode(self.record_count()))

    def record_count(self):
        """
        get the count of instance dir in the selected directory
        :return: integer
        """
        return len([name for name in os.listdir(self.path)
                    if os.path.isdir(os.path.join(self.path, name))
                    if name.startswith(self.profile_formater())])

    def profile_formater(self):
        """
        Format the profile name by removing underscore character
        :return:
        """
        if self.txt_filter.text() != '':
            filter_text = self.txt_filter.text()
            return filter_text
        else:
            return self.profile

    def update_files_with_custom_filter(self):
        """
        Get the new file count with the user custom filter text
        :return: file count
        """
        self.available_records()
        self.on_dir_path()
        self.profile_instance_entities()

    def projection_settings(self):
        """
        let user select the projections for the data
        :return:
        """
        project_select = ProjectionSelector(self)
        projection = project_select.loadAvailableSystems()
        self.txt_srid.setText(str(projection))

    def on_projection_select(self):
        """
        Get the selected projection and set it during data import
        :return:
        """
        vals = self.txt_srid.text().split(":")
        return vals[1]

    def on_directory_search(self):
        """
        Let the user choose the directory with instances
        :return:
        """
        home_path = 'home'
        if self.txt_directory.text() != '':
            home_path = self.txt_directory.text()

        dir_name = QFileDialog.getExistingDirectory(
                self, 'Open Directory', home_path, QFileDialog.ShowDirsOnly
                )
        if dir_name:
            self.txt_directory.setText(str(dir_name))
            self.current_profile_changed()
        self.check_state_on()

    def unique_counter_counter(self):
        """
        Keep a list of all the table imported since some table will appear in multiples
        in the instance file.
        Store id, and name
        :return:
        """



    def feedback_message(self, msg):
        """
        Create a dialog box to capture and display errrors related to db
        while importing data
        :param: msg
        :type: string
        :return:Qdialog
        """
        msgbox = QMessageBox()
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msgbox.setWindowTitle("Data Import")
        msgbox.setText(msg)
        msgbox.exec_()
        msgbox.show()
        return msgbox

    def save_instance_data_to_db(self, entity_info):
        """
                Get the user selected entities and insert them into database
                params: selected entities
                rtype: list
                :return:Object
                :type: dbObject
                """
        cu_obj = ''
        import_status = False
        self.txt_feedback.clear()
        self.txt_feedback.append("Starting import...\n")
        self._notif_bar_str.clear()
        self.has_foreign_keys_parent(entity_info)
        if len(self.parent_table_isselected()) > 0:
            if QMessageBox.information(self, QApplication.translate('GeoODKMobileSettings', " Import Warning"),
                                       QApplication.translate('GeoODKMobileSettings',
                                                              'Some of dependent tables (entities)'
                                                              'which may not be part of the selected tables '
                                                              'I.e: {} will be imported'
                                                                      .format(self.parent_table_isselected())),
                                       QMessageBox.Ok | QMessageBox.No) == QMessageBox.No:
                return
        try:
            counter = 0
            if len(self.instance_list) > 0:
                #print len(self.instance_list)
                self.pgbar.setRange(counter, len(self.instance_list))
                self.pgbar.setValue(0)
                self.importlogger.onlogger_action("Starting import...\n")
                for instance in self.instance_list:
                    parents_info = []
                    import_status = False
                    counter = counter + 1
                    self.parent_ids = {}
                    entity_importer = EntityImporter(instance)

                    self.uuid_extractor.set_file_path(instance)
                    self.archive_this_import_file(counter, instance)
                    field_data = self.uuid_extractor.document_entities_with_data(current_profile().name,
                                                                                 self.user_selected_entities())
                    single_occuring, repeated_entities = self.uuid_extractor.attribute_data_from_nodelist(field_data)

                    for entity, entity_data in single_occuring.iteritems():
                        import_status = False
                        if entity in self.relations:
                            self.count_import_file_step(counter, entity)
                            log_timestamp = '======= starting import for parent table ===== : {0}' \
                                .format(entity)
                            cu_obj = entity
                            self.log_table_entry(log_timestamp)
                            entity_add = Save2DB(entity, entity_data)
                            entity_add.objects_from_supporting_doc(instance)
                            # entity_add.get_srid(GEOMPARAM)
                            ref_id = entity_add.save_parent_to_db()
                            import_status = True
                            self.parent_ids[entity] = [ref_id, entity]
                            log_timestamp = ' -------- import succeeded:        {0}' \
                                .format(str(import_status))
                            self.log_table_entry(log_timestamp)
                            parents_info.append(entity)
                            single_occuring.pop(entity)
                            #
                        elif entity not in self.relations:
                            import_status = False
                            ##   .format(entity)
                            #self.log_table_entry(log_timestamp)
                            self.count_import_file_step(counter, entity)
                            entity_add = Save2DB(entity, entity_data, self.parent_ids)
                            entity_add.objects_from_supporting_doc(instance)
                            child_id = entity_add.save_to_db()
                            cu_obj = entity
                            import_status = True
                            parents_info.append(entity)
                            if entity in self.parent_ids:
                                continue
                            else:
                                self.parent_ids[entity] = [child_id, entity]
                            self.log_table_entry(" ---------{0}  table import succeeded:      {1} "
                                                 .format(entity,import_status))
                        #print self.parent_ids

                    if repeated_entities:
                        self.log_table_entry(" ========== starting import of repeated tables ============")
                        import_status = False
                        for repeated_entity, entity_data in repeated_entities.iteritems():
                            """We are assuming that the number of repeat table cannot exceed 99"""
                            enum_index = repeated_entity[:2]
                            if enum_index.isdigit():
                                repeat_table = repeated_entity[2:]
                            else:
                                repeat_table = repeated_entity[1:]
                            log_timestamp = '          child table {0} >> : {1}' \
                                    .format(repeated_entity[1:], repeat_table)
                            self.count_import_file_step(counter, repeat_table)
                            self.importlogger.onlogger_action(log_timestamp)
                            if repeat_table in self.user_table_filter():
                                entity_add = Save2DB(repeat_table, entity_data, self.parent_ids)
                                entity_add.objects_from_supporting_doc(instance)
                                child_id = entity_add.save_to_db()
                                cu_obj = repeat_table
                                import_status = True
                                self.log_table_entry(" ------------- import succeeded:      {0} "
                                                     .format(import_status))
                            else:
                                continue
                    if self.uuid_extractor.has_str_captured_in_instance():
                        if self.parent_ids is not None:
                            self.txt_feedback.append('----Creating social tenure relationship')
                            entity_importer.process_social_tenure(self.parent_ids)
                            self.log_table_entry(" ----- saving social tenure relationship")
                            self.txt_feedback.append(
                            'saving record "{0}" to database'.format(counter))
                        self.pgbar.setValue(counter)

                    self.txt_feedback.append('Number of records successfully imported:  {}'
                                                .format(counter))
            else:
                self._notif_bar_str.insertErrorNotification("No user selected entities to import")
                self.pgbar.setValue(0)
                return
        except SQLAlchemyError as ae:
            self.feedback_message(unicode(ae.message))
            self.txt_feedback.append("current table {0}import failed...\n".format(cu_obj))
            self.txt_feedback.append(str(ae.message))
            self.log_table_entry(unicode(ae.message))
        except Exception as ex:
            self.txt_feedback.append("\n \n {0}  table "
                                     "import failed...  \n".format(cu_obj)+ '\n See error '
                                                                             'message below!\n')
            self.txt_feedback.append(str(ex.message))
            self.log_table_entry(
                 unicode(ex.message)+'----- {0} import succeeded:    '.format(cu_obj)+unicode(import_status))
            self.feedback_message(unicode(ex.message))
            return

    def count_import_file_step(self, count = None, table = None):
        """
        Tracking method to record the current import activity
        :param count: int
        :param table: string
        :return:
        """
        #self.txt_feedback.append('File :  {}'.format(count))
        self.txt_feedback.append('      Table : {}'.format(table))

    def accept(self):
        """
        Execute the import dialog once the save button has been clicked
        :return:
        """
        self.buttonBox.setEnabled(False)

        try:
            if self.lst_widget.count() < 1:
                msg = 'No mobile records could be found for the current profile'
                self._notif_bar_str.insertErrorNotification(msg)
                self.buttonBox.setEnabled(True)
                return
            entities = self.user_selected_entities()
            if len(entities) < 1:
                if QMessageBox.information(self,
                        QApplication.translate('MobileForms', 'Import Warning'),
                        QApplication.translate('MobileForms',
                        'You have not '
                        'selected any entity for import. All entities '
                        'will be imported'), QMessageBox.Ok |
                                            QMessageBox.No) == QMessageBox.Ok:
                    entities = self.instance_entities()
                else:
                    self.buttonBox.setEnabled(True)
                    return

            self.save_instance_data_to_db(entities)
            self.buttonBox.setEnabled(True)
        except Exception as ex:
            self._notif_bar_str.insertErrorNotification(ex.message)
            self.feedback_message(str(ex.message))
            self.buttonBox.setEnabled(True)







