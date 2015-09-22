# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : xmlconfig_reader
Description          :
Date                 : 24/September/2013
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
#from lxml import  objectify


from PyQt4.QtGui import *

from xml.etree.ElementTree import ElementTree as ET
from collections import OrderedDict
from configfile_paths import FilePaths
import xml.etree.ElementTree as Elt
from stdm.data.enums import non_editable_tables

try:
    xmlobject = FilePaths()
    #doc = xmlobject.xml_file()
    xml_doc = xmlobject.set_user_xml_file()
    html_doc = xmlobject.html_file()
except Exception as ex:
    raise ex

def parseRootElement():
    if not xml_doc:
        return
    else:
        tree = ET()
        root = tree.parse(xml_doc)
        return tree, root   

def XMLTableElement(profile):
    tree = ET()
    root = tree.parse(xml_doc)
    tables = []
    level = (".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
        if elem.get('name') in non_editable_tables:
            continue
        else:
            tables.append(elem.get('name'))

    return tables

def checktableExist(profile,tableName):
    is_found = False
    tree, root = parseRootElement()
    level = (".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
         if elem.get('name') == tableName:
             is_found = True
    return is_found

def table_column_exist(profile, tableName, idcol):
    is_found = False
    tree, root = parseRootElement()
    level = (".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
         if elem.get('name') == tableName:
             for child in elem.findall('columns/column'):
                if child.get('name') == idcol:
                    is_found = True
    return is_found
        
def deleteProfile(profileName):
    tree, root = parseRootElement()
    for elem in root.findall('profile'):
        if elem.get('name') == profileName:
            root.remove(elem)
    tree.write(xml_doc)

def profileFullDescription(profile):
    tree, root = parseRootElement()
    for elem in root.findall('profile'):
        if elem.get('name') == profile:
            return elem.get('fullname')

def tableFullDescription(profile):
    tree,root = parseRootElement()
    tablDesc = []
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        ordDict = OrderedDict()
        ordDict["Name"] = elem.get('name')
        ordDict["Description"]= elem.get('fullname')
        tablDesc.append(ordDict)
    return tablDesc

def tableColumns(profile,tableName):
    #scan the xml file and return all the table defined columns information
    tree,root = parseRootElement()
    tableData = []
    bool = False
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == tableName:
            for child in elem.findall('columns/column'):
                ordDict = OrderedDict()
                ordDict["Column label"] = child.get('name')
                ordDict["Description"] = child.get('fullname')
                ordDict["Data type"] = child.get('type')
                ordDict["Length"] = child.get('size')
                ordDict["Searchable"] = child.get('searchable')
                if child.get('lookup'):
                    ordDict["Lookup"] = child.get('lookup')
                else:
                    ordDict["Lookup"] = bool
                tableData.append(ordDict)                          
    return tableData

def social_tenure_tables(profile):
    """
    Method to read tables that are part of STR definition
    """
    tree,root = parseRootElement()
    str_table = []
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('is_str_table')== 'yes':
            str_table.append(elem.get('name'))
    return str_table

def social_tenure_tables_type(profile):
    """
    Method to read tables that are part of STR definition
    """
    tree,root = parseRootElement()
    party_table =''
    sp_table = ''
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('is_str_table')== 'yes' and elem.get('str_type')=='party':
            party_table = elem.get('name')
        if elem.get('is_str_table')== 'yes' and elem.get('str_type')== 'spatial unit':
            sp_table = elem.get('name')
    return party_table, sp_table

def tableLookUpCollection():
    tree, root = parseRootElement()
    tableDict = ['table','lookup']
    table=[]
    for name in tableDict:
        pLevel = ('profile/%s')%name
        for elem in root.findall(pLevel):
            table.append(elem.get('name'))
    return table

def lookupColumn(tableName):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root = tree.parse(xml_doc)
    tableData = []
    for elem in root.findall("profile/lookup"):
        if elem.get('name') == tableName:
            for child in elem[0]:
                ordDict=OrderedDict()
                ordDict["Column label"] = child.get('name')
                ordDict["Description"] = child.get('fullname')
                ordDict["Data type"] = child.get('type')
                ordDict["Length"] = child.get('size')
                ordDict["Lookups"] = bool
                tableData.append(ordDict)                           
    return tableData

def lookupTable():
    tree = ET()
    root = tree.parse(xml_doc)
    table = []
    for elem in root.findall('profile/lookup'):
        table.append(elem.get('name'))
    return table
    
def columns(tableName):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root= tree.parse(xml_doc)
    tabCols={}
    bool=False
    for elem in root.findall('table'):
        if elem.get('name') == tableName:
            for child in elem[0]:
                tabCols = child.attrib
    return tabCols

def profiles():
    tree, root = parseRootElement()
    pfList = []
    for profile in root.findall('profile'):
        pfList.append(profile.get('name'))
    return pfList

    
def tableRelations(tableName,element):
    tree,root = parseRootElement()
    relationData = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == tableName:
            child = elem.find(element)
            if child is None:
                return None
            else:
                for child in elem[1]:
                    ordDict = OrderedDict()
                    ordDict["Relation Name"] = child.get('name')
                    ordDict["Referenced table"] = child.get('table')
                    ordDict["Local column"] = child.get('fk')
                    ordDict["Foreign column"] = child.get('column')
                    ordDict["On delete"] = child.get('ondelete')
                    ordDict["On update"] = child.get('onupdate')
                    ordDict["Display field"] = child.get('display_name')
                    relationData.append(ordDict) 
                return relationData  
            
def geometryColumns(tableName, element):
    tree, root = parseRootElement()
    geomData = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == tableName:
            childs = elem.find(element)
            if childs:
                for child in childs:
                    ordDict=OrderedDict()
                    ordDict["Table Name"] = child.get('table')
                    ordDict["Geometry Column Name"] = child.get('column')
                    ordDict["Geometry Type"] = child.get('type')
                    ordDict["Projection"] = child.get('srid')
                    ordDict["Schema"] = 'default'
                    geomData.append(ordDict) 
    return geomData

def lookupData(tableName):    
    lstLookup = []
    tree, root = parseRootElement()
    for elem in root.findall('profile/lookup'):
        if elem.get('name') == tableName:
            child = elem.find('data')
            if child is None:
                return
            else:
                lookups = child.findall('value')
                for text in lookups:
                    lstLookup.append(text.text)
            return lstLookup

def lookupData2List(profile, tableName):
    '''read lookup data list values for generation of insert statement'''
    tree, root = parseRootElement()
    lkVals = []
    filter = (".//*[@name='%s']/lookup")%profile
    for elem in root.findall(filter):
        if elem.get('name') == tableName:
            for child in elem.findall('data'):
                for node in child.findall('value'):
                    lkVals.append(node.text)
    return lkVals

def contentGroup(tableName):
    tree,root = parseRootElement()
    codeList = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == tableName:
            childs = elem.find('contentgroups')
            if childs is not None:
                return [(child.get('code')) for child in childs]
            else:
                return None

def check_if_display_name_exits(layer_name):
    """
    Check if user defined display name exists
    """
    tree = Elt.parse(xml_doc)
    root = tree.getroot()

    for display_name in root.findall('display_names/display_name'):
        if display_name.get("layer_name") == layer_name:
            return True
        else:
            continue
    return False

def get_xml_display_name(layer_name):
    tree = Elt.parse(xml_doc)
    root = tree.getroot()

    for display_name in root.findall('display_names/display_name'):
        existing_layer_name = display_name.get("layer_name")
        if existing_layer_name == layer_name:
            # QMessageBox.information(None,"Title",display_name.text)
            return display_name.text

def description_for_table(profile, table):
    tree,root = parseRootElement()
    str_table = []
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')== table:
            return elem.get('fullname')

def read_str_col_collection(profile, table):
    tree, root = parseRootElement()
    filter = (".//*[@name='%s']/table")%profile
    str_cols = []
    for elem in root.findall(filter):
        if elem.get('name')==table:
            node=elem.find("columns")
            for col in node.findall('column'):
                if col.get('str_col') == 'yes':
                    str_cols.append(col.get('name'))
    return str_cols

def config_version():
    tree, root = parseRootElement()
    for elem in root.findall('config'):
        if elem is not None:
            return elem.get('version')
        else:
            return 0

