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
    QListWidgetItem

)
from PyQt4.Qt import QDirIterator
from PyQt4.QtCore import (
    QDir,
    QFile,

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

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_import.ui'))

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/Downloads'

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

        self.entity_model = EntitiesModel()
        self.uuid_extractor = InstanceUUIDExtractor(self.path)

        self.cbo_profile.currentIndexChanged.connect(self.current_profile_changed)
        self.btn_chang_dir.clicked.connect(self.entity_attribute_to_database)
        self.lst_widget.itemClicked.connect(self.user_selected_entities)


        self.load_profiles()
        self.instance_dir()

        self._notif_bar_str = NotificationBar(self.vlnotification)


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

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        try:
            profiles = []
            self.cbo_profile.clear()
            for profile in self.profiles():
                profiles.append(profile.name)
            self.cbo_add_profiles(profiles)
            self.current_profile_highlighted()
            self.current_profile_changed()
        except TypeError as ex:
            self._notif_bar_str.insertErrorNotification(ex.message)
            return


    def cbo_add_profiles(self, profiles):
        """
        param profiles: list of profiles to add in the profile combobox
        type profiles: list
        """
        self.cbo_profile.insertItems(0, profiles)

    def profiles(self):
        """
        Get all profiles
        :return:
        """
        return self.load_config().values()

    def current_profile_highlighted(self):
        """
        Get the current profile so that it is the one selected at the combo box
        :return:
        """
        return setComboCurrentIndexWithText(self.cbo_profile, current_profile().name)

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


    def set_profile_model_view(self, entity_model):
        """
        Set profile view model
        :return:
        """
        self.lst_profiles.setModel(entity_model)


    def active_profile(self):
        """
        get the user selected profile
        :return:p
        """
        self.profile = self.load_config().get(self.cbo_profile.currentText()).name
        return self.profile

    def instance_dir(self):
        """

        :return:
        """
        self.inst_path = self.path+"/instance"
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
        self.path = HOME + "/.stdm/Downloads"
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
        Extract the specific folder information
        :return:
        """
        self.uuid_extractor.new_list = []
        if self.record_count() > 1:
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
                list_widget = QListWidgetItem(entity, self.lst_widget)
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
                    user_list.append(item.text())
            return user_list
        else:
            return None

    def instance_entities(self):
        """
        Enumerate the user entities that are in the form to be imported into database
        :return:
        """
        dirs = self.xform_xpaths()

        if len(dirs) > 0:
            dir_f = dirs[0]
            instance_file = [f for f in os.listdir(dir_f)]
            self.uuid_extractor.set_file_path(os.path.join(dir_f, instance_file[0]))
            entity_list = self.uuid_extractor.document_entities(self.profile)
            if len(entity_list)>0:
                entity_list.pop(0)
                entity_list.pop(len(entity_list) - 1)

                return entity_list


    def entity_attribute_to_database(self, values):
        """
        Get the user selected entities and insert tehm into database
        params: selected entities
        rtype: list
        :return:Object
        :type: dbObject
        """
        self.txt_feedback.clear()
        #self._notif_bar_str.clear()
        #try:
        if len(self.instance_list)>0:
            self.pgbar.setRange(0, len(self.instance_list))
            counter = 0
            if len(self.instance_list) > 0:
                self.pgbar.setValue(0)
                for instance in self.instance_list:
                    counter = counter + 1
                    entity_importer = EntityImporter(instance)
                    for entity in values:
                        entity_importer.process_import_to_db(entity)

                    self.txt_feedback.append('saving record "{0}"'
                                             ' to database'.format(counter))
                    self.pgbar.setValue(counter)
                    self.move_imported_file(instance)
                self.txt_feedback.append('Number of record successfully imported:  {}'
                                             .format(counter))
        else:
            self._notif_bar_str.insertErrorNotification("No user selected entities to import")
            self.pgbar.setValue(0)
        #
        # except AttributeError as ex:
        #     self._notif_bar_str.insertErrorNotification(ex.message)
        #
        # except TypeError as te:
        #     self._notif_bar_str.insertErrorNotification(te.message)

    def delete_imported_file(self):
        """
        Ensure that only import are done once
        :return:
        """
        for file in self.instance_list:
            os.removedirs(os.path.dirname(file))

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
        return self.profile.replace("_", " ")

    def feedback_message(self, msg):
        """

        :return:
        """
        msgbox = QMessageBox()
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msgbox.setWindowTitle("Information box")
        msgbox.setText(msg)
        msgbox.exec_()
        msgbox.show()
        return msgbox

    def accept(self):
        """

        :return:
        """
        self._notif_bar_str.clear()
        #try:
        msg = 'Saving {0} records into db.....'
        if len(self.instance_list) > 1:
            if self.lst_widget.count() < 1:
                msg = 'No entities found to import'
                self._notif_bar_str.insertErrorNotification(msg)
                return
            if len(self.user_selected_entities())<1:
                if QMessageBox.information(self,
                                        QApplication.translate('MobileForms', 'Import Error'),
                                        QApplication.translate('MobileForms',
                                                    'The user has not '
                                                    'selected any entity. All entities '
                                                    'will be imported'),QMessageBox.Ok |
                                                   QMessageBox.No) == QMessageBox.Ok:
                    entities = self.instance_entities()
                    self._notif_bar_str.insertInformationNotification(msg.format(len(entities)))
                    self.entity_attribute_to_database(entities)
            else:

                entities = self.user_selected_entities()
                self._notif_bar_str.insertInformationNotification(msg.format(len(entities)))
                self.entity_attribute_to_database(entities)
            self._notif_bar_str.clear()
        else:
            msg = "Unable to read records in the current profile"
            self._notif_bar_str.insertInformationNotification(msg)
        # except TypeError as ty:
        #     self._notif_bar_str.insertErrorNotification(ty.message)
        #     return







