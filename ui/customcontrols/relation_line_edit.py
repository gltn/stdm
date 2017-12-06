"""
/***************************************************************************
Name                 : RelatedEntityLineEdit
Description          : Line edit that enables browsing of related entities
Date                 : 16/June/2016
copyright            : (C) 2016 by UN-Habitat and implementing partners.
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
from PyQt4.QtGui import (
    QDialog,
    QHBoxLayout,
    QApplication,
    QMessageBox,
    QIcon,
    QItemSelectionModel,
    QLineEdit,
    QPixmap,
    QStyle,
    QToolButton,
    QWidget
)
from PyQt4.QtCore import (
    Qt,
    QModelIndex
)
from qgis.utils import (
    iface
)
from stdm.data.database import AdminSpatialUnitSet
from stdm.data.configuration.columns import BaseColumn
from stdm.data.configuration import entity_model
from stdm.data.code_generator import CodeGenerator
from stdm.ui.admin_unit_selector import AdminUnitSelector
from stdm.ui.admin_unit_manager import SELECT
from stdm.ui.lookup_value_selector import LookupValueSelector
from stdm.settings import current_profile

class ForeignKeyLineEdit(QLineEdit):
    """
    Line edit that enables the browsing of related entities defined through
    foreign key constraint.
    """
    def __init__(self, column, parent=None, pixmap=None):
        """
        Class constructor.
        :param column: Column object containing foreign key information.
        :type column: BaseColumn
        :param parent: Parent widget for the control.
        :type parent: QWidget
        :param pixmap: Pixmap to use for the line edit button.
        :type pixmap: QPixmap
        """
        QLineEdit.__init__(self, parent)

        self.column = column
        self._entity = self.column.entity

        #Configure load button
        self.btn_load = QToolButton(parent)
        self.btn_load.setCursor(Qt.PointingHandCursor)
        self.btn_load.setFocusPolicy(Qt.NoFocus)
        px = QPixmap(':/plugins/stdm/images/icons/select_record.png')
        if not pixmap is None:
            px = pixmap
        self.btn_load.setIcon(QIcon(px))
        self.btn_load.setIconSize(px.size())
        self.btn_load.setStyleSheet('background: transparent; padding: 0px; '
                                    'border: none;')
        self.btn_load.clicked.connect(self.on_load_foreign_key_browser)

        clear_px = QPixmap(':/plugins/stdm/images/icons/clear.png')

        self.btn_clear = QToolButton(parent)
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.setFocusPolicy(Qt.NoFocus)
        self.btn_clear.setIcon(QIcon(clear_px))
        self.btn_clear.setIconSize(clear_px.size())
        self.btn_clear.setStyleSheet('background: transparent; padding: 0px; '
                                    'border: none;')

        self.btn_clear.clicked.connect(self.clear_line_edit)


        frame_width = self.set_button_minimum_size(self.btn_load)
        self.set_button_minimum_size(self.btn_clear)
        # Ensure that text does not overlay button
        padding = self.btn_load.sizeHint().width() + frame_width + 1

        self.setStyleSheet('padding-right: ' + str(padding * 2) + 'px;')

        # Set layout
        self.button_layout = QHBoxLayout(self)

        self.button_layout.addWidget(self.btn_clear, 0, Qt.AlignRight)
        self.button_layout.addWidget(self.btn_load, 0, Qt.AlignRight)

        self.button_layout.setSpacing(0)
        self.button_layout.setMargin(5)

        self.btn_clear.setVisible(False)
        # Readonly as text is loaded from the related entity
        self.setReadOnly(True)

        # Current model object
        self._current_item = None

    def set_button_minimum_size(self, button):
        """
        Sets the minimum button size.
        :param button: The button to be set.
        :type button: QToolButton
        :return: Returns the frame width of the button
        :rtype: Integer
        """
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        msz = self.minimumSizeHint()
        self.setMinimumSize(
            max(
                msz.width(),
                button.sizeHint().height() + frame_width * 2 + 2
            ), max(
                msz.height(),
                button.sizeHint().height() + frame_width * 2 + 2
            )
        )
        return frame_width

    @property
    def current_item(self):
        return self._current_item

    @current_item.setter
    def current_item(self, value):
        # Update display every time the current item is changed.
        self._current_item = value
        self.format_display()

    @property
    def entity(self):
        """
        :return: Returns the entity object corresponding to this widget.
        :rtype: Entity
        """
        return self._entity

    def clear_line_edit(self):
        """
        Clears the text in the line edit.
        """
        self.clear()
        self.hide_clear_button()

    def hide_clear_button(self):
        """
        Hides the clear button.
        """
        self.btn_clear.setVisible(False)
        self.button_layout.setStretch(0, 0)

    def show_clear_button(self):
        """
        Shows the clear button if a text exists.
        """
        if len(self.text()) > 0:
            self.btn_clear.setVisible(True)
            self.button_layout.setStretch(0, 5)

    def on_load_foreign_key_browser(self):
        """
        Slot raised to load browser for selecting foreign key entities. To be
        implemented by subclasses.
        """
        raise NotImplementedError

    def format_display(self):
        """
        Extract object values to show in the line edit based on the specified
        display columns.
        """
        raise NotImplementedError

    def parent_entity_model(self):
        """
        :return: Returns the database model corresponding to the parent table
        of the relation defined by this column. Please note that the database
        model will not contain relationship configurations in its attributes.
        :rtype: object
        """
        entity = self.column.entity_relation.parent

        return entity_model(entity, entity_only=True)

    def load_current_item_from_id(self, id):
        """
        Loads the current item from the id corresponding to the primary
        key.
        :param id: Primary key of the referenced entity.
        :type id: int
        """
        QApplication.processEvents()
        model = self.parent_entity_model()

        if model is None:
            return

        model_obj = model()
        res = model_obj.queryObject().filter(model.id == id).first()

        if not res is None:
            self.current_item = res


class RelatedEntityLineEdit(ForeignKeyLineEdit):
    """
    For browsing entity records through a EntityBrowser dialog.
    """
    # Use space for separating column values
    COLUMN_SEPARATOR = ' '

    def _on_record_selected(self, rec_id):
        self.load_current_item_from_id(rec_id)
        self.show_clear_button()

    @classmethod
    def process_display(cls, column, model_object):
        """
        Format display value.
        """
        display_columns = column.entity_relation.display_cols
        display_vals = []
        QApplication.processEvents()
        for c in display_columns:
            if hasattr(model_object, c):

                display_val = getattr(model_object, c)
                if isinstance(display_val, bool):
                    if display_val:
                        display_val = QApplication.translate(
                            'DateEditValueHandler', 'Yes'
                        )
                    else:
                        display_val = QApplication.translate(
                            'DateEditValueHandler', 'No'
                        )

                display_vals.append(display_val)
        try:
            return cls.COLUMN_SEPARATOR.join(display_vals)

        except RuntimeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'DateEditValueHandler',
                    "Attribute Table Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'DateEditValueHandler',
                    "Display Error"
                ),
                'Could not set display name. '
                'Please check if the data is saved.'
            )

    def format_display(self):
        #Display based on the configured display columns.
        if self.current_item is None:
            return
        QApplication.processEvents()
        display_value = RelatedEntityLineEdit.process_display(
            self.column,
            self.current_item
        )
        try:
            self.setText(display_value)
        except RuntimeError:

            QMessageBox.warning(
                None,
                QApplication.translate(
                    'AdministrativeUnitLineEdit',
                    "Attribute Table Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            pass

    def on_load_foreign_key_browser(self):
        # Show entity browser dialog.
        from stdm.ui.entity_browser import EntityBrowser
        parent_entity = self.column.entity_relation.parent
        eb = EntityBrowser(parent_entity, parent=self.parent(), state=SELECT)

        # Set item to be selected once records have been loaded
        if not self._current_item is None:
            eb.set_selection_record_id(self._current_item.id)

        # Use recordSelected signal to get the selected item
        eb.recordSelected.connect(self._on_record_selected)

        eb.exec_()


class AdministrativeUnitLineEdit(ForeignKeyLineEdit):
    """
    Custom implementation for selecting and displaying administrative areas
    using the name and corresponding code.
    """
    def __init__(self, *args, **kwargs):
        # Use a different pixmap
        px = QPixmap(':/plugins/stdm/images/icons/hierarchy.png')
        kwargs['pixmap'] = px

        ForeignKeyLineEdit.__init__(self, *args, **kwargs)

    def format_display(self):
        if self.current_item is None:
            return

        admin_name = self.current_item.Name
        if self.current_item.Code:
            admin_name = u'{0} ({1})'.format(
                admin_name,
                self.current_item.Code
            )
        try:
            self.setText(admin_name)
        except RuntimeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'AdministrativeUnitLineEdit',
                    "Attribute Table Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            pass

    def parent_entity_model(self):
        # Use default admin unit model class.
        return AdminSpatialUnitSet

    def _search_current_item_index(self, model, parent_index):
        # Recursively search for model index corresponding to current item
        if self.current_item is None:
            return None

        current_item_idx = None

        if model.hasChildren(parent_index):
            row_count = model.rowCount(parent_index)
            for i in range(row_count):
                #Check value from previous iteration
                if not current_item_idx is None:
                    break

                c_idx = model.index(i, 0, parent_index)
                node = c_idx.internalPointer()
                id = node.data(2)

                #Item found
                if id == self.current_item.id:
                    current_item_idx = c_idx
                    break

                else:
                    #Search children indices
                    current_item_idx = self._search_current_item_index(
                        model,
                        c_idx
                    )

        return current_item_idx

    def _select_current_item(self, model, selection_model, tv):
        #Selects the row corresponding to the current item
        if self._current_item is None:
            return

        root_idx = QModelIndex()
        current_item_idx = self._search_current_item_index(model, root_idx)

        #Expand items at the current item index
        self._expand_parent_indices(current_item_idx, tv)

        #Select item
        selection_model.select(
            current_item_idx,
            QItemSelectionModel.ClearAndSelect|QItemSelectionModel.Rows
        )

    def _expand_parent_indices(self, ref_index, tv):
        """
        Expand all parents of ref_index so that the hierarchy is better
        visualized.
        """
        parent_idx = ref_index.parent()
        while parent_idx.isValid():
            tv.expand(parent_idx)
            parent_idx = parent_idx.parent()

    def on_load_foreign_key_browser(self):
        #Show the selector for administrative units
        au_selector = AdminUnitSelector(self.parent())
        au_selector.setManageMode(False)

        item_model = au_selector.adminUnitManager.model()
        selection_model = au_selector.adminUnitManager.selection_model()

        #Highlight previously selected item
        self._select_current_item(
            item_model,
            selection_model,
            au_selector.adminUnitManager.tvAdminUnits
        )

        if au_selector.exec_() == QDialog.Accepted:
            self.current_item = au_selector.selectedAdminUnit
            self.show_clear_button()



class AutoGeneratedLineEdit(ForeignKeyLineEdit):
    """
    Custom implementation for selecting and displaying administrative areas
    using the name and corresponding code.
    """
    def __init__(self, *args, **kwargs):
        #Use a different pixmap
        px = QPixmap(':/plugins/stdm/images/icons/code.png')
        kwargs['pixmap'] = px
        self._code = None
        self._current_profile = current_profile()
        self._admin_hierarchy_code = None
        ForeignKeyLineEdit.__init__(self, *args, **kwargs)
        self.code_generator = CodeGenerator(self.entity, self.column)

    def format_display(self):
        try:
            self.setText(self._code)
        except RuntimeError:
            QMessageBox.warning(
                None,
                QApplication.translate(
                    'AutoGeneratedLineEdit',
                    "Value Error"
                ),
                'The change is not saved. '
                'Please use the form to edit data.'
            )
        except TypeError:
            pass

    def parent_entity_model(self):
        #Use default admin unit model class.
        return AdminSpatialUnitSet

    def _search_current_item_index(self, model, parent_index):
        #Recursively search for model index corresponding to current item
        if self.current_item is None:
            return None

        current_item_idx = None

        if model.hasChildren(parent_index):
            row_count = model.rowCount(parent_index)
            for i in range(row_count):
                #Check value from previous iteration
                if not current_item_idx is None:
                    break

                c_idx = model.index(i, 0, parent_index)
                node = c_idx.internalPointer()
                id = node.data(2)

                #Item found
                if id == self.current_item.id:
                    current_item_idx = c_idx
                    break

                else:
                    #Search children indices
                    current_item_idx = self._search_current_item_index(
                        model,
                        c_idx
                    )

        return current_item_idx

    def _select_current_item(self, model, selection_model, tv):
        #Selects the row corresponding to the current item
        if self._current_item is None:
            return

        root_idx = QModelIndex()
        current_item_idx = self._search_current_item_index(model, root_idx)

        #Expand items at the current item index
        self._expand_parent_indices(current_item_idx, tv)

        #Select item
        selection_model.select(
            current_item_idx,
            QItemSelectionModel.ClearAndSelect|QItemSelectionModel.Rows
        )

    def _expand_parent_indices(self, ref_index, tv):
        """
        Expand all parents of ref_index so that the hierarchy is better
        visualized.
        """
        parent_idx = ref_index.parent()
        while parent_idx.isValid():
            tv.expand(parent_idx)
            parent_idx = parent_idx.parent()

    def on_load_foreign_key_browser(self):
        if self.column.prefix_source == self.tr('None'):
            self.set_code_from_no_prefix()

        elif self.column.prefix_source == 'admin_spatial_unit_set':
            self.set_code_from_admin_unit()

        elif self.column.prefix_source == '':
            pass
        else:
            self.set_code_from_lookup()
        self.show_clear_button()

    def set_code_from_lookup(self):
        """
        Creates code from a lookup value code.
        Creates a code containing lookup value code and serial number.
        """
        lookup_selector = LookupValueSelector(
            iface.mainWindow(), self.column.prefix_source
        )
        result = lookup_selector.exec_()

        if result == QDialog.Accepted:
            self.current_item = lookup_selector
            self._code = self.code_generator.generate(
                lookup_selector.selected_code,
                self.column.separator,
                self.column.leading_zero
            )
            self.format_display()

    def set_code_from_admin_unit(self):
        """
        Set code from administrative unit. Creates code containing admin
        unit codes and serial number.
        """
        # Show the selector for administrative units
        au_selector = AdminUnitSelector(self.parent())
        au_selector.setManageMode(False)
        item_model = au_selector.adminUnitManager.model()
        selection_model = au_selector.adminUnitManager.selection_model()
        # Highlight previously selected item
        self._select_current_item(
            item_model,
            selection_model,
            au_selector.adminUnitManager.tvAdminUnits
        )
        if au_selector.exec_() == QDialog.Accepted:
            self.current_item = au_selector.selectedAdminUnit
            self._admin_hierarchy_code = self.current_item.hierarchyCode(
                self.column.separator
            )
            self._code = self.code_generator.generate(
                self._admin_hierarchy_code,
                self.column.separator,
                self.column.leading_zero
            )
            self.format_display()

    def set_code_from_no_prefix(self):
        """
        Set code from None prefix. Creates a serial number without prefix.
        """
        self.current_item = ''
        # The prefix and separator should be '' for a serial.
        self._code = self.code_generator.generate(
            '',
            '',
            self.column.leading_zero
        )
        self._code = self._code[1:]
        self.format_display()
