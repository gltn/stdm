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
from stdm.ui.flts.workflow_manager.config import (
    DocumentConfig,
    HolderConfig,
    FilterQueryBy,
    SchemeConfig,
)
from stdm.data.configuration import entity_model


class DataService:
    """
    Data service abstract class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def columns(self):
        """
        Scheme columns options
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
    def __init__(self, current_profile, widget_obj_name, parent):
        self._profile = current_profile
        self.entity_name = "Scheme"
        self._parent = parent
        self._widget_obj_name = widget_obj_name

    @property
    def columns(self):
        """
        Scheme table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return SchemeConfig().columns

    @property
    def lookups(self):
        """
        Scheme table view lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return SchemeConfig(self._parent).lookups

    @property
    def update_columns(self):
        """
        Scheme table view update column options
        :return: Update column options
        :rtype: List
        """
        return SchemeConfig().scheme_update_columns

    def related_entity_name(self):
        """
        Related entity name
        :return entity_name: Related entity name
        :rtype entity_name: List
        """
        fk_entity_name = []
        collection_name = []
        model = self._entity_model(self.entity_name)
        for relation in model.__mapper__.relationships.keys():
            if relation.endswith("_collection"):
                collection_name.append(relation)
            else:
                fk_entity_name.append(relation)
        return fk_entity_name, collection_name

    def run_query(self):
        """
        Run query on an entity
        :return query_obj: Query results
        :rtype query_obj: List
        """
        workflow_id = self.get_workflow_id(self._widget_obj_name)
        scheme_workflow_model = self._entity_model("Scheme_workflow")
        model = self._entity_model(self.entity_name)
        entity_object = model()
        try:
            query_object = entity_object.queryObject(). \
                options(joinedload(model.cb_check_lht_land_rights_office)). \
                options(joinedload(model.cb_check_lht_region)). \
                options(joinedload(model.cb_check_lht_relevant_authority)). \
                options(joinedload(model.cb_cdrs_title_deed)).\
                filter(
                    scheme_workflow_model.scheme_id == model.id,
                    scheme_workflow_model.workflow_id == workflow_id
                )
            return query_object.all()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def get_workflow_id(self, attr):
        """
        Return workflow id/primary key
        :param attr: Workflow lookup attribute
        :return workflow_id: Workflow id/primary key
        :rtype workflow_id: Integer
        """
        workflow_id = getattr(self.lookups, attr, None)
        if workflow_id:
            workflow_id = workflow_id()
        return workflow_id

    def filter_in(self, entity_name, filters):
        """
        Return query objects as a collection of filter using in_ operator
        :param entity_name: Name of entity to be queried
        :type entity_name: String
        :param filters: Query filter columns and values
        :type filters: Dictionary
        :return: Query object results
        :rtype: Query
        """
        model = self._entity_model(entity_name)
        entity_object = model()
        filters = [
            getattr(model, key).in_(value) for key, value in filters.iteritems()
        ]
        return entity_object.queryObject().filter(*filters)

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

    @staticmethod
    def filter_query_by(entity_name, filters):
        """
        Filters query result by a column value
        :param entity_name: Entity name
        :type entity_name: String
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            filter_by = FilterQueryBy()
            return filter_by(entity_name, filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def workflow_ids(self):
        """
        Returns workflow IDs
        :return workflow_ids: Workflow record ID
        :rtype workflow_ids: List
        """
        workflow_ids = [
            self.lookups.schemeLodgement(),
            self.lookups.schemeEstablishment(),
            self.lookups.firstExamination(),
            self.lookups.secondExamination(),
            self.lookups.thirdExamination()
        ]
        return workflow_ids


class DocumentDataService(DataService):
    """
    Scheme supporting documents data model service
    """
    def __init__(self, current_profile, scheme_id):
        self._profile = current_profile
        self._scheme_id = scheme_id
        self.entity_name = "supporting_document"

    @property
    def columns(self):
        """
        Scheme supporting documents
        table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return DocumentConfig().columns

    def related_entity_name(self):
        """
        Related entity name
        :return entity_name: Related entity name
        :rtype entity_name: List
        """
        fk_entity_name = []
        collection_name = []
        model, sp_doc_model = self._entity_model(self.entity_name)
        for relation in model.__mapper__.relationships.keys():
            if relation.endswith("_collection"):
                collection_name.append(relation)
            else:
                fk_entity_name.append(relation)
        return fk_entity_name, collection_name

    def run_query(self):
        """
        Run query on an entity
        :return query_obj: Query results
        :rtype query_obj: List
        """
        model, sp_doc_model = self._entity_model(self.entity_name)
        scheme_model, sc_doc_model = self._entity_model("Scheme")
        entity_object = model()
        try:
            query_object = entity_object.queryObject().filter(
                sc_doc_model.supporting_doc_id == model.id,
                sc_doc_model.scheme_id == self._scheme_id
            ).order_by(model.last_modified).all()
            return query_object
        except (exc.SQLAlchemyError, Exception) as e:
            raise e

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


# class HolderDataService(DataService):
#     """
#     Scheme holders data model service
#     """
#     def __init__(self, current_profile, scheme_id):
#         self._profile = current_profile
#         self._scheme_id = scheme_id
#         self.entity_name = "Holder"
#
#     @property
#     def columns(self):
#         """
#         Scheme holder table view columns options
#         :return: Table view columns and query columns options
#         :rtype: List
#         """
#         return HolderConfig().columns
#
#     def related_entity_name(self):
#         """
#         Related entity name
#         :return entity_name: Related entity name
#         :rtype entity_name: List
#         """
#         fk_entity_name = []
#         collection_name = []
#         model, sp_doc_model = self._entity_model(self.entity_name)
#         for relation in model.__mapper__.relationships.keys():
#             if relation.endswith("_collection"):
#                 collection_name.append(relation)
#             else:
#                 fk_entity_name.append(relation)
#         return fk_entity_name, collection_name
#
#     def run_query(self):
#         """
#         Run query on an entity
#         :return query_obj: Query results
#         :rtype query_obj: List
#         """
#         scheme_holder_model = self._entity_model("Scheme_holder")
#         model = self._entity_model(self.entity_name)
#         entity_object = model()
#         try:
#             query_object = entity_object.queryObject(). \
#                 options(joinedload(model.cb_check_lht_gender)). \
#                 options(joinedload(model.cb_check_lht_marital_status)). \
#                 options(joinedload(model.cb_check_lht_disability)). \
#                 options(joinedload(model.cb_check_lht_income_level)). \
#                 options(joinedload(model.cb_check_lht_occupation)). \
#                 filter(
#                     scheme_holder_model.holder_id == model.id,
#                     scheme_holder_model.scheme_id == self._scheme_id
#                 )
#             return query_object.all()
#         except (AttributeError, exc.SQLAlchemyError, Exception) as e:
#             raise e
#
#     def _entity_model(self, name=None):
#         """
#         Gets entity model
#         :param name: Name of the entity
#         :type name: String
#         :return model: Entity model;
#         :rtype model: DeclarativeMeta
#         """
#         try:
#             entity = self._profile.entity(name)
#             model = entity_model(entity)
#             return model
#         except AttributeError as e:
#             raise e
