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
    QgsLayoutItemMap,
    QgsReadWriteContext,
    QgsRectangle
)

from qgis.PyQt.QtXml import (
        QDomDocument,
        QDomElement
)

from stdm.ui.gui_utils import GuiUtils
from stdm.composer.map_extent import MapExtent

STDM_MAP_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 3


class StdmMapLayoutItem(QgsLayoutItemMap):

    def __init__(self, layout):
        super().__init__(layout)
        
        self._geom_type = None
        self._zoom = 4
        self._zoom_type = None
        self._srid = None
        self._label_field = None
        self._name = None
        self._map_extent = None

    def type(self):
        return STDM_MAP_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('add_map.png')

    @property
    def geom_type(self) -> str:
        return self._geom_type

    def set_geom_type(self, g_type: str):
        self._geom_type = g_type

    @property
    def zoom(self) -> str:
        return self._zoom

    def set_zoom(self, z):
        self._zoom = z

    @property
    def zoom_type(self) -> str:
        return self._zoom_type

    def set_zoom_type(self, z_type: str):
        self._zoom_type = z_type

    @property
    def srid(self) -> str:
        return self._srid

    def set_srid(self, s_rid: str):
        self._srid = s_rid

    @property
    def label_field(self) -> str:
        return self._label_field

    def set_label_field(self, l_field: str):
        self._label_field = l_field

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, n):
        self._name = n

    def map_extent(self) ->MapExtent:
        return self._map_extent

    def set_map_extent(self, map_ext):
        self._map_extent = map_ext
 


    def writePropertiesToElement(self, element: QDomElement, document: QDomDocument,
            context: QgsReadWriteContext) -> bool:
        super().writePropertiesToElement(element, document, context)

        if self._geom_type:
            element.setAttribute('geomType', self._geom_type)

        if self._zoom:
            element.setAttribute('zoom', self._zoom)

        if self._zoom_type:
            element.setAttribute('zoomType', self._zoom_type)

        if self._srid:
            element.setAttribute('srid', self._srid)

        if self._label_field:
            element.setAttribute('labelField', self._label_field)

        if self._name:
            element.setAttribute('name', self._name)

        if self._map_extent is not None:
            extent_element = self._map_extent.to_dom_element(document)
            element.appendChild(extent_element)

        return True


    def readPropertiesFromElement(self, element: QDomElement, document: QDomDocument,
            context: QgsReadWriteContext) -> bool:
        super().readPropertiesFromElement(element, document, context)


        self._geom_type = element.attribute('geomType') or None
        self._zoom = element.attribute('zoom') or None
        self._zoom_type = element.attribute('zoomType') or None
        self._srid = element.attribute('srid') or None
        self._label_field = element.attribute('labelField') or None
        self._name = element.attribute('name') or None

        self._map_extent = MapExtent.create_from_dom(element.firstChildElement("Extent"))

        if self._map_extent is not None:
            self.setExtent(self._map_extent.extent())
            #self.zoomToExtent(self._map_extent.extent())

        return True


class StdmMapLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_MAP_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Map'))

    def createItem(self, layout):
        return StdmMapLayoutItem(layout)
