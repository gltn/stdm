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

# from stdm.composer.chart_configuration import (
#      ChartConfiguration
#      #VerticalBarConfiguration
#  )

from stdm.ui.gui_utils import GuiUtils

STDM_CHART_ITEM_TYPE = QgsLayoutItemRegistry.PluginItem + 2337 + 5


class StdmChartLayoutItem(QgsLayoutItemPicture):

    def __init__(self, layout):
        super().__init__(layout)

        self._linked_table = None
        self._source_field = None
        self._linked_field = None

        self._referencing_field = None

        # self._chart_configuration = ChartConfiguration()

    def type(self):
        return STDM_CHART_ITEM_TYPE

    def icon(self):
        return GuiUtils.get_icon('chart.png')

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

    def referencing_field(self) -> str:
        return self._referencing_field

    def set_referencing_field(self, value: str):
        self._referencing_field = value

    # def chart_configuration(self) -> ChartConfiguration:
    #     return self._chart_configuration

    # def set_chart_configuration(self, configuration: ChartConfiguration):
    #     self._chart_configuration = configuration

    def writePropertiesToElement(self, element: QDomElement, document: QDomDocument,
                                 context: QgsReadWriteContext) -> bool:
        super().writePropertiesToElement(element, document, context)
        if self._linked_field:
            element.setAttribute('linked_field', self._linked_field)
        if self._source_field:
            element.setAttribute('source_field', self._source_field)
        if self._linked_table:
            element.setAttribute('linked_table', self._linked_table)

        if self._referencing_field:
            element.setAttribute('referencing_field', self._referencing_field)

        # config_element = self._chart_configuration.to_dom_element(document)
        # element.appendChild(config_element)

        return True

    def readPropertiesFromElement(self, element: QDomElement, document: QDomDocument,
                                  context: QgsReadWriteContext) -> bool:
        super().readPropertiesFromElement(element, document, context)
        self._linked_field = element.attribute('linked_field') or None
        self._source_field = element.attribute('source_field') or None
        self._linked_table = element.attribute('linked_table') or None
        self._referencing_field = element.attribute('referencing_field') or None


        #self._chart_configuration = VerticalBarConfiguration.create(element.firstChildElement('Plot'))
        # self._chart_configuration = ChartConfiguration.create(element.firstChildElement('Plot'))

        return True


class StdmChartLayoutItemMetadata(QgsLayoutItemAbstractMetadata):

    def __init__(self):
        super().__init__(STDM_CHART_ITEM_TYPE, QCoreApplication.translate('StdmItems', 'STDM Chart'))

    def createItem(self, layout):
        return StdmChartLayoutItem(layout)
