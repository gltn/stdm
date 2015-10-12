"""
/***************************************************************************
Name                 : SQL Highlighter
Description          : Custom SQL Syntax Highlighter
Date                 : 14/October/11 
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
from PyQt4.QtGui import (
                         QSyntaxHighlighter,
                         QTextCharFormat,
                         QFont
                         )

from PyQt4.QtCore import (
                          Qt,
                          QRegExp
                          )

class SqlHighlighter(QSyntaxHighlighter):     
    def __init__(self, parent=None):         
        QSyntaxHighlighter.__init__(self, parent) 
        self.parent = parent
        sql_keyword = QTextCharFormat()
        sql_operator = QTextCharFormat()
        
        self.highlightingRules = []
        
        #Keywords           
        sql_keyword.setFontWeight(QFont.Bold)
        sql_keyword.setForeground(Qt.blue)
        
        sql_keywords = ["AND", "OR", "LIKE"]
        for word in sqlKeywords:
            reg_exp = QRegExp("\\b" + word + "\\b", Qt.CaseInsensitive)
            rule = HighlightingRule(reg_exp, sql_keyword)
            self.highlightingRules.append(rule)
            
        #Comparison Operators
        sql_operator.setForeground(Qt.magenta)
        sql_operators = ["<", ">", "="]
        for operator in sql_operators:
            reg_exp = QRegExp("\\W" + operator + "\\W", Qt.CaseInsensitive)
            rule = HighlightingRule(reg_exp, sql_operator)
            self.highlightingRules.append(rule)
                
    def highlightBlock(self, text):  # overriden 
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text, index+length)
                
        self.setCurrentBlockState(0)
        
class HighlightingRule():
    def __init__( self, pattern, highlight_format):
        self.pattern = pattern
        self.format = highlight_format
                
        
