from qgis.PyQt.QtXml import (
    QDomDocument,
    QDomElement
)

from qgis.core import QgsRectangle

class MapExtent:
    def __init__(self):
        self.tag_name = "Extent"
        self._xmin = -3.5
        self._xmax = 3.5
        self._ymin = -2.0
        self._ymax = 2.0

    def set_xmin(self, xmin):
        self._xmin = xmin

    def set_xmax(self, xmax):
        self._xmax = xmax

    def set_ymin(self, ymin):
        self._ymin = ymin

    def set_ymax(self, ymax):
        self._ymax = ymax

    def xmin(self):
        return self._xmin
    
    def xmax(self):
        return self._xmax

    def ymin(self):
        return self._ymin
    
    def ymax(self):
        return self._ymax

    def to_dom_element(self, dom_element: 'QDomElement'):
        extent_elem = dom_element.createElement(self.tag_name)
        extent_elem.setAttribute("xmin", self._xmin)
        extent_elem.setAttribute("xmax", self._xmax)
        extent_elem.setAttribute("ymin", self._ymin)
        extent_elem.setAttribute("ymax", self._ymax)

        return extent_elem

    def from_dom_element(self, dom_element):
        self.set_xmin(dom_element.attribute("xmin"))
        self.set_xmax(dom_element.attribute("xmax"))
        self.set_ymin(dom_element.attribute("ymin"))
        self.set_ymax(dom_element.attribute("ymin"))

    def extent(self):
        return QgsRectangle(float(self.xmin()), float(self.ymin()), float(self.xmax()), float(self.ymax()))


    @staticmethod
    def create_from_dom(dom_element: QDomDocument):
        dflt_xmin = -3.5
        dflt_xmax = 3.5
        dflt_ymin = -2.1
        dflt_ymax = 2.1

        max_extent = MapExtent()

        if dom_element:

            xmin = dom_element.attribute("xmin")
            xmax = dom_element.attribute("xmax")
            ymin = dom_element.attribute("ymin")
            ymax = dom_element.attribute("ymax")

            if xmin == "0":
                xmin = dflt_xmin
            if xmax == "0":
                xmax = dflt_xmax
            if ymin == "0":
                ymin = dflt_ymin
            if ymax == "0":
                ymax = dflt_ymax

            max_extent.set_xmin(xmin)
            max_extent.set_xmax(xmax)
            max_extent.set_ymin(ymin)
            max_extent.set_ymax(ymax)
        else:
            max_extent.set_xmin(dflt_xmin)
            max_extent.set_xmax(dflt_xmax)
            max_extent.set_ymin(dflt_ymin)
            max_extent.set_ymax(dflt_ymax)

        return max_extent
    