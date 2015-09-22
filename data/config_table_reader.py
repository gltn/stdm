"""
/***************************************************************************
Name                 : ConfigTableReader
Description          : Reads table configuration information in an XML config
                       file.
Date                 : 30/March/2014
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
from stdm.data import (
    XMLTableElement,
    tableColumns,
    tableRelations,
    lookupTable,
    lookupColumn,
    profiles,
    tableLookUpCollection,
    lookupData,
    config_version,
    geometryColumns,
    writeSQLFile,
    writeHTML,
    setLookupValue,updateSQL,
    listEntityViewer,
    EntityColumnModel,
    FilePaths,
    tableFullDescription,
    set_str_tables,
    social_tenure_tables,
    str_type_tables,
    str_col_collection,
    social_tenure_tables_type,


)
from .config_utils import (
    activeProfile,
    ProfileException,
    table_searchable_cols,
    tableCols,
    read_social_relation_cols,
    current_table_exist
)
from stdm.settings import dataIcon


from stdm.settings import (
    RegistryConfig,
    PATHKEYS
)
from PyQt4.QtGui import QMessageBox

class ConfigTableReader(object):
    def __init__(self, parent=None, args=None):
        
        self._doc = ''
        self.args = args
        self.file_handler = FilePaths()
        self.config = RegistryConfig()   
   
    def table_list_model(self, profile):
        '''pass the table list to a listview model'''
        tdata = self.table_names(profile)
        if not tData is None:
            model = listEntityViewer(tdata)
            return model
        else:
            return None

    def profile_tables(self, profile):
        table_desc = tableFullDescription(profile)
        if table_desc:
            headers = table_desc[0].keys()
            row_data = [row.values() for row in table_desc]
            table_desc_model = EntityColumnModel(headers, row_data)
            return table_desc_model
    
    def table_names(self, profile):
        tbl_data = XMLTableElement(profile)
        if tbl_data is not None:
            return tbl_data

    def current_profile_tables(self):
        """
        :return: Returns a list containing table names in the current
        profile.
        :rtype: list
        """
        try:
            curr_profile = activeProfile()
            return self.table_names(curr_profile)
        except ProfileException:
            raise

    def table_columns(self, table):
        """
        :param table: Name of the table.
        :type table: str
        :return: Returns a list of the columns of the specified in order in
        which they were created.
        :rtype: list
        """
        return tableCols(table)
    
    def full_table_list(self):
        tbl_list = tableLookUpCollection()
        if not tbl_list is None:
            return tbl_list

    def on_main_table_selection(self):
        """
        Method required by the wizard for loading all the table in a model
        to a combo box
        :return:
        """
        tbl_list= self.full_table_list()
        tbl_model = listEntityViewer(tbl_list)
        return tbl_model
        
    def stdm_profiles(self):
        prof_list=profiles()
        return prof_list
    
    def lookup_table_model(self):
        model=listEntityViewer(self.lookup_table())
        return model
    
    def lookup_table(self):
        return lookupTable()

    def lookup_columns(self, lookup_name):
        column_model = None
        table_attrib = lookupColumn(lookup_name)
        if len(table_attrib)>0:
            col_headers = table_attrib[0].keys()
            col_vals= []
            for item in table_attrib:
                col_vals.append(item.values())
            column_model=EntityColumnModel(col_headers, col_vals)

            return column_model

        else: 
            return None
    
    def columns(self, profile, table_name):
        '''Functions to read columns details from the config for the given table''' 
        column_model = None
        table_attrib = tableColumns(profile, table_name)
        if len(table_attrib) > 0:
            col_headers = table_attrib[0].keys()
            col_vals = [item.values() for item in table_attrib]
            column_model = EntityColumnModel(col_headers, col_vals)

            return column_model

        else: 
            return None

    def column_labels(self, col_list):
        """
        Method to read and return the defined column labels for the table as a model
        :param list:
        :return:Listmodel
        """
        return listEntityViewer(col_list, icon=dataIcon)

    def table_searchable_columns(self, table):
        """
        Method to read all searchable field from the config for the table
        :param table:
        :return:cols: List
        """
        return table_searchable_cols(table)

    def social_tenure_tables(self):
        """
        Method to read all tables participating in STR
        :return:tables: List
        """
        if not social_tenure_tables(activeProfile()):
            return []

        else:
            return social_tenure_tables(activeProfile())

    def table_relation(self, table_name):
        '''Method to read all defined table relationship in the config file'''
        relation_model = None
        table_attrib = tableRelations(tableName, "relations")
        if table_attrib is None:
            return table_attrib
        if len(table_attrib)>0:
            col_headers = table_attrib[0].keys()
            col_vals = []
            for item in table_attrib:
                col_vals.append(item.values())
            relation_model = EntityColumnModel(col_headers, col_vals)
            return relation_model
        
    def geometry_collection(self, table_name):
        '''Method to read all defined table relationship in the config file'''
        geometry_model = None
        geom_attrib = geometryColumns(tableName, 'geometryz')
        if geom_attrib == None:
            return geom_attrib
        if len(geom_attrib) > 0:
            col_headers = geom_attrib[0].keys()
            col_vals = []
            for item in geom_attrib:
                col_vals.append(item.values())
            geometry_model = EntityColumnModel(col_headers, col_vals)
            return geometry_model

    def sql_table_definition(self):
        '''load the table definition info in html file'''
        doc_file = self.file_handler.SQLFile()
        return doc_file
    
    def html_table_definition(self):
        '''load the table definition info in html file'''
        doc_file = self.file_handler.HtmlFile()
        return doc_file
    
    def user_profile_dir(self):
        return self.file_handler.STDMSettingsPath()

    def update_dir(self, path):
        return  self.file_handler.userConfigPath(path)

    def save_xml_changes(self):
        writeSQLFile()
        writeHTML()
                
    def update_sql_schema(self):
        #To be implemented to allow updating of schema
        updateSQL()
        
    def set_profile_settings(self, profile_data):
        '''write the current profile in Qsettings'''            
        self.config.write(profile_data) 
    
    def settings_keys(self):
        '''
        Keys used to store directory paths in the database
        '''
        return PATHKEYS
    
    def path_settings(self):
        path_keys = self.settings_keys()
        path_setting = self.config.read(path_keys)
        return path_keys, path_setting
    
    def create_dir(self, paths):
        if paths != None:
            for file_path in paths:
                self.file_handler.create_dir(file_path)
    
    def add_lookup_value(self, table, value_text):
        setLookupValue(table, value_text)
        
    def read_lookup_list(self, table):
        lookup_list=[]
        try:
            lookup_list=lookupData(table)
        except:
            pass
        lookup_model = listEntityViewer(lookup_list, icon=dataIcon)
        return lookup_model
        
    def set_documentation_path(self):
        '''get the help contents available to user'''
        help_file=self.file_handler.HelpContents()
        return help_file
    
    def track_xml_changes(self):
        self.file_handler.createBackup()

    def check_config_version(self, path):
        self.file_handler.compare_config_version(path)

    def active_profile(self):
        return activeProfile()

    def selected_table_columns(self, table):
        """
        Method to return the selected table colums as alist
        :param table name STR:
        :return: List
        """
        return tableCols(table)

    def update_str_tables(self, table, level):
        set_str_tables(activeProfile(), table, level)

    def set_str_type_collection(self, table, option_type):
        """
        Method to update the config to show the str type of individual str table
        :param table:
        :return:
        """
        str_type_tables(activeProfile(), table, option_type)

    def set_table_str_columns(self, table, col_list):
        """
        Method to set all the tables column participating in STR
        :param table:
        :return:
        """
        str_col_collection(activeProfile(), table, col_list)

    def social_tenure_col(self, table):
        """
        Method to read str columns from config
        :param table:
        :return:
        """
        return read_social_relation_cols(table)

    def social_tenure_table_types(self):
        """
        Method to read and return the party and spatial unit str tables
        respectively
        :return:String
        """
        return social_tenure_tables_type(activeProfile())

    def read_config_version(self):
        """
        Method to read and return the config version to avoid obsolete method
        returning none
        :return:
        """
        return config_version()

    def update_config_file(self):
        """
        Try and update the config file if old one is detected
        :return:
        """
        self.file_handler.change_config()

    def check_table_exist(self, table):
        """
        If the table is already defined in config
        :return:
        """
        if current_table_exist(table):
            return True
        else:
            return False

