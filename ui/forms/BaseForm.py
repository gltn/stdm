__author__ = 'SOLOMON'
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.ui.ui_base_form import Ui_Dialog
from stdm.ui.notification import NotificationBar
from stdm.ui.entity_browser import PartyEntitySelector
from stdm.ui.foreign_key_mapper import ForeignKeyMapper


class MapperDialog(QDialog,Ui_Dialog):
    def __init__(self,parent=None):
        QDialog.__init__(self)
        self.setupUi(self)

        self.setWindowModality(Qt.WindowModal)

        self.foreign_key_modeller()
        self._notifBar = NotificationBar(self.vlNotification)
        self.center()

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def foreign_key_modeller(self):
        self.model()

        self.personFKMapper = ForeignKeyMapper(self)
        self.personFKMapper.setDatabaseModel(self._dbModel)
        self.personFKMapper.setEntitySelector(PartyEntitySelector)
        self.personFKMapper.setSupportsList(True)
        self.personFKMapper.setDeleteonRemove(False)
        self.personFKMapper.initialize()
        #self.boxLayout.addWidget(self.personFKMapper)
       # self.setLayout(self.boxLayout)


    def model(self):
        from stdm.ui.stdmdialog import DeclareMapping
        mapping=DeclareMapping.instance()
        self._dbModel=mapping.tableMapping('party')
        return self._dbModel


