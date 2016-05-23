"""
/***************************************************************************
Name                 : social_tenure_updater
Description          : Creates a generic database view that joins all the
                        STR entities..
Date                 : 20/February/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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

from sqlalchemy.sql.expression import text
from migrate.changeset import *

from stdm.data.pg_utils import (
    _execute,
    drop_view,
    pg_table_exists
)
from stdm.data.configuration.columns import (
    ForeignKeyColumn,
    MultipleSelectColumn
)
from stdm.data.configuration.exception import ConfigurationException

LOGGER = logging.getLogger('stdm')

BASE_STR_VIEW = 'vw_social_tenure_relationship'

#Columns types which should not be incorporated in the STR view
_exclude_view_column_types = ['MULTIPLE_SELECT']

def view_deleter(social_tenure, engine):
    """
    Deletes the database view using the information in the social tenure
    object.
    :param social_tenure: Social tenure object containing the view
    information.
    :type social_tenure: SocialTenure
    :param engine: SQLAlchemy connectable object.
    :type engine: Engine
    """
    view_name = social_tenure.view_name

    LOGGER.debug('Attempting to delete %s view...', view_name)

    drop_view(view_name)

def view_updater(social_tenure, engine):
    """
    Creates a generic database view linking all STR entities.
    :param social_tenure: Social tenure object.
    :type social_tenure: SocialTenure
    :param engine: SQLAlchemy connectable object.
    :type engine: Engine
    """
    view_name = social_tenure.view_name

    #Check if there is an existing one and delete if it exists
    LOGGER.debug('Checking if %s view exists...', view_name)

    #Do not create if it already exists
    if pg_table_exists(view_name):
        return

    #Create the SQL statement for creating the view where party is the
    # primary entity
    str_columns, str_join = _entity_select_column(social_tenure, True, True)
    party_columns, party_join = _entity_select_column(social_tenure.party,
                                                      True, True, True)
    spatial_unit_columns, spatial_unit_join =  _entity_select_column(
        social_tenure.spatial_unit, True
    )

    view_columns = str_columns + party_columns +  spatial_unit_columns
    join_statement = str_join + party_join + spatial_unit_join

    if len(view_columns) == 0:
        LOGGER.debug('There are no columns for creating the social tenure '
                     'relationship view.')

        return

    #Create SQL statement
    create_view_sql = u'CREATE VIEW {0} AS SELECT {1} FROM {2} {3}'.format(
        view_name, ','.join(view_columns), social_tenure.name,
        ' '.join(join_statement))

    normalized_create_view_sql = text(create_view_sql)

    result = _execute(normalized_create_view_sql)

def _entity_select_column(entity, use_inner_join=False, join_parents=False,
                          is_primary=False):
    #Check if the entity exists in the database
    if not pg_table_exists(entity.name):
        msg = u'{0} table does not exist, social tenure view will not be ' \
              u'created.'.format(entity.name)
        LOGGER.debug(msg)

        raise ConfigurationException(msg)

    column_names = []
    join_statements = []

    columns = entity.columns.values()

    for c in columns:
        if not c.TYPE_INFO in _exclude_view_column_types:
            normalized_entity_sname = entity.short_name.replace(' ', 
                    '_').lower()
            pseudo_column_name = u'{0}_{1}'.format(normalized_entity_sname, 
                    c.name)
            col_select_name = u'{0}.{1}'.format(entity.name,
                                                       c.name)

            select_column_name = u'{0} AS {1}'.format(col_select_name,
                                                      pseudo_column_name)

            if is_primary and c.name == 'id':
                select_column_name = col_select_name

            if isinstance(c, ForeignKeyColumn) and join_parents:
                LOGGER.debug('Creating STR: Getting parent for %s column', c.name)
                parent_table = c.entity_relation.parent.name
                LOGGER.debug('Parent found')
                select_column_name = ''

                #Map lookup values by default
                if c.TYPE_INFO == 'LOOKUP':
                    select_column_name = u'{0}.value AS {1}'.format(
                        parent_table, pseudo_column_name)

                #These are outer joins
                join_type = 'LEFT JOIN'
                if use_inner_join:
                    join_type = 'INNER JOIN'

                join_statement = u'{0} {1} ON {2} = {1}.{3}'.format(
                    join_type, parent_table, col_select_name,
                    c.entity_relation.parent_column
                )
                join_statements.append(join_statement)

            if select_column_name:
                column_names.append(select_column_name)

    return column_names, join_statements







