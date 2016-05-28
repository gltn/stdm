"""
/***************************************************************************
Name                 : Entity
Description          : A container for table information and collection of
                       columns contained therein.
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
from collections import OrderedDict
from copy import deepcopy

from PyQt4.QtCore import (
    pyqtSignal,
    QObject
)
from stdm.data.configuration.columns import BaseColumn
from stdm.data.configuration.columns import (
    BaseColumn,
    ForeignKeyColumn,
    GeometryColumn,
    SerialColumn
)
from stdm.data.configuration.db_items import (
    DbItem,
    TableItem
)
from stdm.data.configuration.entity_updaters import entity_updater
from stdm.data.pg_utils import table_view_dependencies

LOGGER = logging.getLogger('stdm')


def entity_factory(name, profile, **kwargs):
    """
    Factory method for creating an instance of an Entity object. This
    function is passed on to a profile instance to create the Entity.
    :param name: Entity name.
    :type name: str
    :param profile: Profile that the entity will belong to.
    :type profile: Profile
    :param kwargs:
    :returns: Instance of an Entity object.
    :rtype: Entity
    """
    return Entity(name, profile, **kwargs)


class Entity(QObject, TableItem):
    """
    A wrapper for a database table object.
    """
    TYPE_INFO = 'ENTITY'
    sql_updater = entity_updater

    column_added = pyqtSignal(BaseColumn)
    column_removed = pyqtSignal(unicode)

    def __init__(self, name, profile, create_id_column=True, supports_documents=True,
                 is_global=False, is_proxy=False):
        """
        :param name: Name of the entity. The profile prefix will be appended
        to this name.
        :type name: str
        :param is_global: True if the entity should be applied across all
        profiles.
        :type is_global: bool
        :param profile: Profile that the entity will belong to.
        :type profile: Profile
        :param create_id_column: True to append an id serial column which
        will also be the table's primary key. This will always be True (bug).
        :type create_id_column: bool
        :param supports_documents: True if supporting documents can be
        attached to this entity.
        :type supports_documents: bool
        :param is_proxy: Table will not be created in the database as there
        is an existing table created by another process. This is useful when
        defining ForeignKey references to tables created outside of the
        configuration process.
        :type is_proxy: bool
        """
        QObject.__init__(self, profile)
        self.profile = profile
        self.is_global = is_global
        self.short_name = name

        #Append profile prefix if not global
        if not self.is_global:
            # format the internal name, replace spaces between words 
            # with underscore and make all letters lower case.
            name = unicode(name).strip()

        name = name.replace(' ', "_")
        name = name.lower()
            
        #Ensure prefix is not duplicated in the names
        prfx = self.profile.prefix
        prefix_idx = name.find(prfx, 0, len(prfx))

        #If there is no prefix then append
        if prefix_idx == -1 and not is_global:
            name = u'{0}_{1}'.format(self.profile.prefix, name)

        TableItem.__init__(self, name)

        self.description = ''
        self.is_associative = False
        self.user_editable = True
        self.columns = OrderedDict()

        '''
        We will always create an ID column due to a bug in SQLAlchemy-migrate
        as setting the 'id' column as a primary key does not create a serial
        column type in the database.
        '''
        self.create_id_column = True

        self.supports_documents = supports_documents
        self.supporting_doc = None
        self.is_proxy = is_proxy
        self.updated_columns = OrderedDict()

        #Create PK if flag is specified
        if self.create_id_column:
            LOGGER.debug('Creating primary key for %s entity.', self.name)

            self._create_serial_column()

        #Enable the attachment of supporting documents if flag is specified
        if self.supports_documents:
            self.supporting_doc = EntitySupportingDocument(self.profile, self)
            self.profile.add_entity(self.supporting_doc)

        LOGGER.debug('%s entity created.', self.name)

    def _create_serial_column(self):
        """
        Creates a serial column which becomes the primary key of the table.
        """
        sc = SerialColumn('id', self)
        self.add_column(sc)

    def add_column(self, column):
        """
        Add a column object to the collection.
        :param column: Column object.
        :type column: BaseColumn
        """
        self.columns[column.name] = column

        self.column_added.emit(column)

        LOGGER.debug('%s column added to %s entity.', column.name, self.name)

        self.append_updated_column(column)

    def column(self, name):
        """
        :param name: Column name.
        :type name: str
        :returns: Returns a column object with the given name from the
        collection, else None if not found.
        :rtype: BaseColumn
        """
        return self.columns.get(name, None)

    def remove_column(self, name):
        """
        Removes a column with the given name from the collection.
        :param name: Column name.
        :type name: str
        :return: True if the column was successfully removed, else False.
        :rtype: bool
        """
        if not name in self.columns:
            LOGGER.debug('%s column not found, item does '
                         'not exist in the collection.', name)

            return False

        col = self.columns.pop(name)

        LOGGER.debug('%s column removed from %s entity', name, self.name)

        col.action = DbItem.DROP

        #Add column to the collection of updated columns
        self.append_updated_column(col)

        self.column_removed.emit(name)

        return True

    def append_updated_column(self, col):
        """
        Append a column to the list of column that need to be altered or
        dropped.
        :param col: Column instance
        :type col: BaseColumn
        """
        if self.action == DbItem.CREATE:
            return

        self.updated_columns[col.name] = col

        #Update action
        if self.action == DbItem.NONE:
            self.action = DbItem.ALTER

    def _constructor_args(self):
        """
        :return: Returns a collection of the constructor keys and
        corresponding values for cloning the this object.
        """
        constructor_args = {}

        constructor_args['create_id_column'] = self.create_id_column
        constructor_args['supports_documents'] = self.supports_documents
        constructor_args['is_global'] = self.is_global
        constructor_args['is_proxy'] = self.is_proxy

        return constructor_args

    def _copy_columns(self, entity):
        """
        Copies the columns in the current object into the specified entity.
        :param entity: Target entity of the columns to be copied.
        :type entity: Entity
        """
        for c in self.columns.values():
            new_col = c.clone()
            entity.add_column(new_col)

    def _copy_attrs(self, entity):
        """
        Copies the attributes of the current object into the given entity object.
        :param entity: Target of the copied entity attributes.
        :type entity: Entity
        """
        entity.description = self.description
        entity.is_associative = self.is_associative
        entity.user_editable = self.user_editable

        #Copy columns
        #self._copy_columns(entity)


    def on_delete(self):
        """
        Specify additional action for cleaning up any additional references
        upon deleting this item. Default implementation does nothing.
        """
        pass

    def update(self, engine, metadata):
        """
        Update the entity in the database using the 'sql_updater' callable
        attribute.
        :param engine: SQLAlchemy engine which contains the database
        connection properties.
        :param metadata: Object containing all the schema constructs
        associated with our database.
        :type metadata: MetaData
        """
        if self.sql_updater is None:
            LOGGER.debug('%s entity has no sql_updater callable class.', self.name)

            return

        self.sql_updater(engine, metadata)

    def parents(self):
        """
        :return: Returns a collection of entities which this entity refers to
        through one or more entity relations (implemented as foreign key constraints
        in the database).
        :rtype: list
        """
        entity_relations = self.profile.child_relations(self)

        return [er.parent for er in entity_relations if er.valid()[0]]

    def children(self):
        """
        :return: Returns a collection of entities that refer to this entity
        as the parent through one or more entity relations (implemented as
        foreign key constraints in the database).
        :rtype: list
        """
        entity_relations = self.profile.parent_relations(self)

        return [er.child for er in entity_relations if er.valid()[0]]

    def dependencies(self):
        """
        Gets the tables and views that are related to the specified entity.
        :return: A dictionary containing a list of related entity names and
        views respectively.
        :rtype: dict
        """
        parents = self.parents()
        children = self.children()

        all_relations = parents + children

        #Dependent entity names
        dep_ent = [e.short_name for e in all_relations]

        #Add views as well
        dep_views = table_view_dependencies(self.name)

        return {'entities': dep_ent, 'views': dep_views}

    def column_children_relations(self, name):
        """
        :param name: Column name
        :type name: str
        :return: Returns a list of entity relations which reference the
        column with the given name as the child column in the entity relation.
        :rtype: list
        """
        entity_relations = self.profile.child_relations(self)

        return [er for er in entity_relations if er.child_column == name]

    def column_parent_relations(self, name):
        """
        :param name: Column name
        :type name: str
        :return: Returns a list of entity relations which reference the
        column with the given name as the parent column in the entity
        relation.
        These are basically entity relations in foreign key columns.
        :rtype: list
        """
        entity_relations = self.profile.parent_relations(self)

        return [er for er in entity_relations if er.parent_column == name]

    def columns_by_type_info(self, type_info):
        """
        :param type_info: Column TYPE_INFO
        :type type_info: str
        :returns: A list of columns based on the specified TYPE_INFO
        e.g. VARCHAR, DOUBLE etc.
        :rtype: Entity
        """
        return [c for c in self.columns.values()
                if c.TYPE_INFO == type_info]

    def geometry_columns(self):
        """
        :return: A list of Geometry-type columns.
        :rtype: list
        """
        return self.columns_by_type_info(GeometryColumn.TYPE_INFO)

    def has_geometry_column(self):
        """
        :return: True if the entity contains a spatial column, else False.
        :rtype: True
        """
        return True if len(self.geometry_columns()) > 0 else False


class EntitySupportingDocument(Entity):
    """
    An association class that provides the link between a given Entity and
    a SupportingDocument class.
    """
    TYPE_INFO = 'ENTITY_SUPPORTING_DOCUMENT'

    def __init__(self, profile, parent_entity):
        self.parent_entity = parent_entity

        name = u'{0}_{1}'.format(parent_entity.short_name,
                                 'supporting_document')

        Entity.__init__(self, name, profile, supports_documents=False)

        self.user_editable = False

        supporting_doc_prefix = u'{0}_{1}'.format(self.profile.prefix, 'supporting_doc_id')
        self.document_reference = ForeignKeyColumn(supporting_doc_prefix, self)

        entity_ref_name = u'{0}_{1}'.format(self.parent_entity.short_name,
                                            'id')
        self.entity_reference = ForeignKeyColumn(entity_ref_name, self)

        #Append columns
        self.add_column(self.document_reference)
        self.add_column(self.entity_reference)

        LOGGER.debug('Updating foreign key references in %s entity.',
                     self.name)

        #Update foreign key references
        self._update_fk_references()

        LOGGER.debug('%s entity successfully initialized', self.name)

    def _update_fk_references(self):
        #Update ForeignKey references.
        #check if there is an 'id' column
        entity_id = self._entity_id_column(self.parent_entity)

        LOGGER.debug('Attempting to set %s entity as the parent entity to '
                     'this supporting document reference.',
                     self.parent_entity.name)

        if entity_id is None:
            err = self.tr('%s does not have an id column. This is required '
                          'in order to link it to the supporting document '
                          'table through this association '
                          'table.'%(self.parent_entity.name))

            LOGGER.debug(err)

            raise AttributeError(err)

        self.entity_reference.set_entity_relation_attr('parent',
                                                       self.parent_entity)
        self.entity_reference.set_entity_relation_attr('parent_column', 'id')

        #Supporting document reference
        self.document_reference.set_entity_relation_attr('parent',
                                            self.profile.supporting_document)
        self.document_reference.set_entity_relation_attr('parent_column',
                                                         'id')

    def _entity_id_column(self, entity):
        """
        Check if the entity has an ID column and return it, else returns None.
        """
        return entity.column('id')
