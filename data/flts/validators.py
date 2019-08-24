"""
/***************************************************************************
Name                 : Vector Layer Validator
Description          : Module for validating a QgsVectorLayer data source
                       against the mapped entity in the database.
Date                 : 24/August/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
from collections import OrderedDict
from ConfigParser import ConfigParser

from PyQt4.QtCore import (
    QObject
)

from stdm.settings import current_profile
from stdm.settings.registryconfig import (
    holders_config_path
)

CONFIG_COL_MAPPING_SECTION = 'ColumnMapping'


def entity_vector_layer_mapping():
    """
    :return: Returns the column mapping object based on the holders
    configuration file specified in the settings. Returns None if
    no path is defined in the settings.
    :rtype: EntityVectorLayerColumnMapping
    """
    conf_path = holders_config_path()
    if not conf_path:
        return None

    return EntityVectorLayerColumnMapping.from_configuration_file(conf_path)


class EntityVectorLayerColumnMapping(object):
    """
    Contains the mapping of vector layer columns to the corresponding entity
    columns as specified in the given configuration file.
    """
    def __init__(self, col_mapping=OrderedDict()):
        self._col_mapping = col_mapping

    @property
    def column_mapping(self):
        """
        :return: Returns the collection containing the column mappings in the
        source vector layer and corresponding target entity respectively i.e.
        keys correspond to the vector layer columns and values to the ones
        in the target entity.
        :rtype: OrderedDict
        """
        return self._col_mapping

    @column_mapping.setter
    def column_mapping(self, column_mapping):
        """
        Sets the collection containing the column mappings in the
        source vector layer and corresponding target entity respectively i.e.
        keys correspond to the vector layer columns and values to the ones
        :param column_mapping: Collection containg the column mapping.
        :type column_mapping: OrderedDict
        """
        self._col_mapping = column_mapping

    def is_empty(self):
        """
        :return: Returns True if there are no column mappings defined.
        :rtype: bool
        """
        return len(self._col_mapping) == 0

    def contains_source_column(self, name):
        """
        Checks if the given source column name exists.
        :param name: Name of the source column.
        :type name: str
        :return: Returns True if the source column exists, else False.
        :rtype: bool
        """
        return name in self._col_mapping

    def destination_column(self, source_column):
        """
        :param source_column: Name of the source column.
        :type source_column: str
        :return: Returns the name of the destination column matched to the
        given source column else None if the source column does not exist.
        :rtype: str
        """
        return self._col_mapping.get(source_column, None)

    @staticmethod
    def from_configuration_file(config_path):
        """
        Creates an EntityVectorLayerColumnMapping from the definition in a
        configuration file.
        :param config_path: Path to the config file.
        :type config_path: str
        :return: Returns an EntityVectorLayerColumnMapping object. Exceptions
        raised if the configuration file does not exist, the user does not
        have permissions to the file or the column mapping section is missing.
        :rtype: EntityVectorLayerColumnMapping
        """
        cp = ConfigParser()
        cp.optionxform = str
        cp.read(config_path)
        conf_mappings = cp.items(CONFIG_COL_MAPPING_SECTION)
        col_mapping = OrderedDict(conf_mappings)

        return EntityVectorLayerColumnMapping(col_mapping)


class EntityVectorLayerValidator(QObject):
    """
    Validates a vector layer object against the given entity object
    """
    def __init__(
            self,
            entity,
            vector_layer,
            exclude_columns=None,
            parent=None
    ):
        super(EntityVectorLayerValidator, self).__init__(parent)

        self._entity = entity
        # If entity is string then get the corresponding entity object
        if isinstance(self._entity, basestring):
            curr_profile = current_profile()
            if not curr_profile:
                raise TypeError('Current profile in None')
            self._entity = curr_profile.entity(self._entity)

        self._vl = vector_layer
        self._exclude_cols = exclude_columns
        if not self._exclude_cols:
            self._exclude_cols = []

    @property
    def entity(self):
        """
        :return: Returns the entity object whose columns will form the basis
        of the validation based on the vector layer feature values.
        :rtype: Entity
        """
        return self._entity

    @property
    def vector_layer(self):
        """
        :return: Returns the vector layer whose features will be validated.
        :rtype: QgsVectorLayer
        """
        return self._vl