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


from collections import OrderedDict
from PyQt4.QtGui import *

from xml.etree.ElementTree import ElementTree as ET
import xml.etree.ElementTree as Elt

from configfile_paths import FilePaths
from stdm.data.enums import non_editable_tables

try:
    xml_object = FilePaths()
    xml_doc = xml_object.set_user_xml_file()
    html_doc = xml_object.html_file()
except Exception as ex:
    raise ex

def parse_root_element():
    if not xml_doc:
        return
    else:
        tree = ET()
        root = tree.parse(xml_doc)
        return tree, root   

def xml_table_element(profile):
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

def check_table_exist(profile, table_name):
    is_found = False
    tree, root = parse_root_element()
    level = (".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
         if elem.get('name') == table_name:
             is_found = True
    return is_found

def table_column_exist(profile, table_name, idcol):
    is_found = False
    tree, root = parse_root_element()
    level = (".//*[@name='%s']/table")%profile
    for elem in root.findall(level):
         if elem.get('name') == table_name:
             for child in elem.findall('columns/column'):
                if child.get('name') == idcol:
                    is_found = True
    return is_found
        
def delete_profile(profile_name):
    tree, root = parse_root_element()
    for elem in root.findall('profile'):
        if elem.get('name') == profile_name:
            root.remove(elem)
    tree.write(xml_doc)

def profile_full_description(profile):
    tree, root = parse_root_element()
    for elem in root.findall('profile'):
        if elem.get('name') == profile:
            return elem.get('fullname')

def table_full_description(profile):
    tree, root = parse_root_element()
    table_desc = []
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        ordDict = OrderedDict()
        ordDict["Name"] = elem.get('name')
        ordDict["Description"]= elem.get('fullname')
        table_desc.append(ordDict)
    return table_desc

def table_columns(profile, table_name):
    #scan the xml file and return all the table defined columns information
    tree, root = parse_root_element()
    table_data = []
    bool = False
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name') == table_name:
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
                table_data.append(ordDict)                          
    return table_data

def social_tenure_tables(profile):
    """
    Method to read tables that are part of STR definition
    """
    tree,root = parse_root_element()
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
    tree,root = parse_root_element()
    party_table =''
    sp_table = ''
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('is_str_table')== 'yes' and elem.get('str_type')=='party':
            party_table = elem.get('name')
        if elem.get('is_str_table')== 'yes' and elem.get('str_type')== 'spatial unit':
            sp_table = elem.get('name')
    return party_table, sp_table

def table_lookup_collection():
    tree, root = parse_root_element()
    tableDict = ['table','lookup']
    table=[]
    for name in tableDict:
        pLevel = ('profile/%s')%name
        for elem in root.findall(pLevel):
            table.append(elem.get('name'))
    return table

def lookup_column(table_name):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root = tree.parse(xml_doc)
    table_data = []
    for elem in root.findall("profile/lookup"):
        if elem.get('name') == table_name:
            for child in elem[0]:
                ordDict=OrderedDict()
                ordDict["Column label"] = child.get('name')
                ordDict["Description"] = child.get('fullname')
                ordDict["Data type"] = child.get('type')
                ordDict["Length"] = child.get('size')
                ordDict["Lookups"] = bool
                table_data.append(ordDict)                           
    return table_data

def lookup_table():
    tree = ET()
    root = tree.parse(xml_doc)
    table = []
    for elem in root.findall('profile/lookup'):
        table.append(elem.get('name'))
    return table
    
def columns(table_name):
    #scan the xml file and return all the table defined columns information
    tree = ET()
    root = tree.parse(xml_doc)
    tab_cols={}
    bool=False
    for elem in root.findall('table'):
        if elem.get('name') == table_name:
            for child in elem[0]:
                tab_cols = child.attrib
    return tab_cols

def profiles():
    tree, root = parse_root_element()
    pfList = []
    for profile in root.findall('profile'):
        pfList.append(profile.get('name'))
    return pfList
    
def table_relations(table_name, element):
    tree,root = parse_root_element()
    relation_data = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == table_name:
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
                    relation_data.append(ordDict) 
                return relation_data  
            
def geometry_columns(table_name, element):
    tree, root = parse_root_element()
    geom_data = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == table_name:
            childs = elem.find(element)
            if childs:
                for child in childs:
                    ordDict=OrderedDict()
                    ordDict["Table Name"] = child.get('table')
                    ordDict["Geometry Column Name"] = child.get('column')
                    ordDict["Geometry Type"] = child.get('type')
                    ordDict["Projection"] = child.get('srid')
                    ordDict["Schema"] = 'default'
                    geom_data.append(ordDict) 
    return geom_data

def lookup_data(table_name):    
    lst_lookup = []
    tree, root = parse_root_element()
    for elem in root.findall('profile/lookup'):
        if elem.get('name') == table_name:
            child = elem.find('data')
            if child is None:
                return
            else:
                lookups = child.findall('value')
                for text in lookups:
                    lst_lookup.append(text.text)
            return lst_lookup

def lookup_data2_list(profile, table_name):
    '''read lookup data list values for generation of insert statement'''
    tree, root = parse_root_element()
    lk_vals = []
    filter = (".//*[@name='%s']/lookup")%profile
    for elem in root.findall(filter):
        if elem.get('name') == table_name:
            for child in elem.findall('data'):
                for node in child.findall('value'):
                    lk_vals.append(node.text)
    return lk_vals

def content_group(table_name):
    tree, root = parse_root_element()
    code_list = []
    for elem in root.findall('profile/table'):
        if elem.get('name') == table_name:
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
    tree,root = parse_root_element()
    str_table = []
    filter = (".//*[@name='%s']/table")%profile
    for elem in root.findall(filter):
        if elem.get('name')== table:
            return elem.get('fullname')

def read_str_col_collection(profile, table):
    tree, root = parse_root_element()
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
    tree, root = parse_root_element()
    for elem in root.findall('config'):
        if elem is not None:
            return elem.get('version')
        else:
            return 0

