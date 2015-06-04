"""
/***************************************************************************
Name                 : FKMapperDialog
Description          : class supporting access to foreign key attribute of another class
                        foreign key relations.
Date                 : 8/April/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
 ****
"""

from .foreign_key_mapper import ForeignKeyMapper

from stdm.ui.stdmdialog import DeclareMapping
from PyQt4.QtGui import QMessageBox, QWidget

class FKMapperDialog(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        #self.personFKMapper = ForeignKeyMapper()
        self.attribute = None

    def foreign_key_modeller(self, editor =None):
        self.model()
        self.personFKMapper = ForeignKeyMapper()
        #self.editor = ForeignKeyBrowser
        #QMessageBox.information(None,"Loading Foreign Key",str(self._dbModel.__name__))
        self.personFKMapper.setDatabaseModel(self._dbModel)
        self.personFKMapper.setEntitySelector(editor)
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
            if not self.personFKMapper.global_id.display_value():
                return "0"
            else:
                return self.personFKMapper.global_id.display_value()
        except:
            pass



