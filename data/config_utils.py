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
from .xmlconfig_reader import tableColumns,deleteProfile,tableFullDescription,profileFullDescription
from stdm.settings import RegistryConfig
regConfig = RegistryConfig()            
#rofileName=lookupReg['currentProfile']

def formatColumnName(txtName):
    txtName=str(txtName).strip()
    return txtName.replace(" ", "_").lower()

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
        cols=tableColumns(profileName,table)
        tcols=[]
        for colD in cols:
            colLabel=colD.get('Column label')
            tcols.append(colLabel)
        return tcols

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
        ordDict=OrderedDict(collectionType.items())
        combo.clear()
        for k, v in ordDict.iteritems():
            combo.addItem(k,v)
            combo.setInsertPolicy(QComboBox.InsertAlphabetically)
        combo.setMaxVisibleItems(len(collectionType))

def getOpenFileChooser(self,message,file_filter):
        #Load dialog for selecting logo file from disk
        try:
            filePath=QFileDialog.getOpenFileName(self,message,"/home",file_filter)
        except:
            return
        return filePath



    