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
    EntityModel
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
        super(ProfileInstanceRecords, self).__init__(parent)
        self.setupUi(self)

        self.path = self.geoODK_instance_file_path()
        self.txt_directory.setText(self.path)

        #self.xml_files = []
        self.parent_ids = {}
        self.importlogger = ImportLogger()
        self._notif_bar_str = NotificationBar(self.vlnotification)

        self.chk_all.setCheckState(Qt.Checked)

        self.entity_model = EntitiesModel()

        self.uuid_extractor = InstanceUUIDExtractor()

        self.btn_chang_dir.setIcon(GuiUtils.get_icon("open_file.png"))
        self.btn_refresh.setIcon(GuiUtils.get_icon("update.png"))

        self.chk_all.stateChanged.connect(self.change_check_state)
        self.btn_chang_dir.clicked.connect(self.on_directory_search)
        self.lst_widget.itemClicked.connect(self.user_selected_entities)
        self.btn_refresh.clicked.connect(self.update_files_with_custom_filter)

        self.buttonBox.button(QDialogButtonBox.Save).setText('Import')

        # self.load_config()
        self.xml_files = []
        self.profile_name = current_profile().name
        self.show_instances_count(self.path)
        self.profile_entities = self.instance_entities()
        self.show_profile_entities(self.profile_entities)

        self.fk_relations = self.extract_fk_relations(self.profile_entities)
        #self.read_instances_folder(self.path)

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
        bad_instances = self.verify_required_xml_file_count(self.path)

        for instance_folder, value in bad_instances.items():
            if value == 0:
                self.txt_feedback.append(f'No xml files found for instance: {instance_folder}')

            elif value > 1:
                self.txt_feedback.append(f'{value} xml files found for instance: {instance_folder}')

        self.xml_files = self.fetch_xml_files(self.path, list(bad_instances.keys()))

        #if len(bad_instances) == 0:
        #self.read_instances_folder()

            #return

        # self.txt_feedback.append('Errors found in data files, import failed.')
        # self.txt_feedback.append('')

        # for instance, count in instances.items():
        #     self.txt_feedback.append(f'{instance}: =>  {count}')

        #self.txt_feedback.append('')
        #self.txt_feedback.append('Fix the errors then try again.')
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(True)


    def verify_required_xml_file_count(self, instances_parent_folder: str):
        """
        Returns the number of xml files in the instance folder.
        """
        instances = {}

        instance_folders = self.instances_folders(instances_parent_folder)
        
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

    # def read_instances_folder(self, instances_folder: str):
    #     self.show_instances_count(instances_folder)
        #self.fetch_xml_files(instances_folder)
        #self.show_profile_entities()

    # def active_profile(self) -> str:
    #     """
    #     Return active profile name
    #     """
    #     self.profile = current_profile().name
    #     return self.profile

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
        #self.path = self.geoODK_file_path(self.txt_directory.text())
        self.path = self.geoODK_instance_file_path()
        self.txt_directory.setText(self.path)

    def geoODK_instance_file_path(self) -> str:
        """
        Check if geoODK file path has been configured, if not configure default
        and return it.
        """
        if not os.access(GEOODK_FORM_HOME, os.F_OK):
            os.makedirs(str(GEOODK_FORM_HOME))
        return GEOODK_FORM_HOME

        #return self.make_path(GEOODK_FORM_HOME)
        # if not path.strip():
        #     path = self.make_path(GEOODK_FORM_HOME)
        # return path

    # def make_path(self, path: str) -> str:
    #     """
    #     Create and return a file path if is not available.
    #     """
    #     if not os.access(path, os.F_OK):
    #         os.makedirs(str(path))
    #     return path

    def instances_folders(self, parent_path) -> List[str]:
        """
        Return the full path to the default config path and filter geoodk
        instance that matches the current profile path
        :return: directories
        :rtype: list
        """
        return [os.path.join(parent_path, name) for name in os.listdir(parent_path)
                if os.path.isdir(os.path.join(parent_path, name))
                if name.startswith(self.profile_name)]

    def fetch_xml_files(self, instances_parent_folder:str, bad_instances:list) -> list:

        instances_folders = self.instances_folders(instances_parent_folder)

        if len(instances_folders) == 0:
            return

        xml_files = []

        for instance_folder in instances_folders:
            if instance_folder in bad_instances:
                continue
            xml_file = self.extract_xml_file(instance_folder)
            xml_files.append(xml_file)

        return xml_files

        #return self.uuid_extractor.get_xml_files()
        self.importlogger.start_json_file()
        self.previous_import_instances()

        #self.txt_count.setValue(len(self.xml_files))

    def extract_xml_file(self, instance_folder: str) -> str:
        """
        Extract the unique uuid and rename the file
        so that we can uniquely identify each file
        :return:
        """
        xml_file = ""

        for xml_file in os.listdir(instance_folder):
            if os.path.isfile(os.path.join(instance_folder, xml_file)) and xml_file.endswith('.xml'):
                xml_full_filepath = os.path.normcase(os.path.join(instance_folder, xml_file))
                if os.path.isfile(xml_full_filepath):
                    xml_file = self.uuid_extractor.fix_name(xml_full_filepath)
                    break

        return xml_file

    def extract_xml_data(self, xml_files:list) -> Dict[str, tuple[str, InstanceData]]:
        """
        Read all instance data once and store them in a dict
        """
        xml_data = OrderedDict()
        self.uuid_extractor.unset_path()

        profile_name = self.profile_name.replace(' ', '_')

        entities = self.profile_entities
        entities.append('social_tenure')

        for xml_file in xml_files:
            if os.path.isfile(xml_file):
                filepath, filename = os.path.split(xml_file)
                #self.uuid_extractor.set_file_path(xml_file)

            entities_data = self.uuid_extractor.extract_entities_data(xml_file,
                                                                      profile_name, entities)

            xml_data[filename] = (xml_file, InstanceData( entities_data, None) )

            self.uuid_extractor.close_document()

        return xml_data

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

    def show_profile_entities(self, entities: list):
        """
        Add entities in the instance file into a list view widget
        """
        self.lst_widget.clear()
        # entities = self.instance_entities()

        if len(entities) > 0:
            for entity_name in entities:
                list_widget = QListWidgetItem( entity_name, self.lst_widget)
                list_widget.setIcon(GuiUtils.get_icon("table02.png"))
                #current_profile().entity_by_name(entity).short_name, self.lst_widget)
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

    def instance_entities(self) -> List[str]:
        """
        Enumerate the entities that are in the current profile
        and also that are captured in the form so that we are only
        importing relevant entities to database
        :return: List of enitity names
        """
        # TODO: Refactor this method
        current_entities = []
        instance_collections = self.instance_collection()
        if len(instance_collections) > 0:
            for entity_name in self.profile_entities_names(current_profile()):
                if current_profile().entity_by_name(entity_name) is not None:
                    current_entities.append(entity_name)

        # Add supporting document entity
        return current_entities

    def instance_collection(self) -> List[FileName]:
        """
        Enumerate all the instances found in the instance directory
        rtype: list of xml file names
        """
        dirs = self.instances_folders(self.path)
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
        return self.uuid_extractor.document_entities(self.profile_name)

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

    def extract_fk_relations(self, entity_names:List[str] ) -> OrderedDict:
        """
        Ensure we check that the table is not parent else
        import parent table first
        Revised in version 1.7. It explicitly assumes str is captured. before it was optional.
        :return:
        """
        #has_relations = False
        str_tables = current_profile().social_tenure
        party_tbls = str_tables.parties
        sp_tbls = str_tables.spatial_units

        fk_relations = OrderedDict()

        # if len(self.xml_files) > 0:
        #     if self.uuid_extractor.has_str_captured_in_instance(self.xml_files[0]):

        for party_tbl in party_tbls:
            fk_relations[party_tbl.name] = ['social_tenure_relationship',
                                                party_tbl.short_name.lower() + '_id']
        for sp_tbl in sp_tbls:
            fk_relations[sp_tbl.name] = ['social_tenure_relationship',
                                            sp_tbl.short_name.lower() + '_id']

        for entity_name in entity_names:
            entity = current_profile().entity_by_name(entity_name)
            cols = list(entity.columns.values())

            for col in cols:
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    #parent_object = entity.columns[col.name]
                    if col.parent:
                        if col.parent.name in fk_relations:
                            fk_relations[col.parent.name].append([entity_name, col.name])
                        else:
                            fk_relations[col.parent.name] = [entity_name, col.name]
                    #has_relations = True
        return fk_relations

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
                for table in self.fk_relations.keys():
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
            for files in self.xml_files:
                current_dir = os.path.basename(files)
                exist = self.importlogger.check_file_exist(current_dir)
                if exist:
                    self.xml_files.remove(files)
            self.txt_count.setValue(len(self.xml_files))
            if len(self.instances_folders(self.path)) != len(self.xml_files):
                msg = 'Some files have been already imported and therefore ' \
                      'not enumerated'
                self._notif_bar_str.insertErrorNotification(msg)
        except IOError as io:
            self._notif_bar_str.insertErrorNotification(MSG + ": " + str(io))

    def show_instances_count(self, instances_folder):
        self.txt_count.setValue(
            len(self.instances_folders(instances_folder))
        )

    # def profile_formater(self) -> str:
    #     """
    #     Format the profile name by removing underscore character
    #     """
    #     # if self.txt_filter.text() != '':
    #     #     filter_text = self.txt_filter.text()
    #     #     return filter_text
    #     # else:
    #     return self.profile_name

    def update_files_with_custom_filter(self):
        """
        Get the new file count with the user custom filter text
        :return: file count
        """
        self.show_instances_count()
        self.fetch_xml_files(self.path)
        self.show_profile_entities()
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

        instances_folder = QFileDialog.getExistingDirectory(
            self, 'Open Directory', home_path, QFileDialog.ShowDirsOnly
        )

        if instances_folder:
            self.txt_directory.setText(str(instances_folder))
            self.show_instances_count(instances_folder)
            bad_instances = self.verify_required_xml_file_count(instances_folder)
            self.xml_files = self.fetch_xml_files(instances_folder, 
                                                        list(bad_instances.keys()))
            #self.read_instances_folder(instances_folder)

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

    def save_instance_data_to_db(self, entities : List[str], xml_files: List[str]):
        cu_obj = ''

        self.txt_feedback.clear()
        self.txt_feedback.append("Import started, please wait...\n")

        QCoreApplication.processEvents()
        self._notif_bar_str.clear()

        print(f'Extract xml data...')

        xml_data = self.extract_xml_data(xml_files)
        
        if not xml_data:
            self.feedback_message('Not matching data in mobile files')
            return 

        counter = 0

        try:
            self.pgbar.setRange(counter, len(self.xml_files))
            self.pgbar.setValue(0)
            ImportLogger.log_action("Import started ...\n")

            #xml_data[filename] = (xml_file, InstanceData( entities_data, str_data) )

            for xml_filename, instance_data in xml_data.items():

                xml_file = instance_data[0]
                instance_obj_data = instance_data[1]

                ImportLogger.log_action("File {} ...\n".format(xml_filename))

                parents_info = []
                self.parent_ids = {}
                counter = counter + 1

                instance_nodes = self.uuid_extractor.instance_data_from_nodelist(
                    instance_obj_data.field_data_nodes, self.fk_relations)

                for entity_name, data in instance_nodes.items():
                    log_timestamp = f'Parent entity import... : {entity_name}'
                    self.log_table_entry(log_timestamp)

                    entity_data = data['data']

                    entity_model = EntityModel(entity_name, entity_data, self.parent_ids)
                    entity_model.objects_from_supporting_doc(xml_file)

                    if entity_name == 'social_tenure':
                            entity = current_profile().social_tenure
                            entity_model.save_str(self.parent_ids, entity, entity_data)
                            continue

                    ref_id = entity_model.save_parent_to_db()

                    self.parent_ids[entity_name] = [(ref_id, entity_name)]
                    parents_info.append(entity_name)

                    for entity_child in data['children']:

                        child_name = entity_child['child_name']

                        self.count_import_file_step(counter, child_name)
                        log_timestamp = f"Multiple table import... : {child_name}"
                        self.log_table_entry(log_timestamp)

                        child_data =  entity_child['data']

                        child_model = EntityModel(child_name, child_data, self.parent_ids)

                        child_model.entity.supports_documents = True

                        child_model.objects_from_supporting_doc(xml_file)
                        child_id = child_model.save_to_db(child_data)

                        parents_info.append(entity_name)
                        if child_name in self.parent_ids.keys():
                            self.parent_ids[child_name].append((child_id, child_name))
                        else:
                            self.parent_ids[child_name] = [(child_id, child_name)]


                self.txt_feedback.append(f"saving record '{counter}' to database")
                self.pgbar.setValue(counter)
                self.log_instance(xml_filename)
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
        if self.txt_count.value() == 0:
            return

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
            # entities = self.instance_entities()
            # entities = self.profile_entities
            
            self.save_instance_data_to_db(self.profile_entities, self.xml_files)

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
            for instance in self.xml_files:
                # dir_path, file_name = os.path.split(instance)
                # if log_data.has_key(instance) or log_data.has_key(file_name):
                try:
                    if os.path.split(instance)[1] in log_data:
                        # del_list. append(instance)
                        self.xml_files.remove(instance)
                    else:
                        continue
                except DummyException:
                    continue
            # if len(del_list)>0:
            # [self.xml_files.remove(inst) for inst in del_list]

    def close(self):
        """
        when the user interrupts data import operations, we should close exit
        """
        self.xml_files = None
        QApplication.restoreOverrideCursor()
        QCoreApplication.processEvents()
        self.close()
