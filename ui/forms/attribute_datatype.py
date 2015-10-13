"""
/***************************************************************************
Name                 : Generic application for forms
Description          : forms generator functions
Date                 : 30/June/2013 
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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

from stdm.data.config_utils import tableColType
from stdm.data.config_utils import foreign_key_columns
from stdm.ui.stdmdialog import DeclareMapping
from stdm.data import data_types

class AttributePropretyType(object):
    """

    """
    def __init__(self, model):
        self.model = model
        self._mapper = DeclareMapping.instance()
        
    def attribute_type(self):
        """Enumerate column and datatype for the selected model
        :return: dict
        """
        type_mapping = tableColType(self.model)
        db_mapping = self._mapper.column_data_types(self.model)
        db_mapping.update(type_mapping)

        try:
            """
            Compare table columns definition in the database and configuration file.
            """
            if cmp(db_mapping, type_mapping) != 0:
                QMessageBox.information(None,"Table Columns ",
                                QApplication.translate(u"AttributePropertyType",
                                u"Database columns and configuration table columns do not "
                                u"match. Database table columns will be used instead\n"
                                u"Please update configuration tables for complete dialog mapping"))
            updated_table_mapping = self.table_config_has_changed(db_mapping, type_mapping)
            if type_mapping:
                foreignk_attr = self.foreign_key_attribute_for_model()
                """
                Only the foreign key attributes defined in the configuration shall be considered in the foreign key definition
                """
                if foreignk_attr:
                    updated_table_mapping.update(foreignk_attr)
            return updated_table_mapping

        except Exception as ex:
                QMessageBox.information(None, "Reading %s columns"%self.model,
                                        QApplication.translate(u"AttributeDataType", u"Error reading the columns"))

    def foreign_key_attribute_for_model(self):
        """
        Scan trough the model attributes for foreign key columns in the configuration file
        :return:dict
        """
        foreignk_attr = foreign_key_columns(self.model)
        return foreignk_attr

    def table_config_has_changed(self, dbtable_mapping, config_table_mapping):
        """
        Method to update the column datatype with the default types pre defined in the STDM: data/enums.py
        :param dbtablemapping:
        :param configtablemapping:
        :return:
        """
        if config_table_mapping:
            try:
                for col, col_type in dbtable_mapping.iteritems():
                    if not col in config_table_mapping:
                        match_type = self. convert_db_data_types(col_type)
                        if not match_type:
                            """If the column datatype cannot be matched, use string as the datatype"""
                            match_type = 'character varying'
                            dbtable_mapping[col] = [match_type, False]
                        elif len(match_type) < 1:
                            continue
                        else:
                            """Check if the column can be formatted on the fly"""
                            dbtable_mapping[col] = [match_type[0], False]
            except IndexError as ie:
                QMessageBox.information(None,
                                    QApplication.translate(u"AttributePropertyType", u"Data Type Error"),
                                    QApplication.translate(u"AttributePropertyType", u"data type error: %s")%str(ie.message))
        else:
            for col, col_type in dbtable_mapping.iteritems():
                match_type = self.convert_db_data_types(col_type)
                if not match_type:
                    match_type = 'character varying'
                    dbtable_mapping[col] = [match_type, False]
                elif len(match_type) < 1:
                    continue
                else:
                    """Check if the column can be formatted on the fly"""
                    dbtable_mapping[col] = [match_type[0], False]
        return dbtable_mapping

    @staticmethod
    def convert_db_data_types(db_type):
        """
        Method to convert the sqlalchemy datatype to default type that is recognized by STDM
        i.e VARCHAR(50) to character varying
        :param datatype:
        :return:
        """
        db_type = str(db_type).lower()
        option_type = [user_type for user_type in data_types.values() if db_type[:4] in user_type]
        if option_type:
            return option_type
        else:
            return None
