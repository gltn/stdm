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
from .entity_browser import ForeignKeyBrowser
from stdm.ui.stdmdialog import DeclareMapping

class FKMapperDialog(object):

    def __init__(self, parent = None):
        super(FKMapperDialog, self).__init__()
        self.personFKMapper = ForeignKeyMapper()

    def foreign_key_modeller(self):
        self.model()
        self.editor = ForeignKeyBrowser

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
            if self.personFKMapper.global_id.display_value() == None:
                return "0"
            else:
                return self.personFKMapper.global_id.display_value()
        except:
            pass



