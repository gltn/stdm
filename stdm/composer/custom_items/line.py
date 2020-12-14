# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Custom line type
"""

from qgis.PyQt.QtCore import (
    QCoreApplication,
    QPointF
)
from qgis.PyQt.QtGui import QPolygonF
from qgis.core import (
    QgsLayoutItemRegistry,
    QgsLayoutItemAbstractMetadata,
    QgsLayoutItemPolyline
)

from stdm.ui.gui_utils import GuiUtils

STDM_LINE_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 0


class StdmLineLayoutItem(QgsLayoutItemPolyline):

    def __init__(self, layout):
        super().__init__(layout)
        self._size = None
        self._point = None

    def type(self):
        return STDM_LINE_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('line.png')

    def attemptResize(self, size, includesFrame):
        if not self.nodes():
            self._size = size
            self._set_initial_line()
        else:
            super().attemptResize(size, includesFrame)

    def attemptMove(self, point, useReferencePoint, includesFrame, page):
        if not self.nodes():
            self._point = point
            self._set_initial_line()
        else:
            super().attemptMove(point, useReferencePoint, includesFrame, page)

    def _set_initial_line(self):
        if self._point is not None and self._size is not None:
            self.setNodes(QPolygonF([QPointF(self._point.x(), self._point.y()),
                                     QPointF(self._point.x() + self._size.width(),
                                             self._point.y() + self._size.height())]))
            self._point = None
            self._size = None


class StdmLineLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_LINE_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Line'))

    def createItem(self, layout):
        return StdmLineLayoutItem(layout)
