# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdmDialog
                                 A QGIS plugin
 Securing land and property rights for all
                             -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : gltn_stdm@unhabitat.org
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
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#from .entity_browser import ContentGroupEntityBrowser

# create the dialog for zoom to point

from sqlalchemy import Table
from sqlalchemy.orm import mapper
from stdm.data import (
    Model,
    Base,
    STDMDb
)
from .python_object import class_from_table
from collections import OrderedDict
import types

from stdm.data.database import Singleton
from stdm.third_party.sqlalchemy.exc import NoSuchTableError

        
@Singleton                  
class DeclareMapping(object):
    """
    this class takes an instance of the table defined the pg schema and returns a sqlalchemy table mapper model
    """
    def __init__(self, tlist=None):
        self.list = tlist
        self._mapping = {}
        self.attDictionary = OrderedDict()
        self.tablecol_mapping = OrderedDict()
    
    def setTableMapping(self, tablist):
        """
        Method to convert a list of table to mapped table object
        :return Mapper calass
        """
        for table in tablist:

            try:
                self.mapper_for_table(table)
            except:
                pass
        Base.metadata.reflect(STDMDb.instance().engine)

    def mapper_for_table(self, table):
        """
        Create a slqalchamey table mapping from the table name
        :param table: string
        :return: table: slqalchemy table model
        """
        try:
            class_object = self.pythonize_tablename(table)
            mapper_table = Table(table, Base.metadata, autoload=True, autoload_with=STDMDb.instance().engine)
            mapper(class_object, mapper_table)
            self._mapping[table] = class_object
            self.table_property(mapper_table)
        except:
            return None

    def pythonize_tablename(self, table):
        """
        Method to create a python object from a table name
        :param table:
        :return:
        """
        class_name = table.capitalize()
        class_object = class_from_table(class_name)
        return class_object

    def table_property(self, reflectedtab):
        """
        Method to query table and its column attribute and format to dictionary
        :param mappedtable:
        :return:
        """
        self.column_mapping_for_table(reflectedtab)
        self.table_columns_metadata(reflectedtab)

    def tableMapping(self, table):
        """
        Method to ensure accessor for table finds it well formatted into a sqlalchemy model
        :param table:
        :return: reflected table : sqlalchemy table class
        """
        if table not in self._mapping:
            self.mapper_for_table(table)
        model_cls = self._mapping[table]
        Model.attrTranslations = self.displayMapping(table)

        return model_cls

    def displayMapping(self, table=None):
        """
        Replaces the depreciated method where column names were read from the config.
        column names already stored in a dictionary.
        :param table:
        :return:
        """
        attribs = OrderedDict()
        if table:
            col_list = self.attDictionary.get(table)

            for col in col_list:
                attribs[col] = col.replace('_', ' ').title()
        else:
            return None

        return attribs
        
    def column_mapping_for_table(self, table):
        """
        Method to store all the columns names from the database table into an dict.
        :param table: str
        :return  a list of table column names: dict
        """
        self.attDictionary[table.name] = [column.name for column in table.columns]

    def table_columns_metadata(self, table):
        """
        Method to package the table columns and their datatype into a dictionary mapping.
        :param  table name :str
        :return dict:
        """
        type_mapping = OrderedDict()
        for column in table.columns:
            type_mapping[column.name] = column.type
        self.tablecol_mapping[table.name] = type_mapping

    def column_data_types(self, table):
        """
        Return the selected table columns datatype as a dictionary
        :return:
        """
        return self.tablecol_mapping.get(table)

    def raw_table(self,table):
        """
        Method to return a table reflection from postgres to sqlalchemy object: not a mapper
        :param table:
        :return:
        """
        return Table(table, Base.metadata, autoload=True, autoload_with=STDMDb.instance().engine)
