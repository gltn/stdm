"""
/***************************************************************************
Name                 : PhotoConfiguration
Description          : Container for photo configuration options in the
                       database.
Date                 : 11/December/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from PyQt4.QtXml import (
    QDomDocument,
    QDomElement
)

from .configuration_collection_base import (
    ConfigurationCollectionBase,
    LinkedTableItemConfiguration
)

class PhotoConfiguration(LinkedTableItemConfiguration):
    tag_name = "Source"

    def to_dom_element(self, dom_document):
        """
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :return: A XML DOM element that contains the photo configuration
        settings.
        :rtype: QDomElement
        """
        ph_element = dom_document.createElement(self.tag_name)
        self.write_to_dom_element(ph_element)

        return ph_element

    @staticmethod
    def create(dom_element):
        """
        Create a PhotoConfiguration object from a QDomElement instance.
        :param dom_element: QDomDocument that represents composer configuration.
        :type dom_element: QDomElement
        :return: PhotoConfiguration instance whose properties have been
        extracted from the composer document instance.
        :rtype: PhotoConfiguration
        """
        linked_table_props = PhotoConfiguration.linked_table_properties(dom_element)

        item_id = dom_element.attribute("itemid")
        ph_table = linked_table_props.linked_table
        source_col = linked_table_props.source_field
        ref_col= linked_table_props.linked_field

        return PhotoConfiguration(linked_table=ph_table,
                                  source_field=source_col,
                                  linked_field=ref_col,
                                  item_id=item_id)

class PhotoConfigurationCollection(ConfigurationCollectionBase):
    """
    Class for managing multiple instances of PhotoConfiguration objects.
    """
    from stdm.ui.composer import ComposerPhotoDataSourceEditor

    collection_root = "Photos"
    editor_type = ComposerPhotoDataSourceEditor
    config_root = PhotoConfiguration.tag_name
    item_config = PhotoConfiguration
