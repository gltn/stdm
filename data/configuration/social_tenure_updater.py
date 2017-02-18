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

from copy import deepcopy

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

# Columns types which should not be incorporated in the STR view
_exclude_view_column_types = ['MULTIPLE_SELECT']


def view_deleter(social_tenure, engine):
    """
    Deletes str database views using the information in the social tenure
    object.
    :param social_tenure: Social tenure object containing the view
    information.
    :type social_tenure: SocialTenure
    :param engine: SQLAlchemy connectable object.
    :type engine: Engine
    """
    views = social_tenure.views.keys()

    for v in views:
        LOGGER.debug('Attempting to delete %s view...', v)
        drop_view(v)


def view_updater(social_tenure, engine):
    """
    Creates a generic database view linking all STR entities.
    :param social_tenure: Social tenure object.
    :type social_tenure: SocialTenure
    :param engine: SQLAlchemy connectable object.
    :type engine: Engine
    """
    view_name = social_tenure.view_name

    views = social_tenure.views
    # Loop thru view name, primary entity items
    for v, pe in views.iteritems():
        # Check if there is an existing one and omit delete if it exists
        LOGGER.debug('Checking if %s view exists...', v)

        # Do not create if it already exists
        if pg_table_exists(v):
            continue

        # Create view based on the primary entity
        _create_primary_entity_view(social_tenure, pe, v)


def _create_primary_entity_view(
        social_tenure,
        primary_entity,
        view_name,
        distinct_column=None
):
    """
    Creates a basic view for the given primary entity.
    :param social_tenure:
    :param primary_entity:
    :param view_name:
    :param distinct_column:
    """
    # Collection for foreign key parents so that appropriate pseudo names
    # can be constructed if more than one parent is used for the same entity.
    fk_parent_names = {}
    omit_view_columns = []
    omit_join_statement_columns = []

    party_col_names = deepcopy(social_tenure.party_columns.keys())

    # Flag to check if primary entity is a spatial unit entity
    pe_is_spatial = False

    # Check if the primary entity is a party in the STR collection
    if not social_tenure.is_str_party_entity(primary_entity):
        pe_is_spatial = True

    else:
        p_fk_col_name = u'{0}_id'.format(primary_entity.short_name.lower())
        # Exclude other parties from the join statement
        if p_fk_col_name in party_col_names:
            party_col_names.remove(p_fk_col_name)

    # Create the SQL statement WRT the primary entity
    str_columns, str_join = _entity_select_column(
        social_tenure,
        True,
        True,
        foreign_key_parents=fk_parent_names,
        omit_join_statement_columns=party_col_names
    )

    party_columns, party_join = [], []

    # Omit party entities in the spatial unit join
    if not pe_is_spatial:
        party_columns, party_join = _entity_select_column(
            primary_entity, True, True, True,
            foreign_key_parents=fk_parent_names,
            omit_view_columns=omit_view_columns,
            omit_join_statement_columns=omit_join_statement_columns
        )

        # Set removal of all spatial unit columns apart from the id column
        omit_view_columns = deepcopy(social_tenure.spatial_unit.columns.keys())
        if 'id' in omit_view_columns:
            omit_view_columns.remove('id')

    else:
        # Set id column to be distinct
        distinct_column = '{0}.id'.format(primary_entity.name)

        # Omit STR columns if primary entity is spatial unit
        str_columns = []

    spatial_unit_columns, spatial_unit_join = _entity_select_column(
        social_tenure.spatial_unit,
        True,
        join_parents=True,
        is_primary=pe_is_spatial,
        foreign_key_parents=fk_parent_names,
        omit_view_columns=omit_view_columns,
        omit_join_statement_columns=omit_join_statement_columns
    )

    view_columns = party_columns + str_columns + spatial_unit_columns

    # Set distinct column if specified
    if not distinct_column is None:
        view_columns = _set_distinct_column(distinct_column, view_columns)

    join_statement = str_join + party_join + spatial_unit_join

    if len(view_columns) == 0:
        LOGGER.debug('There are no columns for creating the social tenure '
                     'relationship view.')

        return

    # Create SQL statement
    create_view_sql = u'CREATE VIEW {0} AS SELECT {1} FROM {2} {3}'.format(
        view_name, ','.join(view_columns), social_tenure.name,
        ' '.join(join_statement))

    normalized_create_view_sql = text(create_view_sql)

    result = _execute(normalized_create_view_sql)


def _entity_select_column(
        entity,
        use_inner_join=False,
        join_parents=False,
        is_primary=False,
        foreign_key_parents=None,
        omit_view_columns=None,
        omit_join_statement_columns=None
):
    # Check if the entity exists in the database
    if not pg_table_exists(entity.name):
        msg = u'{0} table does not exist, social tenure view will not be ' \
              u'created.'.format(entity.name)
        LOGGER.debug(msg)

        raise ConfigurationException(msg)

    if omit_view_columns is None:
        omit_view_columns = []

    if omit_join_statement_columns is None:
        omit_join_statement_columns = []

    column_names = []
    join_statements = []

    columns = entity.columns.values()

    # Create foreign key parent collection if none is specified
    if foreign_key_parents is None:
        foreign_key_parents = {}

    str_entity = entity.profile.social_tenure

    for c in columns:
        if c.TYPE_INFO not in _exclude_view_column_types:
            normalized_entity_sname = entity.short_name.replace(
                ' ', '_'
            ).lower()
            pseudo_column_name = u'{0}_{1}'.format(normalized_entity_sname,
                    c.name)
            col_select_name = u'{0}.{1}'.format(entity.name, c.name)

            select_column_name = u'{0} AS {1}'.format(col_select_name,
                                                      pseudo_column_name)

            if is_primary and c.name == 'id':
                select_column_name = col_select_name

            # Use custom join flag
            use_custom_join = False

            if isinstance(c, ForeignKeyColumn) and join_parents:
                LOGGER.debug('Creating STR: Getting parent for %s column', c.name)
                fk_parent_entity = c.entity_relation.parent
                parent_table = c.entity_relation.parent.name
                LOGGER.debug('Parent found')
                select_column_name = ''

                # Handle renaming of parent table names to appropriate
                # pseudonames.
                if not parent_table in foreign_key_parents:
                    foreign_key_parents[parent_table] = []

                pseudo_names = foreign_key_parents.get(parent_table)
                # Get pseudoname to use
                table_pseudo_name = u'{0}_{1}'.format(
                    parent_table, (len(pseudo_names) + 1)
                )
                pseudo_names.append(table_pseudo_name)

                # Map lookup and admin unit values by default
                if c.TYPE_INFO == 'LOOKUP':
                    select_column_name = u'{0}.value AS {1}'.format(
                        table_pseudo_name,
                        pseudo_column_name
                    )
                    use_custom_join = True

                    # Check if the column is for tenure type
                    if c.name != 'tenure_type':
                        use_inner_join = False

                elif c.TYPE_INFO == 'ADMIN_SPATIAL_UNIT':
                    select_column_name = u'{0}.name AS {1}'.format(
                        table_pseudo_name, pseudo_column_name)
                    use_custom_join = True
                    use_inner_join = False

                # These are outer joins
                join_type = 'LEFT JOIN'

                # Use inner join only if parent entity is an STR entity
                if use_inner_join and \
                        str_entity.is_str_entity(fk_parent_entity):
                    join_type = 'INNER JOIN'

                if use_custom_join:
                    join_statement = u'{0} {1} {2} ON {3} = {2}.{4}'.format(
                        join_type, parent_table, table_pseudo_name,
                        col_select_name, c.entity_relation.parent_column
                    )
                else:
                    join_statement = u'{0} {1} ON {2} = {1}.{3}'.format(
                        join_type, parent_table, col_select_name,
                        c.entity_relation.parent_column
                    )

                # Assert if the column is in the list of omitted join columns
                if c.name not in omit_join_statement_columns:
                    join_statements.append(join_statement)

            # Assert if the column is in the list of omitted view columns
            if c.name not in omit_view_columns:
                if select_column_name:
                    column_names.append(select_column_name)

    return column_names, join_statements


def _abs_column_name(name):
    # Returns the absolute column name from the pseudo name
    if 'AS' in name:
        names = name.split('AS')
        name = names[0].strip()

    return name


def _insert_distinct_exp(abs_name, pseudo_name):
    # Insert the DISTINCT ON expression for the given column name
    return 'DISTINCT ON ({0}) {1}'.format(abs_name, pseudo_name)


def _set_distinct_column(column, column_collection):
    # Re-arrange the list to that the distinct column is inserted at the
    # top and DISTINCT keyword is included as well.
    rev = []

    for c in column_collection[:]:
        norm_c = _abs_column_name(c)

        if norm_c == column:
            column_collection.remove(c)
            distinct_exp = _insert_distinct_exp(norm_c, c)
            rev.append(distinct_exp)

    rev.extend(column_collection)

    return rev





