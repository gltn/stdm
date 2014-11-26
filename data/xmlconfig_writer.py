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
from xml.etree.ElementTree import ElementTree as ET , Element, SubElement,iselement
from xml2ddl.xml2html import Xml2Html, xml2ddl
from xml2ddl.diffxml2ddl import DiffXml2Ddl
from xml2ddl.xml2ddl import Xml2Ddl, readMergeDict
from xml2ddl.xml2html import Xml2Html


from .configfile_paths import FilePaths
xmlobject=FilePaths()
xml_doc=xmlobject.setUserXMLFile()
#xml_doc=xmlobject.XMLFile()
destPath=xmlobject.SQLFile()
destHtml=xmlobject.HtmlFile()
sourcePath=xml_doc
oldPath=xmlobject.cacheFile()


def writeTable(data,profile,tableName):
    #method to addnew table definition in the config file
    filter=(".//*[@name='%s']/table")%profile
    try:
        tree, root=parseRootElement()
        for elem in root.findall(filter):
            #Check if the table has been defined already
            if elem.get('name')==tableName:
                return
        for elem in root.findall('profile'):
            if elem.get('name')==profile:
                table= SubElement(elem,'table',data)
                SubElement(table,"columns")
                SubElement(table,"relations")
                SubElement(table,"constraints")
                SubElement(table,"contentgroups",data)
        tree.write(xml_doc,xml_declaration=True, encoding='utf-8')
    except:
        pass
  
def writeLookup(data,profile,tableName):
    #method to addnew table definition in the config file
    filter=(".//*[@name='%s']/lookup")%profile
    try:
        tree, root=parseRootElement()
        for elem in root.findall(filter):
            #Check if the table has been defined already
            if elem.get('name')==tableName:
                return
        for elem in root.findall('profile'):
            if elem.get('name')==profile:
                table= SubElement(elem,'lookup',data)
                columns=SubElement(table,"columns")
        tree.write(xml_doc,xml_declaration=True, encoding='utf-8')
    except:
        pass
                
def writeTableColumn(data,profile,category,tableName,tableNode):
    #Get new data to write to the config as a table column
    #node=None
    tree, root=parseRootElement()
    filters=(".//*[@name='%s']/%s")%(profile,category)
    for elem in root.findall(filters):
        if elem.get('name')==tableName:
            parent=Element(tableName)
            if iselement(parent):
                node=elem.find(tableNode)
                if node!=None:
                    nodeElem=tableNode[:(len(tableNode)-1)]
                    SubElement(node,nodeElem, data)
                if node==None:
                    node=SubElement(parent,tableNode)
                    nodeElem=tableNode[:(len(tableNode)-1)]
                    SubElement(node,nodeElem, data)
        tree.write(xml_doc,xml_declaration=True, encoding='utf-8')
        
def writeGeomConstraint(profile,level,tableName,data = None):
    #Get new data to write to the config as a table column
    #node=None
    tree, root=parseRootElement()
    filters=(".//*[@name='%s']/%s")%(profile,level)
    for elem in root.findall(filters):
        if elem.get('name')==tableName:
            geomElem = elem.find('geometryz')
            if geomElem is not None:
                continue
            else:
                SubElement(elem,'geometryz')
        tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
        
def parseRootElement():
    if xml_doc==None:
        return
    else:
        tree=ET()
        root= tree.parse(xml_doc)
        return tree, root   

def deleteColumn(level,category,tableName,elemnt,key,value):
    tree, root=parseRootElement()
    for profile in root.findall('profile'):
        if profile.get('name')==level:
            tables=profile.findall(category)
            for table in tables:
                if table.get('name')==tableName:
                    node=table.find(elemnt)
                    nodeElem=elemnt[:(len(elemnt)-1)]
                    for col in node.findall(nodeElem):
                        if col.get(key)==value:
                            node.remove(col)
                            tree.write(xml_doc,xml_declaration=True, encoding='utf-8')
        else:
            continue
            #print "Not founded"+str(profile.attrib)
    
def editTableColumn(profile,tableName, key, value, newValue,type,size):
    tree, root=parseRootElement()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==tableName:
            node=elem.find("columns")
            for col in node.findall('column'):
                if col.get(key)==value:
                    col.set(key,newValue)
                    col.set('oldname',value)
                    col.set('type',type)
                    col.set('size',size)
    tree.write(xml_doc,xml_declaration=True, encoding='utf-8')

def renameTable(profile,oldName, newName):
    tree, root=parseRootElement()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==oldName:
            elem.set('name',newName)
    tree.write(xml_doc,xml_declaration=True, encoding='utf-8')

def deleteTable(level,tableName):
    tree, root=parseRootElement()
    for profile in root.findall('profile'):
        if profile.get('name')==level:
            tables=profile.findall('table')
            for table in tables:
                if table.get('name')==tableName:
                    profile.remove(table)
                else:
                    lookups=profile.findall('lookup')
                    for lkUp in lookups:
                        if lkUp.get('name')==tableName:
                            profile.remove(lkUp)
                    
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
    
def inheritTableColumn(profile,sourceTable,destTable):
    tree, root=parseRootElement()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==sourceTable:
            for child in elem.findall('columns'):
                for node in child.findall('column'):
                    dict=node.attrib
                    #Remove the primary key definition from the source table
                    if dict.has_key('key'):
                        dict.pop("key")
                    writeTableColumn(dict, profile,'table', destTable, 'columns')

def writeProfile(data):
    '''Add user defined profile'''
    tree, root=parseRootElement()
    profile=SubElement(root,'profile',data)
    tree.write(xml_doc,xml_declaration=True, encoding='utf-8')

def checkProfile(profileName): 
    tree, root=parseRootElement() 
    for profile in root.findall('profile'):
        if profile.get('name')==profileName:
            return profile.get('name')

def writeSQLFile(dropTable=False):
    configdoc = Xml2Ddl()
    configdoc.setDbms("postgres")
    configdoc.params['drop-tables'] = dropTable
           
    #strFilename = path
    xml = readMergeDict(sourcePath)
    results = configdoc.createTables(xml)
    fileN=open(destPath,"w")
    for result in results:
        fileN.write(result[1])
        fileN.write("\n")

    fileN.close()

def updateSQL(dropTable=False):
    configdoc = DiffXml2Ddl()
    configdoc.setDbms("postgres")
    #configdoc.params['drop-tables'] = dropTable
           
    #strFilename = path
    #fc = DiffXml2Ddl()
  
    strNewFile = sourcePath
    strOldFile = oldPath
    
    #strOldFile = './.svn/text-base/%s.svn-base' % strNewFile
    # raise  NameError strNewFile
    fileN=open(destPath,"w")
    results = configdoc.diffFiles(strOldFile, strNewFile)
    for result in results:
        fileN.write(result[1])
        fileN.write("\n")
    fileN.close()
    return results
 
def writeHTML():
    #Generate a html file from the configuration xml
    xml2html = Xml2Html()
    strFilename = sourcePath
    xml = readMergeDict(strFilename)
    lines = xml2html.outputHtml(xml)
    strOutfile =destHtml
        
    of = open(strOutfile, "w")
    for line in lines:
        of.write("%s\n" % (line))
    of.close() 

def setLookupValue(tableName, valueText):
    '''add lookup value specified by the user
    :type tableName: object
    '''
    tree, root= parseRootElement()
    node = None
    for elem in root.findall('profile/lookup'):
        if elem.get('name')== tableName:
            child = elem.find('data')
            if child is not None:
                node = SubElement(child, "value")
            if child is None:
                dataNode = SubElement(elem, 'data')
                node = SubElement(dataNode, "value")
            node.text = valueText
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def deleteLookupChoice(level,category,tableName,elemnt,key,value):
    tree, root=parseRootElement()
    for profile in root.findall('profile'):
        if profile.get('name')==level:
            tables=profile.findall(category)
            for table in tables:
                if table.get('name')==tableName:
                    node=table.find(elemnt)
                    #nodeElem=elemnt[:(len(elemnt)-1)]
                    for col in node.findall(key):
                        if col.text==value:
                            node.remove(col)
                            tree.write(xml_doc,xml_declaration=True, encoding='utf-8')
        else:
            continue

