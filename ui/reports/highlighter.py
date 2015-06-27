"""
/***************************************************************************
Name                 : SQL Highlighter
Description          : Custom SQL Syntax Highlighter
Date                 : 14/October/11 
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
    def __init__(self,parent=None):         
        QSyntaxHighlighter.__init__(self,parent) 
        self.parent = parent
        sqlKeyword = QTextCharFormat()
        sqlOperator = QTextCharFormat()
        
        self.highlightingRules = []
        
        #Keywords           
        sqlKeyword.setFontWeight(QFont.Bold)
        sqlKeyword.setForeground(Qt.blue)
        
        sqlKeywords = ["AND","OR","LIKE"]
        for word in sqlKeywords:
            regExp = QRegExp("\\b" + word + "\\b",Qt.CaseInsensitive)
            rule = HighlightingRule(regExp,sqlKeyword)
            self.highlightingRules.append(rule)
            
        #Comparison Operators
        sqlOperator.setForeground(Qt.magenta)
        sqlOperators = ["<",">","="]
        for operator in sqlOperators:
            regExp = QRegExp("\\W" + operator + "\\W",Qt.CaseInsensitive)
            rule=HighlightingRule(regExp,sqlOperator)
            self.highlightingRules.append(rule)
                
    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = expression.indexIn(text,index+length)
                
        self.setCurrentBlockState(0)
        
class HighlightingRule():
    def __init__( self, pattern, highlightFormat):
        self.pattern = pattern
        self.format = highlightFormat
                
        