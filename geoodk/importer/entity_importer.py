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
from stdm.data.configuration.columns import GeometryColumn
from stdm.data.configuration.entity import (
    Entity
)
GEOMPARAM = 0

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
        self.key_watch = 0

    def set_instance_document(self, file_p):
        """

        :return:
        """
        file_path = QFile(file_p)
        if file_path.open(QIODevice.ReadOnly):
            self.instance_doc.setContent(file_path)

    def geomsetter(self, val):
        """
        Get user input on geometry
        :param val:
        :return:
        """
        global GEOMPARAM
        GEOMPARAM = val
        return GEOMPARAM

    def geom(self):
        """
        Return the geometry value
        :return:
        """
        return GEOMPARAM

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
                attributes[node_val.nodeName()] = node_val.text().rstrip()
        return attributes

    def instance_group_identity(self):
        """
        Get the unique identifier for the current instance
        :return:
        """
        pass

    def process_import_to_db(self, entity,ids):
        """
        Save the object data to the database
        :return:
        """
        success = False
        if self.instance_doc is not None:
            attributes = self.entity_attributes_from_instance(entity)
            entity_add = Save2DB(entity, attributes,ids)
            entity_add.save_to_db()
            entity_add.get_srid(GEOMPARAM)
            self.key_watch = entity_add.key
            success = True
        return success

    def process_parent_entity_import(self, entity):
        """

        :param entity:
        :return:
        """
        if self.instance_doc is not None:
            attributes = self.entity_attributes_from_instance(entity)
            entity_add = Save2DB(entity, attributes)
            entity_add.get_srid(GEOMPARAM)
            ref_id = entity_add.save_parent_to_db()
        return ref_id


class Save2DB:
    """
    Class to insert entity data into db
    """
    def __init__(self, entity, attributes, ids=None):
        """
        Initialize class and class variable
        """
        self.attributes = attributes
        self.form_entity = entity
        self.entity = self.object_from_entity_name(self.form_entity)
        self.model = self.dbmodel_from_entity()
        self.key = 0
        self.parents_ids = ids
        self.geom = 4326

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
        entity_object = entity_model(self.entity)
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
                col_type = self.column_info().get(k)
                col_prop = self.entity.columns[k]
                var = self.attribute_formatter(col_type, col_prop, v)
                setattr(self.model, k, var)
        self.model.save()
        self.cleanup()


    def save_parent_to_db(self):
        """
        Format object attribute data from entity
        attribute
        :return:
        """
        for k, v in self.attributes.iteritems():
            if hasattr(self.model, k):
                col_type = self.column_info().get(k)
                col_prop = self.entity.columns[k]
                var = self.attribute_formatter(col_type, col_prop, v)
                setattr(self.model, k, var)
        self.model.save()
        self.key = self.model.id
        return self.key

    def column_info(self):
        """

        :return:
        """
        type_mapping ={}
        cols = self.entity.columns.values()
        for c in cols:
            type_mapping[c.name] = c.TYPE_INFO
        return type_mapping

    def cleanup(self):
        """

        :return:
        z"""
        self.model = None
        self.entity = None
        self.attributes = None

    def get_srid(self, srid):
        """
        Let the user specify the coordinate system during data import
        :param srid:
        :return:
        """
        self.geom = srid
        return self.geom

    def attribute_formatter(self, col_type, col_prop, var):
        """

        :return:
        """
        if col_type == 'LOOKUP':
            if not len(var) > 3 and var != 'Yes' and var != 'No':
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
            defualt_srid = 0
            geom_provider = GeomPolgyon(var)
            if isinstance(col_prop, GeometryColumn):
               defualt_srid = col_prop.srid
            if defualt_srid != 0:
                geom_provider.set_user_srid(defualt_srid)
            else:
                geom_provider.set_user_srid(GEOMPARAM)
            return geom_provider.polygon_to_Wkt()
        elif col_type == 'FOREIGN_KEY':
            if len(self.parents_ids) < 0:
                return
            else:
                for val in self.parents_ids.values():
                    if col_prop.parent.name == val[1]:
                        return val[0]
        else:
            return var

