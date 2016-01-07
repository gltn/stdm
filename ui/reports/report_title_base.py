"""
/***************************************************************************
Name                 : STDM Report Builder
Description          : Report Builder Dialog
Date                 : 07/September/11 
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
from PyQt4.QtCore import *

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import (
                                 cm,
                                 inch
                                 )
from reportlab.lib.enums import (
                                 TA_CENTER, 
                                 TA_RIGHT,
                                 TA_LEFT
                                 )
from reportlab.lib.colors import HexColor

from reportlab.lib.fonts import (
                                 addMapping, 
                                 ps2tt, 
                                 tt2ps
                                 )
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from geraldo import Report, ReportBand, Label, ObjectValue, SystemField,\
    FIELD_ACTION_COUNT, FIELD_ACTION_AVG, FIELD_ACTION_MIN,\
    FIELD_ACTION_MAX, FIELD_ACTION_SUM, FIELD_ACTION_DISTINCT_COUNT, BAND_WIDTH,\
    RoundRect, Line

from stdm.utils import *
from stdm.data.reports.sys_fonts import SysFonts
from stdm.data.reports.persistence import (
    TitleDialogSettings,
    ReportElement,
    SFont
)
    
from .ui_rpt_title_base import Ui_frmRptTitleBase

class TitleBase(QWidget,Ui_frmRptTitleBase):      
    def __init__(self,id,parent = None):         
        QWidget.__init__(self,parent)
        self.setupUi(self)  
        
        #Form identifier  
        self.ID=id
        #Report Element Container
        self._rptEl = ReportElement()
        self._rptEl.parent = "Elements"
        self._rptEl.name = id
        
        #Fonts Helper
        self.sysFonts = SysFonts()
        
        #Initialize variables
        self.initVars()
        
        #Initialize control
        self.initControls()

        #Remove option for selecting font until translation issues are fixed
        self.label_2.setVisible(False)
        self.btnTitleFont.setVisible(False)
        
        #Event Handlers
        self.btnTitleFont.clicked.connect(self.setFontType)
        self.btnTitleColor.clicked.connect(self.setFontColor)
    
    def initVars(self):
        #Font
        self.elFont = QFont("Times New Roman",12)
        
        #Color
        self.elFontColor=QColor(Qt.black)
        self.elText=str(self.ID)     
                   
        if self.ID=="Title":
            self.elFont = QFont("Times New Roman",18,75)
            self.elText="STDM Report" 
            self.elFontColor = QColor(Qt.blue)   
            self.elWidth=BAND_WIDTH 
            self.cboTitleHAlign.setCurrentIndex(2) 
             
        else:
            self.cboTitleHAlign.setCurrentIndex(0)
            self.elWidth=3 
                        
        self.elHeight=0.5        
        self.elLeft=0
        self.elTop=0        
        self.elBorder={"all":None} 
        
    def initControls(self):
        #Initialize the controls' settings
        settingVal = QDoubleValidator(0,10,2,self)
        self.txtTitleHeight.setValidator(settingVal)
        self.txtTitleLeft.setValidator(settingVal)
        self.txtTitleTop.setValidator(settingVal)
        self.txtTitleWidth.setValidator(settingVal)
        self.btnTitleColor.setColor(self.elFontColor)
        
    def setBorder(self):
        #Set the border
        dBorder=self.cboBorder.currentText()
        if dBorder=="All":self.elBorder={"all":True} 
        elif dBorder=="Top":self.elBorder={"top":True}    
        elif dBorder=="Right":self.elBorder={"right":True}
        elif dBorder=="Bottom":self.elBorder={"bottom":True}
        elif dBorder=="Left":self.elBorder={"left":True}
        elif dBorder=="None":self.elBorder={"all":False}
        
    def setFontColor(self):
        #Slot for setting the font color from the color dialog
        widgClr = QColorDialog.getColor(self.elFontColor, self)
        if widgClr.isValid():
            self.elFontColor=widgClr
            self.btnTitleColor.setColor(widgClr)
        
    def setFontType(self):
        #Slot for setting the font type specified in the font dialog            
        (widgFont,ok) = QFontDialog.getFont(self.elFont,self)
        if ok:
            if widgFont.family() == "MS Shell Dlg 2":
                widgFont.setFamily("Times New Roman")

            self.elFont=widgFont
        
    def setHeight(self):
        #Set the height specified by the user
        if str(self.txtTitleHeight.text())!="":
            (dHeight,ok)=self.txtTitleHeight.text().toInt()
            if ok:
                self.elHeight=dHeight
                
    def setHAlign(self):
        #Set Horizontal Alignment
        hAl=self.cboTitleHAlign.currentText()
        if hAl=="Left":self.hAlign=TA_LEFT
        elif hAl=="Right":self.hAlign=TA_RIGHT
        elif hAl=="Center":self.hAlign=TA_CENTER
        
    def setLeft(self):
        #Set the LEFT specified by the user
        if str(self.txtTitleLeft.text())!="":
            (dLeft,ok)=self.txtTitleLeft.text().toInt()
            if ok:
                self.elLeft=dLeft
                
    def setUserText(self):
        #Set the text specified by the user
        if str(self.txtTitleText.text())!="":            
            self.elText=str(self.txtTitleText.text())
        
    def setTop(self):
        #Set the TOP specified by the user
        if str(self.txtTitleTop.text())!="":
            (dTop,ok)=self.txtTitleTop.text().toInt()
            if ok:
                self.elTop=dTop
    
    def setWidth(self):
        #Set the WIDTH specified by the user
        if self.txtTitleWidth.text():
            (dWidth,ok)=self.txtTitleWidth.text().toInt()
            if ok:
                self.elWidth=dWidth
                
    def compileEntry(self): 
        #Compile the user specified values
        self.setBorder()
        self.setHeight()
        self.setHAlign()
        self.setLeft()
        self.setUserText()
        self.setTop()
        self.setWidth()    
        
    def systemExpression(self,sysExpression="%(report_title)s"):
        '''
        Build a GERALDO-STYLE system expression with the TITLE 
        set as the default field
        '''         
        self.compileEntry()
        sysExp=SystemField(expression=sysExpression, top=self.elTop*cm, left=self.elLeft*cm,\
                           width=self.elWidth,height=self.elHeight*cm,style=self.getStyle())
        return sysExp    
        
    def getStyle(self):
        '''
        Returns the style (color and font details) specified 
        by the user through a dictionary
        '''        
        fontDB = QFontDatabase()        
        matchFont=self.sysFonts.matchingFontName(str(self.elFont.rawName()))

        qFontStyle=str(fontDB.styleString(self.elFont))

        matchFontStyle = ''

        if qFontStyle.find("Normal") != -1:
            matchFontStyle = matchFont

        else:            
            #matchFontStyle = matchFont + " " + qFontStyle
            matchFontStyle = matchFont + " Bold"
        
        #Register the fonts to be used in the report
        fontStyle = self._buildFontFamily()
        for k,v in fontStyle.iteritems():
            pdfmetrics.registerFont(TTFont(k,v))

        #Add font mappings
        psMappings=self._postScriptMappings(fontStyle)
        for ps in psMappings:
            addMapping(matchFont,ps["Bold"],ps["Italic"],ps["Style"])            
            
        dStyle={}                            
        dStyle["fontName"] = matchFontStyle
        dStyle["fontSize"]=self.elFont.pointSize()
        dStyle["alignment"]=self.hAlign
        dStyle["textColor"]=HexColor(str(self.elFontColor.name()))

        return dStyle
    
    def _buildFontFamily(self):
        #Dictionary containing the font style names and corresponding file names
        styleMapping={}
        fontMembers=self.sysFonts.fontMembers(str(self.elFont.rawName()))
        if len(fontMembers)>0:
            for f in fontMembers:
                fontFile=self.sysFonts.fontFile(f)
                styleMapping[f]=fontFile                
        return styleMapping
    
    def _postScriptMappings(self,fontStyle):
        #Build post script mappings
        psMappings=[]
        for s in fontStyle.keys():
            ps={}
            ps["Style"]=s
            if s.find("Bold")!=-1 and s.find("Italic")==-1:
                ps["Bold"]=1
                ps["Italic"]=0                
            elif s.find("Bold")==-1 and s.find("Italic")!=-1:
                ps["Bold"]=0
                ps["Italic"]=1
            elif s.find("Bold")!=-1 and s.find("Italic")!=-1:
                ps["Bold"]=1
                ps["Italic"]=1
            else:
                ps["Bold"]=0
                ps["Italic"]=0 
            psMappings.append(ps)
        return psMappings 
    
    def loadSettings(self,dialogSettings):
        '''
        Load report dialog settings stored for the given report element
        '''
        ds = dialogSettings
        
        if not ds:
            self.txtTitleTop.setText(ds.top)
            self.txtTitleLeft.setText(ds.left)
            self.txtTitleHeight.setText(ds.height)
            self.txtTitleText.setText(ds.displayName)
            self.txtTitleWidth.setText(ds.width)
            Utils.setCurrentText(self.cboBorder, ds.border)
            Utils.setCurrentText(self.cboTitleHAlign, ds.hAlighment)
            Utils.setCurrentText(self.cboTitleVAlign, ds.vAlignment)                     
            self.elFont = ds.font.font()            
            self.elFontColor = ds.foreColor
            #Immediately update the color displayed by the font color button
            self.btnTitleColor.setColor(self.elFontColor)
    
    def getSettings(self):
        '''
        Capture the user settings 
        '''
        dlgSt = TitleDialogSettings()
        dlgSt.top = str(self.txtTitleTop.text())
        dlgSt.left = str(self.txtTitleLeft.text())
        dlgSt.border = str(self.cboBorder.currentText())
        dlgSt.foreColor = self.elFontColor
        dlgSt.font = SFont(self.elFont)
        dlgSt.height = str(self.txtTitleHeight.text())
        dlgSt.hAlighment = str(self.cboTitleHAlign.currentText())
        dlgSt.displayName = str(self.txtTitleText.text())
        dlgSt.vAlignment = str(self.cboTitleVAlign.currentText())
        dlgSt.width = str(self.txtTitleWidth.text())        
        
        self._rptEl.dialogSettings = dlgSt
            
        return self._rptEl
    
    def InfoMessage(self,Message):            
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(Message)
        msg.exec_()   
                           
        