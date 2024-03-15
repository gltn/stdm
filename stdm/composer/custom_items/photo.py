# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Contains custom layout item types
"""

from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement
)

from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPicture,
    QgsReadWriteContext
)

from stdm.ui.gui_utils import GuiUtils

STDM_PHOTO_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 4


class StdmPhotoLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

        self._linked_table = None
        self._source_field = None
        self._linked_field = None
        self._document_type = None
        self._document_type_id = -1
        self._referencing_field = None

    def type(self):
        return STDM_PHOTO_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('photo_24.png')

    @property
    def linked_table(self) -> str:
        """
        :return: Name of the referenced table.
        :rtype: str
        """
        return self._linked_table

    def set_linked_table(self, table: str):
        """
        Set the name of the referenced table.
        :param table: Table name.
        :type table: str
        """
        self._linked_table = table

    @property
    def source_field(self) -> str:
        """
        :return: Column name in the referenced data source.
        :rtype: str
        """
        return self._source_field

    def set_source_field(self, field: str):
        """
        Set the name of the column in the referenced data source.
        :param field: Column name.
        """
        self._source_field = field

    @property
    def linked_field(self) -> str:
        """
        :return: Name of the matching column in the linked table.
        :rtype: str
        """
        return self._linked_field

    def set_linked_column(self, field: str):
        """
        Set the name of the matching column in the linked table.
        :param field: Column name.
        :type field: str
        """
        self._linked_field = field

    @property
    def document_type(self):
        return self._document_type

    def set_document_type(self, document_type):
        self._document_type = document_type

    @property
    def document_type_id(self):
        return self._document_type_id

    def set_document_type_id(self, document_type_id):
        self._document_type_id = document_type_id

    def referencing_field(self) -> str:
        return self._referencing_field

    def set_referencing_field(self, field: str):
        self._referencing_field = field

    def writePropertiesToElement(self, element: QDomElement, document: QDomDocument,
                                 context: QgsReadWriteContext) -> bool:
        super().writePropertiesToElement(element, document, context)
        if self._linked_field:
            element.setAttribute('linked_field', self._linked_field)
        if self._source_field:
            element.setAttribute('source_field', self._source_field)
        if self._linked_table:
            element.setAttribute('linked_table', self._linked_table)
        if self._document_type is not None:
            element.setAttribute('documentType', self._document_type)
        if self._document_type_id != -1:
            element.setAttribute('documentTypeId', str(self._document_type_id))

        if self._referencing_field:
            element.setAttribute('referencing_field', self._referencing_field)

        return True

    def readPropertiesFromElement(self, element: QDomElement, document: QDomDocument,
                                  context: QgsReadWriteContext) -> bool:
        super().readPropertiesFromElement(element, document, context)
        self._linked_field = element.attribute('linked_field') or None
        self._source_field = element.attribute('source_field') or None
        self._linked_table = element.attribute('linked_table') or None
        self._document_type = element.attribute('documentType') or None
        self._referencing_field = element.attribute('referencing_field') or None

        elem = element.attribute('documentTypeId')

        if elem == '' or elem == 'None':
            self._document_type_id = -1
            return True

        if element.attribute('documentTypeId') is None:
            self._document_type_id = -1
            return True

        if element.attribute('documentTypeId') == '': 
            self._document_type_id = -1
        else:
            self._document_type_id = int(element.attribute('documentTypeId', '-1'))

        return True


class StdmPhotoLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_PHOTO_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Photo'))

    def createItem(self, layout):
        return StdmPhotoLayoutItem(layout)
