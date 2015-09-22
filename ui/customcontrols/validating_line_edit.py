"""
/***************************************************************************
Name                 : Validating Line Edit
Description          : Custom QLineEdit control that validates user input
                       against database values as the user types.
Date                 : 1/March/2014
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
from PyQt4.QtCore import pyqtSignal, QTimer, SIGNAL
from PyQt4.QtGui import QLineEdit

from sqlalchemy import func

INVALIDATESTYLESHEET = "background-color: rgba(255, 0, 0, 100);"


class ValidatingLineEdit(QLineEdit):
    """
    Custom QLineEdit control that validates user input against database
    values as the user types.
    """
    # Signal raised when the user input is invalid.
    invalidatedInput = pyqtSignal()

    def __init__(self, parent=None, notification_bar=None, db_model=None,
                 attr_name=None):
        '''
        :param parent: Parent widget
        :param notification_bar: instance of stdm.ui.NotificationBar class.
        '''
        QLineEdit.__init__(self, parent)
        self._notif_bar = notification_bar
        self._db_model = None
        self._attr_name = None
        self._timer = QTimer(self)
        self._timer.setInterval(800)
        self._timer.setSingleShot(True)
        self._invalid_msg = ""
        self._filter_operator = "="
        self._default_style_sheet = self.styleSheet()
        self._is_valid = True
        self._curr_invalid_msg = ""

        # Connect signals
        self.connect(self._timer, SIGNAL("timeout()"), self.validate_input)
        self.connect(self, SIGNAL("textChanged(const QString&)"),
                     self.on_text_changed)

    def validate_input(self):
        """
        Validate user input.
        """
        if self._db_model:
            if callable(self._db_model):
                model_obj = self._db_model()

            # Then it is a class instance
            else:
                model_obj = self._db_model
                self._db_model = self._db_model.__class__

            obj_query_property = getattr(self._db_model, self._attr_name)
            model_record = model_obj.queryObject().filter(func.lower(
                obj_query_property) == func.lower(self.text())).first()

            if model_record is not None:
                self.setStyleSheet(INVALIDATESTYLESHEET)
                self._curr_invalid_msg = self._invalid_msg.format(
                    "'" + self.text() + "'")
                self._is_valid = False

                if self._notif_bar:
                    self._notif_bar.insertErrorNotification(
                        self._curr_invalid_msg)

    def set_invalid_message(self, message):
        """
        The message to be displayed when the user input is invalid.
        :param message:
        """
        self._invalid_msg = message

    def invalid_message(self):
        """
        Returns the invalidation message for the control.
        """
        return self._invalid_msg

    def set_database_model(self, db_model):
        """
        Set database model which should be callable.
        :param db_model:
        """
        self._db_model = db_model

    def set_attribute_name(self, attr_name):
        """
        Attribute name of the database model for validating against.
        :param attr_name:
        """
        self._attr_name = attr_name

    def set_model_attr(self, model, attribute_name):
        """
        Set a callable model class and attribute name.
        :param model:
        :param attribute_name:
        """
        self._db_model = model
        self._attr_name = attribute_name

    def set_notification_bar(self, notif_bar):
        """
        Sets the notification bar.
        :param notif_bar:
        """
        self._notif_bar = notif_bar

    def set_query_operator(self, query_op):
        """
        Specify a string-based value for the filter operator that validates
        the user input.
        :param query_op:
        """
        self._filter_operator = query_op

    def query_operator(self):
        """
        Return the current query operator. Default is '=' operator.
        """
        return self._filter_operator

    def validate(self):
        """
        Convenience method that can be used to validate the current state of
        the control.
        :rtype : bool
        """
        if not self._is_valid:
            if self._notif_bar:
                self._notif_bar.insertErrorNotification(self._curr_invalid_msg)
            return False

        else:
            return True

    def on_text_changed(self, user_text):
        """
        Slot raised whenever the text changes in the control.
        :param user_text:
        """
        self.setStyleSheet(self._default_style_sheet)
        self._is_valid = True

        if self._notif_bar is not None:
            self._notif_bar.clear()

        self._timer.start()
