"""
/***************************************************************************
Name                 : STDM Report Builder
Description          : Report Builder Dialog
Date                 : 07/September/11 
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
from stdm.data.reports import (
                               SysFonts,
                               TitleDialogSettings, 
                               ReportElement, 
                               SFont
                               )
    
from .ui_rpt_title_base import Ui_frmRptTitleBase

class TitleBase(QWidget, Ui_frmRptTitleBase):      
    def __init__(self,id, parent=None):         
        QWidget.__init__(self, parent)
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
        self.init_controls()

        #Remove option for selecting font until translation issues are fixed
        self.label_2.setVisible(False)
        self.btnTitleFont.setVisible(False)
        
        #Event Handlers
        self.btnTitleFont.clicked.connect(self.set_font_type)
        self.btnTitleColor.clicked.connect(self.set_font_color)
    
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
        
    def init_controls(self):
        #Initialize the controls' settings
        setting_val = QDoubleValidator(0, 10, 2, self)
        self.txtTitleHeight.setValidator(setting_val)
        self.txtTitleLeft.setValidator(setting_val)
        self.txtTitleTop.setValidator(setting_val)
        self.txtTitleWidth.setValidator(setting_val)
        self.btnTitleColor.setColor(self.elFontColor)
        
    def set_border(self):
        #Set the border
        d_border = self.cboBorder.currentText()
        if d_border == "All":self.elBorder = {"all":True} 
        elif d_border == "Top":self.elBorder = {"top":True}    
        elif d_border == "Right":self.elBorder = {"right":True}
        elif d_border == "Bottom":self.elBorder = {"bottom":True}
        elif d_border == "Left":self.elBorder = {"left":True}
        elif d_border == "None":self.elBorder = {"all":False}
        
    def set_font_color(self):
        #Slot for setting the font color from the color dialog
        widg_clr = QColorDialog.getColor(self.elFontColor, self)
        if widg_clr.isValid():
            self.elFontColor = widg_clr
            self.btnTitleColor.setColor(widg_clr)
        
    def set_font_type(self):
        #Slot for setting the font type specified in the font dialog            
        (widg_font, ok) = QFontDialog.getFont(self.elFont, self)
        if ok:
            if widg_font.family() == "MS Shell Dlg 2":
                widg_font.setFamily("Times New Roman")

            self.elFont = widg_font
        
    def set_height(self):
        #Set the height specified by the user
        if str(self.txtTitleHeight.text()) != "":
            (d_height, ok) = self.txtTitleHeight.text().toInt()
            if ok:
                self.elHeight = d_height
                
    def set_h_align(self):
        #Set Horizontal Alignment
        h_al = self.cboTitleHAlign.currentText()
        if h_al == "Left":self.hAlign = TA_LEFT
        elif h_al == "Right":self.hAlign = TA_RIGHT
        elif h_al == "Center":self.hAlign = TA_CENTER
        
    def set_left(self):
        #Set the LEFT specified by the user
        if str(self.txtTitleLeft.text())!="":
            (d_left, ok) = self.txtTitleLeft.text().toInt()
            if ok:
                self.elLeft = d_left
                
    def set_user_text(self):
        #Set the text specified by the user
        if str(self.txtTitleText.text()) != "":            
            self.elText=str(self.txtTitleText.text())
        
    def set_top(self):
        #Set the TOP specified by the user
        if str(self.txtTitleTop.text())!="":
            (d_top, ok) = self.txtTitleTop.text().toInt()
            if ok:
                self.elTop = d_top
    
    def set_width(self):
        #Set the WIDTH specified by the user
        if self.txtTitleWidth.text():
            (d_width, ok) = self.txtTitleWidth.text().toInt()
            if ok:
                self.elWidth = d_width
                
    def compile_entry(self): 
        #Compile the user specified values
        self.set_border()
        self.set_height()
        self.set_h_align()
        self.set_left()
        self.set_user_text()
        self.set_top()
        self.set_width()    
        
    def systemExpression(self,sysExpression="%(report_title)s"):
        '''
        Build a GERALDO-STYLE system expression with the TITLE 
        set as the default field
        '''         
        self.compile_entry()
        sysExp=SystemField(expression=sysExpression, top=self.elTop*cm, left=self.elLeft*cm,\
                           width=self.elWidth,height=self.elHeight*cm,style=self.get_style())
        return sysExp    
        
    def get_style(self):
        '''
        Returns the style (color and font details) specified 
        by the user through a dictionary
        '''        
        font_db = QFontDatabase()        
        match_font = self.sysFonts.matchingFontName(str(self.elFont.rawName()))

        q_font_style = str(font_db.styleString(self.elFont))

        match_font_style = ''

        if q_font_style.find("Normal") != -1:
            match_font_style = match_font

        else:            
            #matchFontStyle = matchFont + " " + qFontStyle
            match_font_style = match_font + " Bold"
        
        #Register the fonts to be used in the report
        font_style = self._build_font_family()
        for k,v in font_style.iteritems():
            pdfmetrics.registerFont(TTFont(k,v))

        #Add font mappings
        ps_mappings = self._post_script_mappings(font_style)
        for ps in ps_mappings:
            addMapping(match_font, ps["Bold"], ps["Italic"], ps["Style"])            
            
        d_style = {}                            
        d_style["fontName"] = match_font_style
        d_style["fontSize"] = self.elFont.pointSize()
        d_style["alignment"] = self.hAlign
        d_style["textColor"] = HexColor(str(self.elFontColor.name()))

        return d_style
    
    def _build_font_family(self):
        #Dictionary containing the font style names and corresponding file names
        style_mapping = {}
        font_members = self.sysFonts.fontMembers(str(self.elFont.rawName()))
        if len(font_members) > 0:
            for f in font_members:
                font_file = self.sysFonts.fontFile(f)
                style_mapping[f] = font_file                
        return style_mapping
    
    def _post_script_mappings(self, font_style):
        #Build post script mappings
        ps_mappings = []
        for s in font_style.keys():
            ps = {}
            ps["Style"] = s
            if s.find("Bold") != -1 and s.find("Italic") == -1:
                ps["Bold"] = 1
                ps["Italic"] = 0                
            elif s.find("Bold") == -1 and s.find("Italic") != -1:
                ps["Bold"] = 0
                ps["Italic"] = 1
            elif s.find("Bold") != -1 and s.find("Italic") != -1:
                ps["Bold"] = 1
                ps["Italic"] = 1
            else:
                ps["Bold"] = 0
                ps["Italic"] = 0 
            ps_mappings.append(ps)
        return ps_mappings 
    
    def load_settings(self, dialog_settings):
        '''
        Load report dialog settings stored for the given report element
        '''
        ds = dialog_settings
        
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
    
    def get_settings(self):
        '''
        Capture the user settings 
        '''
        dlg_st = TitleDialogSettings()
        dlg_st.top = str(self.txtTitleTop.text())
        dlg_st.left = str(self.txtTitleLeft.text())
        dlg_st.border = str(self.cboBorder.currentText())
        dlg_st.foreColor = self.elFontColor
        dlg_st.font = SFont(self.elFont)
        dlg_st.height = str(self.txtTitleHeight.text())
        dlg_st.hAlighment = str(self.cboTitleHAlign.currentText())
        dlg_st.displayName = str(self.txtTitleText.text())
        dlg_st.vAlignment = str(self.cboTitleVAlign.currentText())
        dlg_st.width = str(self.txtTitleWidth.text())        
        
        self._rptEl.dialogSettings = dlg_st
            
        return self._rptEl
    
    def info_message(self, message):            
        #General Info Message Box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.exec_()   
                           
        
