"""
/***************************************************************************
Name                 : NotificationWidget
Description          : A table widget that provides a quick access menus for
                       uploading and viewing supporting documents.
Date                 : 16/July/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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

from PyQt4.QtGui import (
    QTreeWidget,
    QTreeWidgetItem
)


class NotificationWidget(QTreeWidget):
    """
    A widget for displaying notification information after Login
    """

    def __init__(self, parent=None):
        super(NotificationWidget, self).__init__(parent)
        self._init_view()

        # Notification state
        READ, UNREAD = range(2)

    def _init_view(self):
        """
        Set the notification details to be shown
        """
        # Header title
        self.setHeaderLabels([self.tr('Content'),
                              self.tr('Status'),
                              self.tr('Timestamp')])

        # Setting up the column number
        self.setColumnCount(3)

        # Widget items
        self.notif_detail = QTreeWidgetItem()


