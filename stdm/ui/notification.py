"""
/***************************************************************************
Name                 : Notification Handler
Description          : A class which is used to add notification
                       messages to the parent layout. This can be used as a
                       handy replacement for message boxes in a form.
Date                 : 22/June/2013
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
from uuid import uuid4

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    QObject,
    pyqtSignal,
    QTimer,
    QEvent
)
from qgis.PyQt.QtWidgets import (
    QVBoxLayout,
    QWidget
)

from stdm.ui.gui_utils import GuiUtils

# Enums for type of notification to be displayed
ERROR = 2005
SUCCESS = 2006
WARNING = 2007
INFORMATION = 2008


class NotificationBar(QObject, object):
    '''
    Used to display notifications in a vertical layout in order for
    important user messages to be inserted in a widget.
    By default, the notification(s) will be removed after 10 seconds.
    To change this default behaviour, change the value of the 'timerinterval'
    parameter in the constructor.
    '''
    userClosed = pyqtSignal()
    onShow = pyqtSignal()
    onClear = pyqtSignal()

    def __init__(self, layout, timerinterval=10000):
        QObject.__init__(self)
        self.interval = timerinterval

        if isinstance(layout, QVBoxLayout):
            self.layout = layout
            self.layout.setSpacing(2)

            # Set notification type stylesheet
            self.errorStyleSheet = "background-color: #FFBABA;"
            self.error_font_color = 'color: #D8000C;'

            self.successStyleSheet = "background-color: #DFF2BF;"
            self.success_font_color = 'color: #4F8A10;'

            self.informationStyleSheet = "background-color: #BDE5F8;"
            self.information_font_color = 'color: #555;'

            self.warningStyleSheet = "background-color: #FEEFB3;"
            self.warning_font_color = 'color: #9F6000;'
            # Timer settings
            self.timer = QTimer(self.layout)
            self.timer.setInterval(self.interval)
            self.timer.timeout.connect(self.clear)

        else:
            self.layout = None

        self._notifications = {}

    def insertNotification(self, message, notificationType):
        '''
        Insert a message into notification bar/layout
        '''
        if self.layout != None:
            notificationItem = NotificationItem()
            notificationItem.messageClosed.connect(self.onNotificationClosed)

            font_color = "color: rgb(255, 255, 255);"
            frameStyle = "background-color: rgba(255, 255, 255, 0);"
            if notificationType == ERROR:
                frameStyle = self.errorStyleSheet
                font_color = self.error_font_color

            elif notificationType == SUCCESS:
                frameStyle = self.successStyleSheet
                font_color = self.success_font_color

            elif notificationType == INFORMATION:
                frameStyle = self.informationStyleSheet
                font_color = self.information_font_color

            elif notificationType == WARNING:
                frameStyle = self.warningStyleSheet
                font_color = self.warning_font_color

            notificationItem.setMessage(
                message, notificationType, frameStyle, font_color
            )
            self.layout.addWidget(notificationItem)
            self._notifications[
                str(notificationItem.code)
            ] = notificationItem

            # Reset the timer
            self.timer.start()
            self.onShow.emit()

    def insertErrorNotification(self, message):
        '''
        A convenience method for inserting error messages
        '''
        self.insertNotification(message, ERROR)

    def insertWarningNotification(self, message):
        '''
        A convenience method for inserting warning messages
        '''
        self.insertNotification(message, WARNING)

    def insertSuccessNotification(self, message):
        '''
        A convenience method for inserting information messages
        '''
        self.insertNotification(message, SUCCESS)

    def insertInformationNotification(self, message):
        '''
        A convenience method for inserting information messages
        '''
        self.insertNotification(message, INFORMATION)

    def clear(self):
        '''
        Remove all notifications.
        '''
        if self.layout != None:
            for code, lbl in self._notifications.items():
                self.layout.removeWidget(lbl)
                lbl.setVisible(False)
                lbl.deleteLater()
            self._notifications = {}
        self.onClear.emit()

    def onNotificationClosed(self, code):
        '''
        Slot raised when a user chooses to close a notification item.
        Prevents an error from occurring when removing all notifications from the container.
        '''
        strCode = str(code)
        if strCode in self._notifications:
            del self._notifications[strCode]
            self.userClosed.emit()


WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_notif_item.ui'))


class NotificationItem(BASE, WIDGET):
    # Close signal
    messageClosed = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self.lblClose.setPixmap(GuiUtils.get_icon_pixmap('close_msg.png'))

        # Unique identifier for the message
        self.code = str(uuid4())

        # Set event filter for closing the message
        self.lblClose.installEventFilter(self)

        # Set labels to maximum transparency so that they do not inherit the background color of the frame
        clearBGStyle = "background-color: rgba(255, 255, 255, 0);"
        self.lblNotifIcon.setStyleSheet(clearBGStyle)
        self.lblNotifMessage.setStyleSheet("color: rgb(255, 255, 255);" + clearBGStyle)

    def eventFilter(self, watched, e):
        '''
        Capture mouse release event when the user clicks to close the message
        '''
        if QEvent is None:
            return False
        if watched == self.lblClose and e.type() == QEvent.MouseButtonRelease:
            self.messageClosed.emit(self.code)
            self.deleteLater()
            return True
        else:
            return QWidget.eventFilter(self, watched, e)

    def setMessage(self, message, notificationType, stylesheet, font_color):
        '''
        Set display properties
        '''
        # Background color
        if notificationType == ERROR:
            # Set icon resource and frame background color
            notifPixMap = GuiUtils.get_icon_pixmap("remove.png")
        elif notificationType == SUCCESS:
            notifPixMap = GuiUtils.get_icon_pixmap("success.png")
        elif notificationType == INFORMATION:
            notifPixMap = GuiUtils.get_icon_pixmap("info_small.png")
        elif notificationType == WARNING:
            notifPixMap = GuiUtils.get_icon_pixmap("warning.png")

        self.lblNotifIcon.setPixmap(notifPixMap)
        self.lblNotifMessage.setText(message)
        self.frame.setStyleSheet(stylesheet)
        self.lblNotifMessage.setStyleSheet(font_color)
