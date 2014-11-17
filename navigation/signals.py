"""
/***************************************************************************
Name                 : STDM Signals
Description          : Custom STDM signals raised by custom navigation components
                        when the item is authorized in the given context
Date                 : 3/June/2013 
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
from PyQt4.QtCore import QObject, pyqtSignal

class STDMContentSignal(QObject):
    '''
    Name of the STDM content item
    '''
    authorized = pyqtSignal('QString')
    finished = pyqtSignal()
