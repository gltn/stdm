"""
/***************************************************************************
Name                 : SupportingDocument
Description          : Classes for enabling attachment of supporting documents.
Date                 : 28/December/2015
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

from stdm import (
    DateTimeColumn,
    IntegerColumn,
    VarCharColumn
)
from stdm import Entity

LOGGER = logging.getLogger('stdm')


class SupportingDocument(Entity):
    """
    Base class containing information on all documents that are appended to
    different entities within a given profile.
    """
    TYPE_INFO = 'SUPPORTING_DOCUMENT'

    def __init__(self, profile):
        Entity.__init__(self, 'supporting_document', profile, supports_documents=False)

        self.user_editable = False

        self.creation_date = DateTimeColumn('creation_date', self)
        self.document_identifier = VarCharColumn('document_identifier',
                                                 self, maximum=50)
        self.document_type = VarCharColumn('source_entity', self, maximum=150)
        self.document_size = IntegerColumn('document_size', self)
        self.filename = VarCharColumn('filename', self, maximum=200)

        LOGGER.debug('%s supporting document initialized.', self.name)

        # Add columns to the entity
        self.add_column(self.creation_date)
        self.add_column(self.document_identifier)
        self.add_column(self.document_type)
        self.add_column(self.document_size)
        self.add_column(self.filename)