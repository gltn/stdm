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
from stdm.utils.util import entity_attr_to_id, entity_attr_to_model
from stdm.data.configuration import entity_model
from stdm.geoodk.importer.geometry_provider import STDMGeometry
from stdm.data.configuration.columns import GeometryColumn
from stdm.ui.sourcedocument import SourceDocumentManager
from PyQt4.QtCore import \
    (
    QUuid,
    QDateTime,
    QDir
)

from PyQt4.QtGui import QVBoxLayout

GEOMPARAM = 0
GROUPCODE = 0
HOME = QDir.home().path()

CONFIG_FILE = HOME + '/.stdm/geoodk/instances'

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
        :param file_p: str
        :return: file
        :rtype QFile
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
                attributes[node_val.nodeName()] = node_val.text().rstrip()
        return attributes

    def social_tenure_definition_captured(self):
        """
        Let find find out if str is defined for the particular data collection
        file instance. if exist, bool the result
        :return:
        """
        has_str_defined = False
        try:
            attributes = self.entity_attributes_from_instance('social_tenure')
            if attributes is not None or len(attributes) > 0:
                has_str_defined = True
        except:
            pass
        return has_str_defined

    def process_social_tenure(self, attributes, ids):
        """
        Save social tenure entity. It has to be saved separately
        because its need to be saved last and its handled differently
        :return:
        """
        if attributes and ids:
            entity_add = Save2DB('social_tenure', attributes, ids)
            entity_add.objects_from_supporting_doc(self.instance)
            entity_add.save_to_db()

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
        self.doc_model = None
        self._doc_manager =None
        self.entity = self.object_from_entity_name(self.form_entity)
        self.model = self.dbmodel_from_entity()
        self.key = 0
        self.parents_ids = ids
        self.geom = 4326

    def object_from_entity_name(self, entity):
        """

        :return:
        """
        if entity == 'social_tenure':
            return current_profile().social_tenure
        else:
            user_entity = current_profile().entity_by_name(entity)
            return user_entity

    def entity_has_supporting_docs(self):
        """
        Check if the entity has supporting document before importing
        :return: Bool
        """
        if self.entity.supports_documents:
            return self.entity.supports_documents
        else:
            return None

    def entity_supported_document_types(self):
        """
        Get the supported document types before importing so that they are captured
        during import process
        :return: List
        """
        return self.entity.document_types_non_hex()

    def dbmodel_from_entity(self):
        """
        Format model attributes from passed entity attributes
        :return:
        """
        if self.entity_has_supporting_docs():
            entity_object, self.doc_model = entity_model(self.entity, with_supporting_document=True)
            entity_object_model = entity_object()
            if hasattr(entity_object_model, 'documents'):
                if self.entity.TYPE_INFO == 'SOCIAL_TENURE':
                    obj_doc_col = current_profile().social_tenure.supporting_doc
                else:
                    obj_doc_col = self.entity.supporting_doc

                self._doc_manager = SourceDocumentManager(
                        obj_doc_col, self.doc_model
                    )
        else:
            entity_object = entity_model(self.entity)
            entity_object_model = entity_object()
        return entity_object_model

    def objects_from_supporting_doc(self, instance_file = None):
        """
        Create supporting doc path  instances based on the collected documents
        :return:paths
        :rtype: document object instance
        """
        if instance_file:
            f_dir, file_name = os.path.split(instance_file)
            for document, val in self.attributes.iteritems():
                if str(document).endswith('supporting_document'):
                    if val != '':
                        doc = self.format_document_name_from_attribute(document)
                        doc_path = os.path.normpath(f_dir+'/'+val)
                        abs_path = doc_path.replace('\\','/').strip()
                        if QFile.exists(abs_path):
                            self.supporting_document_model(abs_path, doc)

    def supporting_document_model(self,doc_path,doc):
        """
        :param doc_path: absolute document path
        :param doc: document name
        :type: str
        Construct supporting document model instance to add into the db
        :return:
        """
        # Create document container
        doc_container = QVBoxLayout()
        supporting_doc_entity = self.entity.supporting_doc.document_type_entity
        document_type_id = entity_attr_to_id(supporting_doc_entity, 'value', doc, lower=False)
        # Register container
        self._doc_manager.registerContainer(
            doc_container,
            document_type_id
        )
        #Copy the document to STDM working directory
        self._doc_manager.insertDocumentFromFile(
                doc_path,
                document_type_id,
                self.entity
        )

    def format_document_name_from_attribute(self, doc):
        """
        Get the type of document from attribute name
        So that supporting document class instance can save it in the right format
        :return:
        """
        formatted_doc_list = self.entity_supported_document_types()
        default = 'General'
        doc_type = str(doc).split('_',1)
        if doc_type[0].startswith('supporting') and formatted_doc_list[0] == default:
            return default
        elif doc_type[0].startswith('supporting') and formatted_doc_list[0] != default:
            return formatted_doc_list[0]
        elif not doc_type[0].startswith('supporting'):
            actual_doc_name = doc_type[0].replace('-', ' ')
            for doc_name in formatted_doc_list:
                if actual_doc_name in doc_name or doc_name.startswith(actual_doc_name):
                    return doc_name
            else:
                return formatted_doc_list[0]
        else:
            return formatted_doc_list[0]

    def save_to_db(self):
        """
        Format object attribute data from entity and save them into database
        :return:
        """
        if self.entity.short_name == 'social_tenure_relationship':

            prefix = current_profile().prefix+'_'
            if hasattr(self.attributes, 'party'):
                full_party_ref_column = self.attributes.get('party')
                party_ref_column = full_party_ref_column+ '_id'

                setattr(self.model, party_ref_column, self.parents_ids.get(prefix+full_party_ref_column)[0])

                self.attributes.pop('party')
            if hasattr(self.attributes, 'spatial_unit'):
                full_spatial_ref_column = self.attributes.get('spatial_unit')
                spatial_ref_column = full_spatial_ref_column+ '_id'
                setattr(self.model, spatial_ref_column, self.parents_ids.get(prefix+full_spatial_ref_column)[0])
                self.attributes.pop('spatial_unit')
        for k, v in self.attributes.iteritems():
            if hasattr(self.model, k):
                col_type = self.column_info().get(k)
                col_prop = self.entity.columns[k]
                var = self.attribute_formatter(col_type, col_prop, v)
                setattr(self.model, k, var)
        if self.entity_has_supporting_docs():
            self.model.documents = self._doc_manager.model_objects()
        self.model.save()
        return self.model.id
        #self.cleanup()

    def save_parent_to_db(self):
        """
        Format object attribute data from entity and save them into database
        attribute
        :return:
        """
        for k, v in self.attributes.iteritems():
            if hasattr(self.model, k):
                col_type = self.column_info().get(k)
                col_prop = self.entity.columns[k]
                var = self.attribute_formatter(col_type, col_prop, v)
                setattr(self.model, k, var)
        if self.entity_has_supporting_docs():
            self.model.documents = self._doc_manager.model_objects()
        self.model.save()
        self.key = self.model.id
        return self.key

    def save_foreign_key_table(self):
        """
        Get the table with foreign keys only
        :return:
        """
        for col, type_info in self.column_info().iteritems():
            col_prop = self.entity.columns[col]
            var = self.attribute_formatter(type_info, col_prop, None)
            setattr(self.model, col, var)
        self.model.save()
        self.cleanup()

    def column_info(self):
        """

        :return:
        """
        type_mapping = {}
        cols = self.entity.columns.values()
        for c in cols:
            type_mapping[c.name] = c.TYPE_INFO
        return type_mapping

    def get_srid(self, srid):
        """
        Let the user specify the coordinate system during data import
        :param srid:
        :return:
        """
        self.geom = srid
        return self.geom

    def id_from_model_object(self, obj):
        """
        We need to obtian id from object instance
        :param obj:
        :return:
        """
        return obj.id

    def attribute_formatter(self, col_type, col_prop, var=None):
        """
        Format geoodk attributes collected in the field
        to conform to STDM database contrains
        :return:
        """
        if col_type == 'BOOL':
            if len(var) < 1:
                return None
            if len(var)>1:
                if var == '' or var is None:
                    return None
                if var == 'Yes' or var == True:
                    return True
                if var == 'No' or var == False:
                    return False
            else:
                return None

        if col_type == 'LOOKUP':
            if len(var) < 1 or var is None:
                return None
            if len(var) <4:
                if var == 'Yes' or var == 'No':
                    return entity_attr_to_model(col_prop.parent, 'value', var).id
                if var != 'Yes' and var != 'No':
                    lk_code = entity_attr_to_id(col_prop.parent, "code", var)
                    if not str(lk_code).isdigit():
                        return None
                    else:
                        return lk_code

            if len(var) > 3:
                if not str(entity_attr_to_id(col_prop.parent, 'code', var)).isdigit():
                    id_value = entity_attr_to_model(col_prop.parent, 'value', var)
                    if id_value is not None:
                        return id_value.id
                    #return entity_attr_to_model(col_prop.parent, 'value', var).id
                else:
                    lk_code = entity_attr_to_id(col_prop.parent, "code", var)
                    if not str(lk_code).isdigit():
                        return None
                    else:
                        return lk_code
            else:
                return None
        elif col_type == 'ADMIN_SPATIAL_UNIT':
            var_code = None
            if len(var) < 1 or var is None:
                return None
            elif not len(var) > 3:
                var_code = entity_attr_to_id(col_prop.parent, "code", var)
                if var_code is not None:
                    return var_code
                elif entity_attr_to_id(col_prop.parent, "name", var) is not None:
                    return entity_attr_to_id(col_prop.parent, "name", var)
                else:
                    return None

            else:
                if entity_attr_to_id(col_prop.parent, "name", var) is None:
                    var_code = entity_attr_to_id(col_prop.parent, "code", var)
                    if not var_code:
                        return None

        elif col_type == 'MULTIPLE_SELECT':
            print 'multiple select {}'.format(var)
            if var == '' or var is None:
                return None
            else:
                print var
                col_parent = col_prop.association.first_parent
                lk_val_list = col_parent.values.values()
                choices_list = []
                for code in lk_val_list:
                    choices_list.append(entity_attr_to_id(
                        col_parent.association.first_parent, 'value', code.value))
                print choices_list

                if len(choices_list) > 1:
                    return choices_list
                else:
                    return None

        elif col_type == 'GEOMETRY':
            defualt_srid = 0
            if var:
                geom_provider = STDMGeometry(var)
                if isinstance(col_prop, GeometryColumn):
                    defualt_srid = col_prop.srid
                if defualt_srid != 0:
                    geom_provider.set_user_srid(defualt_srid)
                else:
                    geom_provider.set_user_srid(GEOMPARAM)
                if col_prop.geometry_type() == 'POINT':
                    return geom_provider.point_to_Wkt()
                if col_prop.geometry_type() == 'POLYGON':
                    return geom_provider.polygon_to_Wkt()
            else:
                return None
        elif col_type == 'FOREIGN_KEY':
            if self.parents_ids is None or len(self.parents_ids) < 0:
                return None
            else:
                for code, val in self.parents_ids.iteritems():
                    if col_prop.parent.name == code:
                        return val[0]
                    else:
                        return None
        elif col_type == 'INT' or col_type == 'DOUBLE' or col_type == 'PERCENT':
            if var == '':
                return None
            else:
                return var

        elif col_type == 'DATETIME' or col_type == 'DATE':
            if var is None:
                return None
            if var == '':
                return None
            else:
                return var

        else:
            return var

    def cleanup(self):
        """
        Reset all the model and entity data before we process
        the next entity data
        :return: None
        z"""
        self.model = None
        self.entity = None
        self.attributes = None
        self._doc_manager = None


