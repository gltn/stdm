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
from .configfile_paths import FilePaths
from .config_utils import (
    activeProfile,
    ProfileException,
    table_searchable_cols,
    tableCols,
    read_social_relation_cols,
    current_table_exist
)
from .xmlconfig_reader import (
    XMLTableElement,
    tableColumns,
    tableRelations,
    tableFullDescription,
    tableLookUpCollection,
    lookupData,
    geometryColumns,
    lookupColumn,
    lookupTable,
    profiles,
    social_tenure_tables,
    social_tenure_tables_type,
    config_version
)
from .xmlconfig_writer import(
    writeSQLFile,
    writeHTML,
    setLookupValue,
    updateSQL,
    set_str_tables,
    str_type_tables,
    str_col_collection
)
from .usermodels import (
    listEntityViewer,
    EntityColumnModel
)

from stdm.settings.path_settings import dataIcon

from stdm.settings.registryconfig import (
    RegistryConfig,
    PATHKEYS
)

class ConfigTableReader(object):
    def __init__(self, parent=None, args=None):
        
        self._doc = ''
        self.args = args
        self.fileHandler = FilePaths()
        self.config = RegistryConfig()   
   
    def tableListModel(self, profile):
        '''pass the table list to a listview model'''
        tData = self.tableNames(profile)
        if not tData is None:
            model = listEntityViewer(tData)
            return model

        else:
            return None

    def profile_tables(self, profile):
        table_desc = tableFullDescription(profile)
        if table_desc:
            headers = table_desc[0].keys()
            rowData = [row.values() for row in table_desc]
            table_desc_model = EntityColumnModel(headers, rowData)
            return table_desc_model
    
    def tableNames(self, profile):
        tbl_data = XMLTableElement(profile)
        if tbl_data is not None:
#            if "social_tenure" in tData:
#                tData.remove('social_tenure')
            return tbl_data

    def current_profile_tables(self):
        """
        :return: Returns a list containing table names in the current
        profile.
        :rtype: list
        """
        try:
            curr_profile = activeProfile()

            return self.tableNames(curr_profile)

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
    
    def fulltableList(self):
        tbList = tableLookUpCollection()
        if not tbList is None:
            return tbList

    def on_main_table_selection(self):
        """
        Method required by the wizard for loading all the table in a model
        to a combo box
        :return:
        """
        tbl_list= self.fulltableList()
        tbl_model = listEntityViewer(tbl_list)
        return tbl_model
        
    def STDMProfiles(self):
        pfList=profiles()
        return pfList
    
    def lookupTableModel(self):
        model=listEntityViewer(self.lookupTable())
        return model
    
    def lookupTable(self):
        return lookupTable()

    def lookupColumns(self,lookupName):
        columnModel = None
        tableAttrib = lookupColumn(lookupName)
        if len(tableAttrib)>0:
            colHeaders = tableAttrib[0].keys()
            colVals= []
           # [item.values for item in tableAttrib]
            for item in tableAttrib:
                colVals.append(item.values())
            columnModel=EntityColumnModel(colHeaders,colVals)

            return columnModel

        else: 
            return None
    
    def columns(self,profile,tableName):
        '''Functions to read columns details from the config for the given table''' 
        columnModel = None
        tableAttrib = tableColumns(profile,tableName)
        if len(tableAttrib) > 0:
            colHeaders = tableAttrib[0].keys()
            colVals = [item.values() for item in tableAttrib]
            #for item in tableAttrib:
             #   colVals.append(item.values())
            columnModel = EntityColumnModel(colHeaders, colVals)

            return columnModel

        else: 
            return None

    def column_labels(self,col_list):
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

    def tableRelation(self,tableName):
        '''Method to read all defined table relationship in the config file'''
        relationModel = None
        tableAttrib = tableRelations(tableName,"relations")
        if tableAttrib is None:
            return tableAttrib
        if len(tableAttrib)>0:
            colHeaders = tableAttrib[0].keys()
            colVals = []
            for item in tableAttrib:
                colVals.append(item.values())
            relationModel = EntityColumnModel(colHeaders,colVals)
            return relationModel
        
    def geometry_collection(self,tableName):
        '''Method to read all defined table relationship in the config file'''
        geometryModel = None
        geomAttrib = geometryColumns(tableName, 'geometryz')
        if geomAttrib == None:
            return geomAttrib
        if len(geomAttrib) > 0:
            colHeaders = geomAttrib[0].keys()
            colVals = []
            for item in geomAttrib:
                colVals.append(item.values())
            geometryModel = EntityColumnModel(colHeaders, colVals)
            return geometryModel

    def sqlTableDefinition(self):
        '''load the table definition info in html file'''
        docfile = self.fileHandler.SQLFile()
        return docfile
    
    def htmlTableDefinition(self):
        '''load the table definition info in html file'''
        docfile = self.fileHandler.HtmlFile()
        return docfile
    
    def userProfileDir(self):
        return self.fileHandler.STDMSettingsPath()

    def updateDir(self, path):
        return  self.fileHandler.userConfigPath(path)

    def saveXMLchanges(self):
        writeSQLFile()
        writeHTML()
                
    def upDateSQLSchema(self):
        #To be implemented to allow updating of schema
        updateSQL()
        
        
    def setProfileSettings(self,profileData):
        '''write the current profile in Qsettings'''            
        self.config.write(profileData) 
    
    def settingsKeys(self):
        '''
        Keys used to store directory paths in the database
        '''
        return PATHKEYS
    
    def pathSettings(self):
        pathKeys = self.settingsKeys()
        pathSetting = self.config.read(pathKeys)
        return pathKeys, pathSetting
    
    def createDir(self, paths):
        if paths != None:
            for fPath in paths:
                self.fileHandler.createDir(fPath)
    
    def addLookupValue(self,table,valueText):
        setLookupValue(table,valueText)
        
    def readLookupList(self,table):
        lookupList=[]
        try:
            lookupList=lookupData(table)
        except:
            pass
        lookupModel = listEntityViewer(lookupList, icon=dataIcon)
        return lookupModel
        
    def setDocumentationPath(self):
        '''get the help contents available to user'''
        helpFile=self.fileHandler.HelpContents()
        return helpFile
    
    def trackXMLChanges(self):
        self.fileHandler.createBackup()

    def check_config_version(self, path):
        self.fileHandler.compare_config_version(path)

    def active_profile(self):
        return activeProfile()

    def selected_table_columns(self, table):
        """
        Method to return the selected table colums as alist
        :param table name STR:
        :return: List
        """
        return tableCols(table)

    def update_str_tables(self, table,level):
        set_str_tables(activeProfile(),table,level)

    def set_str_type_collection(self,table, optiontype):
        """
        Method to update the config to show the str type of individual str table
        :param table:
        :return:
        """
        str_type_tables(activeProfile(), table, optiontype)

    def set_table_str_columns(self, table, collist):
        """
        Method to set all the tables column participating in STR
        :param table:
        :return:
        """
        str_col_collection(activeProfile(),table,collist)

    def social_tenure_col(self,table):
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
        self.fileHandler.change_config()

    def chect_table_exist(self, table):
        """
        If the table is already defined in config
        :return:
        """
        if current_table_exist(table):
            return True
        else:
            return False

