"""
/***************************************************************************
Name                 : PyQT model formatters
Description          : When using foreign key relations in a table model, it
                       is useful to display the information derived from the
                       foreign key table rather than display the id of the 
                       foreign key. Hence, these classes are ideal for using 
                       in Qt models for displaying the text/or custom object
                       properties as well as setting the model data
Date                 : 13/June/2013 
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from database import Enumerator, Respondent, CheckGender,CheckMaritalStatus, \
CheckRespondentType,CheckWitnessRelationship,CheckSavingsOption,CheckInputService, \
CheckSocioEconomicImpact,CheckFoodCropCategory,STDMDb

def intFromQType(intitem):
    '''
    OBSOLETE:Converts integer from QVariant or QString to Python int, otherwise returns -1
    '''
    pyint = intitem   
    if isinstance(intitem,QVariant) or isinstance(intitem,QString):
        qint, ok = intitem.toInt()
        if ok:
            pyint = qint
    return pyint

def dateFromQType(dateitem):
    '''
    Converts date from QVariant or QDate to Python Date
    '''
    pydate = dateitem   
    if isinstance(pydate,QVariant):        
        pydate = pydate.toDate()
    if isinstance(pydate,QDate):        
        pydate = pydate.toPyDate()
               
    return pydate    

class LookupFormatter(object):
    """
    Formatter for displaying user-friendly information about a checkup model
    """
    def __init__(self,model):
        self._model = model
        self._modelInstance = self._model()
        
    def setDisplay(self,itemid):
        """
        Set display information
        """
        md = self._modelInstance.queryObject().filter(self._model.id == itemid).first()
        if md:            
            return md.name
        else:
            return QPyNullVariant
        
class BasePersonFormatter(LookupFormatter):
    """
    Formatter for classes that implement base person mixin. It formats the object to
    return a string containing the first and last names.
    """
    def setDisplay(self, itemid):
        md = self._modelInstance.queryObject().filter(self._model.id == itemid).first()
        if md:            
            return "{0} {1}".format(md.FirstName,md.LastName)
        else:
            return QPyNullVariant

def geometryFormatter(geom):
    '''
    Reads point data in WKB format to X,Y coordinate value.
    '''
    x = y = 0
    
    dbSession = STDMDb.instance().session
    geomType = dbSession.scalar(geom.ST_GeometryType())
    if geomType == "ST_Point":
        x = dbSession.scalar(geom.ST_X())
        y = dbSession.scalar(geom.ST_Y())
    
    return "X: {0}, Y: {1}".format(str(x),str(y))

def dateFormatter(dt):
    """
    Formats the date object to a string representation.
    """
    return dt.strftime("%d-%b-%Y")
            
def respondentRoleFormatter(roleId):
    lkFormatter = LookupFormatter(CheckRespondentType)
    return lkFormatter.setDisplay(roleId)

def respondentNamesFormatter(respondentId):
    bpFormatter = BasePersonFormatter(Respondent)
    return bpFormatter.setDisplay(respondentId)

def enumeratorNamesFormatter(enumeratorId):
    bpFormatter = BasePersonFormatter(Enumerator)
    return bpFormatter.setDisplay(enumeratorId)

def witnessRelationshipFormatter(relationshipId):
    lkFormatter = LookupFormatter(CheckWitnessRelationship)
    return lkFormatter.setDisplay(relationshipId)

def genderFormatter(genderId):
    lkFormatter = LookupFormatter(CheckGender)
    return lkFormatter.setDisplay(genderId)

def maritalStatusFormatter(mStatusId):
    lkFormatter = LookupFormatter(CheckMaritalStatus)
    return lkFormatter.setDisplay(mStatusId)

def savingOptionFormatter(optionId):
    lkFormatter = LookupFormatter(CheckSavingsOption)
    return lkFormatter.setDisplay(optionId)

def inputServiceFormatter(serviceId):
    lkFormatter = LookupFormatter(CheckInputService)
    return lkFormatter.setDisplay(serviceId)

def socioEconImpactFormatter(impactId):
    lkFormatter = LookupFormatter(CheckSocioEconomicImpact)
    return lkFormatter.setDisplay(impactId)

def foodCropCategoryFormatter(foodCropId):
    lkFormatter = LookupFormatter(CheckFoodCropCategory)
    return lkFormatter.setDisplay(foodCropId)
    
class DoBFormatter(object):
    '''
    Formatter for displaying the current age (in years) calculated from the date of birth
    '''
    def setDisplay(self,dob):
        '''
        Set display information
        '''
        dob = dateFromQType(dob)        
        if dob > QDate.currentDate().toPyDate():
            return QVariant()
        
        tmDelta = (QDate.currentDate().toPyDate()) - dob
        diffDays = tmDelta.days
        years = diffDays/365.2425
        
        return int(years)
    
class LocalityFormatter(object):
    '''
    Formatter for displaying user-friendly information about a locality
    '''
    def __init__(self):
        self.locality = Locality()
        
    def setDisplay(self,locality):
        '''
        Display the area name and street number
        '''
        if isinstance(locality,int):                     
            loc = self.locality.queryObject().filter(Locality.id == locality).first()
            if loc:                
                locality = loc                
            else:
                return QVariant("")
         
        localityInfo = ("%s - %s")%(locality.area,locality.street_number)
        
        return QVariant(localityInfo)
        
        
            
    
    
    
    
        
        
        
        
        