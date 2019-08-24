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
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from stdm.ui.flts.workflow_manager.config import SchemeConfig
from stdm.data.configuration import entity_model


class SchemeDataService:
    """
    Scheme data model services
    """
    def __init__(self, current_profile):
        self._profile = current_profile
        self.entity_name = "Scheme"

    @property
    def field_option(self):
        """
        Scheme field option
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
        for fk in self._entity_model().__table__.foreign_keys:
            entity_name.append(fk.column.table.name)
        return entity_name

    def run_query(self):
        """
        Run query on an entity
        :return query_object: Query results
        :rtype query_object: Query
        """
        model = self._entity_model()
        entity_object = model()
        try:
            query_object = entity_object.queryObject(). \
                options(joinedload(model.cb_check_lht_land_rights_office)). \
                options(joinedload(model.cb_check_lht_region)). \
                options(joinedload(model.cb_check_lht_relevant_authority)). \
                options(joinedload(model.cb_cdrs_title_deed)).order_by(model.date_of_approval)
            return query_object
        except (exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_model(self):
        """
`       Scheme entity model
        :return model: Scheme entity model;
        :rtype model: DeclarativeMeta
        """
        try:
            entity = self._profile.entity(self.entity_name)
            model = entity_model(entity)
            return model
        except AttributeError as e:
            raise e