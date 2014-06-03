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
from decimal import Decimal
import binascii,string,random
from collections import OrderedDict

from PyQt4.QtCore import QDir

from stdm.settings import RegistryConfig

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
        comboref.addItem(item.name,item.id) 
            
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
    
    itemValue,ok = combo.itemData(combo.currentIndex()).toInt()  
    setattr(model,attributename,itemValue)
    
def setComboCurrentIndexWithItemData(combo,itemdata,onNoneSetCurrentIndex = True):
    '''
    Convenience method for setting the current index of the combo item
    with the specified value of the item data
    '''    
    if itemdata == None and onNoneSetCurrentIndex:
        combo.setCurrentIndex(0)
    elif itemdata == None and not onNoneSetCurrentIndex:
        return
    
    currIndex = combo.findData(itemdata)
    if currIndex != -1:
        combo.setCurrentIndex(currIndex)
        
def replaceNoneText(dbvalue,replacewith=""):
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
    '''
    Extracts the file extension from the file name. It is also enabled to work with files 
    containing double extensions.
    '''
    root,ext = os.path.splitext(filename)
    if any([filename.endswith(x) for x in DOUBLE_FILE_EXTENSIONS]):
        root,first_ext = os.path.splitext(root)
        ext = first_ext + ext
    return root,ext

def gen_random_string(numbytes=10):
    '''
    Generates a random string based on the number of bytes specified.
    '''
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
        

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     


    