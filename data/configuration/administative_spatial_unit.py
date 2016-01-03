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

from .entity import Entity
from .columns import (
    VarCharColumn
)

LOGGER = logging.getLogger('stdm')


class AdministrativeSpatialUnit(Entity):
    """
    Hierarchy of administrative spatial units.
    """
    TYPE_INFO = 'ADMINISTRATIVE_SPATIAL_UNIT'

    def __init__(self, profile):
        Entity.__init__(self, 'admin_spatial_unit_set', profile,
                        is_global=True, is_proxy=True)

        self.name = VarCharColumn('name', self)
        self.code = VarCharColumn('code', self)

        LOGGER.debug('%s Administrative Spatial Unit set initialized.', self.name)