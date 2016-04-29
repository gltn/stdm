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

from qgis.gui import QgsEncodingFileDialog

from stdm.data.configuration.profile import Profile
from stdm.data.configuration.stdm_configuration import StdmConfiguration
from stdm.settings.registryconfig import (
    CURRENT_PROFILE,
    RegistryConfig
)

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

def current_profile():
    """
    :return: Returns the current profile in the configuration currently
    being used.
    :rtype: Profile
    """
    reg_config = RegistryConfig()
    profile_info = reg_config.read([CURRENT_PROFILE])
    profile_name = profile_info.get(CURRENT_PROFILE, '')

    #Return None if there is no current profile
    if not profile_name:
        return None

    profiles = StdmConfiguration.instance().profiles

    return profiles.get(unicode(profile_name), None)

def save_current_profile(name):
    """
    Save the profile with the given name as the current profile.
    :param name: Name of the current profile.
    :type name: unicode
    """
    if not name:
        return

    #Save profile in the registry/settings
    reg_config = RegistryConfig()
    reg_config.write({CURRENT_PROFILE: name})

def show_message(message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("STDM")
    msg.setText(message)
    msg.exec_()