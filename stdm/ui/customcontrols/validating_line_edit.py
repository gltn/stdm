"""
/***************************************************************************
Name                 : Validating Line Edit
Description          : Custom QLineEdit control that validates user input
                       against database values as the user types.
Date                 : 1/March/2014
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
from qgis.PyQt.QtCore import (
    pyqtSignal,
    QTimer
)
from qgis.PyQt.QtWidgets import (
    QLineEdit
)
from sqlalchemy import func

INVALIDATESTYLESHEET = "background-color: rgba(255, 0, 0, 100);"


class ValidatingLineEdit(QLineEdit):
    '''
    Custom QLineEdit control that validates user input against database
    values as the user types.
    '''
    # Signal raised when the user input is invalid.
    invalidatedInput = pyqtSignal()

    def __init__(self, parent=None, notificationbar=None, dbmodel=None, attrname=None):
        '''
        :param parent: Parent widget
        :param notificationbar: instance of stdm.ui.NotificationBar class.
        '''
        QLineEdit.__init__(self, parent)
        self._notifBar = notificationbar
        self._dbmodel = None
        self._attrName = None
        self._timer = QTimer(self)
        self._timer.setInterval(800)
        self._timer.setSingleShot(True)
        self._invalidMsg = ""
        self._filterOperator = "="
        self._defaultStyleSheet = self.styleSheet()
        self._isValid = True
        self._currInvalidMsg = ""

        # Connect signals
        self._timer.timeout.connect(self.validateInput)
        self.textChanged.connect(self.onTextChanged)

    def validateInput(self):
        '''
        Validate user input.
        '''
        if self._dbmodel:
            if callable(self._dbmodel):
                modelObj = self._dbmodel()

            # Then it is a class instance
            else:
                modelObj = self._dbmodel
                self._dbmodel = self._dbmodel.__class__

            objQueryProperty = getattr(self._dbmodel, self._attrName)
            modelRecord = modelObj.queryObject().filter(func.lower(objQueryProperty) == func.lower(self.text())).first()

            if modelRecord != None:
                self.setStyleSheet(INVALIDATESTYLESHEET)
                self._currInvalidMsg = self._invalidMsg.format("'" + self.text() + "'")
                self._isValid = False

                if self._notifBar:
                    self._notifBar.insertErrorNotification(self._currInvalidMsg)

    def setInvalidMessage(self, message):
        '''
        The message to be displayed when the user input is invalid.
        '''
        self._invalidMsg = message

    def invalidMessage(self):
        '''
        Returns the invalidation message for the control.
        '''
        return self._invalidMsg

    def setDatabaseModel(self, dbmodel):
        '''
        Set database model which should be callable.
        '''
        self._dbmodel = dbmodel

    def setAttributeName(self, attrname):
        '''
        Attribute name of the database model for validating against.
        '''
        self._attrName = attrname

    def setModelAttr(self, model, attributeName):
        '''
        Set a callable model class and attribute name.
        '''
        self._dbmodel = model
        self._attrName = attributeName

    def setNotificationBar(self, notifBar):
        '''
        Sets the notification bar.
        '''
        self._notifBar = notifBar

    def setQueryOperator(self, queryOp):
        '''
        Specify a string-based value for the filter operator that validates
        the user input.
        '''
        self._filterOperator = queryOp

    def queryOperator(self):
        '''
        Return the current query operator. Default is '=' operator.
        '''
        return self._filterOperator

    def validate(self):
        '''
        Convenience method that can be used to validate the current state of the control.
        '''
        if not self._isValid:
            if self._notifBar:
                self._notifBar.insertErrorNotification(self._currInvalidMsg)
            return False

        else:
            return True

    def onTextChanged(self, userText):
        '''
        Slot raised whenever the text changes in the control.
        '''
        self.setStyleSheet(self._defaultStyleSheet)
        self._isValid = True

        if self._notifBar != None:
            self._notifBar.clear()

        self._timer.start()
