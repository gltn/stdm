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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_notif_item import Ui_frmNotificationItem

#Enums for type of notification to be displayed
ERROR = 2005
INFO = 2006
WARNING = 2007

class NotificationBar(object): 
    '''
    Used to display notifications in a vertical layout in order for 
    important user messages to be inserted in a widget.
    By default, the notification(s) will be removed after 10 seconds.
    To change this default behaviour, change the value of the 'timerinterval'
    parameter in the constructor.
    '''
    def __init__(self,layout,timerinterval = 10000): 
        self.interval = timerinterval

        if isinstance(layout,QVBoxLayout):                        
            self.layout = layout 
            self.layout.setSpacing(2)
            
            #Set notification type stylesheet
            self.errorStyleSheet = "background-color: rgb(248, 0, 0);"
            
            self.infoStyleSheet = "background-color: rgb(70, 211, 0);"
            
            self.warningStyleSheet = "background-color: rgb(255, 170, 0);"
    
            #Timer settings
            self.timer = QTimer(self.layout)
            self.timer.setInterval(self.interval)
            QObject.connect(self.timer, SIGNAL("timeout()"),self.clear)
            
        else:
            self.layout = None                  
                    
        self._notifications = {}
        
    def insertNotification(self,message,notificationType):
        '''
        Insert a message into notification bar/layout
        '''
        if self.layout != None:    
            notificationItem = NotificationItem() 
            QObject.connect(notificationItem, SIGNAL("messageClosed(QString)"),self.onNotificationClosed)
            
            if notificationType == ERROR:                        
                frameStyle = self.errorStyleSheet
            elif notificationType == INFO:
                frameStyle = self.infoStyleSheet
            elif notificationType == WARNING:
                frameStyle = self.warningStyleSheet
                
            notificationItem.setMessage(message,notificationType,frameStyle)
            self.layout.addWidget(notificationItem)
            self._notifications[str(notificationItem.code)] = notificationItem
            
            #Reset the timer
            self.timer.start() 
            
    def insertErrorNotification(self,message):
        '''
        A convenience method for inserting error messages 
        '''
        self.insertNotification(message, ERROR)
        
    def insertWarningNotification(self,message):
        '''
        A convenience method for inserting warning messages
        '''
        self.insertNotification(message, WARNING)
        
    def insertInfoNotification(self,message):
        '''
        A convenience method for inserting information messages
        '''
        self.insertNotification(message, INFO)
            
    def clear(self):
        '''
        Remove all notifications.
        '''  
        if self.layout != None:
            for code,lbl in self._notifications.iteritems():
                self.layout.removeWidget(lbl)
                lbl.setVisible(False)
                lbl.deleteLater()
            self._notifications = {}
            
    def onNotificationClosed(self,code):
        '''
        Slot raised when a user chooses to close a notification item.
        Prevents an error from occurring when removing all notifications from the container.
        '''
        strCode = str(code)
        if strCode in self._notifications:
            del self._notifications[strCode]
   
class NotificationItem(QWidget,Ui_frmNotificationItem):
    
    #Close signal
    messageClosed = pyqtSignal(str)
    
    def __init__(self,parent = None):
        QWidget.__init__(self,parent)
        self.setupUi(self) 
        
        #Unique identifier for the message
        self.code = str(uuid4())
        
        #Set event filter for closing the message  
        self.lblClose.installEventFilter(self)
        
        #Set labels to maximum transparency so that they do not inherit the background color of the frame
        clearBGStyle = "background-color: rgba(255, 255, 255, 0);"    
        self.lblNotifIcon.setStyleSheet(clearBGStyle)
        self.lblNotifMessage.setStyleSheet("color: rgb(255, 255, 255);" + clearBGStyle)
        
    def eventFilter(self,watched,e):
        '''
        Capture mouse release event when the user clicks to close the message
        '''
        if watched == self.lblClose and e.type() == QEvent.MouseButtonRelease:
            self.messageClosed.emit(self.code)
            self.deleteLater()
            return True
        else:
            return QWidget.eventFilter(self,watched, e)
        
    def setMessage(self,message,notificationType,stylesheet):
        '''
        Set display properties
        '''
        #Background color
        if notificationType == ERROR:   
            #Set icon resource and frame background color                     
            notifPixMap = QPixmap(":/plugins/stdm/images/icons/remove.png")
        elif notificationType == INFO:
            notifPixMap = QPixmap(":/plugins/stdm/images/icons/success.png")
        elif notificationType == WARNING:
            notifPixMap = QPixmap(":/plugins/stdm/images/icons/warning.png")
        
        self.lblNotifIcon.setPixmap(notifPixMap)
        self.lblNotifMessage.setText(message)
        self.frame.setStyleSheet(stylesheet)
        
        
    
    
    
        
               
        
          
                

        
            
            
            
            
            
            
            
            
            
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            