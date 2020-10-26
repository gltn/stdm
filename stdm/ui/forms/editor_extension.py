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

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QWidget
)

from stdm.ui.forms import REG_EDITOR_CLS_EXTENSIONS


LOGGER = logging.getLogger('stdm')


def data_context(profile, entity):
    """
    A decorator function for registering custom extension classes that are
    subclasses of AbstractEditorExtension class.
    :param profile: Profile name.
    :type profile: str
    :param entity: Entity name.
    :type entity: str
    """
    def register_ext(cls):
        if issubclass(cls, AbstractEditorExtension):
            REG_EDITOR_CLS_EXTENSIONS[(profile, entity)] = cls
        else:
            LOGGER.debug(
                'Cannot register editor extension for %s entity '
                'in %s profile.',
                profile,
                entity
            )

        return cls

    return register_ext


def cascading_field_ctx(src_lk, target_lk, src_values, target_values):
    """
    Creates a CascadingFieldContext object and adds the corresponding
    mapping for source and target values respectively.
    :param src_lk: Name of the source lookup column.
    :type src_lk: str
    :param target_lk: Name of the target lookup column whose corresponding
    widget will filter its values based on the selected value in the source
    combobox.
    :type target_lk: str
    :param src_values: A list of string values representing codes in the
    source lookup table which will be paired with the corresponding target
    values.
    :type src_values: list
    :param target_values: A list of tuples where each tuple contains the
    codes of the values in the target lookup table. For correct pairing, the
    index of each tuple in the list needs to match with that of the list of
    the source values.
    :type target_values: list
    :return: Returns a CascadingFieldContext object whose source values have
    been mapped to the corresponding target values.
    :rtype: CascadingFieldContext
    """
    cf_ctx = CascadingFieldContext(src_lk, target_lk)
    idx_clc = zip(src_values, target_values)
    for i in idx_clc:
        cf_ctx.add_mapping(i[0], i[1])

    return cf_ctx


class CascadingFieldContext(object):
    """
    Provides a mechanism for defining cascading or drill down functionality
    for comboboxes containing related data.
    The values in the source and target comboboxes must have codes defined
    as specified in the configuration. These codes will be used to specify
    the source-target value mapping.
    The target combobox is empty when no item has been selected in the
    source combobox or if there are no matching code values specified for
    the target items.
    """
    class _TargetCodeIdx(object):
        """
        Container for an item including text, code value, original index and
        database primary key in the target combo.
        """
        def __init__(self, text, code_value, idx, db_idx):
            self.text = text
            self.cd = code_value
            self.idx = idx
            self.db_idx = db_idx

    def __init__(self, source_lookup_col, target_lookup_col):
        """
        :param source_lookup_col: Name of the lookup column in an entity whose
        corresponding lookup values will be used to filter items in the
        target combobox.
        :type source_lookup_col: str
        :param target_lookup_col: Name of the lookup column whose corresponding
        lookup values will be filtered based on the selected item in the
        source combobox.
        :type target_lookup_col: str
        """
        self._src_cbo_str = source_lookup_col
        self._target_cbo_str = target_lookup_col
        self._id = hash(
            (self._src_cbo_str, self._target_cbo_str)
        )
        self._src_target_mapping = {}
        self._src_cbo = None
        self._target_cbo = None
        self._ext_editor = None
        self._entity = None
        self._src_vl = None
        self._target_vl = None
        self._is_sig_connected = False

        # Store the index of the code values in the target combobox
        self._target_cd_idx = {}

    @property
    def source_attribute(self):
        """
        :return: Returns the name of the lookup column in an entity whose
        corresponding lookup values will be used to filter items in the
        target combobox.
        :rtype: str
        """
        return self._src_cbo_str

    @property
    def target_attribute(self):
        """
        :return: Name of the lookup column whose corresponding lookup values
        will be filtered based on the selected item in the source combobox.
        :rtype: str
        """
        return self._target_cbo_str

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
        if self._ext_editor is None:
            self._ext_editor = ext_editor
            self._src_cbo = self._ext_editor.widget(self._src_cbo_str)
            self._target_cbo = self._ext_editor.widget(self._target_cbo_str)
            self._entity = self._ext_editor.entity_dialog.entity
            self._src_vl = self._entity.column(self._src_cbo_str).value_list
            self._target_vl = self._entity.column(
                self._target_cbo_str
            ).value_list

            # Update cache of code/idx in target combo
            self._update_target_code_idx()

            # Remove all items in the target combobox
            self._target_cbo.clear()
        else:
            LOGGER.debug(
                'Extension editor has already been set.'
            )

    def _update_target_code_idx(self):
        # Update the cache of code values in the target combobox.
        for i in range(self.target_combobox.count()):
            db_idx = self.target_combobox.itemData(i)
            text = self.target_combobox.itemText(i)
            cv = self._target_vl.code_value(text)
            cd = ''
            if cv:
                cd = cv.code
            if cd:
                cd_idx_obj = CascadingFieldContext._TargetCodeIdx(
                    text,
                    cd,
                    i,
                    db_idx
                )
                self._target_cd_idx[cd] = cd_idx_obj

    def restore_target_values(self):
        """
        Restore all items in the target combobox.
        """
        for tci in self._target_cd_idx.values():
            self.target_combobox.insertItem(
                tci.idx,
                tci.text,
                tci.db_idx
            )

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

    def target_values(self, source_value):
        """
        Fetches the collection of target code values mapped to the specified
        source code value.
        :param source_value: Source code value.
        :type source_value: str
        :return: Returns the collection of target code values mapped to the
        specified source code value, otherwise None if there is no source
        code value existing in the collection.
        :rtype: tuple
        """
        return self._src_target_mapping.get(source_value, None)

    def connect(self):
        """
        Connect the source combo's currentIndexChanged signal to filter the
        items in the target combobox based on the source-target value mapping.
        """
        if self.source_combobox is None:
            LOGGER.debug(
                'Source combobox for %s attribute is None.',
                self.source_attribute
            )
            return

        if self.target_combobox is None:
            LOGGER.debug(
                'Target combobox for %s attribute is None.',
                self.target_attribute
            )
            return

        self.source_combobox.currentIndexChanged.connect(
            self._on_source_idx_changed
        )

        self._is_sig_connected = True

    def _on_source_idx_changed(self, idx):
        # Slot raised when the currentIndex in the source combo changes
        # Remove all items in target combobox
        self._target_cbo.clear()

        if idx < 0:
            return

        src_val = self.source_combobox.itemText(idx)

        # Get code stored in the source value list
        cd = self._src_vl.code_value(src_val)
        if cd is None:
            LOGGER.debug(
                'Code for lookup value %s could not be found.',
                src_val
            )
            return

        self.filter_target_values(cd.code)

    def filter_target_values(self, source_value):
        """
        Filter target values based on selected source code value.
        :param source_value: Source code value.
        :type source_value: str
        """
        if not source_value:
            LOGGER.debug(
                'Source code value is empty, cannot filter target values.'
            )
            return

        if source_value in self._src_target_mapping:
            target_items = self._src_target_mapping[source_value]

            # Add an empty item
            self.target_combobox.addItem('', None)

            # Populate the target combobox while maintaining the order in
            # the cache
            for ti in self._target_cd_idx.values():
                if ti.cd in target_items:
                    self.target_combobox.insertItem(
                        ti.idx,
                        ti.text,
                        ti.db_idx
                    )
        else:
            LOGGER.debug(
                'No mapping defined for %s source value.',
                source_value
            )

    def disconnect(self):
        """
        Disconnects the source combo's currentIndexChanged signal after which
        no filtering will be applied when the currentIndex of the source
        combo changes.
        """
        self.source_combobox.currentIndexChanged.disconnect(
            self._on_source_idx_changed
        )

        # Restore target values
        self.restore_target_values()

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
    Used internally by the AbstractEditorExtension.
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
        :return: Returns the number of contexts in the context manager.
        :rtype: int
        """
        return len(self._cf_ctxts)

    def contexts(self):
        """
        :return: Returns a list of contexts in the context manager.
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

    @property
    def entity_dialog(self):
        """
        :return: Returns an instance of the EntityEditorDialog associated
        with the editor extension.
        :rtype: EntityEditorDialog
        """
        return self._entity_dlg

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

    def connect_cf_contexts(self):
        """
        Connect cascading field contexts.
        """
        self._cfc_mgr.connect()

    def disconnect_cf_contexts(self):
        """
        Disconnect all cascading field contexts in the collection.
        """
        self._cfc_mgr.disconnect()

    def add_cascading_field_ctx(self, context):
        """
        Adds a cascading field context object to the collection.
        :param context: Instance of a cascading field context object.
        :type context: CascadingFieldContext
        """
        self._cfc_mgr.add_cascading_field_ctx(context)

    def is_update_mode(self):
        """
        :return: Returns True if the parent form is in UPDATE mode,
        otherwise False if in SAVE mode when creating a new record.
        :rtype: bool
        """
        return self._entity_dlg.is_update_mode()

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
        The default implementation returns True.
        :return: Return True if the validation is successful, else False.
        :rtype: bool
        """
        return True

    def post_init(self):
        """
        Enables custom extension classes to insert custom logic after the
        editor dialog's initialization is complete in the constructor.
        To be overridden by subclasses.
        The default implementation does nothing.
        """
        pass

    def post_save(self, model):
        """
        Custom extension classes can incorporate additional logic once form
        data has been saved based on the information contained in the model
        object.
        Default implementation does nothing.
        :param model: SQALchemy model containing information about the
        saved record.
        :type model: object
        """
        pass


