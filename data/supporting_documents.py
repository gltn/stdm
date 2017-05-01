"""
/***************************************************************************
Name                 : Supporting Documents
Description          : Module for retrieving supporting documents.
Date                 : 15/September/2014
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
from collections import defaultdict
from collections import OrderedDict
from PyQt4.QtCore import (
    QRegExp
)
from stdm.settings import current_profile
from stdm.data.configuration import entity_model
from .pg_utils import foreign_key_parent_tables

SUPPORTING_DOC_TAGS = ["supporting_document"]

def supporting_doc_tables_regexp():
    """
    :return: Returns an instance of a Regex class for filtering supporting
    documents tables in the database.
    :rtype: QRegExp
    """
    doc_tables_filter = "|".join(SUPPORTING_DOC_TAGS)
    return QRegExp(doc_tables_filter)

def supporting_doc_tables(ref_table):
    """
    Get the list of tables containing information on supporting documents
    related to the specified table.
    :param ref_table: Table name whose entity enables supporting documents to
    be attached.
    :type ref_table: str
    :return: A list containing table names and corresponding foreign key
    reference information on supporting documents related to the reference
    table.
    :rtype: list
    """
    doc_regexp = supporting_doc_tables_regexp()

    return  foreign_key_parent_tables(ref_table, False, doc_regexp)


def document_models(entity, link_column, link_value):
    """
    Create supporting document models using information from the linked
    document table.
    :param entity: The entity in which the supporting document are uploaded.
    :type entity: Class
    :param link_column: Name of the column linking the
    source document tables to the primary entity table.
    :type link_column: str
    :param link_value: Value of the linked column which is used to retrieve
    the corresponding values of the supporting document primary keys.
    :type link_value: int
    :return: Instances of supporting document models corresponding to the
    specified record in the document linked table grouped by document type.
    :rtype: list
    """
    _str_model, _doc_model = entity_model(
        entity, False, True
    )

    if _doc_model is None:
        return []

    if not hasattr(_doc_model, link_column):
        return []

    _doc_obj = _doc_model()
    # get the column object for column entity id
    # in entity supporting_document table.
    entity_doc_col_obj = getattr(_doc_model, link_column)
    result = _doc_obj.queryObject().filter(
        entity_doc_col_obj == link_value
    ).all()

    doc_objs = defaultdict(list)

    for doc_obj in result:
        doc_objs[doc_obj.document_type].append(doc_obj)

    doc_objs = OrderedDict(doc_objs)
    return doc_objs
