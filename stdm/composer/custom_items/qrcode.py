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

from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPicture
)

from stdm.ui.gui_utils import GuiUtils

STDM_QR_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 6


class StdmQrCodeLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_QR_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('qrcode.png')


class StdmQrCodeLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_QR_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'QR Code'))

    def createItem(self, layout):
        return StdmQrCodeLayoutItem(layout)
