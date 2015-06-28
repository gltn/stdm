"""
/***************************************************************************
Name                 : QTableWidget Combo Box
Description          : Custom Combo Box that stores the row number of its container
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
from PyQt4.QtGui import QComboBox

__all__ = ["TableComboBox"]

class TableComboBox(QComboBox):     
    #Class constructor  
    def __init__(self,row):         
        QComboBox.__init__(self) 
        self.row=row
    
                
        