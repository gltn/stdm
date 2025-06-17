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

from qgis.PyQt.QtCore import (
    pyqtSignal,
    QObject
)

from stdm.data.configuration.columns import (
    BaseColumn,
    ForeignKeyColumn,
    GeometryColumn,
    LookupColumn,
    MultipleSelectColumn,
    SerialColumn
)
from stdm.data.configuration.db_items import (
    DbItem,
    TableItem
)
from stdm.data.configuration.entity_updaters import entity_updater
from stdm.data.pg_utils import table_view_dependencies
from stdm.utils.renameable_dict import RenameableKeyDict

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
    column_removed = pyqtSignal(str)

    def __init__(self, name, profile, create_id_column=True, supports_documents: bool=True,
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

        name = self._shortname_to_name(name)

        TableItem.__init__(self, name)

        self.description = ''
        self.is_associative = False
        self.user_editable = True
        self.columns = RenameableKeyDict()
        self.updated_columns = OrderedDict()

        # Added in version 1.7
        self.label = ''

        '''
        We will always create an ID column due to a bug in SQLAlchemy-migrate
        as setting the 'id' column as a primary key does not create a serial
        column type in the database.
        '''
        self.create_id_column = True

        # Create primary key
        if self.create_id_column:
            LOGGER.debug('Creating primary key for %s entity.', self.name)

            self._create_serial_column()

        self.supporting_doc = None

        # FIXME: Refactor the names for following supports_documents assignments
        self._supports_documents = supports_documents

        if self._supports_documents:
            self.supports_documents = True

        self.is_proxy = is_proxy

        # Sync this with row index of the viewer
        self.row_index = -1

        self.entity_in_database = False

        LOGGER.debug('%s entity created.', self.name)

    def _shortname_to_name(self, name: str) -> str:
        # Append profile prefix if not global
        if not self.is_global:
            # format the internal name, replace spaces between words
            # with underscore and make all letters lower case.
            name = str(name).strip()

        name = name.replace(' ', "_")
        name = name.lower()

        # Ensure prefix is not duplicated in the names
        prfx = self.profile.prefix
        prefix_idx = name.find('{}_'.format(prfx), 0, len(prfx) + 1)

        # If there is no prefix then append
        if prefix_idx == -1 and not self.is_global:
            name = '{0}_{1}'.format(self.profile.prefix, name)

        return name

    def rename(self, shortname):
        """
        Updates the entity short name and name to use the new name. This
        function is used by the profile object and should not be used
        directly.
        To rename an entity, please use
        :py:class:Profile.rename(original_name, new_name) function.
        :param shortname: New shortname. The table name will also be derived
        from this as well.
        :type shortname: str
        """
        self.short_name = shortname
        self.name = self._shortname_to_name(shortname)

        # Rename supporting documents if enabled
        if self.supports_documents:
            self.supporting_doc.rename(shortname)

    @property
    def supports_documents(self):
        return self._supports_documents

    @supports_documents.setter
    def supports_documents(self, value):
        # Enable the attachment of supporting documents if flag is specified
        self._supports_documents = value
        if value:
            self.supporting_doc = EntitySupportingDocument(self.profile, self)
            self.profile.add_entity(self.supporting_doc)

    def _create_serial_column(self):
        """
        Creates a serial column which becomes the primary key of the table.
        """
        sc = SerialColumn('id', self)
        self.add_column(sc)

    def ui_display(self):
        """
        :return: Returns a more friendly name for the entity as this will
        allow non-ASCII characters to be used to describe the entity in a
        user-interface context. The 'label' attribute is given preference,
        otherwise the short_name is used.
        :rtype: str
        """
        return self.label or self.short_name.replace(
            '_', ' '
        ).title()

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

    def rename_column(self, old_name, new_name):
        """
        Renames the column with the given old_name to the new_name. This is
        applicable only if the column has not yet been created in the
        database.
        :param old_name: Existing column name to be renamed.
        :type old_name: str
        :param new_name: New column name.
        :type new_name: str
        :return: Returns True if the column was successfully renamed, else
        False.
        :rtype: bool
        """
        if old_name not in self.columns:
            LOGGER.debug('%s column not found, item does '
                         'not exist in the collection.', old_name)

            return False

        col = self.column(old_name)
        col.rename(new_name)

        # Update column collection
        self.columns.rename(old_name, new_name)

    def remove_column(self, name):
        """
        Removes a column with the given name from the collection.
        :param name: Column name.
        :type name: str
        :return: True if the column was successfully removed, else False.
        :rtype: bool
        """
        if name not in self.columns:
            LOGGER.debug('%s column not found, item does '
                         'not exist in the collection.', name)

            return False

        col = self.columns.pop(name)

        LOGGER.debug('%s column removed from %s entity', name, self.name)

        col.action = DbItem.DROP

        # Add column to the collection of updated columns
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
        if col.name in self.updated_columns:
            del self.updated_columns[col.name]

        self.updated_columns[col.name] = col

        # Update action
        if self.action == DbItem.NONE:
            self.action = DbItem.ALTER

    def _constructor_args(self):
        """
        :return: Returns a collection of the constructor keys and
        corresponding values for cloning the this object.
        """
        constructor_args = {'create_id_column': self.create_id_column, 'supports_documents': self.supports_documents,
                            'is_global': self.is_global, 'is_proxy': self.is_proxy}

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
        # Copy columns
        # self._copy_columns(entity)

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

    def associations(self):
        """
        :return: Returns a collection of entities which are indirectly linked
        to this entity through association entities. A multiple select column
        is an example of an object that uses association entities.
        :rtype: list
        """
        assoc_entities = self.profile.entities_by_type_info(
            'ASSOCIATION_ENTITY'
        )

        rel_entities = []

        for ase in assoc_entities:
            if ase.first_parent.name == self.name:
                rel_entities.append(ase.first_parent)
            elif ase.second_parent.name == self.name:
                rel_entities.append(ase.second_parent)

        return rel_entities

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

        # Dependent entity names
        dep_ent = [e.short_name for e in all_relations]

        # Add views as well
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
        :rtype: bool
        """
        return True if len(self.geometry_columns()) > 0 else False

    def document_types(self):
        """
        :return: Returns a list of document types specified for this entity.
        An AttributeError is raised if supporting documents are not enabled for this
        entity.
        :rtype: list
        """
        if not self.supports_documents:
            raise AttributeError('Supporting documents are not enabled for '
                                 'this entity.')

        return list(self.supporting_doc.document_types().keys())

    def document_types_non_hex(self):
        """
        :return: Returns a list of document type String specified for this entity.
        An AttributeError is raised if supporting documents are not enabled for this
        entity.
        :rtype: list
        """
        if not self.supports_documents:
            raise AttributeError('Supporting documents are not enabled for '
                                 'this entity.')

        return self.supporting_doc.document_types_non_hex()

    def document_path(self):
        """
        :return: Returns a subpath for locating supporting documents using
        the profile and entity names respectively. This is concatenated to
        the root path to locate documents for this particular entity.
        :rtype: str
        """
        if not self.supports_documents:
            raise AttributeError('Supporting documents are not enabled for '
                                 'this entity.')

        return self.supporting_doc.document_path()

    def virtual_columns(self):
        """
        :return: Returns a list of derived column names such as multi-select
        columns, supporting document columns separated by document type etc.
        :rtype: list
        """
        virtual_cols = []

        if self.supports_documents:
            doc_types = self.document_types()
            for doc_type in doc_types:
                u_doc_type = str(doc_type)
                text_value = self.supporting_doc._doc_types_value_list.values[
                    u_doc_type
                ]

                virtual_cols.append(text_value.value)

        multi_select_cols = self.columns_by_type_info(
            MultipleSelectColumn.TYPE_INFO
        )

        # Get column names
        multi_select_cols = [c.name for c in multi_select_cols]

        virtual_cols.extend(multi_select_cols)

        return virtual_cols

    def __eq__(self, other):
        """
        Compares entity using the name.
        :param other: Entity object.
        :type other: Entity
        :return: True if the entity is equal, else False.
        :rtype: bool
        """
        if other.name != self.name:
            return False

        return True

    # Added in 1.7
    def update_column_row_index(self, name, index):
        if name in self.columns:
            self.columns[name].row_index = index

    def sort_columns(self):
        self.columns = RenameableKeyDict(sorted(list(self.columns.items()), key=lambda e: e[1].row_index))

class EntitySupportingDocument(Entity):
    """
    An association class that provides the link between a given Entity and
    a SupportingDocument class.
    """
    TYPE_INFO = 'ENTITY_SUPPORTING_DOCUMENT'

    def __init__(self, profile, parent_entity):
        self.parent_entity = parent_entity

        name = self._entity_short_name(parent_entity.short_name)
        Entity.__init__(self, name, profile, supports_documents=False)

        self.user_editable = False

        # Supporting document ref column
        self.document_reference = ForeignKeyColumn('supporting_doc_id', self)

        normalize_name = self.parent_entity.short_name.replace(
            ' ',
            '_'
        ).lower()

        # Entity reference column
        entity_ref_name = '{0}_{1}'.format(normalize_name, 'id')
        self.entity_reference = ForeignKeyColumn(entity_ref_name, self)

        # Document types
        vl_name = self._doc_type_name(normalize_name)

        self._doc_types_value_list = self._doc_type_vl(vl_name)

        if self._doc_types_value_list is None:
            self._doc_types_value_list = self.profile.create_value_list(
                vl_name
            )
            # Add a default type
            self._doc_types_value_list.add_value(self.tr('General'))

            self.profile.add_entity(self._doc_types_value_list)

        # Document type column
        self.doc_type = LookupColumn('document_type', self)
        self.doc_type.value_list = self._doc_types_value_list

        # Append columns
        self.add_column(self.document_reference)
        self.add_column(self.entity_reference)
        self.add_column(self.doc_type)

        LOGGER.debug('Updating foreign key references in %s entity.',
                     self.name)

        # Update foreign key references
        self._update_fk_references()

        LOGGER.debug('%s entity successfully initialized', self.name)

    def _entity_short_name(self, parent_entity_name):
        name = '{0}_{1}'.format(parent_entity_name,
                                 'supporting_document')
        return name

    def _doc_type_name(self, normalize_name):
        vl_name = 'check_{0}_document_type'.format(normalize_name)

        return vl_name

    def _doc_type_vl(self, name: str) ->list:
        # Search for the document type value list based on the given name
        value_lists = self.profile.value_lists()

        doc_type_vl = [v for v in value_lists if v.short_name == name]
        # Return first item

        if len(doc_type_vl) > 0:
            return doc_type_vl[0]

        return None

    def _update_fk_references(self):
        # Update ForeignKey references.
        # check if there is an 'id' column
        entity_id = self._entity_id_column(self.parent_entity)

        LOGGER.debug('Attempting to set %s entity as the parent entity to '
                     'this supporting document reference.',
                     self.parent_entity.name)

        if entity_id is None:
            err = self.tr('%s does not have an id column. This is required '
                          'in order to link it to the supporting document '
                          'table through this association '
                          'table.' % self.parent_entity.name)

            LOGGER.debug(err)

            raise AttributeError(err)

        self.entity_reference.set_entity_relation_attr('parent',
                                                       self.parent_entity)
        self.entity_reference.set_entity_relation_attr('parent_column', 'id')

        # Supporting document reference
        self.document_reference.set_entity_relation_attr('parent',
                                                         self.profile.supporting_document)
        self.document_reference.set_entity_relation_attr('parent_column',
                                                         'id')

    def rename(self, shortname):
        """
        Updates the supporting document references when the parent entity is
        renamed. This renames the shortname and name, foreign key column and
        the name of the document type lookup.
        :param shortname: Shortname of the parent entity.
        :type shortname: str
        """
        # Remove the object then re-insert so as to update index
        doc_entity = self.profile.entities.pop(self.short_name)

        supporting_docs_shortname = self._entity_short_name(
            shortname
        ).replace(
            ' ',
            '_'
        ).lower()

        # Update shortname and name
        super(EntitySupportingDocument, self).rename(
            supporting_docs_shortname
        )

        # Re-insert the entity
        self.profile.add_entity(self, True)

        # Get entity relations and update entity references
        parent_relations = self.profile.parent_relations(self)
        child_relations = self.profile.child_relations(self)

        # Update relations
        for pr in parent_relations:
            pr.parent = self

        for cr in child_relations:
            cr.child = self

        # Rename lookup for supporting documents lookup
        if self._doc_types_value_list is not None:
            norm_parent_short_name = self.parent_entity.short_name.replace(
                ' ',
                '_'
            ).lower()
            vl_name = self._doc_type_name(norm_parent_short_name)
            self._doc_types_value_list.rename_entity(vl_name)

    def document_types(self):
        """
        :return: Returns a collection of document type names and
        corresponding codes.
        :rtype: OrderedDict
        """
        return self._doc_types_value_list.values

    def document_types_non_hex(self):
        # Added in version 1.7
        """
        :return: Returns a collection of document type names and
        corresponding codes.
        :rtype: OrderedDict
        """
        non_hex_values = []
        for v in self._doc_types_value_list.values:
            cv = self._doc_types_value_list.values[v]
            if cv.updated_value == '':
                txt = cv.value
            else:
                txt = cv.updated_value
            non_hex_values.append(txt)
        return non_hex_values

    def document_path(self):
        """
        :return: Returns a subpath for locating supporting documents using
        the profile and entity names respectively. This is concatenated to
        the root path to locate documents for this particular entity.
        :rtype: str
        """
        return '{0}/{1}'.format(self.profile.key, self.parent_entity.name)

    @property
    def document_type_entity(self):
        """
        :return: ValueList object containing the entity types.
        :rtype: ValueList
        """
        return self._doc_types_value_list

    def _entity_id_column(self, entity):
        """
        Check if the entity has an ID column and return it, else returns None.
        """
        return entity.column('id')

        
