"""
/***************************************************************************
Name                 : ContentGroup
Description          : Groups related content items together
Date                 : 29/April/2014
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
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import pyqtSignal, QObject

from security import Authorizer
from stdm.data import Content, Role
from utils import HashableMixin

__all__ = ["ContentGroup,TableContentGroup"]


class ContentGroup(QObject, HashableMixin):
    """
    Groups related content items together.
    """
    content_authorized = pyqtSignal(Content)

    def __init__(self, username, container_item=None, parent=None):
        QObject.__init__(self, parent)
        HashableMixin.__init__(self)
        self._user_name = username
        self._content_items = []
        self._authorizer = Authorizer(self._user_name)
        self._container_item = container_item

    def has_permission(self, content):
        """
        Checks whether the currently logged in user has permissions to access
        the given content item.
        :rtype : bool
        :param content:
        """
        return self._authorizer.CheckAccess(content.code)

    @staticmethod
    def content_item_from_qaction(qaction):
        """
        Creates a Content object from a QAction object.
        :rtype : object
        :param qaction:
        """
        cnt = Content()
        cnt.name = qaction.text()

        return cnt

    def content_items(self):
        """
        Returns a list of content items in the group.
        :rtype : list
        """
        return self._content_items

    def add_content(self, name, code):
        """
        Create a new Content item and add it to the collection.
        :param name:
        :param code:
        """
        cnt = Content()
        cnt.name = name
        cnt.code = code

        self._content_items.append(cnt)

    def add_content_items(self, contents):
        """
        Append list of content items to the group's collection.
        :param contents:
        """
        self._content_items.extend(contents)

    def add_content_item(self, content):
        """
        Adds a Content instance to the collection.
        :param content:
        """
        self._content_items.append(content)

    def set_container_item(self, container_item):
        """
        ContainerItem can be a QAction, QListWidgetItem, etc. that can be
        associated with the group.
        :param container_item:
        """
        self._container_item = container_item

    def container_item(self):
        """
        Returns an instance of a ContainerItem associated with this group.
        :rtype : object
        """
        return self._container_item

    def check_content_access(self):
        """
        Asserts whether each content item(s) in the group has access
        permissions. For each item that has permission then a signal is
        raised containing the
        Content item as an argument.
        Those items which have been granted permission will be returned in a
        list.
        :rtype : list
        """
        allowed_content = []

        for c in self.content_items():
            has_perm = self.has_permission(c)
            if has_perm:
                allowed_content.append(c)
                self.content_authorized.emit(c)

        return allowed_content

    def register(self):
        """
        Registers the content items into the database. Registration only
        works for a postgres user account.
        """
        pg_account = "postgres"

        if self._user_name == pg_account:
            for c in self.content_items():
                if isinstance(c, Content):
                    cnt = Content()
                    # self.content=Table('content_base',Base.metadata,
                    # autoload=True,autoload_with=STDMDb.instance().engine)
                    qo = cnt.queryObject()
                    cn = qo.filter(Content.code == c.code).first()

                    # If content not found then add
                    if cn is None:
                        # Check if the 'postgres' role is defined, if not then
                        # create one
                        rl = Role()
                        role_query = rl.queryObject()
                        role = role_query.filter(
                            Role.name == pg_account).first()

                        if role is None:
                            rl.name = pg_account
                            rl.contents = [c]
                            rl.save()
                        else:
                            existing_contents = role.contents
                            # Append new content to existing
                            existing_contents.append(c)
                            role.contents = existing_contents
                            role.update()

            # Initialize lookup values
            # initLookups()


class TableContentGroup(ContentGroup):
    """
    For grouping CRUD operations for a specific model corresponding
    to a given database table.
    """
    create_op = QApplication.translate("DatabaseContentGroup", "Create")
    read_op = QApplication.translate("DatabaseContentGroup", "Select")
    update_op = QApplication.translate("DatabaseContentGroup", "Update")
    delete_op = QApplication.translate("DatabaseContentGroup", "Delete")

    def __init__(self, user_name, group_name, action=None):
        ContentGroup.__init__(self, user_name, action)
        self._group_name = group_name
        self._create_db_op_content()

    def _create_db_op_content(self):
        """
        Create content for database operations.
        The code for each content needs to be set by the caller.
        """
        self._create_cnt = Content()
        self._create_cnt.name = self._build_name(self.create_op)
        self.add_content_item(self._create_cnt)

        self._read_cnt = Content()
        self._read_cnt.name = self._build_name(self.read_op)
        self.add_content_item(self._read_cnt)

        self._update_cnt = Content()
        self._update_cnt.name = self._build_name(self.update_op)
        self.add_content_item(self._update_cnt)

        self._delete_cnt = Content()
        self._delete_cnt.name = self._build_name(self.delete_op)
        self.add_content_item(self._delete_cnt)

    def _build_name(self, content_name):
        """
        Appends group name to the content name
        :rtype : unicode
        :param content_name:
        """
        return u"{0} {1}".format(content_name, self._group_name)

    def create_content_item(self):
        """
        Returns Create content item.
        :rtype : object
        """
        return self._create_cnt

    def read_content_item(self):
        """
        Returns Read/Select content item.
        :rtype : object
        """
        return self._read_cnt

    def update_content_item(self):
        """
        Returns Update content item.
        :rtype : object
        """
        return self._update_cnt

    def delete_content_item(self):
        """
        Returns Delete content item.
        :rtype : object
        """
        return self._delete_cnt

    def can_read(self):
        """
        Returns whether the current user has read permissions.
        :rtype : bool
        """
        return self.has_permission(self._read_cnt)

    def can_create(self):
        """
        Returns whether the current user has create permissions.
        :rtype : bool
        """
        return self.has_permission(self._create_cnt)

    def can_update(self):
        """
        Returns whether the current user has update permissions.
        :rtype : bool
        """
        return self.has_permission(self._update_cnt)

    def can_delete(self):
        """
        Returns whether the current user has delete permissions.
        :rtype : bool
        """
        return self.has_permission(self._delete_cnt)
