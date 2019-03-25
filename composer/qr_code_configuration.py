"""
/***************************************************************************
Name                 : QRCodeConfiguration
Description          : Container for QR Code configuration options for the
                       document designer.
Date                 : 19/March/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
from PyQt4.QtCore import (
    QTemporaryFile
)

import pyqrcode

from stdm.utils.util import (
    is_ascii
)

from .configuration_collection_base import (
    ConfigurationCollectionBase,
    ItemConfigBase,
    ItemConfigValueHandler
)


class QRCodeConfiguration(ItemConfigBase):
    """Configuration item for specifying QRCode properties."""
    tag_name = "Code"

    def __init__(self, **kwargs):
        self._ds_field = kwargs.pop('data_source_field', '')
        super(QRCodeConfiguration, self).__init__(**kwargs)

    @property
    def data_source_field(self):
        """
        :return: Returns the name of the data source field whose value is
        used to generate the QR code.
        :rtype: str
        """
        return self._ds_field

    @data_source_field.setter
    def data_source_field(self, field):
        """
        Set the name of the data source field whose value will be used to
        generate the QR code.
        :param field: Name of the data source field.
        :type field: str
        """
        self._ds_field = field

    def to_dom_element(self, dom_document):
        """
        :param dom_document: Root composer element.
        :type dom_document: QDomDocument
        :return: A XML DOM element that contains the QR code configuration
        settings.
        :rtype: QDomElement
        """
        qrc_element = dom_document.createElement(self.tag_name)
        qrc_element.setAttribute("itemid", self._item_id)
        qrc_element.setAttribute('dataSourceField', self.data_source_field)

        return qrc_element

    def create_handler(self, composition, query_handler=None):
        """
        Override for returning object that will be responsible for creating
        the QR code.
        """
        return QRCodeConfigValueHandler(composition, self, query_handler)

    @staticmethod
    def create(dom_element):
        """
        Create a QRCodeConfiguration object from a QDomElement instance.
        :param dom_element: QDomDocument that represents composer configuration.
        :type dom_element: QDomElement
        :return: QRCodeConfiguration instance whose properties have been
        extracted from the composer document instance.
        :rtype: PhotoConfiguration
        """
        item_id = dom_element.attribute("itemid")
        ds_field = dom_element.attribute('dataSourceField')

        return QRCodeConfiguration(
            item_id=item_id,
            data_source_field = ds_field
        )


def generate_qr_code(qr_content):
    """
    Generates a QR code SVG item and saves it as a temporary file.
    :param qr_content: Content used to generate a QR code.
    :type qr_content: str
    :return: Returns a QTemporaryFile object containing the SVG file with the
    QR code.
    :rtype: QTemporaryFile
    """
    tmpf = QTemporaryFile()
    if tmpf.open():
        file_path = tmpf.fileName()
        qr_code = pyqrcode.create(qr_content)
        qr_code.svg(file_path, scale=6)
        tmpf.close()

    return tmpf


class QRCodeConfigValueHandler(ItemConfigValueHandler):
    """
    Generates the QR code base on the value of the data source field in the
    referenced record.
    """
    def _ds_field(self):
        # Return the name of data source field in the configuration
        return self.config_item().data_source_field

    def set_data_source_record(self, record):
        field_value = getattr(record, self._ds_field(), None)
        if not field_value:
            return

        # Convert numeric types to string
        if isinstance(field_value, (int, float, long)):
            field_value = str(field_value)
        elif isinstance(field_value, basestring):
            # Test if ASCII. PyQRCode only allows ASCII characters
            if not is_ascii(field_value):
                return
        else:
            # All other types not applicable
            return

        # Generate QR code and set file path of composer item
        qrc_tmpf = generate_qr_code(field_value)
        if qrc_tmpf.fileName():
            self.composer_item().setPictureFile(qrc_tmpf.fileName())


class QRCodeConfigurationCollection(ConfigurationCollectionBase):
    """
    Class for managing multiple instances of QRCodeConfiguration objects.
    """
    from stdm.ui.composer import ComposerQREditor

    collection_root = "QRCodes"
    editor_type = ComposerQREditor
    config_root = QRCodeConfiguration.tag_name
    item_config = QRCodeConfiguration