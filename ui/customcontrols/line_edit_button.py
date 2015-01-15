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
from PyQt4.QtGui import QLineEdit, QToolButton, QStyle, QMessageBox
from PyQt4.QtCore import *
from stdm.settings import pbIcon

class SearchableLineEdit(QLineEdit):
    """Subclass the QLineEdit to support a toolbutton"""
    def __init__(self, parent=None):
        QLineEdit.__init__(self, parent)
        self.button = QToolButton(self)
        self.button.setCursor(Qt.ArrowCursor)
        self.button.setIcon(pbIcon)
        self.button.clicked.connect(self.button_click_event())


    def resizeEvent(self,event):
        rect = self.rect()
        frameWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        buttonWidth = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        self.button.resize(buttonWidth,rect.height()-2*frameWidth)
        self.button.move(rect.right() - buttonWidth, frameWidth)

    def button_click_event(self):
        name="Hello foreign Key"
        #return QMessageBox.information(None, "button test",name)

