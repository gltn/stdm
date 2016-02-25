"""
/***************************************************************************
Name                 : ConfigurationSchemaUpdater
Description          : Updates the StdmConfiguration instance in the databaase.
Date                 : 25/December/2015
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
 ***************************************************************************/
"""
import logging

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)

from sqlalchemy.exc import ProgrammingError

from stdm.data.database import (
    metadata,
    STDMDb
)
from stdm.data.configuration.db_items import DbItem
from stdm.data.configuration.stdm_configuration import StdmConfiguration

LOGGER = logging.getLogger('stdm')


class ConfigurationSchemaUpdater(QObject):
    """
    Updates the database for the given StdmConfiguration.
    """
    update_started = pyqtSignal()

    #Signal contains message type and message
    update_progress = pyqtSignal(int, unicode)

    #Signal indicates True if the update succeeded, else False.
    update_completed = pyqtSignal(bool)

    #Message types
    INFORMATION, WARNING, ERROR = range(0, 3)

    def __init__(self, engine=None, parent=None):
        QObject.__init__(self, parent)

        self.config = StdmConfiguration.instance()
        self.engine = engine
        self.metadata = metadata

        #Use the default engine if None is specified.
        if self.engine is None:
            self.engine = STDMDb.instance().engine

        #Ensure there is a connectable set in the metadata
        if self.metadata.bind is None:
            self.metadata.bind = self.engine

    def exec_(self):
        """
        Initiate the process of updating the schema based on the specified
        configuration. The object will determine whether the schema needs to
        be created or updated.
        """
        self.update_started.emit()

        if self.config.is_null:
            msg = self.tr('The specified configuration is empty, the schema '
                          'will not be updated.')

            LOGGER.debug(msg)

            self.update_progress.emit(ConfigurationSchemaUpdater.ERROR, msg)

            self.update_completed.emit(False)

            return

        try:
            #Iterate through profiles
            for p in self.config.profiles.values():
                self.update_profile(p)

            msg = self.tr('The schema has been successfully updated!')

            self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, msg)

            LOGGER.debug(msg)

            self.update_completed.emit(True)

        except ProgrammingError as pe:
            msg = unicode(pe)

            self.update_progress.emit(ConfigurationSchemaUpdater.ERROR, msg)

            LOGGER.debug(msg)

            self.update_completed.emit(False)

    def update_profile(self, profile):
        """
        Updates the given profile.
        :param profile: Profile instance.
        :type profile: Profile
        """
        trans_msg = u'Scanning for changes in {0} profile...'.format(
            profile.name)

        msg = self.tr(trans_msg)

        LOGGER.debug(trans_msg)

        self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, msg)

        trans_msg = self.tr('Removing redundant foreign key constraints...')

        self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, trans_msg)

        #Drop removed relations
        for er in profile.removed_relations:
            status = er.drop_foreign_key_constraint()

            if not status:
                msg = self.tr(u'Error in removing {0} foreign key '
                                  'constraint.'.format(er.name))
                self.update_progress.emit(ConfigurationSchemaUpdater.ERROR, msg)

            else:
                del profile.relations[er.name]

                msg = self.tr(u'{0} foreign key constraint successfully '
                                  'removed.'.format(er.name))
                self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, msg)

            LOGGER.debug(msg)

        #Drop removed entities first
        self._update_entities(profile.removed_entities)
        self.removed_entities = []

        #Now iterate through new or updated entities
        self._update_entities(profile.entities.values())

        #Update entity relations by creating foreign key references
        self.update_entity_relations(profile)

        #Create basic STR database view
        profile.social_tenure.create_view(self.engine)

    def _update_entities(self, entities):
        for e in entities:
            action = e.action

            if action != DbItem.NONE:
                action_txt = unicode(self._action_text(action))
                trans_msg = u'{0} {1} entity...'.format(
                    action_txt.capitalize(), e.short_name)

                msg = self.tr(trans_msg)

                LOGGER.debug(trans_msg)

                self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, msg)

                e.update(self.engine, self.metadata)

    def update_entity_relations(self, profile):
        """
        Update entity relations in the profile by creating the corresponding
        foreign key references.
        :param profile: Profile whose foreign key references are to be updated.
        :type profile: Profile
        """
        for er in profile.relations.values():
            #Assert if the EntityRelation object is valid
            if er.valid()[0]:
                status = er.create_foreign_key_constraint()

                if not status:
                    msg = self.tr(u'Error in creating {0} foreign key '
                                  'constraint.'.format(er.name))
                    #self.update_progress.emit(ConfigurationSchemaUpdater.ERROR, msg)

                else:
                    msg = self.tr(u'{0} foreign key constraint successfully '
                                  'created.'.format(er.name))
                    #self.update_progress.emit(ConfigurationSchemaUpdater.INFORMATION, msg)

                LOGGER.debug(msg)

    def _action_text(self, action):
        if action == DbItem.CREATE:
            return self.tr('creating')

        elif action == DbItem.ALTER:
            return self.tr('updating')

        elif action == DbItem.DROP:
            return self.tr('deleting')

        else:
            return 'UNKNOWN ACTION'

