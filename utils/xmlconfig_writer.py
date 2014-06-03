# -*- coding: utf-8 -*-
"""
/***************************************************************************
 stdm
                                 A QGIS plugin
 Securing land and property rights for all
                              -------------------
        begin                : 2014-03-30
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
from xml.etree.ElementTree import ElementTree as ET , Element, SubElement,dump, ParseError,iselement
from xmllib import Error
from xml2ddl.xml2ddl import Xml2Ddl, readMergeDict
from xml2ddl.xml2html import Xml2Html, xml2ddl
from xml2ddl import ddlInterface
from configfile_paths import FilePaths
xmlobject=FilePaths()
xml_doc=xmlobject.XMLFile()
destPath=xmlobject.SQLFile()
destHtml=xmlobject.HtmlFile()

#xml_doc="C:/test/stdmConfig.xml"
sourcePath=xml_doc
# destPath="C:/test/stdmConfig.sql"
# destHtml= "C:/test/stdm_schema.html"
def writeTable(data,tableName):
    #method to addnew table definition in the config file
    try:
        tree, root=parseRootElement()
        for elem in root.findall('table'):
            #Check if the table has been defined already
            if elem.get('name')==tableName:
                return
        table= SubElement(root,'table',data)
        columns=SubElement(table,"columns")
        relations=SubElement(table,"relations")
        tree.write(xml_doc)
    except:
        Error.message
    
def writeLookup(data,tableName):
    #method to addnew table definition in the config file
    try:
        tree, root=parseRootElement()
        for elem in root.findall('lookup'):
            #Check if the table has been defined already
            if elem.get('name')==tableName:
                return
        table= SubElement(root,'lookup',data)
        columns=SubElement(table,"columns")
        tree.write(xml_doc)
    except:
        Error.message
                
def writeTableColumn(data,tableName):
    #Get new data to write to the config as a table column
    try:
        tree, root=parseRootElement()
        for elem in root.findall('table'):
            if elem.get('name')==tableName:
                parent=Element(tableName)
                if iselement(parent):
                    node=elem.find("columns")
                    SubElement(node,"column", data)
        tree.write(xml_doc)
    except:
        pass
    
def parseRootElement():
    if xml_doc==None:
        return
    else:
        tree=ET()
        root= tree.parse(xml_doc)
        return tree, root   


def editTableColumn(tableName, nodet, name, newname):
    tree, root=parseRootElement()
    for elem in root.findall('table'):
        if elem.get('name')==tableName:
            node=elem.find("columns")
            if node[0].get(nodet)==name:
                print node[0].get('fullname')
            node[0].set(nodet,newname)
            print node[0].attrib
    tree.write(xml_doc)

def renameTable(oldName, newName):
    tree, root=parseRootElement()
    for elem in root.findall('table'):
        if elem.get('name')==oldName:
            elem.set('name',newName)
            print elem.attrib
    tree.write(xml_doc)

def deleteTable(tableName):
    tree, root=parseRootElement()
    for item in root.findall('table'):
        if item.get('name')==tableName:
            root.remove(item)
    tree.write(xml_doc)

def writeXml(dropTable=True):
    cd = Xml2Ddl()
    cd.setDbms("postgres")
    cd.params['drop-tables'] = dropTable
           
    #strFilename = path
    xml = readMergeDict(sourcePath)
    results = cd.createTables(xml)
    fileN=open(destPath,"w")
    for result in results:
        fileN.write(result[1])
        fileN.write("\n")

    fileN.close()
 
def writeHTML():
    #Generate a html file from the configuration xml
    x2h = Xml2Html()
    strFilename = sourcePath
    xml = readMergeDict(strFilename)
    lines = x2h.outputHtml(xml)
    strOutfile =destHtml
        
    of = open(strOutfile, "w")
    for line in lines:
        of.write("%s\n" % (line))
    of.close() 

def trimlongtext():
    name="special Name"
    print name.replace(" ","_").lower()
    

if __name__=="__main__":
    trimlongtext()

     