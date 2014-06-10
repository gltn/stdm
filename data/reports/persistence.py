"""
/***************************************************************************
Name                 : Persistence
Description          : LEGACY CODE: Module for report persistence (loading 
                       and saving custom report setting files) in *.trs format.
Date                 : 11/November/2013 
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
import pickle

from PyQt4.QtGui import QFont

class STDMReportConfig(object):
    '''
    Configuration of STDM reports for serialization to file
    '''
    def __init__(self,table):
        self.table = table
        
        #Report Elements Container
        self.reportElementCollection = []
        
        #Simple container for field names
        self.fields = []
        self.filter = ""
        self.version = 1.0
    
    def addElement(self,rptElement):
        '''
        Add Report Element to the collection
        '''
        self.reportElementCollection.append(rptElement)
        if rptElement.parent == "Fields":
            self.fields.append(rptElement.name)
        
    def setFilter(self,filter):
        '''
        Set report filter statement
        '''
        self.filter = filter
        
    def setVersion(self,number):
        '''
        Set report version number
        '''
        self.version = number

class ReportSerializer(object):
    '''
    Handles serialization/deserialization of STDMReportConfig object
    '''
    def __init__(self,reportPath):        
        self.rptPath=reportPath
        
    def serialize(self,reportConfig):
        '''
        Serialize report object to file 
        '''
        success = False
        try:
            with open(self.rptPath,'wb') as f:            
                pickle.dump(reportConfig, f,2)
            success = True
        except:
            pass
        return success
            
    def deserialize(self):
        '''
        Deserialize report config object
        '''
        rptConfig = None
        valid = False
        try:            
            with open(self.rptPath,'rb') as f:
                rptConfig = pickle.load(f)
                if rptConfig.version >= 1:
                    valid = True
        except:
            pass
        return valid,rptConfig
            
class Validator(object):
    '''
    Abstract base class for validating objects
    '''
    def __init__(self):
        self.message=""
        self.isValid=False
        
class SFont(object):
    '''
    STDM Font.
    PyQt classes cannot be pickled hence this class wraps QFont attributes 
    into the elementary data types which are reconstructed on-the-fly
    after deserialization 
    '''
    def __init__(self,qf):        
        self._family = str(qf.family())
        self._pointSize = qf.pointSize()
        self._weight = qf.weight()
        self._italic = qf.italic()
        self._underline = qf.underline()
    def font(self):        
        qFont = QFont(self._family,self._pointSize,self._weight)
        qFont.setItalic(self._italic)
        qFont.setUnderline(self._underline)
        return qFont
        
class BaseDialogSettings(object):
    '''
    Abstract class for report element display settings
    '''
    def __init__(self):
        self.top = 0
        self.left = 0
        
class TitleDialogSettings(BaseDialogSettings):
    '''
    General purpose settings
    '''
    def __init__(self):
        self.border = "None"
        self.foreColor = None        
        self.font = None #SFont type object
        self.height = 0.5
        self.hAlighment = "Left"
        self.displayName = ""
        self.vAlignment = "Top"
        self.width = 3 
        
class LayoutDialogSettings(BaseDialogSettings):
    '''
    Page Layout Settings
    '''
    def __init__(self):
        self.size = "A4"
        self.orientation = "Potrait"
        self.bottom = 1
        self.right = 1
        
class FieldDialogSettings(TitleDialogSettings):
    '''
    Settings for database field
    '''
    def __init__(self):
        self.isImage = False
        
class ReportElement(object):
    '''
    Base class element for STDM report
    '''
    def __init__(self):
        #Takes in an object of type BaseDialogSettings
        self.dialogSettings = None
        #Parent tree element name
        self.parent = ""
        #Element name
        self.name = ""
        
class DbField(ReportElement):
    '''
    Report Element implementation for a database field
    '''
    def __init__(self):        
        #object of type FieldConfig
        self.uiConfiguration = None 
        
class FieldConfig(object):
    '''
    Class for defining the UI configuration for a database field
    '''
    def __init__(self):
        self.reportOrder = 0
        #object of type GroupSettings
        self.groupingInfo = None
        #object of type FieldSort
        self.sortInfo = None
        
class GroupSettings(object):
    '''
    Group settings of the report
    '''
    def __init__(self):
        self.isInGroup = False
        self.order = 0
        #object of type title dialog settings
        self.dialogSettings = None
        
class SortDir(object):
    '''
    Enumeration of the sort direction
    '''
    (Null,Ascending,Descending) = range(0,3)
    
class FieldSort(object):
    '''
    Field sorting property container
    '''
    def __init__(self):
        self.direction = SortDir.Null
        self.order = 0
        
        