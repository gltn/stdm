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
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement
)

from stdm.composer.configuration_collection_base import (
    ConfigurationCollectionBase,
    LinkedTableItemConfiguration
)

from stdm.composer.custom_items.photo import StdmPhotoLayoutItem


class PhotoConfiguration(LinkedTableItemConfiguration):
    tag_name = "Source"

    def __init__(self, document_type=None, document_type_id=None, layout_item=None, **kwargs):
        self.document_type = document_type or ''
        self.document_type_id = document_type_id or -1
        self._layout_item = layout_item or None
        LinkedTableItemConfiguration.__init__(self, **kwargs)

        print('PhotoConfig::C')

    def to_dom_element(self, dom_document: QDomDocument):
        """
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :return: A XML DOM element that contains the photo configuration
        settings.
        :rtype: QDomElement
        """
        ph_element = dom_document.createElement(self.tag_name)
        ph_element.setAttribute('documentType', self.document_type)
        ph_element.setAttribute('documentTypeId', str(self.document_type_id))
        self.write_to_dom_element(ph_element)

        return ph_element

    def layout_item(self):
        return self._layout_item

    # @staticmethod
    # def createXX(dom_element: QDomElement):
    #     """
    #     Create a PhotoConfiguration object from a QDomElement instance.
    #     :param dom_element: QDomDocument that represents composer configuration.
    #     :type dom_element: QDomElement
    #     :return: PhotoConfiguration instance whose properties have been
    #     extracted from the composer document instance.
    #     :rtype: PhotoConfiguration
    #     """
    #     linked_table_props = PhotoConfiguration.linked_table_properties(dom_element)

    #     item_id = dom_element.attribute("itemid")
    #     ph_table = linked_table_props.linked_table
    #     source_col = linked_table_props.source_field
    #     ref_col = linked_table_props.linked_field
    #     document_type = dom_element.attribute('documentType', '')
    #     document_type_id = dom_element.attribute('documentTypeId', '-1')


    #     return PhotoConfiguration(
    #         linked_table=ph_table,
    #         source_field=source_col,
    #         linked_field=ref_col,
    #         item_id=item_id,
    #         document_type=document_type,
    #         document_type_id=document_type_id
    #     )

    @staticmethod
    def create(stdm_photo_item: StdmPhotoLayoutItem):

        return PhotoConfiguration(
            linked_table=stdm_photo_item.linked_table,
            source_field=stdm_photo_item.source_field,
            linked_field=stdm_photo_item.linked_field,
            layout_item=stdm_photo_item,
            item_id=stdm_photo_item.uuid(),
            document_type=stdm_photo_item.document_type,
            document_type_id=stdm_photo_item.document_type_id
        )


class PhotoConfigurationCollection(ConfigurationCollectionBase):
    """
    Class for managing multiple instances of PhotoConfiguration objects.
    """
    from stdm.ui.composer.photo_data_source import ComposerPhotoDataSourceEditor

    collection_root = "Photos"
    editor_type = ComposerPhotoDataSourceEditor
    config_root = PhotoConfiguration.tag_name
    item_config = PhotoConfiguration
    layout_item_type = StdmPhotoLayoutItem
