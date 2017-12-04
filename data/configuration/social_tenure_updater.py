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
from PyQt4.QtGui import QApplication
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

from stdm.data.configuration import entity_model

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

    views = social_tenure.views

    # Loop through view name, primary entity items
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
        omit_join_statement_columns=party_col_names,
        view_name = view_name
    )

    party_columns, party_join = [], []

    # Omit party entities in the spatial unit join
    #### Create party views
    if not pe_is_spatial:
        party_columns, party_join = _entity_select_column(
            primary_entity, True, True, True,
            foreign_key_parents=fk_parent_names,
            omit_view_columns=omit_view_columns,
            omit_join_statement_columns=omit_join_statement_columns,
            view_name = view_name
        )

        # Set removal of all spatial unit columns apart from the id column
        for spatial_unit in social_tenure.spatial_units:
            omit_view_columns = deepcopy(spatial_unit.columns.keys())
            if 'id' in omit_view_columns:
                omit_view_columns.remove('id')

        view_columns = party_columns + str_columns

        # Set distinct column if specified
        if not distinct_column is None:
            view_columns = _set_distinct_column(distinct_column, view_columns)

        join_statement = str_join + party_join #+ spatial_unit_join

        if len(view_columns) == 0:
            LOGGER.debug('There are no columns for creating the social tenure '
                         'relationship view.')

            return

            # Create SQL statement
        create_view_sql = u'CREATE VIEW {0} AS SELECT {1} FROM {2} {3}'.format(
            view_name, ','.join(view_columns), social_tenure.name,
            ' '.join(join_statement))

        normalized_create_view_sql = text(create_view_sql)

        _execute(normalized_create_view_sql)

    else:
        # Set id column to be distinct
        distinct_column = '{0}.id'.format(primary_entity.name)

        # Omit STR columns if primary entity is spatial unit
        # str_columns = []

    #for spatial_unit in social_tenure.spatial_units:
    ### Create spatial_unit views
    if pe_is_spatial:
        spatial_unit_columns, spatial_unit_join = _entity_select_column(
            primary_entity,
            True,
            join_parents=True,
            is_primary=pe_is_spatial,
            foreign_key_parents=fk_parent_names,
            omit_view_columns=omit_view_columns,
            omit_join_statement_columns=omit_join_statement_columns,
            view_name = view_name
        )
        custom_tenure_columns = []
        custom_tenure_join = []
        custom_tenure_entity = social_tenure.spu_custom_attribute_entity(
            primary_entity
        )
        if custom_tenure_entity is not None:

            custom_tenure_columns, custom_tenure_join = _entity_select_column(
                custom_tenure_entity,
                True,
                join_parents=True,
                is_primary=False,
                foreign_key_parents=fk_parent_names,
                omit_view_columns=omit_view_columns,
                omit_join_statement_columns=omit_join_statement_columns,
                view_name=view_name
            )

        view_columns = spatial_unit_columns + str_columns + custom_tenure_columns

        # Set distinct column if specified
        if not distinct_column is None:
            view_columns = _set_distinct_column(distinct_column, view_columns)

        join_statement = str_join + spatial_unit_join + custom_tenure_join

        if len(view_columns) == 0:
            LOGGER.debug('There are no columns for creating the social tenure '
                         'relationship view.')

            return

        # Create SQL statement
        create_view_sql = u'CREATE VIEW {0} AS SELECT {1} FROM {2} {3}'.format(
            view_name, ','.join(view_columns), social_tenure.name,
            ' '.join(join_statement))

        normalized_create_view_sql = text(create_view_sql)

        _execute(normalized_create_view_sql)


def _entity_select_column(
        entity,
        use_inner_join=False,
        join_parents=False,
        is_primary=False,
        foreign_key_parents=None,
        omit_view_columns=None,
        omit_join_statement_columns=None,
        view_name=None
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
    if entity in str_entity.custom_attribute_entities.values():
        custom_tenure = True
    else:
        custom_tenure = False

    i = 0
    for c in columns:
        if c.TYPE_INFO not in _exclude_view_column_types:
            normalized_entity_sname = entity.short_name.replace(' ', '_').lower()

            pseudo_column_name = u'{0}_{1}'.format(normalized_entity_sname,
                    c.name)
            # use sudo name for custom tenure entity
            if custom_tenure:
                col_select_name = u'{0}_1.{1}'.format(
                    entity.name, c.name
                )
            else:
                col_select_name = u'{0}.{1}'.format(entity.name, c.name)
            # Get pseudoname to use

            select_column_name = u'{0} AS {1}'.format(col_select_name,
                                                      pseudo_column_name)

            if is_primary and c.name == 'id':
                # add row number id instead of party.id
                # if multi_party is allowed.
                if str_entity.multi_party:
                    # for party entity add use row number
                    if not entity.has_geometry_column():
                        row_id = 'row_number() OVER () AS id'

                        select_column_name = row_id

                    else:
                        # add spatial unit id as the id.
                        col_spatial_unit_id = u'{0}.{1} AS {1}'.format(
                            entity.name, c.name
                        )
                        select_column_name = col_spatial_unit_id

                else:
                    # add party id or spatial unit as id
                    entity_id = u'{0}.{1} AS {1}'.format(
                        entity.name, c.name
                    )

                    select_column_name = entity_id

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
                    lookup_model = entity_model(c.entity_relation.parent)
                    lookup_model_obj = lookup_model()
                    result = lookup_model_obj.queryObject().filter(
                        lookup_model.code != '').filter(
                        lookup_model.code != None).all()
                    if len(result) == 0:
                        select_column_name = u'{0}.value AS {1}'.format(
                            table_pseudo_name,
                            pseudo_column_name
                        )
                    else:
                        value = u'{0}.value'.format(table_pseudo_name)
                        code = u'{0}.code'.format(table_pseudo_name)
                        select_column_name = u"concat({0}, ' (', {1}, ')') AS {2}".\
                            format(value, code, pseudo_column_name)

                    use_custom_join = True

                    # Check if the column is for tenure type
                    if c.name != 'tenure_type':
                        use_inner_join = False

                elif c.TYPE_INFO == 'ADMIN_SPATIAL_UNIT':
                    select_column_name = u'{0}.name AS {1}'.format(
                        table_pseudo_name, pseudo_column_name)
                    use_custom_join = True
                    use_inner_join = False

                elif c.TYPE_INFO == 'FOREIGN_KEY':
                    if c.entity_relation.parent not in str_entity.parties and \
                        c.entity_relation.parent not in str_entity.spatial_units:

                        if len(c.entity_relation.display_cols) > 0:
                            display_col_names = []
                            for display_col in c.entity_relation.display_cols:
                                name = u'{0}.{1}'.format(table_pseudo_name, display_col)
                                display_col_names.append(name)
                            select_column_name = u"concat_ws(' '::text, {0}) AS {1}".format(
                                ', '.join(display_col_names),
                                pseudo_column_name
                            )

                        else:
                            if not custom_tenure:
                                select_column_name = u'{0}.id AS {1}'.format(
                                    table_pseudo_name,
                                    pseudo_column_name
                                )

                        use_custom_join = True
                        use_inner_join = False
                # These are outer joins
                join_type = 'LEFT JOIN'

                # Use inner join only if parent entity is an STR entity and it is the current entity.
                # Other str entities should use left join.

                if str_entity.is_str_entity(fk_parent_entity) and \
                                fk_parent_entity.name in view_name:

                    join_type = 'INNER JOIN'

                if use_custom_join:
                   # exclude replace str name with custom tenure name in join.
                    if custom_tenure:
                        if c.name == 'social_tenure_relationship_id':
                            i = i + 1
                            # pseudo_names = foreign_key_parents.get(parent_table)
                            col_select_name = u'{0}_{1}.{2}'.format(
                                entity.name, str(i), c.name
                            )
                            # Get pseudoname to use
                            table_pseudo_name = u'{0}_{1}'.format(
                                entity.name, str(i)
                            )
                            join_statement = u'{0} {1} {2} ON {3} = {2}.{4}'.format(
                                join_type, entity.name, table_pseudo_name,
                                col_select_name,
                                c.entity_relation.parent_column
                            )
                            join_statements = [join_statement] + join_statements

                        else:
                            join_statement = u'{0} {1} {2} ON {3} = {2}.{4}'.format(
                                join_type, parent_table, table_pseudo_name,
                                col_select_name,
                                c.entity_relation.parent_column
                            )
                            join_statements.append(join_statement)

                    else:

                        join_statement = u'{0} {1} {2} ON {3} = {2}.{4}'.format(
                            join_type, parent_table, table_pseudo_name,
                            col_select_name, c.entity_relation.parent_column
                        )
                        join_statements.append(join_statement)


                else:

                # Assert if the column is in the list of omitted join columns
                #
                # if c.name in omit_join_statement_columns:
                #     if 'INNER JOIN' in join_statement:
                #         join_statements.append(join_statement)
                # else:

                    join_statement = u'{0} {1} ON {2} = {1}.{3}'.format(
                        join_type, parent_table, col_select_name,
                        c.entity_relation.parent_column
                    )
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





