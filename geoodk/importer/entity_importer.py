"""
/***************************************************************************
Name                 : EntityImporter
Description          : A class to read and enumerate collected data from mobile phones

Date                 : 16/June/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
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
import os
from PyQt4.QtXml import QDomDocument
from PyQt4.QtCore import QFile, QIODevice
from stdm.settings import current_profile
from stdm.utils.util import entity_attr_to_id, lookup_id_from_value
from stdm.data.configuration import entity_model
from stdm.geoodk.importer.geometry_provider import GeomPolgyon


class EntityImporter():
    """
    class constructor
    """
    def __init__(self, instance):
        """
        Initialize variables
        """
        self.instance = instance
        self.instance_doc = QDomDocument()
        self.set_instance_document(self.instance)

    def set_instance_document(self, file_p):
        """

        :return:
        """
        file_path = QFile(file_p)
        if file_path.open(QIODevice.ReadOnly):
            self.instance_doc.setContent(file_path)

    def entity_attributes_from_instance(self, entity):
        """
        Get particular entity attributes from the
        instance document
        param: table short_name
        type: string
        return: table column name and column data
        :rtype: dictionary
        """
        attributes = {}
        nodes = self.instance_doc.elementsByTagName(entity)
        entity_nodes = nodes.item(0).childNodes()
        if entity_nodes:
            for j in range(entity_nodes.count()):
                node_val = entity_nodes.item(j).toElement()
                attributes[node_val.nodeName()] = node_val.text()
        return attributes

    def process_import_to_db(self, entity):
        """
        Save the object data to the database
        :return:
        """
        if self.instance_doc is not None:
            attributes = self.entity_attributes_from_instance(entity)
            entity_add = Save2DB(entity, attributes)
            entity_add.save_to_db()
        else:
            return


class Save2DB:
    """
    Class to insert entity data into db
    """
    def __init__(self, entity, attributes):
        """
        Initialize class and class variable
        """
        self.attributes = attributes
        self.entity = self.object_from_entity_name(entity)
        self.model = self.dbmodel_from_entity()

    def object_from_entity_name(self, entity):
        """

        :return:
        """
        user_entity = current_profile().entity_by_name(entity)
        return user_entity

    def dbmodel_from_entity(self):
        """
        Format model attributes from pass entity attributes
        :return:
        """
        entity_object = entity_model(
            self.entity
        )
        entity_object_model = entity_object()

        return entity_object_model

    def save_to_db(self):
        """
        Format object attribute data from entity
        attribute
        :return:
        """
        for k, v in self.attributes.iteritems():
            if hasattr(self.model, k):
                var = self.attribute_formatter(k, v)
                setattr(self.model, k, var)
        self.model.save()
        self.cleanup()

    def column_info(self):
        """

        :return:
        """
        type_mapping ={}
        cols = self.entity.columns.values()
        for c in cols:
            type_mapping[c.name] = c.TYPE_INFO
        return type_mapping

    def attribute_formatter(self, key, var):
        """

        :return:
        """
        col_type = self.column_info().get(key)
        col_prop = self.entity.columns[key]
        if col_type == 'LOOKUP':
            if not len(var) > 3:
                return entity_attr_to_id(col_prop.parent, "code", var)
            else:
                return lookup_id_from_value(col_prop.parent, var)
        elif col_type == 'ADMIN_SPATIAL_UNIT':
            if not len(var) > 3:
                return entity_attr_to_id(col_prop.parent, "code", var)
            else:
                return entity_attr_to_id(col_prop.parent, "name", var)

        elif col_type == 'MULTIPLE_SELECT':
            if not len(var) > 3:
                return entity_attr_to_id(col_prop.association.first_parent, "code", var)
            else:
                return lookup_id_from_value(col_prop.association.first_parent, var)
        elif col_type == 'GEOMETRY':
            geom_provider = GeomPolgyon(var)
            return geom_provider.polygon_to_Wkt()
        elif col_type == 'FOREIGN_KEY':
            if var != '':
                return
        else:
            return var

    def foreign_key_formatter(self):
        """
        Format the foreign key column to receive the attribute id
        of the parenat column.
        :return:
        """

    def cleanup(self):
        """

        :return:
        """
        self.model = None
        self.entity = None
        self.attributes = None



class ForeignKeyFormatter():
    """
    Class constructor
    """
    def __init__(self, fkval):
        """
        Initialize class variables
        :param fkval: string, key that is foreign key column
        """
        self.fk_val = fkval
        self.unique_key = None

    def parent(self):
        """
        Get the parent table to the child
        :return:
        """
        return self.fk_val

    def set_parent(self, parent):
        """

        :param parent:
        :return:
        """
        self.fk_val = parent

    def parent_name(self):
        """
        Get the name of the parent table
        :return:
        """
        return self.fk_val.name

    def check_parent_in_list(self, parent):
        """
        Check if the table is part of the list and get the attributes
        :param parent:
        :return:
        """
        pass

    def set_object(self):
        """
        Ensure the object is set to db first
        :return:
        """
        pass

    def parent_data_first(self):
        """

        :return:
        """







