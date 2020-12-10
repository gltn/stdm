# /***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

"""
Custom rubber bands for layout items
"""

from qgis.PyQt.QtCore import QRectF, QLineF
from qgis.PyQt.QtWidgets import (
    QGraphicsLineItem
)
from qgis.core import QgsLayout
from qgis.gui import QgsLayoutViewRubberBand


class LinearRubberBand(QgsLayoutViewRubberBand):

    def __init__(self, view):
        super().__init__(view)
        self.line_item = None
        self.start_pos = None

    def __del__(self):
        if self.line_item:
            self.layout().removeItem(self.line_item)
            self.line_item = None

    def create(self, view):
        return LinearRubberBand(view)

    def start(self, position, modifiers):
        self.line_item = QGraphicsLineItem()
        self.line_item.setPen(self.pen())
        self.start_pos = position
        self.line_item.setZValue(QgsLayout.ZViewTool)
        self.layout().addItem(self.line_item)
        self.layout().update()

    def update(self, position, modifiers):
        self.line_item.setLine(QLineF(self.start_pos, position))

    def finish(self, position, modifiers):
        if self.line_item:
            self.layout().removeItem(self.line_item)
            self.line_item = None
        return QRectF(self.start_pos.x(), self.start_pos.y(), position.x() - self.start_pos.x(),
                      position.y() - self.start_pos.y())
