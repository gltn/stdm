"""
/***************************************************************************
Name                 : STR Formatters
Description          : LEGACY CODE: Generic Report
Date                 : 11/November/2011
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

from PyQt4 import QtCore, QtGui

from stdm.utils import *

from third_party.reportlab.lib.pagesizes import A4
from third_party.reportlab.lib.units import cm,inch
from third_party.reportlab.lib.enums import TA_CENTER, TA_RIGHT
from third_party.reportlab.lib.colors import navy, yellow, red, white

from third_party.geraldo import (
                     Report, 
                     ReportBand, 
                     DetailBand, 
                     Label, 
                     ObjectValue, 
                     SystemField,
                     FIELD_ACTION_COUNT,
                     BAND_WIDTH,
                     Line
                     )

from third_party.geraldo.generators import PDFGenerator

class STDMReport(Report):
    def __init__(self,querySet,reportElements):  
        Report.__init__(self,querySet)
        
        self.__reportElements=reportElements
        
        #Set Root Report Properties
        self.title=self.__reportElements.title
        self.author=self.__reportElements.author 
        self.subject=self.__reportElements.subject 
        self.page_size=self.__reportElements.page_size
        self.margin_top=self.__reportElements.margin_top
        self.margin_bottom=self.__reportElements.margin_bottom
        self.margin_left=self.__reportElements.margin_left
        self.margin_right=self.__reportElements.margin_right
        self.groups=self.__reportElements.groups 
        #Set Band Properties
        self.setHeaderElements()
        self.setDetailElemts()  
        self.setFooterElements()      
        
    def setColumnlist(self,reportFields):
        #Set the report's column fields
        self.__columnList=reportFields    
        
    def setHeaderElements(self):
        #set header details
        self.band_page_header.elements=self.__reportElements.headerElements
        self.band_page_header.borders=self.__reportElements.headerBorders  
        
    def setDetailElemts(self):
        self.band_detail.elements=self.__reportElements.detailElements
        self.band_detail.borders=self.__reportElements.detailBorders
        #self.band_detail.groups=self.__reportElements.groups  
        
    def setFooterElements(self):
        #Set footer details
        footerEl=[]
        footerEl.append(Label(text=self.__reportElements.footer, top=0.1*cm, left=0))   
        footerEl.append(SystemField(expression='Page %(page_number)d of %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}))    
        self.band_page_footer.elements=footerEl
    
    def __buildBandElements__(self):
        #Create band detail reports elements
        colLen=len(self.__columnList)
        leftIncr=8/colLen
        elLeft=0
        detailBandEl=[]
        for c in self.__columnList:
            objVal=ObjectValue(attribute_name=str(c),top=0,left=elLeft*inch)
            elLeft+=leftIncr
            detailBandEl.append(objVal)
        self.band_detail.elements=detailBandEl  
            
    class band_page_header(ReportBand):        
        #Header details
        height=1.4*cm                
        
    class band_page_footer(ReportBand):        
        height = 0.5*cm
        margin_top=0.2*cm
        borders = {'top': Line(stroke_color=white)}
        
    class band_detail(DetailBand):        
        height=0.7*cm
        auto_expand_height = True                              
 
class STDMGenerator:                
    #Helper class for generating  the report using the specified generators
    def __init__(self,report,outputPath):        
        self.report=report
        self.location=outputPath
        
    def generateReport(self):                 
        #Generate the report into the specified location
        self.report.generate_by(PDFGenerator,self.location)
         
    