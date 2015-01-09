"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2013 by Solomon Njogu
email                : njoroge.solomon.com
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
from stdm.data.config_utils import tableColType, foreign_key_columns
from stdm.ui.stdmdialog import DeclareMapping
from PyQt4.QtGui import QMessageBox
class AttributePropretyType(object):
    def __init__(self, model):
        self.model=model
        
    def attributeType(self):
        """Enumerate column and datatype for the selected model
        :return: dict
        """
        typeMapping=tableColType(self.model)

        foreignk_attr= self.foreign_key_attribute_for_model()
        """
        Compare the two dictionaries of attributes and return a combined one.
        """
        typeMapping.update(foreignk_attr)

        return typeMapping

    def foreign_key_attribute_for_model(self):
        """
        Scan trough the model attributes for foreign key column
        :return:dict
        """
        foreignk_attr = foreign_key_columns(self.model)
        return foreignk_attr
    
    def displayMapping(self):
        #use the mapped table properties
        self._mapper =  DeclareMapping.instance()
        lkModel = self._mapper.tableMapping(self.model)