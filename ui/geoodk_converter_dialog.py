"""
/***************************************************************************
Name                 : GeoODK Converter
Description          : anchor class that provides interface for user input
                        when generating the XFORM document.
Date                 : 26/May/2017
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

from PyQt4 import uic
from PyQt4.QtGui import (
    QDialog,
    QMessageBox

)
from PyQt4.QtCore import *
from PyQt4.Qt import QApplication
from PyQt4.QtCore import (
    QFile,
    QDir,
    QEvent,
    pyqtSignal,

)
from stdm.ui.notification import NotificationBar
from stdm.data.configuration.db_items import DbItem
from stdm.ui.wizard.custom_item_model import EntitiesModel
from stdm.geoodk.geoodk_writer import GeoodkWriter
from stdm.settings import current_profile
#from stdm.geoodk import  FormUploader


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_converter.ui'))

HOME = QDir.home().path()

FORM_HOME = HOME + '/.stdm/geoodk/forms'


class GeoODKConverter(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Class Constructor."""
        super(GeoODKConverter, self).__init__(parent)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-aut o-connect
        self.connect_action = pyqtSignal(str)
        self.setupUi(self)

        self.chk_all.setCheckState(Qt.Checked)
        self.entity_model = EntitiesModel()
        self.set_entity_model_view(self.entity_model)
        self.stdm_config = None
        self.parent = parent
        self.load_profiles()
        self.check_state_on()

        self.check_geoODK_path_exist()

        self.chk_all.stateChanged.connect(self.check_state_on)
        #self.btn_upload.clicked.connect(self.upload_generated_form)

        self._notif_bar_str = NotificationBar(self.vlnotification)

    def check_state_on(self):
        """
        Ensure all the items in the list are checked
        :return:
        """
        if self.entity_model.rowCount() > 0:
            for row in range(self.entity_model.rowCount()):
                item = self.entity_model.item(row)
                if self.chk_all.isChecked():
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        self.populate_view_models(current_profile())

    def profiles(self):
        """
        Get all profiles
        :return:
        """
        return self.load_config().values()

    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            if entity.action == DbItem.DROP:
                continue

            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                    'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                    'ENTITY_SUPPORTING_DOCUMENT', 'ASSOCIATION_ENTITY']:

                if entity.TYPE_INFO == 'VALUE_LIST':
                    pass
                else:
                    self.entity_model.add_entity(entity)
        self.set_model_items_selectable()

    def set_entity_model_view(self, entity_model):
        """
        Set our list view to the default model
        :return:
        """
        self.trentities.setModel(entity_model)

    def set_model_items_selectable(self):
        """
        Ensure that the entities  are checkable
        :return:
        """
        if self.entity_model.rowCount() >0:
            for row in range(self.entity_model.rowCount()):
                index = self.entity_model.index(row,0)
                item_index = self.entity_model.itemFromIndex(index)
                item_index.setCheckable(True)

    def selected_entities_from_Model(self):
        """
        Get selected entities for conversion
        to Xform from the user selection
        :return:
        """
        entity_list =[]
        if self.entity_model.rowCount() > 0:
            for row in range(self.entity_model.rowCount()):
                item = self.entity_model.item(row)
                if item.isCheckable() and item.checkState() == Qt.Checked:
                    entity_list.append(item.text())
        return entity_list

    def check_geoODK_path_exist(self):
        """
        Check if the geoodk paths are there in the directory
        Otherwise create them
        :return:
        """
        if not os.access(FORM_HOME, os.F_OK):
            os.makedirs(unicode(FORM_HOME))

    def upload_generated_form(self):
        """
        Upload the generated Xform file to mobile phone.
        This eliminates the process of copying the file
        manually to the mobile device
        :return:
        """
        form_uploader = FormUploader(self)
        form_uploader.exec_()

    def generate_mobile_form(self, selected_entities):
        """
        Generate mobile form based on the selected entities.
        :return:
        """
        try:
            self._notif_bar_str.clear()

            if len(selected_entities) == 0:
                self._notif_bar_str.insertErrorNotification(
                    'No entity selected. Please select at least one entity...'
                )
                return
            if len(selected_entities) > 0:
                geoodk_writer = GeoodkWriter(selected_entities, self.str_supported)
                geoodk_writer.write_data_to_xform()
                msg = 'File saved ' \
                      'in: {}'
                self._notif_bar_str.insertInformationNotification(
                    msg.format(FORM_HOME))
        except Exception as ex:
            self._notif_bar_str.insertErrorNotification(ex.message +
                                                        ': Unable to generate Mobile Form')
            return

    def accept(self):
        """
        Generate mobile forms based on user selected entities.
        Check if str is enabled, then ensure str tables are enabled.
        :return:
        """
        user_entities = self.selected_entities_from_Model()
        self.str_supported = False
        if self.ck_social_tenure.isChecked():
            self.str_supported = True
            str_definition = current_profile().social_tenure
            str_definition_party = str_definition.parties[0].short_name
            str_definition_spatial = str_definition.spatial_units[0].short_name
            if str_definition_party not in user_entities or str_definition_spatial not in user_entities:
                self._notif_bar_str.insertErrorNotification(
                    'One of the entities required to define str is not selected. Form not saved'
                )
                return
            else:
                self.generate_mobile_form(user_entities)
        else:
            self.generate_mobile_form(user_entities)

