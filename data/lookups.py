#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
          
"""
/***************************************************************************
Name                 : Table Lookup values
Description          : Lookup values for tables. This is a quickfix for 
                       defining lookup values. This will be used to complement
                       a lookup management module in the future.
Date                 : 22/June/2013 
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
from PyQt4.QtGui import QApplication

from .database import *

from stdm.settings.registryconfig import (
    RegistryConfig,
    DATABASE_LOOKUP
)

'''
Format of the dictionary:
key =  Name of the STDM lookup model
value = List of lookup values to be inserted
'''

stdm_lookups = {
                "CheckGender":[QApplication.translate("Lookup","Male"),QApplication.translate("Lookup","Female")],
                "CheckMaritalStatus":[QApplication.translate("Lookup","Cohabiting"),
                                      QApplication.translate("Lookup","Divorced"),
                                      QApplication.translate("Lookup","Married"),
                                      QApplication.translate("Lookup","Separated"),
                                      QApplication.translate("Lookup","Single"),
                                      QApplication.translate("Lookup","Widow"),
                                      QApplication.translate("Lookup","Widower")],
                "CheckRespondentType":[QApplication.translate("Lookup","Child of Farmer"),
                                      QApplication.translate("Lookup","Farm Manager"),
                                      QApplication.translate("Lookup","Laborer"),
                                      QApplication.translate("Lookup","Smallholder Farmer"),
                                      QApplication.translate("Lookup","Spouse"),
                                      QApplication.translate("Lookup","Other")],
                "CheckWitnessRelationship":[QApplication.translate("Lookup","Unit Leader"),
                                      QApplication.translate("Lookup","Other")],
                "CheckSocialTenureRelationship":[QApplication.translate("Lookup","Adverse Possession"),
                                        QApplication.translate("Lookup","Communal Ownership"),
                                        QApplication.translate("Lookup","Family Ownership"),
                                        QApplication.translate("Lookup","Individual Ownership"),
                                        QApplication.translate("Lookup","Farming"),
                                        QApplication.translate("Lookup","Tenancy")],
                "CheckHouseUseType":[QApplication.translate("Lookup","Residential"),
                                        QApplication.translate("Lookup","Residential Cum Business")],
                "CheckLandType":[QApplication.translate("Lookup","Kibanja"),
                                        QApplication.translate("Lookup","Mailo"),
                                        QApplication.translate("Lookup","Public"),
                                        QApplication.translate("Lookup","Other")],
                "CheckHouseType":[QApplication.translate("Lookup","Permanent"),
                                        QApplication.translate("Lookup","Semi-Permanent"),
                                        QApplication.translate("Lookup","Temporary")],
                "CheckSocioEconomicImpact":[QApplication.translate("Lookup","Improved Access to Financial Services"),
                                        QApplication.translate("Lookup","Improved Access to Health"),
                                        QApplication.translate("Lookup","Improved Housing Conditions"),
                                        QApplication.translate("Lookup","Improved Literacy Levels"),
                                        QApplication.translate("Lookup","Improved Tenure Security"),
                                        QApplication.translate("Lookup","Other")],
                "CheckSavingsOption":[QApplication.translate("Lookup","Bank"),
                                        QApplication.translate("Lookup","House"),
                                        QApplication.translate("Lookup","Not Saving"),
                                        QApplication.translate("Lookup","Saving Group"),
                                        QApplication.translate("Lookup","Other")],
                "CheckFoodCropCategory":[QApplication.translate("Lookup","Intercrop"),
                                        QApplication.translate("Lookup","Purestand")],
                "CheckInputService":[QApplication.translate("Lookup","Farm Tools"),
                                        QApplication.translate("Lookup","Fertilizer"),
                                        QApplication.translate("Lookup","Herbicides"),
                                        QApplication.translate("Lookup","Pesticides"),
                                        QApplication.translate("Lookup","Seedlings"),
                                        QApplication.translate("Lookup","Training"),
                                        QApplication.translate("Lookup","Other")]
               }

def initLookups():
    '''
    Loads the initial lookup values into the STDM database.
    First check if there is a flag in the registry for asserting whether the lookup values have been initialized.
    If False or the key does not exist then initialize then set key to True
    '''                
    regConfig = RegistryConfig()            
    lookupReg = regConfig.read([DATABASE_LOOKUP])
    
    if len(lookupReg) == 0 :
        loadLookups()  
    else:
        lookupState = lookupReg[DATABASE_LOOKUP].lower()  
        if lookupState == "false":loadLookups()            
                                                
def loadLookups():
    for k,v in stdm_lookups.iteritems():
            modelName = k
            Values = v
            model = globals()[modelName]
            modelInstance = model()
            queryObj = modelInstance.queryObject()
            
            #Ensure item does not exist before being inserted
            for lk in v:
                #Convert QString to Python string
                lk = unicode(lk)
                lkObj = queryObj.filter(model.name == lk).first()
                if lkObj == None:
                    lkInst = model()                
                    lkInst.name = lk
                    lkInst.save()  
    
    #Update registry
    regConfig = RegistryConfig()            
    regConfig.write({DATABASE_LOOKUP:str(True)})  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
