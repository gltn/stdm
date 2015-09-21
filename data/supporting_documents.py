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
from PyQt4.QtCore import (
    QRegExp
)

from .database import SupportingDocument
from .pg_utils import foreign_key_parent_tables
from .table_mapper import DeclareMapping

SUPPORTING_DOC_BASE = "supporting_document"
SUPPORTING_DOC_TAGS = ["doc", "document", "photo", "str_relations"]

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

def document_models(doc_link_table, link_column, link_value):
    """
    Create supporting document models using information from the linked
    document table.
    :param doc_link_table: Name of the linked supporting document table.
    :type doc_link_table: str
    :param link_column: Name of the column linked to the primary
    entity table.
    :type link_column: str
    :param link_value: Value of the linked column which is used to retrieve
    the corresponding values of the supporting document primary keys.
    :type link_value: int
    :return: Instances of supporting document models corresponding to the
    specified record in the document linked table.
    :rtype: list
    """
    link_table_model = DeclareMapping.instance().tableMapping(doc_link_table)
    if link_table_model is None:
        return []

    if not hasattr(link_table_model, link_column):
        return []

    #Get the name of the supporting document foreign key column
    linked_tables = foreign_key_parent_tables(doc_link_table)
    supporting_doc_ref = [lt[0] for lt in linked_tables if lt[1] == SUPPORTING_DOC_BASE]

    #No link found to supporting document table
    if len(supporting_doc_ref) == 0:
        return []

    supporting_doc_col = supporting_doc_ref[0]
    linked_table_obj_col = getattr(link_table_model, link_column)

    link_table_instance = link_table_model()
    link_table_query_obj = link_table_instance.queryObject()

    linked_table_models = link_table_query_obj.filter(linked_table_obj_col == link_value).all()

    supporting_doc_instance = SupportingDocument()
    sdi_query_obj = supporting_doc_instance.queryObject()

    doc_models = []

    for ltm in linked_table_models:
        supporting_doc_id = getattr(ltm, supporting_doc_col)
        supporting_doc_model = sdi_query_obj.filter(SupportingDocument.id == supporting_doc_id).first()
        if not supporting_doc_model is None:
            doc_models.append(supporting_doc_model)

    return doc_models



