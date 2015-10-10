"""
/***************************************************************************
Name                 : config_utils
Description          : Database config util functions
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
from collections import OrderedDict
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .xmlconfig_reader import (
    table_columns,
    delete_profile,
    table_full_description,
    table_relations,
    description_for_table,
    read_str_col_collection,
    social_tenure_tables,
    check_table_exist
)

from stdm.settings import RegistryConfig

regConfig = RegistryConfig()

class ProfileException(Exception):
    """
    Raised when an there are issues when reading/writing profile
    information.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class ConfigVersionException(Exception):
    """
    Subclass main exception handler to specific config version problem
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

def formatColumnName(txtName):
    txtName = unicode(txtName).strip()
    return txtName.replace(" ", "_").lower()

def setUniversalCode():
        codGen=QUuid()
        code=codGen.createUuid()
        return code.toString().upper()

def UserData(comboBox):
        #get the user data from the combo box display item
        text=comboBox.currentText()
        index=comboBox.findText(text, Qt.MatchExactly)
        if index!=-1:
            userData=comboBox.itemData(int(index))
            return userData

def tableCols(table):
        #Get table columns from the config file
        profileName = activeProfile()
        cols = table_columns(profileName,table)
        return [col.get('Column label') for col in cols]

def table_searchable_cols(table):
        #Get table columns from the config file
        profileName = activeProfile()
        cols = table_columns(profileName, table)
        return [col.get('Column label') for col in cols if col.get('Searchable') == 'yes']
    
def tableColType(table):
    profileName=activeProfile()
    cols=table_columns(profileName,table)
    colMapping=OrderedDict()
    for col in cols:
        colLabel = col.get('Column label')
        colMapping[colLabel] = [col.get('Data type'),col.get('Lookup')]
    return colMapping

def foreign_key_table_reference(table):
    """
    get the table that is referenced in the child table foreign key definition
    :param table:
    :return:
    """
    cols= table_relations(table,"relations")
    colMapping=OrderedDict()
    for col in cols:
        tableLabel = col.get('Referenced table')
        display_name = col.get('Display field')
    return tableLabel, display_name

def foreign_key_columns(table):
    #profileName=activeProfile()
    cols= table_relations(table,"relations")
    colMapping=OrderedDict()
    for col in cols:
        colLabel = col.get('Local column')
        colMapping[colLabel] = ['foreign key', False]
    return colMapping

def activeProfile():
    try:
        lookupReg = regConfig.read(['currentProfile'])
        #msg = QApplication.translate("ProfileException",str(lookupReg['currentProfile']))
        #return msg
        profile=lookupReg['currentProfile']
        return profile
    except:
        return  None

    # except:
    #     msg = QApplication.translate("ProfileException",
    #                                  "Error in reading the current profile."
    #                                  "\nThe current profile information could "
    #                                  "not be read from the registry, please "
    #                                  "check your settings.")
    #     raise ProfileException(msg)
    
def tableFullname(table):
    table_full_description(table)

def table_description(table):
    """
    Method to show the table description for the selected table
    :param table:
    :return:
    """
    return description_for_table(activeProfile(),table)

def display_name(table):
    """
    :param table: Name of table or column.
    :type table: str
    :return: Formats the table name to a more friendly display name by
    capitalizing and removing underscore.
    :rtype: str
    """
    return table.replace("_"," ").capitalize()
    
def profileDescription(profile):
    profileDescription(profile)
    
def deleteSelectedProfile(profile):
    delete_profile(profile)
    
def setCollectiontypes(collectionType,combo):
        #method to read default  to a sql relations and constraint type to combo box
        ordDict=OrderedDict(collectionType)
        combo.clear()
        for k, v in ordDict.iteritems():
            combo.addItem(QT_TR_NOOP(k), v)
            combo.setInsertPolicy(QComboBox.InsertAlphabetically)
        combo.setMaxVisibleItems(len(collectionType))

def getOpenFileChooser(self,message,file_filter):
        #Load dialog for selecting logo file from disk
        try:
            filePath=QFileDialog.getOpenFileName(self,message,"/home",file_filter)
        except:
            return

        return filePath

def read_social_relation_cols(table):
    """
    Method to read and return all the table column participating in str
    :param table:
    :return:list
    """
    return read_str_col_collection(activeProfile(),table)

def current_table_exist(table):

    return check_table_exist(activeProfile(),table)


