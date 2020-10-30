"""
/***************************************************************************
Name                 : AdministrativeSpatialUnit
Description          : A proxy container for the already created
                       AdminSpatialUnitSet table.
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

from stdm.data.configuration.columns import (
    ForeignKeyColumn,
    VarCharColumn
)
from stdm.data.configuration.entity import Entity

LOGGER = logging.getLogger('stdm')


class AdministrativeSpatialUnit(Entity):
    """
    Hierarchy of administrative spatial units.
    """
    TYPE_INFO = 'ADMINISTRATIVE_SPATIAL_UNIT'

    def __init__(self, profile):
        Entity.__init__(self, 'admin_spatial_unit_set', profile,
                        is_global=True, is_proxy=True, supports_documents=False)

        self.user_editable = False

        self.admin_unit_name = VarCharColumn('name', self, maximum=70)
        self.admin_unit_code = VarCharColumn('code', self, maximum=10)

        self.admin_parent_id = ForeignKeyColumn('parent_id', self)
        self.admin_parent_id.set_entity_relation_attr('parent', self)
        self.admin_parent_id.set_entity_relation_attr('parent_column', 'id')

        LOGGER.debug('%s Administrative Spatial Unit set initialized.', self.name)

        # Add columns
        self.add_column(self.admin_unit_name)
        self.add_column(self.admin_unit_code)
        self.add_column(self.admin_parent_id)
