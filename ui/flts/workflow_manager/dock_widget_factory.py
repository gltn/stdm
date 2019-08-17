"""
/***************************************************************************
Name                 : Dock Widget Factory
Description          : A factory that creates a dockable widget
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
    savedWidgets = {}
    activeWidget = None

    def __init__(self, customWidget, iface=None):
        self._customWidget = customWidget
        self._iface = iface

    def showDockWidget(self):
        """
        Shows dockable widget
        :return: Dockable widget or None
        :rtype: QDockWidget or None
        """
        dockWidget = self.getDockWidget()
        DockWidgetFactory.hideActiveDockWidget()
        if dockWidget and dockWidget.isHidden():
            DockWidgetFactory.activeWidget = dockWidget
            return dockWidget.show()
        self.setDockWidget()

    def getDockWidget(self):
        """
        Returns dock widget if it exists
        :return dockWidget: A dockwidget
        :rtype dockWidget: QDockWidget
        """
        objectName = self._customWidget.objectName()
        savedWidgets = DockWidgetFactory.savedWidgets
        if objectName in savedWidgets:
            dockWidget = savedWidgets.get(objectName, None)
            return dockWidget

    def setDockWidget(self):
        """
        Sets a new dockable widget in QGIS
        :return: A dockable widget
        :rtype: QDockWidget
        """
        savedWidgets = DockWidgetFactory.savedWidgets
        newWidget = DockWidget(self._customWidget, self._iface.mainWindow())
        savedWidgets[newWidget.objectName()] = newWidget
        self._iface.addDockWidget(Qt.BottomDockWidgetArea, newWidget)
        DockWidgetFactory.activeWidget = newWidget

    @classmethod
    def hideActiveDockWidget(cls):
        """
        Hides the active/visible dock widget
        """
        if cls.activeWidget and cls.activeWidget.isVisible():
            cls.activeWidget.hide()







