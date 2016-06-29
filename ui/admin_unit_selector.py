"""
/***************************************************************************
Name                 : Administrative Unit Selector
Description          : Generic dialog that displays and manages the hierarchy 
                       of administrative spatial units.
Date                 : 18/February/2014 
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from stdm.ui.admin_unit_manager import AdminUnitManager
from .admin_unit_manager import VIEW, MANAGE

class AdminUnitSelector(QDialog):
    """
    Generic admin unit manager dialog.
    """
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.resize(400, 410)

        self.verticalLayout = QVBoxLayout(self)
        self.adminUnitManager = AdminUnitManager(self)
        self.verticalLayout.addWidget(self.adminUnitManager)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel|QDialogButtonBox.Close|QDialogButtonBox.Ok
        )
        self.verticalLayout.addWidget(self.buttonBox)
        
        self.selectedAdminUnit = None
        
        #Connect signals
        self.adminUnitManager.stateChanged.connect(self.onStateChanged)
        self.connect(self.buttonBox.button(QDialogButtonBox.Ok),SIGNAL("clicked()"),self.onAcceptDialog)
        self.connect(self.buttonBox.button(QDialogButtonBox.Cancel),SIGNAL("clicked()"),self.onRejectDialog)
        self.connect(self.buttonBox.button(QDialogButtonBox.Close),SIGNAL("clicked()"),self.onRejectDialog)

    def setManageMode(self, enableManage):
        """
        :param enableManage: True to set the selector to manage mode or false to disable.
        """
        if enableManage:
            self.adminUnitManager.setState(MANAGE)
        else:
            self.adminUnitManager.setState(VIEW)
            
    def onStateChanged(self, isManageMode):
        '''
        Slot raised when the state of the admin unit manager widget changes
        '''
        if isManageMode:
            self.buttonBox.button(QDialogButtonBox.Ok).setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Cancel).setVisible(False)
            self.buttonBox.button(QDialogButtonBox.Close).setVisible(True)
            title = self.tr('Manage Administrative Units')
            
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Cancel).setVisible(True)
            self.buttonBox.button(QDialogButtonBox.Close).setVisible(False)
            title = self.tr('Select Administrative Unit')

        self.setWindowTitle(title)
            
    def onAcceptDialog(self):
        '''
        Slot raised on accepting administrative unit selection.
        This is raised when the dialog is in VIEW mode.
        '''
        self.adminUnitManager.notificationBar().clear()

        self.selectedAdminUnit = self.adminUnitManager.selectedAdministrativeUnit()
        
        if self.selectedAdminUnit is None:
            msg = self.tr('Please select an administrative unit '
                          'from the list.')
            self.adminUnitManager.notificationBar().insertWarningNotification(
                msg
            )
            
        else:
            self.accept()
    
    def onRejectDialog(self):
        '''
        Slot raised to close the dialog.
        '''
        self.reject()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        