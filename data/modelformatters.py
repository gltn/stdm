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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def int_from_qtype(intitem):
    '''
    OBSOLETE:Converts integer from QVariant or QString to Python int, otherwise returns -1
    '''
    pyint = intitem   
    if isinstance(intitem,QVariant) or isinstance(intitem,QString):
        qint, ok = intitem.toInt()
        if ok:
            pyint = qint
    return pyint

def date_from_qtype(dateitem):
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
        self._model_instance = self._model()
        
    def set_display(self, itemid):
        """
        Set display information
        """
        md = self._model_instance.queryObject().filter(self._model.id == itemid).first()
        if md:            
            return md.name
        else:
            return QPyNullVariant
        
class BasePersonFormatter(LookupFormatter):
    """
    Formatter for classes that implement base person mixin. It formats the object to
    return a string containing the first and last names.
    """
    def set_display(self, itemid):
        md = self._model_instance.queryObject().filter(self._model.id == itemid).first()
        if md:            
            return "{0} {1}".format(md.FirstName,md.LastName)
        else:
            return QPyNullVariant

def geometry_formatter(geom):
    '''
    Reads point data in WKB format to X,Y coordinate value.
    '''
    x = y = 0
    
    dbSession = STDMDb.instance().session
    geom_type = dbSession.scalar(geom.ST_GeometryType())
    if geom_type == "ST_Point":
        x = dbSession.scalar(geom.ST_X())
        y = dbSession.scalar(geom.ST_Y())
    
    return "X: {0}, Y: {1}".format(str(x),str(y))

def date_formatter(dt):
    """
    Formats the date object to a string representation.
    """
    return dt.strftime("%d-%b-%Y")
            
def respondent_role_formatter(role_id):
    lk_formatter = LookupFormatter(CheckRespondentType)
    return lk_formatter.set_display(role_id)

def respondent_names_formatter(respondent_id):
    bp_formatter = BasePersonFormatter(Respondent)
    return bp_formatter.set_display(respondent_id)

def enumerator_names_formatter(enumerator_id):
    bp_formatter = BasePersonFormatter(Enumerator)
    return bp_formatter.set_display(enumerator_id)

def witness_relationship_formatter(relationship_id):
    lk_formatter = LookupFormatter(CheckWitnessRelationship)
    return lk_formatter.set_display(relationship_id)

def gender_formatter(gender_id):
    lk_formatter = LookupFormatter(CheckGender)
    return lk_formatter.set_display(gender_id)

def marital_status_formatter(mStatus_id):
    lk_formatter = LookupFormatter(CheckMaritalStatus)
    return lk_formatter.set_display(mStatus_id)

def saving_option_formatter(option_id):
    lk_formatter = LookupFormatter(CheckSavingsOption)
    return lk_formatter.set_display(option_id)

def input_service_formatter(service_id):
    lk_formatter = LookupFormatter(CheckInputService)
    return lk_formatter.set_display(service_id)

def socio_econ_impact_formatter(impact_id):
    lk_formatter = LookupFormatter(CheckSocioEconomicImpact)
    return lk_formatter.set_display(impact_id)

def food_crop_category_formatter(food_crop_id):
    lk_formatter = LookupFormatter(CheckFoodCropCategory)
    return lk_formatter.set_display(food_crop_id)
    
class DoBFormatter(object):
    '''
    Formatter for displaying the current age (in years) calculated from the date of birth
    '''
    def set_display(self,dob):
        '''
        Set display information
        '''
        dob = date_from_qtype(dob)        
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
        
    def set_display(self,locality):
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
        
