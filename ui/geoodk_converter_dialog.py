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
        self.buttonBox.clicked.connect(self.accept)

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

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
                    source is self):
            return True

    def accept(self):
        """
        Generate Xform based on user selected entities
        :return:
        """
        self._notif_bar_str.clear()
        user_entities = self.selected_entities_from_Model()
        if len(user_entities) == 0:
            self._notif_bar_str.insertErrorNotification(
                'No entity selected by user'
            )
            return

        if len(user_entities) > 0:
            geoodk_writer = GeoodkWriter(user_entities)
            geoodk_writer.write_data_to_xform()
            msg = 'File saved ' \
                  'in: {}'
            self._notif_bar_str.insertInformationNotification(
                msg.format(FORM_HOME))
            #self.accept()
