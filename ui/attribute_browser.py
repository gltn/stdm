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
from fkbase_form import ForeignKeyMapperDialog


class AttributeBrowser(QWidget, Ui_AttribBrowser):
    """
    Class variables initialization
    """
    def __init__(self, parent= None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.initialize()
        self.base_id = 0
        self._parent_table =None
        self._def_col =None

        self.btn_browse.clicked.connect(self.browse_for_attribute)

    def initialize(self):
        self.txt_attribute.setFocus()
       #self.txt_attribute.setText("Browse attribute")

    def values(self):
        """
        Method to read the foreign key ids when saving the data to db
        :return:
        """
        if self.base_id == 0 and str(self.txt_attribute.text()).isdigit():
            self.base_id = self.txt_attribute.text()
        return self.base_id

    def set_values(self, value):
        """
        Required method to set db values to the control when loading the form
        :param value:
        :return:
        """
        """Fetch the column value instead of passed ids"""
        #modelObj = model.queryObject().filter(self._dbModel.id == value).first()
        """Temporary load the ids"""
        self.txt_attribute.setText(str(value))

    def parent_table(self):
        """
        Method to return the foreign key parent table
        :return:
        """
        return self._parent_table

    def set_parent_table(self, parent):
        """
        Set foreign key parent table
        :param parent:
        :return:
        """
        self._parent_table = parent

    def set_display_column(self, column_name):
        """
        Method to read default display column when browsing for foreign key
        :param column_name:
        :return:
        """
        self._def_col = column_name
        return self._def_col

    def display_column(self):
        """
        Return th default display column
        :return:
        """
        return self._def_col

    def browse_for_attribute(self):
        """
        Method to invoke foreign key browser
        :return: display column value
        :return: row UUID
        """
        #QMessageBox.information(None, "asdfa", str(self._def_col))
        try:
            browser_frm = ForeignKeyMapperDialog(self, self._parent_table, self._def_col)

            browser_frm.foreign_key_modeller()
            if browser_frm.model_display_value():
                self.txt_attribute.setText(browser_frm.model_display_value())
            if browser_frm.model_fkid():
                self.base_id = browser_frm.model_fkid()
        except Exception as ex:
            msg =ex.message
            QMessageBox.information(None,QApplication.translate(u'AttributeBrowser',u'Foreign Keys'),
            QApplication.translate('TypePropertyMapper',u"Error loading foreign keys"+msg))
            return




