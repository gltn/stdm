__author__ = 'SOLOMON'
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.ui.ui_base_form import Ui_Dialog
from stdm.ui.notification import NotificationBar
from stdm.ui.entity_browser import ForeignKeyBrowser
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.stdmdialog import DeclareMapping

class MapperDialog(ForeignKeyMapper):
    def __init__(self, parent):
        super(MapperDialog, self).__init__()
        self.personFKMapper = ForeignKeyMapper()


    def foreign_key_modeller(self):
        self.model()
        self.personFKMapper.setDatabaseModel(self._dbModel)
        self.personFKMapper.setEntitySelector(ForeignKeyBrowser)
        self.personFKMapper.setSupportsList(True)
        self.personFKMapper.setDeleteonRemove(False)
        self.personFKMapper.onAddEntity()
        self.personFKMapper.initialize()

    def model(self):
        mapping=DeclareMapping.instance()
        self._dbModel=mapping.tableMapping('party')
        return self._dbModel

    def model_fkid(self):
        QMessageBox.information(None, "adflafd", str(self.personFKMapper.global_id.baseid()))
        return self.personFKMapper.global_id.baseid()

    def model_display_value(self):
        return self.personFKMapper.global_id.display_value()



