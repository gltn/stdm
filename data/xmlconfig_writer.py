# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : xmldata2sql
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
from xml.etree.ElementTree import ElementTree as ET , Element, SubElement,iselement
from xml2ddl.xml2html import Xml2Html, xml2ddl
from xml2ddl.diffxml2ddl import DiffXml2Ddl
from xml2ddl.xml2ddl import Xml2Ddl, readMergeDict
from xml2ddl.xml2html import Xml2Html
import xml.etree.ElementTree as Elt

from PyQt4.QtGui import *

from .configfile_paths import FilePaths

xml_object = FilePaths()
xml_doc = xml_object.set_user_xml_file()

DEST_PATH = xml_object.sql_file()
DEST_HTML = xml_object.html_file()
SOURCE_PATH = xml_doc
OLD_PATH = xml_object.cache_file()

def write_table(data, profile, table_name):
    #method to addnew table definition in the config file
    filter=(".//*[@name='%s']/table")%profile
    try:
        tree, root=parse_root_element()
        for elem in root.findall(filter):
            #Check if the table has been defined already
            if elem.get('name')==table_name:
                return
        for elem in root.findall('profile'):
            if elem.get('name') == profile:
                table= SubElement(elem, 'table', data)
                SubElement(table, "columns")
                SubElement(table, "relations")
                SubElement(table, "constraints")
                SubElement(table, "contentgroups", data)
        tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
    except:
        pass
  
def write_lookup(data, profile, table_name):
    #method to addnew table definition in the config file
    filter=(".//*[@name='%s']/lookup")%profile
    try:
        tree, root = parse_root_element()
        for elem in root.findall(filter):
            #Check if the table has been defined already
            if elem.get('name') == table_name:
                return
        for elem in root.findall('profile'):
            if elem.get('name') == profile:
                table = SubElement(elem, 'lookup', data)
                columns = SubElement(table, "columns")
        tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
    except:
        pass
                
def write_table_column(data, profile, category, table_name, table_node):
    #Get new data to write to the config as a table column
    #node=None
    tree, root = parse_root_element()
    filters=(".//*[@name='%s']/%s")%(profile, category)
    for elem in root.findall(filters):
        if elem.get('name') == table_name:
            parent = Element(table_name)
            if iselement(parent):
                node = elem.find(table_node)
                if node != None:
                    node_elem = table_node[:(len(table_node)-1)]
                    SubElement(node, node_elem, data)
                if node == None:
                    node = SubElement(parent, table_node)
                    node_elem = table_node[:(len(table_node)-1)]
                    SubElement(node, node_elem, data)
        tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
        
def write_geom_constraint(profile, level, table_name, data=None):
    #Get new data to write to the config as a table column
    #node=None
    tree, root = parse_root_element()
    filters = (".//*[@name='%s']/%s")%(profile, level)
    for elem in root.findall(filters):
        if elem.get('name') == table_name:
            geom_elem = elem.find('geometryz')
            if geom_elem is not None:
                continue
            else:
                SubElement(elem, 'geometryz')
        tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
        
def parse_root_element():
    if xml_doc==None:
        return
    else:
        tree=ET()
        root= tree.parse(xml_doc)
        return tree, root   

def delete_column(level, category, table_name, elemnt, key, value):
    tree, root = parse_root_element()
    for profile in root.findall('profile'):
        if profile.get('name') == level:
            tables = profile.findall(category)
            for table in tables:
                if table.get('name') == table_name:
                    node = table.find(elemnt)
                    node_elem = elemnt[:(len(elemnt)-1)]
                    for col in node.findall(node_elem):
                        if col.get(key) == value:
                            node.remove(col)
                            tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
        else:
            continue

def set_str_tables(profile, table, option):
    tree, root = parse_root_element()
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==table:
            elem.set('is_str_table',option)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def str_type_tables(profile, table, option):
    tree, root = parse_root_element()
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==table:
            elem.set('str_type',option)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def str_col_collection(profile, table, collist):
    tree, root = parse_root_element()
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')==table:
            node=elem.find("columns")
            for col in node.findall('column'):
                if col.get('name') in collist:
                    col.set('str_col', 'yes')
                elif col.get('name') not in collist:
                    col.set('str_col', 'no')
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def edit_table_column(profile, table_name, key, value, new_value, type, size, desc, search, lookup):
    tree, root = parse_root_element()
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == table_name:
            node = elem.find("columns")
            for col in node.findall('column'):
                if col.get(key) == value:
                    col.set(key, new_value)
                    col.set('oldname', value)
                    col.set('type', type)
                    col.set('size', size)
                    col.set('searchable',search)
                    if hasattr(col, 'lookup'):
                        col.set('lookup', lookup)
                    if desc != '':
                        col.set('fullname', desc)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def edit_geom_column(profile, table_name, key, value, new_value, type, srid):
    tree, root = parse_root_element()
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == table_name:
            node=elem.find("geometryz")
            for col in node.findall('geometry'):
                if col.get(key) == value:
                    col.set(key, new_value)
                    col.set('oldname', value)
                    col.set('type', type)
                    col.set('srid', srid)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def rename_table(profile, old_name, new_name, desc):
    tree, root = parse_root_element()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == old_name:
            elem.set('name', new_name)
            if desc != None:
                elem.set('fullname', desc)
        cnt_group = elem.find('contentgroups')
        if cnt_group:
            if cnt_group.get('name') == old_name:
                cnt_group.set('name', new_name)
                if desc != None:
                    cnt_group.set('fullname', desc)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')


def delete_table(level, table_name):
    tree, root = parse_root_element()
    for profile in root.findall('profile'):
        if profile.get('name')==level:
            tables = profile.findall('table')
            for table in tables:
                if table.get('name')==table_name:
                    profile.remove(table)
                else:
                    lookups=profile.findall('lookup')
                    for lkUp in lookups:
                        if lkUp.get('name')==table_name:
                            profile.remove(lkUp)
                    
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
    
def inherit_table_column(profile, source_table, dest_table):
    tree, root = parse_root_element()
    filter=(".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == source_table:
            for child in elem.findall('columns'):
                for node in child.findall('column'):
                    dict = node.attrib
                    #Remove the primary key definition from the source table
                    if dict.has_key('key'):
                        dict.pop("key")
                    write_table_column(dict, profile, 'table', dest_table, 'columns')

def write_profile(data):
    '''Add user defined profile'''
    tree, root = parse_root_element()
    profile = SubElement(root, 'profile', data)
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def check_profile(profile_name):
    tree, root = parse_root_element()
    for profile in root.findall('profile'):
        if profile.get('name') == profile_name:
            return profile.get('name')

def write_sql_file(drop_table=False):
    config_doc = Xml2Ddl()
    config_doc.setDbms("postgres")
    config_doc.params['drop-tables'] = drop_table
           
    xml = readMergeDict(SOURCE_PATH)
    results = config_doc.createTables(xml)
    file_handle = open(DEST_PATH, "w")

    for result in results:
        file_handle.write(result[1])
        file_handle.write("\n")

    file_handle.close()

def update_sql(drop_table=False):
    config_doc = DiffXml2Ddl()
    config_doc.setDbms("postgres")

    str_new_file = SOURCE_PATH
    str_old_file = OLD_PATH

    file_handle = open(DEST_PATH,"w")
    results = config_doc.diffFiles(str_old_file, str_new_file)
    for result in results:
        file_handle.write(result[1])
        file_handle.write("\n")
    file_handle.close()
    return results
 
def write_html():
    #Generate a html file from the configuration xml
    xml_2_html = Xml2Html()
    str_filename = SOURCE_PATH
    xml = readMergeDict(str_filename)
    lines = xml_2_html.outputHtml(xml)
    str_out_file = DEST_HTML
        
    of = open(str_out_file, "w")
    for line in lines:
        of.write("%s\n" % (line))
    of.close() 

def set_lookup_value(table_name, value_text):
    '''add lookup value specified by the user
    :type tableName: object
    '''
    tree, root = parse_root_element()
    node = None
    for elem in root.findall('profile/lookup'):
        if elem.get('name') == table_name:
            child = elem.find('data')
            if child is not None:
                node = SubElement(child, "value")
            if child is None:
                data_node = SubElement(elem, 'data')
                node = SubElement(data_node, "value")
            node.text = value_text
    tree.write(xml_doc, xml_declaration=True, encoding='utf-8')

def delete_lookup_choice(level, category, table_name, elemnt, key, value):
    tree, root = parse_root_element()
    for profile in root.findall('profile'):
        if profile.get('name') == level:
            tables = profile.findall(category)
            for table in tables:
                if table.get('name') == table_name:
                    node=table.find(elemnt)
                    for col in node.findall(key):
                        if col.text == value:
                            node.remove(col)
                            tree.write(xml_doc, xml_declaration=True, encoding='utf-8')
        else:
            continue

def write_display_name(layer_name, user_display_name):
    tree = Elt.parse(xml_doc)
    root = tree.getroot()

    if not root.findall('display_names'):
        display_names = Elt.SubElement(root, "display_names")

    elif root.findall('display_names'):
        display_names = root.findall('display_names')[0]

    display_name = Elt.SubElement(display_names, "display_name")
    display_name.set('layer_name', layer_name)
    display_name.text = user_display_name

    tree = Elt.ElementTree(root)
    tree.write(xml_doc,encoding='utf-8',xml_declaration=True)

def write_changed_display_name(current_layer_name, changed_layer_name):
    tree = Elt.parse(xml_doc)
    root = tree.getroot()

    for display_name in root.findall('display_names/display_name'):
        # if display_name.get("layer_name") == current_layer_name:
        if display_name.text == current_layer_name:
            display_name.text = changed_layer_name
            tree = Elt.ElementTree(root)
            tree.write(xml_doc,encoding='utf-8',xml_declaration=True)
            break
        else:
            continue
