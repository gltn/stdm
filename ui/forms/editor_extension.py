"""
/***************************************************************************
Name                 : Editor extension
Description          : Module for enabling custom logic in editor forms
Date                 : 21/November/2018
copyright            : (C) 2018 by UN-Habitat and implementing partners.
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
import logging
from abc import ABCMeta

from PyQt4.QtGui import (
    QComboBox,
    QWidget
)


LOGGER = logging.getLogger('stdm')


class CascadingFieldContext(object):
    """
    Provides a mechanism for defining cascading or drill down functionality
    for comboboxes containing related data.
    The values in the source and target comboboxes must have codes defined
    as specified in the configuration. These codes will be used to specify
    the source-target value mapping.
    """
    def __init__(self, source_combo, target_combo):
        """
        :param source_combo: Name of the lookup column in an entity whose
        corresponding lookup values will be used to filter items in the
        target combobox.
        :type source_combo: str
        :param target_combo: Name of the lookup column whose corresponding
        lookup values will be filtered based on the selected item in the
        source combobox.
        :type target_combo: str
        """
        self._src_cbo_str = source_combo
        self._target_cbo_str = target_combo
        self._id = hash(
            (self._src_cbo_str, self._target_cbo_str)
        )
        self._src_target_mapping = {}
        self._src_cbo = None
        self._target_cbo = None
        self._ext_editor = None
        self._is_sig_connected = False

    @property
    def extension_editor(self):
        """
        :return: Returns the extension editor object containing this context
        object.
        :rtype: AbstractEditorExtension
        """
        return self._ext_editor

    @extension_editor.setter
    def extension_editor(self, ext_editor):
        """
        Sets the extension editor containing this context object. This is
        called when the context object is added to the custom extension
        editor.
        :param ext_editor: Custom extension editor
        :type ext_editor: AbstractEditorExtension
        """
        self._ext_editor = ext_editor
        self._src_cbo = self._ext_editor.widget(self._src_cbo_str)
        self._target_cbo = self._ext_editor.widget(self._target_cbo_str)

    @property
    def source_combobox(self):
        """
        :return: Returns the combobox whose items are used to filter items
        in the target combobox. None if the extension editor has not been set.
        :rtype: QComboBox
        """
        return self._src_cbo

    @property
    def target_combobox(self):
        """
        :return: Returns the combobox whose items are filtered based on the
        selected item in the source combobox. None if the extension editor
        has not been set.
        :rtype: QComboBox
        """
        return self._target_cbo

    @property
    def id(self):
        """
        :return: Returns an integer value based on the hash of the source
        and target combobox object names respectively.
        :rtype: int
        """
        return self._id

    def __hash__(self):
        """
        Enable the object to the used in hashed collections with the id as
        the key.
        """
        return self._id

    def __eq__(self, other):
        """Use id attribute as comparator."""
        return self._id == other.id

    def __str__(self):
        return str(self._id)

    def add_mapping(self, src_value, target_values):
        """
        Specify pairing of respective source value and matching target
        values. The codes, and NOT lookup values as specified in the
        configuration, are used in this function.
        :param src_value: Code of the source value which when selected
        in the source combobox will be used to filter corresponding values
        in the target combobox.An existing source value will be overridden.
        :type src_value: str
        :param target_values: A tuple containing codes of items that will
        appear in the target combobox when a given source value is selected
        in the source combobox.
        :type target_values: tuple
        """
        self._src_target_mapping[src_value] = target_values

    def connect(self):
        """
        Connect the source combo's currentIndexChanged signal to filter the
        items in the target combobox based on the source-target value mapping.
        """
        self._is_sig_connected = True

    def disconnect(self):
        """
        Disconnects the source combo's currentIndexChanged signal after which
        no filtering will be applied when the currentIndex of the source
        combo changes.
        """
        self._is_sig_connected = False

    @property
    def is_connected(self):
        """
        :return: Returns True if the sourcecombo's currentIndexChanged signal
        is connected to filter items in the target combobox.
        :rtype: bool
        """
        return self._is_sig_connected


class CascadingFieldContextManager(object):
    """
    Container for managing one or more cascading field contexts.
    Used internally by the AbstractEditorExtension to
    """
    def __init__(self, ext_editor):
        self._ext_editor = ext_editor
        self._cf_ctxts = {}

    @property
    def extension_editor(self):
        """
        :return: Returns the custom extension editor used in this context
        manager object.
        :rtype: AbstractEditorExtension
        """
        return self._ext_editor

    def add_cascading_field_ctx(self, context):
        """
        Adds a cascading field context object to the collection.
        :param context: Instance of a cascading field context object.
        :type context: CascadingFieldContext
        """
        context.extension_editor = self._ext_editor
        self._cf_ctxts[context] = context

    def remove_cascading_field_ctx(self, context):
        """
        Removes the given context from the collection.
        :param context: Instance of a cascading field context object.
        :type context: CascadingFieldContext
        :return: Returns True if the context was successfully removed,
        otherwise False if it does not exist in the collection.
        :rtype: bool
        """
        if not context in self._cf_ctxts:
            return False

        # Check connection status and disconnect accordingly
        if context.is_connected:
            context.disconnect()

        del self._cf_ctxts[context]

        return True

    def __len__(self):
        """
        :return: Returns the number of contexts in the collection.
        :rtype: int
        """
        return len(self._cf_ctxts)

    def contexts(self):
        """
        :return: Returns a list of contexts in the collection.
        :rtype: list
        """
        return self._cf_ctxts.values()

    def connect(self):
        """
        Connects all contexts in the collection. It is called internally
        immediately after the custom editor extension post_init.
        """
        for ctx in self.contexts():
            ctx.connect()

    def disconnect(self):
        """
        Disconnects all contexts in the collection.
        """
        for ctx in self.contexts():
            ctx.disconnect()


class AbstractEditorExtension(object):
    """
    Abstract class that provides a basis for implementing extension classes.
    It provides functions for accessing various functionality of an entity
    editor form.
    """
    __metaclass__ = ABCMeta

    def __init__(self, entity_dialog):
        self._entity_dlg = entity_dialog
        self._notif_bar = self._entity_dlg.notification_bar
        self._cfc_mgr = CascadingFieldContextManager(self)

    def widget(self, attribute):
        """
        Get the widget corresponding to the given attribute or entity column.
        :param attribute: Column name for the given entity.
        :type attribute: str
        :return: Returns the widget if found, otherwise None.
        :rtype: QWidget
        """
        attr_map = self._entity_dlg.attribute_mapper(attribute)
        # If attribute does not exist in the MappperMixin collection
        if attr_map is None:
            LOGGER.debug(
                'Attribute named %s does not exist in the collection',
                attribute
            )
            return None

        return attr_map.control()

    @property
    def cascading_field_context_manager(self):
        """
        :return: Returns the manager for managing the cascading field
        context objects.
        :rtype: CascadingFieldContextManager
        """
        return self._cfc_mgr

    def add_cascading_field_ctx(self, context):
        """
        Adds a cascading field context object to the collection.
        :param context: Instance of a cascading field context object.
        :type context: CascadingFieldContext
        """
        self._cfc_mgr.add_cascading_field_ctx(context)

    def insert_error_notification(self, message):
        """
        Insert an error notification message to the editor dialog's
        notification bar.
        :param message: Error message
        :type message: str
        """
        if self._notif_bar is None:
            LOGGER.debug(
                'Instance of notification bar is None. Error message cannot '
                'be inserted'
            )
        else:
            self._notif_bar.insertErrorNotification(message)

    def insert_info_notification(self, message):
        """
        Insert an information notification message to the editor dialog's
        notification bar.
        :param message: Information message
        :type message: str
        """
        if self._notif_bar is None:
            LOGGER.debug(
                'Instance of notification bar is None. Info message cannot '
                'be inserted'
            )
        else:
            self._notif_bar.insertInformationNotification(message)

    def insert_warning_notification(self, message):
        """
        Insert a warning notification message to the editor dialog's
        notification bar.
        :param message: Warning message
        :type message: str
        """
        if self._notif_bar is None:
            LOGGER.debug(
                'Instance of notification bar is None. Warning message cannot'
                ' be inserted'
            )
        else:
            self._notif_bar.insertWarningNotification(message)

    def insert_success_notification(self, message):
        """
        Insert a success notification message to the editor dialog's
        notification bar.
        :param message: Success message
        :type message: str
        """
        if self._notif_bar is None:
            LOGGER.debug(
                'Instance of notification bar is None. Success message cannot'
                ' be inserted'
            )
        else:
            self._notif_bar.insertSuccessNotification(message)

    def debug_msg(self, message):
        """
        Insert a log debug message
        :param message: Message to be inserted in the logger's debug mode.
        :type message: str
        """
        LOGGER.debug(message)

    def validate(self):
        """
        Enables custom extension classes to specify additional validation
        logic before form data is saved or updated.
        To be overridden by subclasses.
        The default implementation returns True
        :return: Return True if the validation is successful, else False.
        :rtype: bool
        """
        return True

    def pre_init(self):
        """
        Eanbles custom extension classes to insert custom logic before the
        editor dialog's initialization in its constructor.
        To be overridden by subclasses.
        The default implementation does nothing.
        """
        pass

    def post_init(self):
        """
        Eanbles custom extension classes to insert custom logic after the
        editor dialog's initialization in its constructor.
        To be overridden by subclasses.
        The default implementation does nothing.
        """
        pass
