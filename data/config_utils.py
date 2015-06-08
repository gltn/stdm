# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-04
        copyright            : (C) 2014 by GLTN
        email                : njoroge.solomon@yahoo.com
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
    tableColumns,
    deleteProfile,
    tableFullDescription,
    tableRelations
)
from stdm.settings import RegistryConfig
regConfig = RegistryConfig()            
#rofileName=lookupReg['currentProfile']

def formatColumnName(txtName):
    txtName=str(txtName).strip()
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
        profileName=activeProfile()
        cols = tableColumns(profileName,table)
        return [col.get('Column label') for col in cols]
    
def tableColType(table):
    profileName=activeProfile()
    cols=tableColumns(profileName,table)
    colMapping=OrderedDict()
    for col in cols:
        colLabel = col.get('Column label')
        colMapping[colLabel] = [col.get('Data type'),col.get('Lookup')]
    return colMapping

def foreign_key_columns(table):
    #profileName=activeProfile()
    cols= tableRelations(table,"relations")
    colMapping=OrderedDict()
    for col in cols:
        colLabel = col.get('Local column')
        colMapping[colLabel] = ['foreign key', False]
    return colMapping

def activeProfile():
    try:
        lookupReg = regConfig.read(['currentProfile'])
        profileName=lookupReg['currentProfile']
        return profileName
    except:
        pass
    
def tableFullname(table):
    tableFullDescription(table)
    
def profileDescription(profile):
    profileDescription(profile)
    
def deleteSelectedProfile(profile):
    deleteProfile(profile)
    
def setCollectiontypes(collectionType,combo):
        #method to read defult  to a sql relations and constraint type to combo box
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
    