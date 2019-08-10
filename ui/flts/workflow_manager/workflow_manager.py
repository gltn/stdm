"""
/***************************************************************************
Name                 : Workflow Manager
Description          : Defines FLTS generic workflow functions and classes
Date                 : 07/August/2019
copyright            : (C) 2019
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class DockWidget(QDockWidget):
    """
    Sets a dockable widget from a widget
    """
    def __init__(self, customWidget, parent=None):
        super(QDockWidget, self).__init__(parent)
        self.setWindowTitle(customWidget.windowTitle())
        self.setObjectName(customWidget.objectName())
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.topLevelChanged.connect(self._onTopLevelChange)
        self.setWidget(customWidget)

    def _onTopLevelChange(self, topLevel):
        """
        Add maximize and minimize buttons on the dock widget
        :param topLevel: Flag to check if dock widget is top level
        :type topLevel: Boolean
        """
        dockWidget = self.sender()
        if dockWidget is None or not isinstance(dockWidget, QDockWidget):
            return
        if dockWidget.isFloating():
            dockWidget.setWindowFlags(
                Qt.CustomizeWindowHint | Qt.Window |
                Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
            )
        dockWidget.show()


class DockWidgetFactory:
    """
    Factory to create dockable widgets from a widget
    """
    addedWidgets = {}

    def __init__(self, customWidget, iface=None):
        self._customWidget = customWidget()
        self._iface = iface

    def getDockWidget(self):
        """
        Returns dock widget if it exists
        :return dockWidget: A dockwidget
        :rtype dockWidget: QDockWidget
        """
        objectName = self._customWidget.objectName()
        dockWidgets = DockWidgetFactory.addedWidgets
        if objectName in dockWidgets:
            dockWidget = dockWidgets[objectName]
            return dockWidget

    def showDockWidget(self, dockWidget):
        """
        Shows hidden dock widget
        :return: A docked widget or None
        :rtype: QDockWidget or None
        """
        self.hideDockWidget(dockWidget)
        if dockWidget.isHidden():
            return dockWidget.show()
        return

    def setDockWidget(self):
        """
        Sets a new dock widget in QGIS
        :return: A docked widget
        :rtype: QDockWidget
        """
        addedWidgets = DockWidgetFactory.addedWidgets
        newWidget = DockWidget(self._customWidget, self._iface.mainWindow())
        addedWidgets[newWidget.objectName()] = newWidget
        self.hideDockWidget()
        self._iface.addDockWidget(Qt.BottomDockWidgetArea, newWidget)

    def hideDockWidget(self, dockWidget=None):
        """
        Hides visible dock widget
        :param dockWidget:
        :type dockWidget: QDockWidget
        """
        for widget_ in DockWidgetFactory.addedWidgets.values():
            if widget_ != dockWidget and widget_.isVisible():
                widget_.hide()






