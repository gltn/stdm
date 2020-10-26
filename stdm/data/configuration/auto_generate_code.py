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

from stdm.data.configuration.entity import Entity
from stdm.data.configuration.columns import VarCharColumn

LOGGER = logging.getLogger('stdm')


class AutoGenerateCode(Entity):
    """
    Hierarchy of administrative spatial units.
    """
    TYPE_INFO = 'AUTO_GENERATE_CODE'

    def __init__(self, profile):
        Entity.__init__(self, 'auto_generate_code', profile,
                    is_global=False, is_proxy=False, supports_documents=False)

        self.user_editable = False

        self.auto_generate_code_name = VarCharColumn('code', self, maximum=50)

        LOGGER.debug('%s Auto Generate Code entity initialized.', self.name)

        # Add columns
        self.add_column(self.auto_generate_code_name)
