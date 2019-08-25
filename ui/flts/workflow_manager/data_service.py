"""
/***************************************************************************
Name                 : Data Service
Description          : Data service package that handles data provision for
                       workflow manager modules; Scheme Establishment and
                       First, Second and Third Examination FLTS modules.
Date                 : 22/August/2019
copyright            : (C) 2019
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
from abc import ABCMeta, abstractmethod
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from stdm.ui.flts.workflow_manager.config import(
    SchemeConfig,
    DocumentConfig,
)
from stdm.data.configuration import entity_model


class DataService:
    """
    Data service abstract class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def field_option(self):
        """
        Scheme field options
        """
        raise NotImplementedError

    def related_entity_name(self):
        """
        Related entity name
        """
        raise NotImplementedError

    def run_query(self):
        """
        Run query on an entity
        :return:
        """
        raise NotImplementedError

    def _entity_model(self, name=None):
        """
        Scheme entity model
        :return:
        """
        raise NotImplementedError


class SchemeDataService(DataService):
    """
    Scheme data model service
    """
    def __init__(self, current_profile):
        self._profile = current_profile
        self.entity_name = "Scheme"

    @property
    def field_option(self):
        """
        Scheme table view field option
        :return: Column and query field options
        :rtype: List
        """
        return SchemeConfig().field_option

    def related_entity_name(self):
        """
        Related entity name
        :return entity_name: Related entity name
        :rtype entity_name: List
        """
        entity_name = []
        for fk in self._entity_model(self.entity_name).__table__.foreign_keys:
            entity_name.append(fk.column.table.name)
        if not entity_name:
            entity_name = entity_name.append(self.entity_name)
        return entity_name

    def run_query(self):
        """
        Run query on an entity
        :return query_object: Query results
        :rtype query_object: List
        """
        model = self._entity_model(self.entity_name)
        entity_object = model()
        try:
            query_object = entity_object.queryObject(). \
                options(joinedload(model.cb_check_lht_land_rights_office)). \
                options(joinedload(model.cb_check_lht_region)). \
                options(joinedload(model.cb_check_lht_relevant_authority)). \
                options(joinedload(model.cb_cdrs_title_deed)).order_by(model.date_of_approval)
            return query_object.all()
        except (exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_model(self, name=None):
        """
        Gets entity model
        :param name: Name of the entity
        :type name: String
        :return model: Entity model;
        :rtype model: DeclarativeMeta
        """
        try:
            entity = self._profile.entity(name)
            model = entity_model(entity)
            return model
        except AttributeError as e:
            raise e


class DocumentDataService(DataService):
    """
    Scheme supporting documents data model service
    """
    def __init__(self, current_profile, scheme_id):
        self._profile = current_profile
        self._scheme_id = scheme_id
        self.entity_name = "supporting_document"

    @property
    def field_option(self):
        """
        Scheme supporting documents
        table view field option
        :return: Column and query field options
        :rtype: List
        """
        return DocumentConfig().field_option

    def related_entity_name(self):
        """
        Related entity name
        :return entity_name: Related entity name
        :rtype entity_name: List
        """
        entity_name = []
        model, sp_doc_model = self._entity_model(self.entity_name)
        for fk in model.__table__.foreign_keys:
            entity_name.append(fk.column.table.name)
        if not entity_name:
            entity_name.append(self.entity_name)
        return entity_name

    def run_query(self):
        """
        Run query on an entity
        :return query_object: Query results
        :rtype query_object: List
        """
        model, sp_doc_model = self._entity_model(self.entity_name)
        scheme_model, sc_doc_model = self._entity_model("Scheme")
        entity_object = model()
        try:
            query_object = entity_object.queryObject().filter(
                sc_doc_model.supporting_doc_id == model.id,
                sc_doc_model.scheme_id == self._scheme_id
            ).order_by(model.last_modified).all()
            query_object = self._dot_dictify(query_object)
            return query_object
        except (exc.SQLAlchemyError, Exception) as e:
            raise e

    def _dot_dictify(self, query_object):
        """
        Convert key dictionary access to dot notation
        and implicitly add a magic method __dict__
        The __dict__ is used in converting query results
        to dict in the view model.
        :param query_object: Query results
        :type query_object: Query
        :return: Query results
        :rtype: List
        """
        results = []
        for row in query_object:
            record = row.__dict__
            document = row.cb_scheme_supporting_document_collection[0].\
                cb_check_scheme_document_type
            record["supporting_document"] = document
            record["data"] = row
            dot_dict = DotDictify()
            dot_dict.update(record)
            results.append(dot_dict)
        return results

    def _entity_model(self, name=None):
        """
        Gets entity and supporting document model
        :param name: Name of the entity
        :type name: String
        :return model: Entity model;
        :rtype model: DeclarativeMeta
        :return document_model: Supporting document entity model;
        :rtype document_model: DeclarativeMeta
        """
        try:
            entity = self._profile.entity(name)
            model, document_model = entity_model(
                entity, with_supporting_document=True
            )
            return model, document_model
        except AttributeError as e:
            raise e


class DotDictify(dict):
    """
    Convert key dictionary access to dot notation
    and implicitly add a magic method __dict__
    """
    def __init__(self, *args, **kwargs):
        super(DotDictify, self).__init__(*args, **kwargs)
        self.__dict__ = self
