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


from xml.etree.ElementTree import ElementTree as ET, Element, SubElement,dump
from collections import OrderedDict
#from stdm.utils.configfile_paths import xmlfilehandler
#xmlobject=xmlfilehandler()
#xml_doc=xmlobject.getFileObject()

xml_doc="C:/test/stdmConfig.xml"
html_doc="C:/test/stdm_schema.html"
def XMLTableElement():
    tree = ET()
    root= tree.parse(xml_doc)
    table=[]
    for elem in root.findall('table'):
        table.append(elem.get('name'))
    return table

def tableColumns(tableName):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root= tree.parse(xml_doc)
    tableData=[]
    bool=False
    for elem in root.findall('table'):
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

def parseRootElement():
    if xml_doc==None:
        return
    else:
        tree=ET()
        root= tree.parse(xml_doc)
        return tree, root   

def XMLtableObject():
    tree, root=parseRootElement()
    tableDict=['table','lookup']
    table=[]
    for name in tableDict:
        for elem in root.findall(name):
            table.append(elem.get('name'))
    return table

def AllColumns(tableName):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root= tree.parse(xml_doc)
    tableData=[]
    bool=False
    tableDict=['table','lookup']
    for name in tableDict:
        for elem in root.findall(name):
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
    for elem in root.findall('lookup'):
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

def tableRelations(tableName):
    tree = ET()
    root= tree.parse(xml_doc)
    relationData=[]
    for elem in root.findall('table'):
        if elem.get('name')==tableName:
            child=elem.find('relations')
            if child is None:
                return None
            else:
                for child in elem[1]:
                    ordDict=OrderedDict()
                    ordDict["Relation Name"]=child.get('name')
                    ordDict["Relation to table"]=child.get('table')
                    ordDict["Table column"]=child.get('column')
                    ordDict["On delete"]=child.get('ondelete')
                    ordDict["On update"]=child.get('onupdate')
                    relationData.append(ordDict) 
                return relationData  


# if __name__=="__main__":
#     import sys
#     getXMLTableElement()
#     
