"""
/***************************************************************************
Name                 : Module Loader
Description          : Loads content items (toolbars, stackwidget items, etc.)
                        based on the approved role(s) of the item
Date                 : 27/May/2013
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

from qgis.PyQt.QtWidgets import (
    QToolBar,
    QMenu,
    QListWidget,
    QApplication
)
from qgis.PyQt.QtCore import (
    QObject,
    pyqtSignal
)

from collections import OrderedDict

from stdm.utils.util import getIndex
from stdm.data.database import (
    Content
)
from stdm.navigation.content_group import ContentGroup

class QtContainerLoader(QObject):
    """
    Loads actions to the specified container based on the approved roles.
    The loader registers new modules if they do not exist.
    If an actionRef parameter is specified then the action will all be added
    before the reference action in the corresponding container widget.
    """
    authorized = pyqtSignal(Content)
    finished = pyqtSignal()
    #contentAdded = pyqtSignal(Content)

    def __init__(self,parent,container, actionRef=None, register=False):
        from stdm.security.authorization import Authorizer

        QObject.__init__(self,parent)
        self._container = container
        self._register = register
        self._actionReference = actionRef
        self._contentGroups = OrderedDict()
        self._widgets = []

        from stdm.data.globals import app_dbconn
        self._userName = app_dbconn.User.UserName
        self._authorizer = Authorizer(app_dbconn.User.UserName)
        self._iter = 0
        self._separatorAction = None

    def addContent(self, content, parents = None):
        """
        Add ContentGroup and its corresponding parent if available.
        """
        self._contentGroups[content] = parents

        #Connect content group signals
        if isinstance(content,ContentGroup):
            content.contentAuthorized.connect(self._onContentAuthorized)

    def addContents(self,contentGroups,parents = None):
        """
        Append multiple content groups which share the same parent widgets.
        """
        for cg in contentGroups:
            self.addContent(cg, parents)

    def loadContent(self):
        """
        Add defined items in the specified container.
        """
        #If the user does not belong to any STDM group then the system will raise an error so gracefully terminate
        from stdm.security.exception import SecurityException

        userRoles = self._authorizer.userRoles

        if len(userRoles) == 0:
            msg = QApplication.translate("ModuleLoader","'%s' must be a member of at least one STDM role in order to access the modules.\nPlease contact " \
                                              "the system administrator for more information."%(self._userName,))
            raise SecurityException(msg)

        for k,v in self._contentGroups.items():
            #Generic content items
            if not isinstance(k,ContentGroup):
                self._addItemtoContainer(k)

            else:
                #Assert permissions then add to container
                allowedContent = k.checkContentAccess()

                if len(allowedContent) > 0:
                    if v is None:
                        #if there is no parent then add directly to container after asserting permissions
                        self._addItemtoContainer(k.containerItem())
                    else:
                        v[0].addAction(k.containerItem())
                        self._insertWidgettoContainer(v[1])

                    '''
                    Raise signal to indicate that an STDMAction has been added to the container
                    self.contentAdded.emit(k)
                    '''

        #Add separator
        if isinstance(self._container,QToolBar) or isinstance(self._container,QMenu):
            self._separatorAction = self._container.insertSeparator(self._actionReference)

        #Remove consecutive separators
        self._rem_consecutive_separators()

        #Emit signal on finishing to load content
        self.finished.emit()

    def _onContentAuthorized(self,content):
        """
        Slot raised when a content item has been approved in the content group.
        The signal is propagated to the caller.
        """
        self.authorized.emit(content)

    def _rem_consecutive_separators(self):
        """
        Removes consecutive separator actions.
        """
        actions = self._container.actions()

        for i, act in enumerate(actions):
            prev_idx = i - 1
            if prev_idx >= 0:
               prev_act = actions[prev_idx]
               if prev_act.isSeparator() and act.isSeparator():
                    self._container.removeAction(act)

        #Check if first action is separator and if so, remove it
        if len(actions) > 0:
            first_act = actions[0]
            if first_act.isSeparator():
                self._container.removeAction(first_act)

    def _addItemtoContainer(self,content):
        '''
        Adds items to specific container
        '''
        if isinstance(self._container,QToolBar) or isinstance(self._container,QMenu):
            if self._actionReference != None:
                self._container.insertAction(self._actionReference, content)
            else:
                self._container.addAction(content)

        elif isinstance(self._container,QListWidget):
            self._container.insertItem(self._iter,content)
            self._iter += 1

    def _insertWidgettoContainer(self, widget):
        '''
        This method inserts the parent widget to the container for those actions
        that have parents defined. But it ensures that only one instance of the parent widget
        is inserted.
        '''
        objName = widget.objectName()
        #Determine if the widget is already in the container
        if getIndex(self._widgets,objName) == -1:
            if isinstance(self._container,QToolBar):
                self._container.insertWidget(self._actionReference,widget)
            elif isinstance(self._container,QMenu):
                self._container.insertMenu(self._actionReference,widget)

            self._widgets.append(objName)

    def unloadContent(self):
        '''
        Remove all items in the container.
        '''
        for k,v in self._contentGroups.items():
            if isinstance(self._container,QToolBar) or isinstance(self._container,QMenu):
                #If there is a parent then delete the widget
                if v!= None:
                    v[1].setParent(None)
                else:
                    if isinstance(k,ContentGroup):
                        k = k.containerItem()

                    self._container.removeAction(k)

        #Remove separator
        if self._separatorAction != None:
            self._container.removeAction(self._separatorAction)





