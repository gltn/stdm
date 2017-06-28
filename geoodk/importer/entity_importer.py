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

class EntityImporter():
    """
    class constructor
    """
    def __init__(self, entities, instances):
        """
        Initialize variables
        """
        self.instances = instances
        self.entities = entities
        self.instance_doc = QDomDocument()
        self.instance_info = {}

    def set_document(self, file_p):
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

    def process_import_to_db(self):
        """
        Save the object data to the database
        :return:
        """
        for instance in self.instances:
            self.set_document(instance)
            for entity in self.entities:
                attributes = self.entity_attributes_from_instance(entity)
                save_entity = Save2DB(entity,attributes)
                save_entity.save_to_db()


class Save2DB():
    """
    Class to insert entity data into db
    """
    def __init__(self, entity, attribs):
        """
        Initialize class and class variable
        """
        self.attribs = attribs
        self.entity  = entity
        self.model = self.dbmodel_from_entity()

    def object_from_entity_name(self):
        """

        :return:
        """
        entity = current_profile().entity_by_name(self.entity)
        return entity

    def dbmodel_from_entity(self):
        """
        Format model attributes from pass entity attributes
        :return:
        """
        self.object_from_entity_name()
        entity_object = entity_model(
            self.object_from_entity_name()
        )
        entity_object_model = entity_object()

        return entity_object_model

    def save_to_db(self):
        """
        Format object attribute data from entity
        attribute
        :return:
        """
        entity = self.object_from_entity_name()
        self.model
        for k, v in self.attribs.iteritems():
            if hasattr(self.model, k):
                var = self.attribute_formatter(entity, k, v)
                setattr(self.model, k, var)
        self.model.save()
        self.cleanup()

    def column_info(self):
        """

        :return:
        """
        type_mapping ={}
        ent_object = self.object_from_entity_name()
        cols = ent_object.columns.values()
        for c in cols:
            type_mapping[c.name] = c.TYPE_INFO
        return type_mapping

    def attribute_formatter(self, entity, key, var):
        """

        :return:
        """
        col_type = self.column_info().get(key)
        if col_type == 'LOOKUP':
            col_prop = entity.columns[key]
            if not len(var) > 3:
                return entity_attr_to_id(col_prop.parent, "code", var)
            else:
                return lookup_id_from_value(col_prop.parent, var)
        else:
            return var

    def cleanup(self):
        """

        :return:
        """
        self.model = None
        self.entity = None
        self.attribs = None











