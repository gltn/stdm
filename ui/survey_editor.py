"""
/***************************************************************************
Name                 : New Survey
Description          : Dialog for entering new survey information.
Date                 : 8/March/2014 
copyright            : (C) 2014 by John Gitau
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
from datetime import datetime

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.data import Enumerator,Survey,Witness, MapperMixin

from stdm.utils import randomCodeGenerator
from .ui_survey import Ui_frmSurvey
from .admin_unit_manager import VIEW, MANAGE,SELECT
from .helpers import SupportsManageMixin
from .entity_browser import EnumeratorEntityBrowser,RespondentEntityBrowser, \
WitnessEntityBrowser
from .notification import NotificationBar
from .stdmdialog import declareMapping

__all__ = ["SurveyEditor"]

class SurveyEditor(QDialog,Ui_frmSurvey,MapperMixin):
    '''
    Dialog for entering new survey information.
    '''
    def __init__(self,parent = None,model = Survey):
        QDialog.__init__(self,parent)
        self.setupUi(self)
        MapperMixin.__init__(self,model)
        
        #Connect signals
        self.buttonBox.accepted.connect(self.submit)
        self.buttonBox.rejected.connect(self.cancel)
        
        #Set current date as maximum date
        currDate = QDate.currentDate()
        self.dtEnumDate.setMaximumDate(currDate)
        self.dtEnumDate.setDate(currDate)
        
        self._notifBar = NotificationBar(self.vlNotification)
        
        #Configure Enumerator FK mapper
        enumFKMapper = self.tabWidget.widget(0)
        enumFKMapper.setDatabaseModel(Enumerator)
        enumFKMapper.setEntitySelector(EnumeratorEntityBrowser)
        enumFKMapper.setSupportsList(False)
        #enumFKMapper.addCellFormatter("GenderID",genderFormatter)
        #enumFKMapper.addCellFormatter("MaritalStatusID",maritalStatusFormatter)
        enumFKMapper.setNotificationBar(self._notifBar)
        enumFKMapper.initialize()
        
        mapping=declareMapping.instance()
        tableCls=mapping.tableMapping('respondent')
        
        
        respondentFKMapper = self.tabWidget.widget(1)
        respondentFKMapper.setDatabaseModel(tableCls)
        respondentFKMapper.setEntitySelector(RespondentEntityBrowser,VIEW|MANAGE)
        
        witnessFKMapper = self.tabWidget.widget(2)
        witnessFKMapper.setDatabaseModel(Witness)
        witnessFKMapper.setEntitySelector(WitnessEntityBrowser,VIEW|MANAGE)
        witnessFKMapper.setSupportsList(True)
        
#         #Configure Respondent FK mapper
#         respondentFKMapper = self.tabWidget.widget(1)
#         #respondentFKMapper.setDatabaseModel(Respondent)
        
#         respondentFKMapper.setSupportsList(False)
#         #respondentFKMapper.addCellFormatter("GenderID",genderFormatter)
#         #respondentFKMapper.addCellFormatter("MaritalStatusID",maritalStatusFormatter)
#         #respondentFKMapper.addCellFormatter("RoleID",respondentRoleFormatter)
        respondentFKMapper.setNotificationBar(self._notifBar)
#         respondentFKMapper.initialize()
#         
#         #Configure Witnesses FK mapper
         
#         #witnessFKMapper.addCellFormatter("GenderID",genderFormatter)
#         #witnessFKMapper.addCellFormatter("MaritalStatusID",maritalStatusFormatter)
#         #witnessFKMapper.addCellFormatter("RelationshipID",witnessRelationshipFormatter)
        witnessFKMapper.setNotificationBar(self._notifBar)
#         witnessFKMapper.initialize()
        
        #Configure attribute mappings
        self.addMapping("Code", self.txtSurveyCode, preloadfunc = self.codeGenerator())
        self.addMapping("EnumerationDate", self.dtEnumDate)
        #self.addMapping("Enumerator", enumFKMapper,True)
        #self.addMapping("Respondent", respondentFKMapper,True)
       # self.addMapping("Witnesses", witnessFKMapper,True)
        
    def codeGenerator(self):
        """
        Survey code generator function which is based on current date/time and a 
        randomly generated 6-digit code.
        """
        rdCode = randomCodeGenerator(5)
        currDate = datetime.now()
        currDateStr = currDate.strftime("%Y%m%d%H%M")[:-1]
        
        return "{0}-{1}".format(currDateStr,rdCode)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        