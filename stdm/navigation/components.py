"""
/***************************************************************************
Name                 : Qt UI Components
Description          : Extension of Qt UI classes that are used to capture
                        the settings of selected STDM components for access
                        authorization services
Date                 : 28/May/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

from qgis.PyQt.QtWidgets import (
    QAction,
    QListWidgetItem,
    QApplication
)


class STDMContent(object):
    """
    Abstract class for welding custom attributes to
    a navigation item.
    """

    def __init__(self, code):
        self.Name = ""
        self.Group = ""
        self.Code = code


class STDMAction(QAction, STDMContent):
    """
    Custom STDM Actions for inclusion in toolbars and/or menus
    """

    def __init__(self, icon, text, parent, code):
        if icon is None:
            QAction.__init__(self, text, parent)
        else:
            QAction.__init__(self, icon, text, parent)
        STDMContent.__init__(self, code)
        self.Name = text + " " + QApplication.translate("STDMModule", "Module")


class STDMListWidgetItem(QListWidgetItem, STDMContent):
    """
    Custom list widget items which attaches a 'Name' attribute
    that is subsequently used for registering the item as a
    content type
    """

    def __init__(self, text, name, icon, parent, code):
        QListWidgetItem.__init__(self, icon, text, parent)
        STDMContent.__init__(self, code)
        self.Name = name + " " + QApplication.translate("STDMEntity", "Entity")


'''
Define enumerations for all administrative unit levels
'''
DEPARTMENT = 2001
MUNICIPALITY = 2002
MUNICIPALITY_SECTION = 2003
LOCALITY = 2004
