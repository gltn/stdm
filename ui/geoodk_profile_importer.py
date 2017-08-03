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
    QFileDialog
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

from stdm.ui.notification import NotificationBar
from stdm.settings import current_profile
from stdm.utils.util import setComboCurrentIndexWithText
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.geoodk.importer.uuid_extractor import InstanceUUIDExtractor
from stdm.ui.wizard.custom_item_model import EntitiesModel
from stdm.data.usermodels import listEntityViewer
from stdm.geoodk.importer import EntityImporter
from stdm.settings.projectionSelector import ProjectionSelector
from stdm.geoodk.importer import ImportLogger


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_import.ui'))

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/downloads'
MSG = 'Error creating log'

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

        self.chk_all.stateChanged.connect(self.check_state_on)
        #self.cbo_profile.currentIndexChanged.connect(self.current_profile_changed)
        self.btn_chang_dir.clicked.connect(self.on_directory_search)
        self.lst_widget.itemClicked.connect(self.user_selected_entities)
        self.btn_srid.clicked.connect(self.projection_settings)


        self.load_config()
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
        self.check_previous_import()
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

        :return:
        """
        self.inst_path = self.path+"/imported_instance"
        if not os.access(self.inst_path, os.F_OK):
            os.makedirs(unicode(self.inst_path))
        else:
            return self.inst_path

    def instance_path(self):
        """
        :return:
        """
        self.instance_dir()
        return self.inst_path

    def on_filepath(self):
        """
        Access the file directory by constructing the full path
        :return: string
        """
        if self.txt_directory.text() != '':
            self.path = self.txt_directory.text()
        else:
            self.path = HOME + "/.stdm/geoodk/instances"
            self.txt_directory.setText(self.path)
        return self.path

    def xform_xpaths(self):
        """
        Return the full path to the default config path
        :return:
        """
        dirs = []
        return [os.path.join(self.path, name) for name in os.listdir(self.path)
                if os.path.isdir(os.path.join(self.path, name))
                if name.startswith(self.profile_formater())]

    def extract_file(self):
        """

        :return:
        """
        path = self.instance_path()
        for dir in os.listdir(path):
            new_path = os.path.join(path, dir)
            for f in os.listdir(new_path):
                if os.path.isfile(os.path.join(new_path, f)):
                    file_instance = os.path.join(new_path, f)
                    self.rename_file_toUUID(file_instance)

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

    def extract_guuid_and_rename_file(self,path):
        """
        Extract teh unique Guuid and rename the file
        so that we can uniquely identify each file
        :return:
        """
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                file_instance = os.path.join(path, f)
                self.rename_file_toUUID(file_instance)

    def rename_file_toUUID(self, file):
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
        instance_path = self.instance_path()
        try:
            basename = os.path.basename(os.path.dirname(file))
            if not os.path.isdir(os.path.join(self.instance_path(), basename)):
               shutil.move(os.path.dirname(file), instance_path)
            else:
                pass

        except Exception as ex:
            return ex

    def profile_instance_entities(self):
        """
        Add the user entities that are in the form to be imported into database
        into a list view widget
        :return: model
        """
        self.lst_widget.clear()
        entity_list = self.instance_entities()
        if entity_list is not None and len(entity_list) > 0:
            for entity in entity_list:
                list_widget = QListWidgetItem(
                    current_profile().entity_by_name(entity).short_name, self.lst_widget)
                list_widget.setCheckState(Qt.Unchecked)
        else:
            return

    def user_selected_entities(self):
        """

        :return:
        """
        user_list= []
        count = self.lst_widget.count()
        if count >0:
            for i in range(count):
                item = self.lst_widget.item(i)
                if item.checkState() == Qt.Checked:
                    user_list.append(current_profile().entity(item.text()).name)
            return user_list
        else:
            return None

    def instance_entities(self):
        """
        Enumerate the user entities that are in the form to be imported into database
        :return:
        """
        dirs = self.xform_xpaths()
        current_etities = []
        if len(dirs) > 0:
            dir_f = dirs[0]
            instance_file = [f for f in os.listdir(dir_f)]
            self.uuid_extractor.set_file_path(os.path.join(dir_f, instance_file[0]))
            entity_list = self.uuid_extractor.document_entities(self.profile)
            for entity_name in entity_list:
                if current_profile().entity_by_name(entity_name) is not None:
                    current_etities.append(entity_name)
            if len(current_etities) > 0:
                return current_etities

    def entity_attribute_to_database(self, values):
        """
        Get the user selected entities and insert tehm into database
        params: selected entities
        rtype: list
        :return:Object
        :type: dbObject
        """
        self.relations = {}
        self.txt_feedback.clear()
        self._notif_bar_str.clear()
        try:
            userlist = []
            parents_info = []
            counter = 0
            if len(self.instance_list) > 0:
                self.pgbar.setRange(0, len(self.instance_list))
                self.pgbar.setValue(0)
                for instance in self.instance_list:
                    counter = counter + 1
                    entity_importer = EntityImporter(instance)
                    #set the geometry coodinate system
                    entity_importer.geomsetter(self.on_projection_select())

                    has_relations = self.has_foreign_keys_parent(values)
                    self.archive_imported_file(counter, instance)
                    if has_relations:
                        #Import parents table first
                        for parent_table in self.relations.values():
                            if parent_table[1] in self.instance_entities():
                                ref_id = entity_importer.process_parent_entity_import(parent_table[1])
                                self.parent_ids[parent_table[1]] = [ref_id, parent_table[1]]
                                log_timestamp = 'Importing {0}.{1} ' \
                                                'as parent table in instance file {2}'.format(
                                    self.profile, parent_table[1], counter)
                                self.log_table_entry(log_timestamp)
                                parents_info.append(parent_table[1])
                                if parent_table[1] in values:
                                    values.remove(parent_table[1])
                    for table in values:
                        if table not in parents_info:
                            log_timestamp1 = 'Importing {0}.{1}  table in instance file {2}'.format(
                                self.profile, table, counter)
                            entity_importer.process_import_to_db(table, self.parent_ids)
                            self.log_table_entry(log_timestamp1)
                    self.txt_feedback.append('saving record "{0}"'
                                          ' to database'.format(counter))
                    self.pgbar.setValue(counter)

                self.txt_feedback.append('Number of record successfully imported:  {}'
                                                  .format(counter))

            else:
                 self._notif_bar_str.insertErrorNotification("No user selected entities to import")
                 self.pgbar.setValue(0)
        except AttributeError as ex:
             self._notif_bar_str.insertErrorNotification(ex.message)

        except TypeError as te:
             self._notif_bar_str.insertErrorNotification(te.message)

    def has_foreign_keys_parent(self, select_entities):
        """
        Ensure we check that the table is not parent else
        import parent table first
        :return:
        """
        has_relations = False
        for table in select_entities:
            table_object = current_profile().entity_by_name(table)
            cols = table_object.columns.values()
            for col in cols:
                if col.TYPE_INFO == 'FOREIGN_KEY':
                    parent_object = table_object.columns[col.name]
                    if parent_object:
                        self.relations[col.name] = [table, parent_object.parent.name]
                        has_relations = True
                    else:
                        self.feedback_message('unable to read foreign key properties')
                        return
        return has_relations

    def archive_imported_file(self, counter, instance):
        """
        Ensure that only import are done once
        :return:
        """
        try:
            current_time = QDateTime()
            import_time = current_time.currentDateTime()
            head, tail= os.path.split(instance)
            self.importlogger.logger_sections()
            file_info = 'File instance ' + str(counter)+ ' : \n' + instance
            self.importlogger.onlogger_action(file_info)
            #self.importlogger.write_section_data(tail,
            #                                   head +"##"+ str(import_time.toPyDateTime()))
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
        dir_name = QFileDialog.getExistingDirectory(
                self, 'Open Directory', "/home", QFileDialog.ShowDirsOnly
                )
        if dir_name:
            self.txt_directory.setText(str(dir_name))
            self.current_profile_changed()

    def feedback_message(self, msg):
        """

        :return:
        """
        msgbox = QMessageBox()
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msgbox.setWindowTitle("Data Import")
        msgbox.setText(msg)
        msgbox.exec_()
        msgbox.show()
        return msgbox

    def accept(self):
        """

        :return:
        """
        try:
            if self.lst_widget.count() < 1:
                msg = 'Current profile matched no records for import'
                self._notif_bar_str.insertErrorNotification(msg)
                return
            entities = self.user_selected_entities()
            if len(entities) < 1:
                if QMessageBox.information(self,
                        QApplication.translate('MobileForms', 'Import Error'),
                        QApplication.translate('MobileForms',
                        'The user has not '
                        'selected any entity. All entities '
                        'will be imported'), QMessageBox.Ok |
                                            QMessageBox.No) == QMessageBox.Ok:
                    entities = self.instance_entities()

                else:
                    return
            self.entity_attribute_to_database(entities)
        except Exception as ex:
            self._notif_bar_str.insertErrorNotification(ex.message)
            self.feedback_message(str(ex.message))







