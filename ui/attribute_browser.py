"""
/***************************************************************************
Name                 : Attribute Browser
Description          : Abstract class for browsing attribute from other table
Date                 : 18/June/2015
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
from stdm.ui.ui_attribute_browser import Ui_AttribBrowser
from fkbase_form import FKMapperDialog


class AttributeBrowser(QWidget, Ui_AttribBrowser):
    """
    Class initialization
    """
    def __init__(self, parent= None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.initialize()
        self.base_id = 0
        self._source =None
        self._def_col =None

        self.btn_browse.clicked.connect(self.browse_for_attribute)

    def initialize(self):
        self.txt_attribute.setFocus()
       #self.txt_attribute.setText("Browse attribute")

    def values(self):
        if self.base_id == 0 and str(self.txt_attribute.text()).isdigit():
            self.base_id= self.txt_attribute.text()
        return self.base_id

    def set_values(self, value):
        self.txt_attribute.setText(str(value))

    def parent_table(self, parent):
        self._source = parent

    def display_column(self, column_name ):
        self._def_col =column_name
        return self._def_col

    def browse_for_attribute(self):
        browser_frm = FKMapperDialog(self, self._source, self._def_col)

        browser_frm.foreign_key_modeller()
        if browser_frm.model_display_value():
            self.txt_attribute.setText(browser_frm.model_display_value())
        if browser_frm.model_fkid():
            self.base_id = browser_frm.model_fkid()




