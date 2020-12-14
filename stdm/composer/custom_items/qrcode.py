# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Custom QR code item
"""
from typing import Optional

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

STDM_QR_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 6


class StdmQrCodeLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)
        self._linked_field = None

    def type(self):
        return STDM_QR_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('qrcode.png')

    def linked_field(self) -> Optional[str]:
        return self._linked_field

    def set_linked_field(self, field: Optional[str]):
        self._linked_field = field

    def writePropertiesToElement(self, element: QDomElement, document: QDomDocument,
                                 context: QgsReadWriteContext) -> bool:
        super().writePropertiesToElement(element, document, context)
        if self._linked_field:
            element.setAttribute('linked_field', self._linked_field)
        return True

    def readPropertiesFromElement(self, element: QDomElement, document: QDomDocument,
                                  context: QgsReadWriteContext) -> bool:
        super().readPropertiesFromElement(element, document, context)
        self._linked_field = element.attribute('linked_field') or None
        return True


class StdmQrCodeLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_QR_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'QR Code'))

    def createItem(self, layout):
        return StdmQrCodeLayoutItem(layout)
