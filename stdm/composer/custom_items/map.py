# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Custom map item
"""

from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemMap
)

from stdm.ui.gui_utils import GuiUtils

STDM_MAP_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 3


class StdmMapLayoutItem(QgsLayoutItemMap):

    def __init__(self, layout):
        super().__init__(layout)

    def type(self):
        return STDM_MAP_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('add_map.png')


class StdmMapLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_MAP_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Map'))

    def createItem(self, layout):
        return StdmMapLayoutItem(layout)
