"""
/***************************************************************************
Name                 : Generic application utility methods
Description          : Util functions
Date                 : 26/May/2013 
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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

import os, os.path
import tempfile
from decimal import Decimal
import binascii,string,random
from collections import OrderedDict
from datetime import (
    date,
    datetime
)

from PyQt4.QtCore import (
    QDir,
    Qt,
    QSettings,
    QFileInfo
)
from PyQt4.QtGui import (
    QPixmap,
    QFileDialog,
    QDialog,
    QMessageBox
)
from stdm.data.configuration import entity_model
from qgis.gui import QgsEncodingFileDialog


PLUGIN_DIR = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.path.pardir)).replace("\\", "/")
CURRENCY_CODE = "" #TODO: Put in the registry
DOUBLE_FILE_EXTENSIONS = ['tar.gz','tar.bz2']

def getIndex(listObj,item):
    '''
    Get the index of the list item without raising an 
    error if the item is not found
    '''
    index=-1
    try:
        index=listObj.index(item)
    except ValueError:
        pass
    return index 

def loadComboSelections(comboref,obj):
    '''
    Convenience method for loading lookup values in combo boxes
    '''
    modelinstance = obj()
    modelItems = modelinstance.queryObject().all()
    comboref.addItem("")
    for item in modelItems:
        comboref.addItem(item.value,item.id) 
            
def readComboSelections(obj):
    '''
    Convenience method for loading lookup values in combo boxes
    '''
    modelinstance = obj()
    modelItems = modelinstance.queryObject().all()
    return modelItems
    
    
def setModelAttrFromCombo(model,attributename,combo,ignorefirstitem = True): 
    '''
    Convenience method for checking whether an item in the combo box
    has been selected an get the corresponding integer stored in the
    item data.
    '''
    if combo.count() == 0:
        return
    
    if ignorefirstitem == True:
        if combo.currentIndex() == 0:
            return
    
    itemValue = combo.itemData(combo.currentIndex()) 
    setattr(model,attributename,itemValue)
    
def setComboCurrentIndexWithItemData(combo,itemdata,onNoneSetCurrentIndex = True):
    '''
    Convenience method for setting the current index of the combo item
    with the specified value of the item data.
    '''    
    if itemdata == None and onNoneSetCurrentIndex:
        combo.setCurrentIndex(0)
    elif itemdata == None and not onNoneSetCurrentIndex:
        return
    
    currIndex = combo.findData(itemdata)
    if currIndex != -1:
        combo.setCurrentIndex(currIndex)
        
def setComboCurrentIndexWithText(combo,text):
    """
    Convenience method for setting the current index of the combo item
    with the specified value of the corresponding display text.
    """
    txtIndex = combo.findText(text)
    if txtIndex != -1:
        combo.setCurrentIndex(txtIndex)
        
def createQuerySet(columnList,resultSet,imageFields):
    '''
    Create a list consisting of dictionary items
    derived from the database result set.
    For image fields, the fxn will write the binary object to disk
    and insert the full path of the image into the dictionary.    
    '''
    qSet=[]
    #Create root directory name to be used for storing the current session's image files
    rtDir=''
    if len(imageFields)>0:        
        rtDir=tempfile.mkdtemp()    
    for r in resultSet:           
        rowItems={}
        for c in range(len(columnList)): 
            clmName=str(columnList[c])
            #Get the index of the image field, if one has been defined
            imgIndex=getIndex(imageFields,clmName) 
            if imgIndex!=-1:
                imgPath=writeImage(rtDir,str(r[c]))
                rowItems[clmName]=imgPath
            else:                        
                rowItems[clmName]=str(r[c])        
        qSet.append(rowItems)       
    
    return rtDir,qSet

def writeImage(rootDir, imageStr):
    '''
    Write an image object to disk under the root directory in the
    system's temp directory. 
    The method returns the absolute path to the image.
    '''
    imgTemp = PLUGIN_DIR + '/images/icons/img_not_available.jpg'  
      
    try:
        os_hnd,imgPath = tempfile.mkstemp(suffix='.JPG',dir=rootDir)
        pimgPix = QPixmap()
        imgPix = pimgPix.scaled(80, 60, aspectRatioMode=Qt.KeepAspectRatio)
        lStatus=imgPix.loadFromData(imageStr) #Load Status
        
        if lStatus:
            wStatus=imgPix.save(imgPath) #Write Status
            if wStatus:
                imgTemp=imgPath  
        os.close(os_hnd)   
                       
    except:
        pass
    
    return imgTemp    
        
def copyattrs(objfrom, objto, names):
    #Copies named attributes over to another object
    for n in names:
        if hasattr(objfrom,n):
            v = getattr(objfrom,n)
            setattr(objto,n,v) 
            
def compareLists(validList, userList):
    #Method for validating if items defined in the user list actually exist in the valid list        
    validList = [x for x in userList if x in validList]    
    #Get invalid items in the user list    
    invalidList = [x for x in userList if x not in validList]
    
    return validList, invalidList
        
def replaceNoneText(dbvalue, replacewith=""):
    '''
    Replaces 'None' string with more friendly text.
    '''
    if str(dbvalue) == "None":
        return replacewith
    else:
        return dbvalue
        
def moneyfmt(value, places=2, curr=CURRENCY_CODE, sep=',', dp='.',
             pos='', neg='-', trailneg=''):
    """Convert Decimal to a money formatted string.

    places:  required number of places after the decimal point
    curr:    optional currency symbol before the sign (may be blank)
    sep:     optional grouping separator (comma, period, space, or blank)
    dp:      decimal point indicator (comma or period)
             only specify as blank when places is zero
    pos:     optional sign for positive numbers: '+', space or blank
    neg:     optional sign for negative numbers: '-', '(', space or blank
    trailneg:optional trailing minus indicator:  '-', ')', space or blank

    """
    q = Decimal(10) ** -places      
    sign, digits, exp = value.quantize(q).as_tuple()
    result = []
    digits = map(str, digits)
    build, next = result.append, digits.pop
    if sign:
        build(trailneg)
    for i in range(places):
        build(next() if digits else '0')
    build(dp)
    if not digits:
        build('0')
    i = 0
    while digits:
        build(next())
        i += 1
        if i == 3 and digits:
            i = 0
            build(sep)
    build(curr)
    build(neg if sign else pos)
    return ''.join(reversed(result))
        
def guess_extension(filename):
    """
    Extracts the file extension from the file name. It is also enabled to work with files 
    containing double extensions.
    """
    root,ext = os.path.splitext(filename)
    if any([filename.endswith(x) for x in DOUBLE_FILE_EXTENSIONS]):
        root,first_ext = os.path.splitext(root)
        ext = first_ext + ext
    return root,ext

def gen_random_string(numbytes=10):
    """
    Generates a random string based on the number of bytes specified.
    """
    return binascii.b2a_hex(os.urandom(numbytes))

def randomCodeGenerator(size=8):
    '''
    Automatically generates a string containing a random sequence of numbers and uppercase ASCII letters.
    '''
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def documentTemplates():
    """
    Return a dictionary of document names and their corresponding absolute file paths.
    """
    from stdm.settings.registryconfig import RegistryConfig

    docTemplates = OrderedDict()
    
    regConfig = RegistryConfig()
    keyName = "ComposerTemplates"
        
    pathConfig = regConfig.read([keyName])
        
    if len(pathConfig) > 0:
        templateDir = pathConfig[keyName]
        
        pathDir = QDir(templateDir)
        pathDir.setNameFilters(["*.sdt"])
        docFileInfos = pathDir.entryInfoList(QDir.Files,QDir.Name)
        
        for df in docFileInfos:
            docTemplates[df.completeBaseName()] = df.absoluteFilePath()
        
    return docTemplates
        
def openDialog( parent, filtering="GPX (*.gpx)", dialogMode="SingleFile"):
    settings = QSettings()
    dirName = settings.value( "/UI/lastShapefileDir" )
    encode = settings.value( "/UI/encoding" )
    fileDialog = QgsEncodingFileDialog( parent, "Save output file", dirName, filtering, encode )
    fileDialog.setFileMode( QFileDialog.ExistingFiles )
    fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
    if not fileDialog.exec_() == QDialog.Accepted:
            return None, None
    files = fileDialog.selectedFiles()
    settings.setValue("/UI/lastShapefileDir", QFileInfo( unicode( files[0] ) ).absolutePath() )
    if dialogMode == "SingleFile":
      return ( unicode( files[0] ), unicode( fileDialog.encoding() ) )
    else:
      return ( files, unicode( fileDialog.encoding() ) )


def datetime_from_string(str_val):
    """
    Converts a datetime in string value to the corresponding datetime object.
    :param str_val: Datetime
    :type str_val: str
    :return: Returns a datetime object from the corresponding string value.
    :rtype: datetime
    """
    return datetime.strptime(str_val, '%Y-%m-%d %H:%M:%S')


def date_from_string(str_val):
    """
    Converts a date in string value to the corresponding date object.
    :param str_val: Date in string.
    :type str_val: str
    :return: Returns a date object from the corresponding string value.
    :rtype: date
    """
    return datetime.strptime(str_val, '%Y-%m-%d')

def format_name(attr):
    """
    Formats the column names by removing id
    from lookups and fk columns and capitalize.
    Used for title and form labels
    :param attr: column name
    :return: string - formatted column name
    """
    if '_id' in attr:
        if attr != 'national_id':
            display_name = attr[:-3]
            display_name = display_name.replace('_', ' ').title()
        else:
            display_name = 'National ID'
    else:
        display_name = attr.replace('_', ' ').title()

    return display_name

def entity_display_columns(entity):
    display_column = [
        c.name
        for c in
        entity.columns.values()
        if c.TYPE_INFO in [
            'VARCHAR',
            'SERIAL',
            'TEXT',
            'BIGINT',
            'DOUBLE',
            'DATE',
            'DATETIME',
            'YES_NO',
            'LOOKUP',
            'ADMIN_SPATIAL_UNIT',
            'MULTIPLE_SELECT'
        ]
    ]
    return display_column

def entity_searchable_columns(entity):
    searchable_column = [
        c.name
        for c in
        entity.columns.values()
        if c.searchable
    ]
    return searchable_column

def model_display_data(model, entity, profile):

    model_display = OrderedDict()
    model_dic = model.__dict__
    for key, value in model_dic.iteritems():
        if key in entity_display_columns(entity) and key != 'id':
            value = lookup_id_to_value(profile, key, value)
            model_display[format_name(key)] = value
    return model_display

def model_display_mapping(model):
    model_display_cols = OrderedDict()
    model_dic = model.__dict__
    for col in model_dic:
        model_display_cols[col] = format_name(col)
    return model_display_cols

def profile_spatial_tables(profile):
    spatial_tables = [
        (e.name, e.short_name)
        for e in
        profile.entities.values()
        if e.TYPE_INFO == 'ENTITY' and e.has_geometry_column()
    ]
    spatial_tables = dict(spatial_tables)
    return spatial_tables

def profile_user_tables(profile, include_views=True):
    from stdm.data.pg_utils import (
        pg_views
    )
    tables = [
        (e.name, e.short_name)
        for e in
        profile.entities.values()
        if e.TYPE_INFO in [
            'ENTITY',
            'ENTITY_SUPPORTING_DOCUMENT',
            'SOCIAL_TENURE',
            'SUPPORTING_DOCUMENT'
        ]
    ]
    if include_views:
        tables = dict(tables)
        for view in pg_views():
            tables[view] = view

    return tables


def profile_lookup_columns(profile):
    lookup_columns = [
        r.child_column for r in profile.relations.values()
    ]
    return lookup_columns

def lookup_parent_entity(profile, col):
    parent_entity = [
        r.parent for r in profile.relations.values()
        if r.child_column == col
    ]
    return parent_entity[0]


def model_lookup_id_to_value(id, db_model):

    if isinstance(id, int):
        db_obj = db_model()
        query = db_obj.queryObject().filter(
            db_model.id == id
        ).all()

        value = getattr(
            query[0],
            'value',
            None
        )
        return value
    else:
        return id

def lookup_id_to_value(profile, col, id):
    if col in profile_lookup_columns(profile):
        parent_entity = lookup_parent_entity(profile, col)
        db_model = entity_model(parent_entity)
        db_obj = db_model()
        query = db_obj.queryObject().filter(
            db_model.id == id
        ).first()
        if query is not None:
            value = getattr(
                query,
                'value',
                None
            )
            return value
        else:
            return id
    else:
        return id

