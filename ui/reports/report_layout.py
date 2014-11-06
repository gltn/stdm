"""
/***************************************************************************
Name                 : STDM Report layout
Description          : General Page Settings of the Report
Date                 : 15/November/11 
copyright            : (C) 2011 by John Gitau
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
from PyQt4.QtGui import * 

import reportlab.lib.pagesizes
from reportlab.lib.pagesizes import *
from reportlab.lib.units import cm,inch

from geraldo import Report

from stdm.utils import *
from stdm.data.reports import (
                               LayoutDialogSettings, 
                               ReportElement
                               )

from .ui_rpt_layout import Ui_frmRptLayout

class ReportLayout(QWidget,Ui_frmRptLayout):     
    #Class constructor  
    def __init__(self,id,parent=None):         
        QWidget.__init__(self,parent)
        
        #Call the initialize component method
        self.setupUi(self)
          
        #Form identifier  
        self.ID = id     
         
        #Report Element Container
        self._rptEl = ReportElement()
        self._rptEl.parent = "Elements"
        self._rptEl.name = id  
        
        #Initialize variables
        self.initVars()
        
        #Initialize control
        self.initControls()
    
    def initVars(self):
        #Initialize class properties            
        self.topMargin = 1*cm  
        self.bottomMargin = 1*cm
        self.leftMargin = 1*cm
        self.rightMargin = 1*cm
        self.pageSize = A4 
        
    def initControls(self):
        #Initialize the controls' settings
        self.cboPageSize.setCurrentIndex(4)
        self.cboPageOrien.setCurrentIndex(0)
        settingVal = QDoubleValidator(0,10,2,self)
        self.txtTopMargin.setValidator(settingVal)
        self.txtBtMargin.setValidator(settingVal)
        self.txtLeftMargin.setValidator(settingVal)
        self.txtRightMargin.setValidator(settingVal)
        
    def PageSize(self):
        pgOrientation = self.cboPageOrien.currentText()
        pgSize=getattr(reportlab.lib.pagesizes,str(self.cboPageSize.currentText()))
        
        if pgOrientation == "Landscape":
            self.pageSize = landscape(pgSize)
        else:
            self.pageSize = portrait(pgSize)
            
        return self.pageSize
        
    def TopMargin(self):
        if str(self.txtTopMargin.text())!="":
            (dTop,ok)=self.txtTopMargin.text().toDouble()
            if ok:
                self.topMargin=dTop*cm
        return self.topMargin
        
    def BottomMargin(self):
        if str(self.txtBtMargin.text())!="":
            (dBottom,ok)=self.txtBtMargin.text().toDouble()
            if ok:
                self.bottomMargin=dBottom*cm
        return self.bottomMargin
        
    def LeftMargin(self):
        if str(self.txtLeftMargin.text())!="":
            (dLeft,ok)=self.txtLeftMargin.text().toDouble()
            if ok:
                self.leftMargin=dLeft*cm
        return self.leftMargin
    
    def RightMargin(self):
        if str(self.txtRightMargin.text())!="":
            (dRight,ok)=self.txtRightMargin.text().toDouble()
            if ok:
                self.rightMargin=dRight*cm
        return self.rightMargin
    
    def loadSettings(self, dialogSettings):
        '''
        Load report settings stored for the given report element
        '''
        ds = dialogSettings
        
        if not ds == None:
            Utils.setCurrentText(self.cboPageSize, ds.size)
            Utils.setCurrentText(self.cboPageOrien, ds.orientation)
            self.txtTopMargin.setText(ds.top)
            self.txtLeftMargin.setText(ds.left)            
            self.txtBtMargin.setText(ds.bottom)            
            self.txtRightMargin.setText(ds.right)
    
    def getSettings(self):
        '''
        Capture the user settings 
        '''
        layoutSettings = LayoutDialogSettings()
        layoutSettings.top = str(self.txtTopMargin.text())
        layoutSettings.left = str(self.txtLeftMargin.text())
        layoutSettings.size = str(self.cboPageSize.currentText())
        layoutSettings.orientation = str(self.cboPageOrien.currentText())
        layoutSettings.bottom = str(self.txtBtMargin.text())
        layoutSettings.right = str(self.txtRightMargin.text())
        
        self._rptEl.dialogSettings = layoutSettings
            
        return self._rptEl
    
    def InfoMessage(self,Message):            
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(Message)
        msg.exec_()   
                           
        