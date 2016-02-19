"""
/***************************************************************************
Name                 : ConfigurationWriter
Description          : Writes configuration object to file.
Date                 : 15/February/2016
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
from PyQt4.QtCore import (
    QFile,
    QFileInfo,
    QIODevice
)
from PyQt4.QtXml import (
    QDomDocument,
    QDomNode
)

from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.data.configuration.exception import ConfigurationException
from stdm.data.configuration.supporting_document import SupportingDocument
from stdm.data.configuration.entity import Entity

class ConfigurationFileSerializer(object):
    """
    (De)serializes configuration object from/to a specified file object.
    """
    def __init__(self, path):
        """
        :param path: File location where the configuration will be saved.
        :type path: str
        """
        self.path = path
        self.config = StdmConfiguration.instance()

    def save(self):
        """
        Serialize configuration object to the given file location.
        """
        if self.config.is_null:
            raise ConfigurationException('StdmConfiguration object is null')

        if not self.path:
            raise IOError('File path for saving the configuration is empty.')

        save_file_info = QFileInfo(self.path)

        #Check if the suffix is in the file name
        #TODO: Remove str function
        if not str(save_file_info.suffix()).lower != 'stc':
            self.path = u'{0}.{1}'.format(self.path, 'stc')
            save_file_info = QFileInfo(self.path)

        #Test if the file is writeable
        save_file = QFile(self.path)
        if not save_file.open(QIODevice.WriteOnly):
            raise IOError(u'The file cannot be saved in '
                          u'{0}'.format(self.path))

        #Create DOM document and populate it with STDM config properties
        config_document = QDomDocument()
        self.write_xml(config_document)

        if save_file.write(config_document.toByteArray()) == -1:
            raise IOError('The configuration could not be written to file.')

    def write_xml(self, document):
        """
        Populate the DOM document with the configuration properties.
        :param document: DOM document to be updated.
        :type document: QDomDocument
        """
        config_element = document.createElement('Configuration')
        config_element.setAttribute('version', str(self.config.VERSION))

        #Append main element
        document.appendChild(config_element)

        #Append profile information
        for p in self.config.profiles.values():
            ProfileSerializer.write_xml(p, config_element, document)


class ProfileSerializer(object):
    """
    (De)serialize profile information.
    """
    @staticmethod
    def write_xml(profile, parent_node, document):
        """
        Appends profile information to the parent node.
        :param profile: Profile object
        :type profile: Profile
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        profile_element = document.createElement('Profile')

        profile_element.setAttribute('name', profile.name)

        exclude_entities = ['admin_spatial_unit_set', 'supporting_document',
                            'social_tenure_relationship']

        #Append entity information
        for e in profile.entities.values():
            item_serializer = EntitySerializerCollection.handler(e.TYPE_INFO)

            if item_serializer:
                item_serializer.write_xml(e, profile_element, document)

        #Append entity relation information
        er_parent_element = document.createElement('Relations')
        for er in profile.relations.values():
            EntityRelationSerializer.write_xml(er, er_parent_element, document)

        profile_element.appendChild(er_parent_element)

        #Append social tenure information
        SocialTenureSerializer.write_xml(profile.social_tenure,
                                         profile_element, document)

        parent_node.appendChild(profile_element)


class SocialTenureSerializer(object):
    """
    (De)serializes social tenure information.
    """
    PARTY = 'party'
    SPATIAL_UNIT = 'spatialUnit'
    TENURE_TYPE = 'tenureTypeList'

    @staticmethod
    def write_xml(social_tenure, parent_node, document):
        """
        Appends social tenure information to the profile node.
        :param social_tenure: Social tenure object
        :type social_tenure: SocialTenure
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        social_tenure_element = document.createElement('SocialTenure')

        social_tenure_element.setAttribute(SocialTenureSerializer.PARTY,
                                           social_tenure.party.short_name)
        social_tenure_element.setAttribute(SocialTenureSerializer.SPATIAL_UNIT,
                                        social_tenure.spatial_unit.short_name)
        social_tenure_element.setAttribute(SocialTenureSerializer.TENURE_TYPE,
                                    social_tenure.tenure_type_collection.short_name)

        parent_node.appendChild(social_tenure_element)


class EntitySerializerCollection(object):
    """
    Container for entity-based serializers which are registered using the
    type info of the Entity subclass.
    """
    _registry = {}

    @classmethod
    def register(cls):
        if not hasattr(cls, 'ENTITY_TYPE_INFO'):
            return

        EntitySerializerCollection._registry[cls.ENTITY_TYPE_INFO] = cls

    @staticmethod
    def handler(type_info):
        return EntitySerializerCollection._registry.get(type_info, None)

    @classmethod
    def group_element(cls, parent_node, document):
        """
        Creates a parent/group element which is then used as the parent node
        for this serializer. If no 'GROUP_TAG' class attribute is specified
        then the profile node is returned.
        :param parent_node: Parent node corresponding to the profile node,
        :type parent_node: QDomNode
        :param document: main document object.
        :type document: QDomDocument
        :return: Prent/group node fpr appending the child node created by
        this serializer.
        :rtype: QDomNode
        """
        if not hasattr(cls, 'GROUP_TAG'):
            return parent_node

        group_tag = getattr(cls, 'GROUP_TAG')

        #Search for group element and create if it does not exist
        group_element = parent_node.firstChildElement(group_tag)

        if group_element.isNull():
            group_element = document.createElement(group_tag)
            parent_node.appendChild(group_element)

        return group_element


class EntitySerializer(EntitySerializerCollection):
    """
    (De)serializes entity information.
    """
    TAG_NAME = 'Entity'

    #Specify attribute names
    GLOBAL = 'global'
    SHORT_NAME = 'shortName'
    NAME = 'name'
    DESCRIPTION = 'description'
    ASSOCIATIVE = 'associative'
    EDITABLE = 'editable'
    CREATE_ID = 'createId'
    PROXY = 'proxy'
    SUPPORTS_DOCUMENTS = 'supportsDocuments'
    ENTITY_TYPE_INFO = 'ENTITY'

    @staticmethod
    def write_xml(entity, parent_node, document):
        """
        ""
        Appends entity information to the profile node.
        :param entity: Social tenure object
        :type entity: SocialTenure
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        entity_element = document.createElement(EntitySerializer.TAG_NAME)

        #Set entity attributes
        entity_element.setAttribute(EntitySerializer.GLOBAL,
                                    str(entity.is_global))
        entity_element.setAttribute(EntitySerializer.SHORT_NAME,
                                    entity.short_name)
        #Name will be ignored when the deserializing the entity object
        entity_element.setAttribute(EntitySerializer.NAME,
                                    entity.name)
        entity_element.setAttribute(EntitySerializer.DESCRIPTION,
                                    entity.description)
        entity_element.setAttribute(EntitySerializer.ASSOCIATIVE,
                                    str(entity.is_associative))
        entity_element.setAttribute(EntitySerializer.EDITABLE,
                                    str(entity.user_editable))
        entity_element.setAttribute(EntitySerializer.CREATE_ID,
                                    str(entity.create_id_column))
        entity_element.setAttribute(EntitySerializer.PROXY,
                                    str(entity.is_proxy))
        entity_element.setAttribute(EntitySerializer.SUPPORTS_DOCUMENTS,
                                    str(entity.supports_documents))

        #Root columns element
        columns_element = document.createElement('Columns')

        #Append column information
        for c in entity.columns.values():
            column_serializer = ColumnSerializerCollection.handler(c.TYPE_INFO)

            if column_serializer:
                column_serializer.write_xml(c, columns_element, document)

        entity_element.appendChild(columns_element)

        parent_node.appendChild(entity_element)

EntitySerializer.register()


class AssociationEntitySerializer(EntitySerializerCollection):
    """
    (De)serializes association entity information.
    """
    GROUP_TAG = 'Associations'
    TAG_NAME = 'Association'

    #Attribute names
    FIRST_PARENT = 'firstParent'
    SECOND_PARENT = 'secondParent'

    #Corresponding type info to (de)serialize
    ENTITY_TYPE_INFO = 'ASSOCIATION_ENTITY'

    #Specify attribute names
    @staticmethod
    def write_xml(association_entity, parent_node, document):
        """
        ""
        Appends association entity information to the profile node.
        :param value_list: Association entity object
        :type value_list: AssociationEntity
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        assoc_entity_element = document.createElement(AssociationEntitySerializer.TAG_NAME)

        assoc_entity_element.setAttribute(EntitySerializer.NAME,
                                          association_entity.name)
        assoc_entity_element.setAttribute(EntitySerializer.SHORT_NAME,
                                          association_entity.short_name)
        assoc_entity_element.setAttribute(AssociationEntitySerializer.FIRST_PARENT,
                                          association_entity.first_parent.short_name)
        assoc_entity_element.setAttribute(AssociationEntitySerializer.SECOND_PARENT,
                                          association_entity.second_parent.short_name)

        group_node = AssociationEntitySerializer.group_element(parent_node, document)

        group_node.appendChild(assoc_entity_element)

AssociationEntitySerializer.register()


class ValueListSerializer(EntitySerializerCollection):
    """
    (De)serializes ValueList information.
    """
    GROUP_TAG = 'ValueLists'
    TAG_NAME = 'ValueList'
    CODE_VALUE_TAG = 'CodeValue'

    #Attribute names
    NAME = 'name'
    CV_CODE = 'code'
    CV_VALUE = 'value'

    #Corresponding type info to (de)serialize
    ENTITY_TYPE_INFO = 'VALUE_LIST'

    #Specify attribute names
    @staticmethod
    def write_xml(value_list, parent_node, document):
        """
        ""
        Appends value list information to the profile node.
        :param value_list: Value list object
        :type value_list: ValueList
        :param parent_node: Parent element.
        :type parent_node: QDomNode
        :param document: Represents main document object.
        :type document: QDomDocument
        """
        value_list_element = document.createElement(ValueListSerializer.TAG_NAME)

        value_list_element.setAttribute(ValueListSerializer.NAME,
                                        value_list.short_name)

        #Add code value elements
        for cv in value_list.values.values():
            cd_element = document.createElement(ValueListSerializer.CODE_VALUE_TAG)

            cd_element.setAttribute(ValueListSerializer.CV_VALUE, cv.value)
            cd_element.setAttribute(ValueListSerializer.CV_CODE, cv.code)

            value_list_element.appendChild(cd_element)

        group_node = ValueListSerializer.group_element(parent_node, document)

        group_node.appendChild(value_list_element)

ValueListSerializer.register()


class EntityRelationSerializer(object):
    """
    (De)serializes EntityRelation information.
    """
    TAG_NAME = 'EntityRelation'

    NAME = 'name'
    PARENT = 'parent'
    PARENT_COLUMN = 'parentColumn'
    CHILD = 'child'
    CHILD_COLUMN = 'childColumn'

    @staticmethod
    def write_xml(entity_relation, parent_node, document):
        """
        Appends entity relation information to the parent node.
        :param entity_relation: Enrity relation object.
        :type entity_relation: EntityRelation
        :param parent_node: Parent node.
        :type parent_node: QDomNode
        :param document: Main document object
        :type document: QDomDocument
        """
        er_element = document.createElement(EntityRelationSerializer.TAG_NAME)

        #Set attributes
        er_element.setAttribute(EntityRelationSerializer.NAME,
                                entity_relation.name)
        er_element.setAttribute(EntityRelationSerializer.PARENT,
                                entity_relation.parent.short_name)
        er_element.setAttribute(EntityRelationSerializer.PARENT_COLUMN,
                                entity_relation.parent_column)
        er_element.setAttribute(EntityRelationSerializer.CHILD,
                                entity_relation.child.short_name)
        er_element.setAttribute(EntityRelationSerializer.CHILD_COLUMN,
                                entity_relation.child_column)

        parent_node.appendChild(er_element)


class ColumnSerializerCollection(object):
    """
    Container for column-based serializers which are registered using the
    type info of the column subclass.
    """
    _registry = {}
    TAG_NAME = 'Column'

    #Attribute names
    DESCRIPTION = 'description'
    NAME = 'name'
    INDEX = 'index'
    MANDATORY = 'mandatory'
    SEARCHABLE = 'searchable'
    UNIQUE = 'unique'
    USER_TIP = 'tip'
    MINIMUM = 'minimum'
    MAXIMUM = 'maximum'

    @classmethod
    def register(cls):
        if not hasattr(cls, 'COLUMN_TYPE_INFO'):
            return

        ColumnSerializerCollection._registry[cls.COLUMN_TYPE_INFO] = cls

    @classmethod
    def write_xml(cls, column, parent_node, document):
        col_element = document.createElement(cls.TAG_NAME)

        #Append general column information
        col_element.setAttribute('TYPE_INFO', cls.COLUMN_TYPE_INFO)
        col_element.setAttribute(ColumnSerializerCollection.DESCRIPTION,
                                 column.description)
        col_element.setAttribute(ColumnSerializerCollection.NAME, column.name)
        col_element.setAttribute(ColumnSerializerCollection.INDEX,
                                 str(column.index))
        col_element.setAttribute(ColumnSerializerCollection.MANDATORY,
                                 str(column.mandatory))
        col_element.setAttribute(ColumnSerializerCollection.SEARCHABLE,
                                 str(column.searchable))
        col_element.setAttribute(ColumnSerializerCollection.UNIQUE,
                                 str(column.unique))
        col_element.setAttribute(ColumnSerializerCollection.USER_TIP,
                                 column.user_tip)

        if hasattr(column, 'minimum'):
            col_element.setAttribute(ColumnSerializerCollection.MINIMUM,
                                     column.minimum)

        if hasattr(column, 'maximum'):
            col_element.setAttribute(ColumnSerializerCollection.MAXIMUM,
                                     column.maximum)

        #Append any additional information defined by subclasses.
        cls._write_xml(column, col_element, document)

        parent_node.appendChild(col_element)

    @classmethod
    def _write_xml(cls, column, column_element, document):
        """
        To be implemented by subclasses if they want to append additional
        information to the column element. Base implementation does nothing.
        """
        pass

    @staticmethod
    def handler(type_info):
        return ColumnSerializerCollection._registry.get(type_info, None)


class TextColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes text column type.
    """
    COLUMN_TYPE_INFO = 'TEXT'

TextColumnSerializer.register()


class VarCharColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes VarChar column type.
    """
    COLUMN_TYPE_INFO = 'VARCHAR'

VarCharColumnSerializer.register()


class IntegerColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes integer column type.
    """
    COLUMN_TYPE_INFO = 'BIGINT'

IntegerColumnSerializer.register()


class DoubleColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes double column type.
    """
    COLUMN_TYPE_INFO = 'DOUBLE'

DoubleColumnSerializer.register()


class SerialColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes serial/auto-increment column type.
    """
    COLUMN_TYPE_INFO = 'SERIAL'

SerialColumnSerializer.register()


class DateColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes date column type.
    """
    COLUMN_TYPE_INFO = 'DATE'

DateColumnSerializer.register()

class DateTimeColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes date time column type.
    """
    COLUMN_TYPE_INFO = 'DATETIME'

DateTimeColumnSerializer.register()


class GeometryColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes geometry column type.
    """
    COLUMN_TYPE_INFO = 'GEOMETRY'
    GEOM_TAG = 'Geometry'

    #Attribute names
    SRID = 'srid'
    GEOMETRY_TYPE = 'type'

    @classmethod
    def _write_xml(cls, column, column_element, document):
        #Append custom geometry information
        geom_element = \
            document.createElement(GeometryColumnSerializer.GEOM_TAG)
        geom_element.setAttribute(GeometryColumnSerializer.SRID,
                                    str(column.srid))
        geom_element.setAttribute(GeometryColumnSerializer.GEOMETRY_TYPE,
                                    column.geom_type)

        column_element.appendChild(geom_element)

GeometryColumnSerializer.register()


class ForeignKeyColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes foreign key column type.
    """
    COLUMN_TYPE_INFO = 'FOREIGN_KEY'
    RELATION_TAG = 'Relation'

    @classmethod
    def _write_xml(cls, column, column_element, document):
        #Append entity relation name
        fk_element = \
            document.createElement(ForeignKeyColumnSerializer.RELATION_TAG)
        fk_element.setAttribute('name', column.entity_relation.name)

        column_element.appendChild(fk_element)

ForeignKeyColumnSerializer.register()


class LookupColumnSerializer(ForeignKeyColumnSerializer):
    """
    (De)serializes lookup column type.
    """
    COLUMN_TYPE_INFO = 'LOOKUP'

LookupColumnSerializer.register()


class AdminSpatialUnitColumnSerializer(ForeignKeyColumnSerializer):
    """
    (De)serializes administrative spatial unit column type.
    """
    COLUMN_TYPE_INFO = 'ADMIN_SPATIAL_UNIT'

AdminSpatialUnitColumnSerializer.register()


class MultipleSelectColumnSerializer(ColumnSerializerCollection):
    """
    (De)serializes multiple select column type information.
    """
    COLUMN_TYPE_INFO = 'MULTIPLE_SELECT'

    ASSOCIATION_TAG = 'associationEntity'

    @classmethod
    def _write_xml(cls, column, column_element, document):
        #Append association entity short name
        association_entity_element = \
            document.createElement(MultipleSelectColumnSerializer.ASSOCIATION_TAG)
        association_entity_element.setAttribute('name',
                                                column.association.name)

        column_element.appendChild(association_entity_element)

MultipleSelectColumnSerializer.register()


def _str_to_bool(bool_str):
    return str(bool_str).upper() == 'T'







