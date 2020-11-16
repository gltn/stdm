"""
/***************************************************************************
Name                 : Graph Type UI Registry Classes
Description          : Container for registering graph type UI settings.
Date                 : 16/April/2015
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QWidget,
    QApplication
)

from stdm.ui.composer.chart_type_editors import (
    VerticalBarGraphEditor
)

class ChartTypeUISettings(object):
    registry = []

    def __init__(self,parent=None):
        self._parent_editor = parent

    @classmethod
    def register(cls, position=-1):
        if position < 0 or position > len(ChartTypeUISettings.registry):
            ChartTypeUISettings.registry.append(cls)

        else:
            ChartTypeUISettings.registry.index(position, cls)

    def title(self):
        """
        :return: Display of the graph type.
        :rtype: str
        """
        raise NotImplementedError

    def icon(self):
        """
        :return: Icon depicting the graph type.
        :rtype: QIcon
        """
        return None

    def short_name(self):
        """
        :return: Returns the shortname of the chart type. This should
        match exactly to the one specified in the ChartConfiguration
        subclass.
        :rtype: str
        """
        return ""

    def editor(self):
        """
        Editor for setting the graph series properties.
        """
        raise NotImplementedError


class VerticalBarChartSettings(ChartTypeUISettings):
    def icon(self):
        return QIcon(":/plugins/stdm/images/icons/chart_bar.png")

    def title(self):
        return QApplication.translate("VerticalBarGraph", "Vertical Bar")

    def editor(self):
        return VerticalBarGraphEditor(self._parent_editor)

    def short_name(self):
        return "vbar"


VerticalBarChartSettings.register()

