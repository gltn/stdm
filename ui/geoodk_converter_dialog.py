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
    pyqtSignal,

)
from stdm.data.configuration.stdm_configuration import (
        StdmConfiguration,
        Profile
)
from stdm.settings.config_serializer import ConfigurationFileSerializer
from stdm.settings import current_profile
from stdm.utils.util import setComboCurrentIndexWithText
from stdm.data.configuration.db_items import DbItem
from stdm.ui.wizard.custom_item_model import EntitiesModel
from stdm.geoodk.geoodk_writer import GeoodkWriter


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_geoodk_converter.ui'))

HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/configuration.stc'

class GeoODKConverter(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Class Constructor."""
        super(GeoODKConverter, self).__init__(parent=None)

        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-aut o-connect
        self.connect_action = pyqtSignal(str)
        self.setupUi(self)

        self.entity_model = EntitiesModel()
        self.set_entity_model_view(self.entity_model)
        self.stdm_config = None
        self.parent = parent
        self.load_config()
        self.load_profiles()

        self.cboProf.currentIndexChanged.connect(self.cbo_text_changed)
        self.buttonBox.accepted.connect(self.acceptDlg)


    def load_config(self):
        """
        Load STDM configuration
        :return:
        """
        stdm_config = None
        if QFile.exists(CONFIG_FILE):
            stdm_config = QFile(CONFIG_FILE)
        ConfigurationFileSerializer(stdm_config)
        profiles = StdmConfiguration.instance().profiles
        return profiles

    def load_profiles(self):
        """
        Read and load profiles from StdmConfiguration instance
        """
        profiles = []
        self.cboProf.clear()
        for profile in self.profiles():
            profiles.append(profile.name)
        self.cbo_add_profiles(profiles)
        self.current_profile_highlighted()
        self.populate_view_models(current_profile())

    def cbo_text_changed(self):
        """
        Set Combo item data based on user selection
        :return:
        """
        self.entity_model = EntitiesModel()
        self.set_entity_model_view(self.entity_model)
        text = self.cboProf.currentText()
        if text != current_profile().name:
            QMessageBox.information(self, QApplication.translate("MobileForms",
                                                          "Error"), QApplication.translate("MobileForms",
                                                        "Generate Forms works with current profile only"))
            return
        self.populate_view_models(self.load_config().get(text))

    def profiles(self):
        """
        Get all profiles
        :return:
        """
        return self.load_config().values()


    def cbo_add_profiles(self, profiles):
        """
        param profiles: list of profiles to add in the profile combobox
        type profiles: list
        """
        self.cboProf.insertItems(0, profiles)

    def current_profile_highlighted(self):
        """
        Get the current profile so that it is the one selected at the combo box
        :return:
        """
        return setComboCurrentIndexWithText(self.cboProf,current_profile().name)

    def populate_view_models(self, profile):
        for entity in profile.entities.values():
            # if item is "deleted", don't show it
            if entity.action == DbItem.DROP:
                continue

            if entity.TYPE_INFO not in ['SUPPORTING_DOCUMENT',
                    'SOCIAL_TENURE', 'ADMINISTRATIVE_SPATIAL_UNIT',
                    'ENTITY_SUPPORTING_DOCUMENT', 'ASSOCIATION_ENTITY']:

                if entity.TYPE_INFO == 'VALUE_LIST':
                    #self.lookup_view_model.add_entity(entity)
                    #self.addValues_byEntity(entity)
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
        QMessageBox.critical(
                self, "Error dia",str(self.entity_model.rowCount()))
        :return:
        """
        if self.entity_model.rowCount() >0:
            for row in range(self.entity_model.rowCount()):
                index = self.entity_model.index(row,0)
                item_index = self.entity_model.itemFromIndex(index)
                item_index.setCheckable(True)

    def selected_entities_from_Model(self):
        """
        Get selected entities for conversion to Xform from the user selection
        :return:
        """
        entity_list =[]
        if self.entity_model.rowCount() > 0:
            for row in range(self.entity_model.rowCount()):
                item = self.entity_model.item(row)
                if item.isCheckable() and item.checkState() == Qt.Checked:
                    entity_list.append(item.text())
        return entity_list

    def acceptDlg(self):
        """
        Generate Xform based on user selected entities
        :return:
        """

        user_entities = self.selected_entities_from_Model()
        if len(user_entities)< 1:
            QMessageBox.critical(
                self, QApplication.translate("MobileForms","Entity Error"), \
                             QApplication.translate("MobileForms","No Entity selected by user"))
            return
        else:
            geoodk_writer = GeoodkWriter(user_entities)
            geoodk_writer.write_data_to_xform()
            QMessageBox.information(
                self, QApplication.translate("MobileForms", " Forms Generation"), \
                QApplication.translate("MobileForms", "Successfully generated geoODK Form in the"
                                             " following location: {}/.stdm".format(HOME)))
            self.accept()
