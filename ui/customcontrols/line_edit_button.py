"""
/***************************************************************************
Name                 : lineEditButton
Description          : subclasses Qline edit to support a button for browsing
                        foreign key relations.
Date                 : 8/January/2015
copyright            : (C) 2015 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from stdm.settings import pbIcon
__all__ = ["SearchableLineEdit"]

class SearchableLineEdit(QLineEdit):
    """Subclass the QLineEdit to support a toolbutton"""
    #signal_sender = pyqtSignal("PyQt_PyObject")
    signal_sender = pyqtSignal(name = 'Button clicked')
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.button = QToolButton(self)
        self.button.setCursor(Qt.ArrowCursor)
        self.key = "0"
        self.button.setIcon(pbIcon)
        self.button.clicked.connect(self.button_click_event)

    def resizeEvent(self,event):
        rect = self.rect()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonWidth = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        self.button.resize(buttonWidth,rect.height()-2*frameWidth)
        self.button.move(rect.right() - buttonWidth, frameWidth)

    def button_click_event(self):
        self.signal_sender.emit()

    def set_value(self, id):
        key = self.list.get(id)
        return key

    def fk_id(self, key):
        self.key = key

    def value(self):
        return self.key




