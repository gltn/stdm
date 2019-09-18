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
    def __init__(self, custom_widget, parent=None):
        super(QDockWidget, self).__init__(parent)
        self.setWindowTitle(custom_widget.windowTitle())
        self.setObjectName(custom_widget.objectName())
        self.setAllowedAreas(Qt.BottomDockWidgetArea | Qt.TopDockWidgetArea)
        self.topLevelChanged.connect(self._on_top_level_change)
        self.setWidget(custom_widget)

    def _on_top_level_change(self, top_level):
        """
        Add maximize and minimize buttons on the dock widget
        :param top_level: Flag to check if dock widget is top level
        :type top_level: Boolean
        """
        dock_widget = self.sender()
        if dock_widget is None or not isinstance(dock_widget, QDockWidget):
            return
        if dock_widget.isFloating():
            dock_widget.setWindowFlags(
                Qt.CustomizeWindowHint | Qt.Window |
                Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
            )
        dock_widget.show()


class DockWidgetFactory:
    """
    Factory to create dockable widgets from a widget
    """
    saved_widgets = {}
    active_widget = None

    def __init__(self, custom_widget, iface=None):
        self._custom_widget = custom_widget
        self._iface = iface

    def show_dock_widget(self):
        """
        Shows dockable widget
        :return: Dockable widget or None
        :rtype: QDockWidget or None
        """
        dock_widget = self.get_dock_widget()
        DockWidgetFactory.hide_active_dock_widget()
        if dock_widget and dock_widget.isHidden():
            DockWidgetFactory.active_widget = dock_widget
            dock_widget.show()
            dock_widget.widget().refresh()
            return
        self.set_dock_widget()

    def get_dock_widget(self):
        """
        Returns dock widget if it exists
        :return dockWidget: A dockwidget
        :rtype dockWidget: QDockWidget
        """
        object_name = self._custom_widget.objectName()
        saved_widgets = DockWidgetFactory.saved_widgets
        if object_name in saved_widgets:
            dock_widget = saved_widgets.get(object_name, None)
            return dock_widget

    def set_dock_widget(self):
        """
        Sets a new dockable widget in QGIS
        :return: A dockable widget
        :rtype: QDockWidget
        """
        saved_widgets = DockWidgetFactory.saved_widgets
        new_widget = DockWidget(self._custom_widget, self._iface.mainWindow())
        saved_widgets[new_widget.objectName()] = new_widget
        self._iface.addDockWidget(Qt.BottomDockWidgetArea, new_widget)
        DockWidgetFactory.active_widget = new_widget

    @classmethod
    def hide_active_dock_widget(cls):
        """
        Hides the active/visible dock widget
        """
        if cls.active_widget and cls.active_widget.isVisible():
            cls.active_widget.hide()







