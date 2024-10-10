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
import glob
import shutil
# from stdm.geoodk.importer.geoodkserver import JSONEXTRACTOR
from collections import OrderedDict
from typing import Dict, List, TypeVar

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QCoreApplication, QDateTime, QDir, QFile, Qt
from qgis.PyQt.QtWidgets import (QApplication, QDialog, QDialogButtonBox,
                                 QFileDialog, QListWidgetItem, QMessageBox)
from sqlalchemy.exc import SQLAlchemyError

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.exceptions import DummyException
from stdm.geoodk.importer.entity_importer import (
    EntityImporter, 
    Save2DB
)

from stdm.geoodk.importer.import_log import ImportLogger

from stdm.geoodk.importer.uuid_extractor import (
    EntityNodeData,
    InstanceUUIDExtractor
)

from stdm.settings import current_profile
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings.projectionSelector import ProjectionSelector
from stdm.ui.gui_utils import GuiUtils
from stdm.ui.notification import NotificationBar
from stdm.ui.wizard.custom_item_model import EntitiesModel

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_import.ui'))

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/geoodk/'
MSG = 'Error creating log'
GEOODK_FORM_HOME = CONFIG_FILE + 'instances'

# Type aliases
QtCheckState = Qt.CheckState
Profile = TypeVar('Profile')
ProfileName = str
EntityName  = str
FileName    = str

class InstanceData:
    def __init__(self, field_data_nodes: List[EntityNodeData], str_data_nodes: List[EntityNodeData]):
        self.field_data_nodes = field_data_nodes
        self.str_data_nodes = str_data_nodes


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
        self.relations = OrderedDict()
        self.parent_ids = {}
        self.importlogger = ImportLogger()
        self._notif_bar_str = NotificationBar(self.vlnotification)

        self.chk_all.setCheckState(Qt.Checked)
        self.entity_model = EntitiesModel()
        self.uuid_extractor = InstanceUUIDExtractor(self.path)
        self.btn_chang_dir.setIcon(GuiUtils.get_icon("open_file.png"))
        self.btn_refresh.setIcon(GuiUtils.get_icon("update.png"))

        self.chk_all.stateChanged.connect(self.change_check_state)
        # self.cbo_profile.currentIndexChanged.connect(self.current_profile_changed)
        self.btn_chang_dir.clicked.connect(self.on_directory_search)
        self.lst_widget.itemClicked.connect(self.user_selected_entities)
        self.btn_refresh.clicked.connect(self.update_files_with_custom_filter)

        self.buttonBox.button(QDialogButtonBox.Save).setText('Import')

        # self.load_config()
        self.active_profile()
        self.init_file_path()
        #self.current_profile_changed()
        self.change_check_state(self.chk_all.checkState())
        self.change_check_state(Qt.Checked)
        self.set_imported_instance_folder()

        self.chk_all.setVisible(False)
        self.txt_filter.setVisible(False)
        self.label_14.setVisible(False)
        self.btn_refresh.setVisible(False)

    def showEvent(self, event):
        # Make sure we ONLY have one xml file in the instance folder
        super(ProfileInstanceRecords, self).showEvent(event)
        instances = self.check_instances_with_bad_count_xml_files()
        if len(instances) == 0:
            self.current_profile_changed()
            return

        self.txt_feedback.append('Errors found in data files, import failed.')
        self.txt_feedback.append('')
        for instance, count in instances.items():
            self.txt_feedback.append(f'{instance}: =>  {count}')

        self.txt_feedback.append('')
        self.txt_feedback.append('Fix the errors then try again.')
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)


    def check_instances_with_bad_count_xml_files(self):
        """
        Returns the number of xml files in the instance folder.
        """
        instances = {}

        instance_folders = self.xform_xpaths()
        for instance_folder in instance_folders:
            xml_folder = os.path.join(instance_folder, '*.xml')
            xml_files = glob.glob(xml_folder)
            if len(xml_files) == 0:
                instances[instance_folder] = 0
            if len(xml_files) > 1:
                instances[instance_folder] = len(xml_files)

        return instances

    def load_config(self) -> Dict[ProfileName, Profile]:
        """
        Load STDM configuration
        Returns an ordered dict
        """
        stdm_config = None
        if QFile.exists(HOME + "/stdm/configuration.stc"):
            stdm_config = QFile(CONFIG_FILE)
        ConfigurationFileSerializer(stdm_config)
        profiles = StdmConfiguration.instance().profiles
        return profiles

    def profiles(self)-> List[Profile]:
        """
        Return a list of all profiles
        :rtype: list
        """
        return list(self.load_config().values())

    def change_check_state(self, state: QtCheckState):
        """
        Change the check state of items in a list widget
        """
        for i in range(self.lst_widget.count()):
            #self.lst_widget.item(i).setCheckState(state)
            self.lst_widget.item(i).setFlags(Qt.ItemIsEnabled)

    def current_profile_changed(self):
        """
        Get the current profile so that it is the one selected at the combo box
        """
        self.instance_list = []
        #self.active_profile()
        self.init_file_path()
        self.available_records()
        self.on_dir_path()
        self.populate_entities_widget()

    def active_profile(self) -> str:
        """
        Return active profile name
        """
        self.profile = current_profile().name
        return self.profile

    def set_imported_instance_folder(self):
        """
        """
        self.inst_path = CONFIG_FILE + "_imported"
        if not os.access(self.inst_path, os.F_OK):
            os.makedirs(str(self.inst_path))

    def imported_instance_folder(self) -> str:
        return self.inst_path

    def init_file_path(self):
        """
        Initialize GeoODK file path
        """
        self.path = self.geoODK_file_path(self.txt_directory.text())
        self.txt_directory.setText(self.path)

    def geoODK_file_path(self, path: str='') -> str:
        """
        Check if geoODK file path has been configured, if not configure default
        and return it.
        """
        if not path.strip():
            path = self.make_path(GEOODK_FORM_HOME)
        return path

    def make_path(self, path: str) -> str:
        """
        Create and return a file path if is not available.
        """
        if not os.access(path, os.F_OK):
            os.makedirs(str(path))
        return path

    def xform_xpaths(self) -> List[str]:
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
        self.importlogger.start_json_file()
        self.previous_import_instances()
        self.txt_count.setText(str(len(self.instance_list)))

    def extract_guuid_and_rename_file(self, path: str):
        """
        Extract the unique Guuid and rename the file
        so that we can uniquely identify each file
        :return:
        """
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)) and f.endswith('.xml'):
                file_instance = os.path.normcase(os.path.join(path, f))
                if os.path.isfile(file_instance):
                    self.rename_file_to_UUID(file_instance)

    def read_instance_data(self) -> Dict[str, tuple[str, InstanceData]]:
        """
        Read all instance data once and store them in a dict
        :str is filename
        """
        mobile_data = OrderedDict()
        #social_tenure_info = OrderedDict()
        self.uuid_extractor.unset_path()

        for full_filename in self.instance_list:
            if os.path.isfile(full_filename):
                filepath, filename = os.path.split(full_filename)
                self.uuid_extractor.set_file_path(full_filename)

            mobile_data[filename] = (full_filename, InstanceData(
                    field_data_nodes=self.uuid_extractor.document_entities_with_data(
                    self.active_profile().replace(' ', '_'),
                    self.user_selected_entities()),
                    str_data_nodes=self.uuid_extractor.document_entities_with_data(
                    self.active_profile().replace(' ', '_'),
                    ['social_tenure'])))

            self.uuid_extractor.close_document()

        return mobile_data

    def rename_file_to_UUID(self, filename: str):
        """
        Extract the UUID from each folder and file
        :return:
        """
        self.uuid_extractor.set_file_path(filename)
        self.uuid_extractor.on_file_passed()
        self.instance_list = self.uuid_extractor.file_list()

    def move_imported_file(self, filename: str):
        """
        Moves the imported files to avoid repetition
        :return:
        """
        instance_path = self.imported_instance_folder()
        try:
            basename = os.path.basename(os.path.dirname(filename))
            if not os.path.isdir(os.path.join(self.imported_instance_folder(), basename)):
                shutil.move(os.path.dirname(filename), instance_path)
        except DummyException as ex:
            return str(ex)

    def populate_entities_widget(self):
        """
        Add entities in the instance file into a list view widget
        """
        self.lst_widget.clear()
        entities = self.instance_entities()
        if len(entities) > 0:
            for entity in entities:
                list_widget = QListWidgetItem(
                    current_profile().entity_by_name(entity).short_name, self.lst_widget)
                list_widget.setIcon(GuiUtils.get_icon("table02.png"))
                # list_widget.setCheckState(Qt.Checked)

    def user_selected_entities(self) -> List[EntityName]:
        """
        """
        # Returna all the entities
        return self.instance_entities()

        entities = []
        count = self.lst_widget.count()
        if count > 0:
            for i in range(count):
                item = self.lst_widget.item(i)
                if item.checkState() == Qt.Checked:
                    entities.append(current_profile().entity(item.text()).name)
        return entities

    def instance_entities(self) -> List[EntityName]:
        """
        Enumerate the entities that are in the current profile
        and also that are captured in the form so that we are only
        importing relevant entities to database
        :return: List of enitity names
        """
        current_entities = []
        instance_collections = self.instance_collection()
        if len(instance_collections) > 0:
            for entity_name in self.profile_entities_names(current_profile()):
                if current_profile().entity_by_name(entity_name) is not None:
                    current_entities.append(entity_name)
        return current_entities

    def instance_collection(self) -> List[FileName]:
        """
        Enumerate all the instances found in the instance directory
        rtype: list of xml file names
        """
        dirs = self.xform_xpaths()
        instance_collections = []
        if len(dirs) > 0:
            for dir_f in dirs:
                xml_files = [dir_f.replace("\\", "/") + '/' + f for f in os.listdir(dir_f) if f.endswith('.xml')]
                if len(xml_files) > 0:
                    instance_collections.append(xml_files[0])
        return instance_collections

    def check_profile_with_custom_name(self):
        """
        Try extract mobile instance with custom filter name.
        Assumption is that there is a profile that bears that name
        :return:
        """
        mismatch_profile = 'Nothing found to import. \n' \
                           ' Ensure the current filter text or profile is correct'
        entity_attr = []
        if self.txt_filter.text() == '':
            return
        for obj in self.profiles():
            if obj.name.startswith(self.txt_filter.text()):
                if obj.name != current_profile().name:
                    self._notif_bar_str.insertErrorNotification(mismatch_profile)
                    return
        return self.uuid_extractor.document_entities(self.profile)

    def profile_entities_names(self, profile: 'Profile') ->List[str]:
        """
        Return names of all entities in a profile
        :param profile: Profile
        :rtype: list
        """
        entities_names = []
        for entity in profile.user_entities():
            entities_names.append(entity.name)
        return entities_names

    def has_foreign_keys_parent(self, select_entities:List[str] ) -> bool:
        """
        Ensure we check that the table is not parent else
        import parent table first
        Revised in version 1.7. It explicitly assumes str is captured. before it was optional.
        :return:
        """
        has_relations = False
        str_tables = current_profile().social_tenure
        party_tbls = str_tables.parties
        sp_tbls = str_tables.spatial_units
        self.relations = OrderedDict()
        if len(self.instance_list) > 0:
            if self.uuid_extractor.has_str_captured_in_instance(self.instance_list[0]):
                for party_tbl in party_tbls:
                    self.relations[party_tbl.name] = ['social_tenure_relationship',
                                                      party_tbl.short_name.lower() + '_id']
                for sp_tbl in sp_tbls:
                    self.relations[sp_tbl.name] = ['social_tenure_relationship',
                                                   sp_tbl.short_name.lower() + '_id']

        for table in select_entities:
            table_object = current_profile().entity_by_name(table)
            cols = list(table_object.columns.values())
            for col in cols:
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    parent_object = table_object.columns[col.name]
                    if parent_object.parent:
                        if parent_object.parent.name in self.relations:
                            self.relations[parent_object.parent.name].append([table, col.name])
                        else:
                            self.relations[parent_object.parent.name] = [table, col.name]
                    has_relations = True
                else:
                    continue
        return has_relations

    def parent_table_isselected(self) -> List[str]:
        """
        Take note that the user selected tables may or may not be imported
        based on parent child table relationship.
        Add those table silently so that we can show them to the user
        :return:
        """
        try:
            silent_list = []
            # entities = self.user_selected_entities()
            entities = self.instance_entities()
            if len(entities) > 0:
                for table in self.relations.keys():
                    if table not in entities:
                        silent_list.append(table)
                return silent_list
        except DummyException as ex:
            self._notif_bar_str.insertErrorNotification(str(ex))

    def XXarchive_this_import_file(self, counter, instance):
        """
        Ensure that only import are done once
        :return:
        """
        try:
            self.importlogger.logger_sections()
            file_info = 'File instance ' + str(counter) + ' : \n' + instance
            ImportLogger.log_action(file_info)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": " + str(io))
            pass

    def log_table_entry(self, message : str):
        """
        Ensure that only import are done once
        :return:
        """
        try:
            current_time = QDateTime()
            import_time = current_time.currentDateTime()
            log_entry = message + ' ' + str(import_time.toPyDateTime())
            ImportLogger.log_action(log_entry)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": " + str(io))
            raise NameError(str(io))

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
            self._notif_bar_str.insertErrorNotification(MSG + ": " + str(io))

    def available_records(self):
        """
        Let the user know how many records have been collected and are available
         for inport process
        :return:
        """
        self.txt_count.setText(str(self.record_count()))

    def record_count(self) -> int:
        """
        Get the count of instance dir in the selected directory
        """
        return len([name for name in os.listdir(self.path)
                    if os.path.isdir(os.path.join(self.path, name))
                    if name.startswith(self.profile_formater())])

    def profile_formater(self) -> str:
        """
        Format the profile name by removing underscore character
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
        self.populate_entities_widget()
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)

    def projection_settings(self):
        """
        let user select the projections for the data
        :return:
        """
        project_select = ProjectionSelector(self)
        projection = project_select.loadAvailableSystems()
        self.txt_srid.setText(str(projection))

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
        self.change_check_state(self.chk_all.checkState())

    def feedback_message(self, msg : str) -> QMessageBox:
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

    def save_instance_data_to_db(self, entities : List[str]):
        """
        Get the user selected entities and insert them into database
        params entities: List of names for the selected entities.
        """
        cu_obj = ''
        import_status = False

        self.txt_feedback.clear()
        self.txt_feedback.append("Import started, please wait...\n")

        QCoreApplication.processEvents()
        self._notif_bar_str.clear()

        mobile_field_data = self.read_instance_data()

        has_fk = self.has_foreign_keys_parent(entities)  # populates self.relations list

        if len(self.parent_table_isselected()) > 0:
            if QMessageBox.information(self, QApplication.translate('GeoODKMobileSettings', " Import Warning"),
                                       QApplication.translate('GeoODKMobileSettings',
                                                              'Some of dependent tables (entities)'
                                                              'which may not be part of the selected tables '
                                                              'I.e: {} will be imported'
                                                                      .format(self.parent_table_isselected())),
                                       QMessageBox.Ok | QMessageBox.No) == QMessageBox.No:
                return

        if not mobile_field_data:
            self.feedback_message('Not matching data in mobile files')
            return 

        counter = 0

        try:
            self.pgbar.setRange(counter, len(self.instance_list))
            self.pgbar.setValue(0)
            ImportLogger.log_action("Import started ...\n")

            for filename, instance_data in mobile_field_data.items():

                instance_full_filename = instance_data[0]
                instance_obj_data = instance_data[1]

                ImportLogger.log_action("File {} ...\n".format(filename))
                parents_info = []
                self.parent_ids = {}
                import_status = False
                counter = counter + 1

                single_occuring, repeated_entities = self.uuid_extractor.instance_data_from_nodelist(
                    instance_obj_data.field_data_nodes)

                single_occurring_keys = list(single_occuring.keys())

                for entity_name in single_occurring_keys:
                    entity_data = single_occuring[entity_name]
                    import_status = False

                    if entity_name in self.relations:
                        #if entity_name not in self.parent_ids.keys():
                        self.count_import_file_step(counter, entity_name)
                        log_timestamp = '=== parent table import  === : {0}'.format(entity_name)
                        self.log_table_entry(log_timestamp)

                        cu_obj = entity_name
                        entity_add = Save2DB(entity_name, entity_data, self.parent_ids)

                        entity_add.objects_from_supporting_doc(instance_full_filename)

                        ref_id = entity_add.save_parent_to_db()

                        import_status = True
                        self.parent_ids[entity_name] = [ref_id, entity_name]
                        parents_info.append(entity_name)
                        single_occuring.pop(entity_name)

                    else: #entity_name not in self.relations:
                        import_status = False
                        self.count_import_file_step(counter, entity_name)
                        log_timestamp = '=== standalone table import  === : {0}'.format(entity_name)
                        cu_obj = entity_name
                        self.log_table_entry(log_timestamp)
                        entity_add = Save2DB(entity_name, entity_data, self.parent_ids)
                        entity_add.objects_from_supporting_doc(instance_full_filename)

                        child_id = entity_add.save_to_db()
                        cu_obj = entity_name
                        import_status = True
                        parents_info.append(entity_name)
                        if entity_name not in self.parent_ids.keys():
                            self.parent_ids[entity_name] = [child_id, entity_name]
                        entity_add.cleanup()

                if repeated_entities:
                    # self.log_table_entry(" ========== starting import of repeated tables ============")
                    import_status = False
                    for repeated_entity, entity_data in repeated_entities.items():
                        """We are assuming that the number of repeat table cannot exceed 99"""
                        enum_index = repeated_entity[:2]
                        if enum_index.isdigit():
                            repeat_table = repeated_entity[2:]
                        else:
                            enum_index = repeated_entity[:1]
                            repeat_table = repeated_entity[1:]
                        log_timestamp = '          child table {0} >> : {1}' \
                            .format(repeat_table, enum_index)
                        self.count_import_file_step(counter, repeat_table)
                        ImportLogger.log_action(log_timestamp)
                        if repeat_table in self.profile_entities_names(current_profile()):
                            entity_add = Save2DB(repeat_table, entity_data, self.parent_ids)
                            entity_add.objects_from_supporting_doc(instance_full_filename)
                            child_id = entity_add.save_to_db()
                            self.parent_ids[repeat_table] = [child_id, repeat_table]
                            cu_obj = repeat_table
                            import_status = True
                            self.log_table_entry(" ------ import succeeded:   {0} ".format(import_status))
                            entity_add.cleanup()
                            QCoreApplication.processEvents()
                        else:
                            continue

                if instance_obj_data.str_data_nodes:
                    '''We treat social tenure entities separately because of foreign key references'''
                    entity_relation = EntityImporter(filename)
                    single_str, multiple_str = self.uuid_extractor.instance_data_from_nodelist(
                        instance_obj_data.str_data_nodes)
                    if len(single_str) > 0:
                        entity_relation.process_social_tenure(single_str, self.parent_ids)

                    elif len(multiple_str) > 1:
                        for repeated_entity, entity_data in multiple_str.items():
                            """We are assuming that the number of repeat str cannot exceed 10"""
                            entity_relation.process_social_tenure(entity_data, self.parent_ids)

                    self.log_table_entry(" ----- saving social tenure relationship")
                    # entity_add.cleanup()

                self.txt_feedback.append('saving record "{0}" to database'.format(counter))
                self.pgbar.setValue(counter)
                self.log_instance(filename)
                QCoreApplication.processEvents()

            self.txt_feedback.append('Number of records successfully imported:  {}'
                                     .format(counter))
        except DummyException as ex:
            self.feedback_message(str(ex))
            QCoreApplication.processEvents()
            QApplication.restoreOverrideCursor()
            self.buttonBox.setEnabled(True)
        except SQLAlchemyError as ae:
            QCoreApplication.processEvents()
            QApplication.restoreOverrideCursor()
            self.feedback_message(str(ae))
            self.txt_feedback.append("current table {0}import failed...\n".format(cu_obj))
            self.txt_feedback.append(str(ae))
            self.log_table_entry(str(ae))
            return

    def count_import_file_step(self, count:int=0, table: str=""):
        """
        Tracking method to record the current import activity
        """
        self.txt_feedback.append('      Table : {}'.format(table))

    def accept(self):
        """
        Execute the import dialog once the save button has been clicked
        :return:
        """
        self.buttonBox.setEnabled(False)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            if self.lst_widget.count() < 1:
                msg = 'No mobile records found for the current profile'
                self._notif_bar_str.insertErrorNotification(msg)
                self.buttonBox.setEnabled(True)
                QApplication.restoreOverrideCursor()
                return

            # entities = self.user_selected_entities()
            entities = self.instance_entities()
            

            # if len(entities) == 0:
            #     if QMessageBox.information(self,
            #                                QApplication.translate('MobileForms', 'Import Warning'),
            #                                QApplication.translate('MobileForms',
            #                                                       'You have not '
            #                                                       'selected any entity for import. All entities '
            #                                                       'will be imported'), QMessageBox.Ok |
            #                                                                            QMessageBox.No) == QMessageBox.Ok:
            #         entities = self.instance_entities()
            #         QApplication.restoreOverrideCursor()
            #     else:
            #         self.buttonBox.setEnabled(True)
            #         QApplication.restoreOverrideCursor()
            #         return
            # else:

            self.save_instance_data_to_db(entities)
            self.buttonBox.setEnabled(True)
            QApplication.restoreOverrideCursor()
        except DummyException as ex:
            QApplication.restoreOverrideCursor()
            self.feedback_message(str(ex))
            self.log_table_entry(str(ex))
            self.buttonBox.setEnabled(True)
            self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)
            QApplication.restoreOverrideCursor()
        return

    def log_instance(self, instance):
        # instance_short_name = self.importlogger.log_data_name(instance)
        log_data = self.importlogger.read_log_data()
        log_data[instance] = self.importlogger.log_date()
        self.importlogger.write_log_data(log_data)

    def previous_import_instances(self):
        count = 0
        del_list = []
        log_data = self.importlogger.read_log_data()
        if len(log_data) > 0:
            for instance in self.instance_list:
                # dir_path, file_name = os.path.split(instance)
                # if log_data.has_key(instance) or log_data.has_key(file_name):
                try:
                    if os.path.split(instance)[1] in log_data:
                        # del_list. append(instance)
                        self.instance_list.remove(instance)
                    else:
                        continue
                except DummyException:
                    continue
            # if len(del_list)>0:
            # [self.instance_list.remove(inst) for inst in del_list]

    def close(self):
        """
        when the user interrupts data import operations, we should close exit
        """
        self.instance_list = None
        QApplication.restoreOverrideCursor()
        QCoreApplication.processEvents()
        self.close()
