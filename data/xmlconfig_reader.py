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
#from lxml import  objectify


from xml.etree.ElementTree import ElementTree as ET
from collections import OrderedDict
from configfile_paths import FilePaths
try:
    xmlobject=FilePaths()
    doc=xmlobject.XMLFile()
    xml_doc=xmlobject.setUserXMLFile()
    #xml_doc="C:/Users/SOLOMON/.stdm/stdmConfig.xml"
    html_doc=xmlobject.HtmlFile()
except:
    pass

def parseRootElement():
    if xml_doc==None:
        return
    else:
        tree=ET()
        root= tree.parse(xml_doc)
        return tree, root   

def XMLTableElement(profile):
    tree = ET()
    root= tree.parse(xml_doc)
    tables=[]
    level=(".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
        tables.append(elem.get('name'))
    return tables

def checktableExist(profile,tableName):
    Exist = False
    tree,root=parseRootElement()
    level=(".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
         if elem.get('name')== tableName:
             Exist = True
    return Exist
        
def deleteProfile(profileName):
    tree,root=parseRootElement()
    for elem in root.findall('profile'):
        if elem.get('name')==profileName:
            root.remove(elem)
    tree.write(xml_doc)

def profileFullDescription(profile):
    tree,root=parseRootElement()
    for elem in root.findall('profile'):
        if elem.get('name')==profile:
            return elem.get('fullname')

def tableFullDescription(profile,tableName):
    tree,root=parseRootElement()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==tableName:
            return elem.get('fullname')

def tableColumns(profile,tableName):
    #scan the xml file and return all the table defined columns information
    tree,root=parseRootElement()
    tableData=[]
    bool=False
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==tableName:
            for child in elem.findall('columns/column'):
                ordDict=OrderedDict()
                ordDict["Column label"]=child.get('name')
                ordDict["Description"]=child.get('fullname')
                ordDict["Data type"]=child.get('type')
                ordDict["Length"]=child.get('size')
                if child.get('lookup')!=None:
                    ordDict["Lookup"]=child.get('lookup')
                else:
                    ordDict["Lookup"]=bool
                tableData.append(ordDict)                          
    return tableData

def tableLookUpCollection():
    tree, root=parseRootElement()
    tableDict=['table','lookup']
    table=[]
    for name in tableDict:
        pLevel=('profile/%s')%name
        for elem in root.findall(pLevel):
            table.append(elem.get('name'))
    return table

def lookupColumn(tableName):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root= tree.parse(xml_doc)
    tableData=[]
    for elem in root.findall("profile/lookup"):
        if elem.get('name')==tableName:
            for child in elem[0]:
                ordDict=OrderedDict()
                ordDict["Column label"]=child.get('name')
                ordDict["Description"]=child.get('fullname')
                ordDict["Data type"]=child.get('type')
                ordDict["Length"]=child.get('size')
                ordDict["Lookups"]=bool
                tableData.append(ordDict)                           
    return tableData

def lookupTable():
    tree = ET()
    root= tree.parse(xml_doc)
    table=[]
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
        if elem.get('name')==tableName:
            for child in elem[0]:
                tabCols=child.attrib
    return tabCols

def profiles():
    tree, root=parseRootElement()
    pfList=[]
    for profile in root.findall('profile'):
        pfList.append(profile.get('name'))
    return pfList

    
def tableRelations(tableName,element):
    tree,root=parseRootElement()
    relationData=[]
    for elem in root.findall('profile/table'):
        if elem.get('name')==tableName:
            child=elem.find(element)
            if child is None:
                return None
            else:
                for child in elem[1]:
                    ordDict=OrderedDict()
                    ordDict["Relation Name"]=child.get('name')
                    ordDict["Reference table"]=child.get('table')
                    ordDict["Foreign column"]=child.get('fk')
                    ordDict["Local column"]=child.get('column')
                    ordDict["On delete"]=child.get('ondelete')
                    ordDict["On update"]=child.get('onupdate')
                    relationData.append(ordDict) 
                return relationData  
            
def geometryColumns(tableName,element):
    tree,root=parseRootElement()
    geomData=[]
    for elem in root.findall('profile/table'):
        if elem.get('name')==tableName:
            childs=elem.find(element)
            if childs!=None:
                for child in childs:
                    ordDict=OrderedDict()
                    ordDict["Table Name"]=child.get('table')
                    ordDict["Geometry Column"]=child.get('column')
                    ordDict["Geometry Type"]=child.get('type')
                    ordDict["Projection"]=child.get('srid')
                    ordDict["Schema"]='default'
                    geomData.append(ordDict) 

def lookupData(tableName):    
    lstLookup=[]
    tree, root=parseRootElement()
    for elem in root.findall('profile/lookup'):
        if elem.get('name')==tableName:
            child=elem.find('data')
            if child is None:
                return
            else:
                lookups=child.findall('value')
                for text in lookups:
                    lstLookup.append(text.text)
            return lstLookup

def lookupData2List(profile,tableName):
    '''read lookup data list values for generation of insert statement'''
    tree, root=parseRootElement()
    lkVals=[]
    filter=(".//*[@name='%s']/lookup")%profile
    for elem in root.findall(filter):
        if elem.get('name')==tableName:
            for child in elem.findall('data'):
                for node in child.findall('value'):
                    lkVals.append(node.text)
    return lkVals

def contentGroup(tableName):
    tree,root=parseRootElement()
    codeList=[]
    for elem in root.findall('profile/table'):
        if elem.get('name')==tableName:
            childs=elem.find('contentgroups')
            if childs is not None:
                for child in childs:
                    codeList.append(child.get('code'))
                return codeList
            else:
                return None
                
