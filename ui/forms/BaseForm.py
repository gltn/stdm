__author__ = 'SOLOMON'
from PyQt4.QtCore import *
from PyQt4.QtGui import *


from stdm.ui import ForeignKeyBrowser
from stdm.ui.foreign_key_mapper import ForeignKeyMapper
from stdm.ui.stdmdialog import DeclareMapping

class MapperDialog(ForeignKeyMapper):
    def __init__(self, parent):
        super(MapperDialog, self).__init__()
        self.personFKMapper = ForeignKeyMapper()


    def foreign_key_modeller(self):
        self.model()
        self.editor = ForeignKeyBrowser
        #self.editor.table ="household"
        self.personFKMapper.setDatabaseModel(self._dbModel)
        self.personFKMapper.setEntitySelector(self.editor)
        self.personFKMapper.setSupportsList(True)
        self.personFKMapper.setDeleteonRemove(False)
        self.personFKMapper.onAddEntity()
        self.personFKMapper.initialize()

    def model(self):
        mapping = DeclareMapping.instance()
        self._dbModel = mapping.tableMapping('household')
        return self._dbModel

    def model_fkid(self):
        try:
            return self.personFKMapper.global_id.baseid()
        except:
            pass

    def model_display_value(self):
        try:
            return self.personFKMapper.global_id.display_value()
        except:
            pass



