"""
/***************************************************************************
Name                 : Work Manager Configuration
Description          : Configuration manager
Date                 : 21/August/2019
copyright            : (C) 2019
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

from collections import namedtuple
from PyQt4.QtCore import (QSize, Qt,)
from PyQt4.QtGui import (
    QApplication,
    QIcon,
    QMessageBox
)
from sqlalchemy import exc
from stdm.settings import current_profile
from stdm.data.configuration import entity_model

configurations = None


class Config(object):
    """
    Workflow Manager configuration interface
    """
    def __init__(self):
        self._configurations = configurations
        self._parent = None

    def get_data(self, option):
        """
        Get configuration data for the given setting
        :param option: Configuration property name
        :return: Configuration data
        :rtype: Multiple types
        """
        return self._configurations.get(option, None)


class ButtonIcons(Config):
    """
    QPushButton icons configuration interface
    """
    def __init__(self):
        super(ButtonIcons, self).__init__()
        self.Icon = namedtuple('Icon', ['icon', 'size'])

    def button_icons(self, config):
        """
        QPushButton icon configuration options
        :param config: QPushButton icon configurations
        :type config: Tuple
        :return: QPushButton icon options
        :rtype: Dictionary
        """

        return {
            button: self.Icon(icon=icon, size=qsize)
            for button, qsize, icon in config
        }


class CommentButtonIcons(ButtonIcons):
    """
    Comment Manager QPushButton icons configuration interface
    """

    def __init__(self, parent=None):
        super(CommentButtonIcons, self).__init__()
        self._parent = parent

    @property
    def buttons(self):
        """
        Comment Manager QPushButton icons options
        :return: Comment Manager QPushButton icon options
        :rtype: Dictionary
        """
        config = self._buttons_config()
        return super(CommentButtonIcons, self).button_icons(config)

    def _buttons_config(self):
        """
        Returns Comment Manager QPushButton icon configurations
        :return: QPushButton icon configurations
        :rtype: Tuple
        """
        return (
            (
                self._parent.submitButton, QSize(24, 24),
                QIcon(":/plugins/stdm/images/icons/flts_comment_reply.png")
            ),
        )


class CommentConfig(Config):
    """
    Comment Manager widget configuration interface
    """
    @property
    def columns(self):
        """
        Comment Manager widget columns options
        :return: Comment Manager widget columns and query columns options
        :rtype: List
        """
        return self.get_data('comment_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('comment_collections')

    @property
    def load_collections(self):
        """
        Related entity collection names to be used as
        primary load data for the Comment Manager widget
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('comment_load_collections')

    @property
    def lookups(self):
        """
        Comment text edit lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')

    @property
    def comment_save_columns(self):
        """
        Comment text edit save column options
        :return: Save column values
        :rtype: List
        """
        return self.get_data('save_columns').\
            get('comment_save', None)


class DocumentConfig(Config):
    """
    Scheme supporting documents table
    view configuration interface
    """
    @property
    def columns(self):
        """
        Scheme supporting documents
        table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('document_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('document_collections')

    @property
    def lookups(self):
        """
        Scheme supporting documents lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')


class HolderConfig(Config):
    """
    Scheme holders table view configuration interface
    """
    @property
    def columns(self):
        """
        Scheme holders table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('holder_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('holder_collections')

    @property
    def load_collections(self):
        """
        Related entity collection names to be used as
        primary table view load
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('holder_load_collections')


class PlotImportFileConfig(Config):
    """
    Scheme plot import file table view
    configuration interface
    """
    @property
    def columns(self):
        """
        Scheme plot import file
        table view columns options
        :return: Table view columns
        :rtype: List
        """
        return self.get_data('plot_file_columns')


class PlotImportPreviewConfig(Config):
    """
    Scheme plot import preview table view
    configuration interface
    """
    @property
    def columns(self):
        """
        Scheme plot import preview
        table view columns options
        :return: Table view columns
        :rtype: List
        """
        return self.get_data('plot_preview_columns')


class StyleSheet(Config):
    """
    Widget style sheet interface
    """
    @property
    def header_style(self):
        """
        Get header style sheet
        :return: Header style sheet
        :rtype: String
        """
        return self.get_data('header_view_style')


class ToolbarButtonsConfig(Config):
    """
    Scheme toolbar QPushButton configuration interface
    """
    def __init__(self):
        super(ToolbarButtonsConfig, self).__init__()

    @property
    def buttons(self):
        """
        Returns toolbar QPushButton configurations
        :return: QPushButton configuration options
        :rtype: Dictionary
        """
        return self.get_data('toolbar_buttons')


class PaginationButtonsConfig(Config):
    """
    Scheme pagination QPushButton configuration interface
    """
    def __init__(self):
        super(PaginationButtonsConfig, self).__init__()

    @property
    def buttons(self):
        """
        Returns pagination QPushButton configurations
        :return: QPushButton configuration options
        :rtype: Dictionary
        """
        return self.get_data('pagination_buttons')


class PlotImportButtonsConfig(Config):
    """
    Scheme plot import QPushButton configuration interface
    """
    def __init__(self):
        super(PlotImportButtonsConfig, self).__init__()

    @property
    def buttons(self):
        """
        Returns plot import QPushButton configurations
        :return: QPushButton configuration options
        :rtype: Dictionary
        """
        return self.get_data('plot_import_buttons')


class SchemeConfig(Config):
    """
    Scheme table view configuration interface
    """
    def __init__(self, parent=None):
        super(SchemeConfig, self).__init__()
        self._parent = parent

    @property
    def columns(self):
        """
        Scheme table view columns options
        :return: Table view columns and query columns options
        :rtype: List
        """
        return self.get_data('scheme_columns')

    @property
    def collections(self):
        """
        Related entity collection names
        :return: Related entity collection names
        :rtype: List
        """
        return self.get_data('scheme_collections')

    @property
    def lookups(self):
        """
        Scheme table view lookup options
        :return: Lookup options
        :rtype: LookUp
        """
        return self.get_data('lookups')

    @property
    def scheme_save_columns(self):
        """
        Scheme table view save column options
        :return: Save column values
        :rtype: List
        """
        return self.get_data('save_columns').\
            get('scheme_save', None)

    @property
    def scheme_update_columns(self):
        """
        Scheme table view update column options
        :return: Update column values
        :rtype: List
        """
        return self.get_data('update_columns').\
            get('scheme_update', None)


class SchemeMessageBox(Config):
    """
    Scheme QMessageBox configuration interface
    """

    @property
    def message_box(self):
        """
        Returns QMessageBox configurations
        :return: QMessageBox configuration options
        :rtype: Dictionary
        """
        return self.get_data('message_box')


class TabIcons(Config):
    """
    QTabWidget icons configuration interface
    """
    def __init__(self):
        super(TabIcons, self).__init__()

    @property
    def icons(self):
        """
        QTabWidget icon options
        :return: QTabWidget icon options
        :rtype: Dictionary
        """
        return self.get_data('tab_icons')


class TableModelIcons(Config):
    """
    QAbstractTableModel icons configuration interface
    """
    def __init__(self):
        super(TableModelIcons, self).__init__()

    @property
    def icons(self):
        """
        QAbstractTableModel icon options
        :return: QAbstractTableModel icon options
        :rtype: Dictionary
        """
        return self.get_data('table_model_icons')


class FilterQueryBy:
    """
    Filters query result by a column value
    """
    def __init__(self):
        self._profile = None

    def __call__(self, entity_name, filters):
        """
        Return query object on filter by a column value
        :param entity_name: Entity name
        :type entity_name: String
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            if not self._profile:
                self._profile = current_profile()
            query_obj = self._entity_query_object(entity_name)
            return self._filter_by(query_obj, filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    @staticmethod
    def _filter_by(query_obj, filters):
        """
        Return filter entity query object
        :param query_obj: Entity query object
        :type query_obj: List
        :param filters: Column filters - column name and value
        :type filters: Dictionary
        :return: Filter entity query object
        :rtype: Entity object
        """
        try:
            return query_obj.filter_by(**filters)
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_query_object(self, entity_name):
        """
        Return query object of an entity
        :param entity_name: Entity name
        :type entity_name: String
        :return:Entity query object
        :rtype List
        """
        model = self._entity_model(entity_name)
        entity_object = model()
        try:
            return entity_object.queryObject()
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e

    def _entity_model(self, name):
        """
        Gets entity model
        :param name: Name of the entity
        :type name: String
        :return model: Entity model;
        :rtype model: DeclarativeMeta
        """
        try:
            entity = self._profile.entity(name)
            model = entity_model(entity)
            return model
        except AttributeError as e:
            raise e


class EntityRecordId(Config):
    """
    Returns entity record ID
    """
    def __init__(self, entity_name, filters):
        super(EntityRecordId, self).__init__()
        self._entity_name = entity_name
        self._filters = filters
        self._results = None

    def __call__(self):
        """
        Return entity record ID filtered by a column value
        :return id: Entity record ID
        :rtype id: Integer
        """
        if not self._results:
            try:
                filter_by = FilterQueryBy()
                self._results = filter_by(
                    self._entity_name, self._filters
                ).first().id
            except (AttributeError, exc.SQLAlchemyError, Exception) as e:
                msg = QApplication.translate(
                    'Workflow Manager',
                    "Failed to get record id: {}".format(e)
                )
                QMessageBox.critical(
                    self._parent,
                    'Workflow Manager',
                    msg
                )
        return self._results


class ColumnSettings:
    """
    Column associated properties
    """
    def __init__(self, name, type_, flag=None):
        self.name = name
        self.type = type_
        self.flag = flag if flag else (False,)

    def settings(self):
        """
        Returns column settings
        :return: Column settings
        :return: Column (namedtuple)
        """
        column = Column(name=self.name, type=self.type, flag=self.flag)
        return column


Column = namedtuple('Column', ['name', 'type', 'flag'])
Icon = namedtuple('Icon', ['icon', 'size'])
LookUp = namedtuple(
    'LookUp',
    [
        'schemeLodgement', 'schemeEstablishment', 'firstExamination',
        'secondExamination', 'thirdExamination', 'importPlot', 'APPROVAL_STATUS',
        'WORKFLOW', 'WORKFLOW_COLUMN', 'APPROVAL_COLUMN', 'APPROVED',
        'PENDING', 'DISAPPROVED', 'HELD', 'CHECK', 'STATUS',
        'SCHEME_COLUMN', 'SCHEME_NUMBER', 'COMMENT_COLUMN', 'VIEW_PDF'
    ]
)
MessageBox = namedtuple(
    'MessageBox', ['name', 'label', 'role', 'icon']
)
buttonConfig = namedtuple(
    'buttonConfig', ['name', 'label', 'icon', 'size', 'enable']
)
SaveColumn = namedtuple('SaveColumn', ['column', 'value', 'entity'])
UpdateColumn = namedtuple('UpdateColumn', ['column', 'value'])

configurations = {
    'comment_columns': [
        {Column(name='Comment', type="text", flag=(Qt.DisplayRole,)): 'comment'},
        {
            Column(
                name='User', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_user': 'user_name'}
        },
        {
            Column(
                name='First Name', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_user': 'first_name'}
        },
        {
            Column(
                name='Last Name', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_user': 'last_name'}
        },
        {Column(
            name='Post Date', type="datetime", flag=(Qt.DisplayRole,)
        ): 'timestamp'}
    ],
    'comment_collections': ['cb_scheme_collection'],
    'comment_load_collections': ['cb_comment_collection'],
    'document_columns': [
        {Column(name='Scheme Number', type="text", flag=(Qt.DisplayRole,)): 'name'},
        {
            Column(
                name='Document Type', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_scheme_document_type': 'value'}
        },
        {
            Column(
                name='Document Size', type="integer", flag=(Qt.DisplayRole,)
            ): 'document_size'
        },
        {
            Column(
                name='Last Modified', type="datetime", flag=(Qt.DisplayRole,)
            ): 'last_modified'
        },
        {Column(name='Created By', type="text", flag=(Qt.DisplayRole,)): 'created_by'},
        {
            Column(
                name='View Document', type="decoration", flag=(Qt.DecorationRole,)
            ): 'View'
        }
    ],
    'document_collections': ['cb_scheme_supporting_document_collection'],
    'header_view_style': 'QHeaderView::section{'
                         'border-top:0px solid #C4C2BF;'
                         'border-left:0px solid #C4C2BF;'
                         'border-right: 1px solid #C4C2BF;'
                         'border-bottom: 1px solid #A9A5A2;'
                         'padding:4px;'
                         'background-color: qlineargradient'
                         '(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}'
                         'QTableCornerButton::section{'
                         'border-top:0px solid #C4C2BF;'
                         'border-left:0px solid #C4C2BF;'
                         'border-right: 1px solid #C4C2BF;'
                         'border-bottom: 1px solid #A9A5A2;'
                         'background-color: qlineargradient'
                         '(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #E4E3E2);'
                         '}',
    'holder_columns': [
        {
            Column(
                name='Scheme Number', type="text", flag=(Qt.DisplayRole,)
            ): {'scheme_number': 'scheme_number'}
        },
        {Column(name='First Name', type="text", flag=(Qt.DisplayRole,)): 'first_name'},
        {Column(name='Surname', type="text", flag=(Qt.DisplayRole,)): 'surname'},
        {
            Column(
                name='Gender', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_gender': 'value'}
        },
        {
            Column(
                name='Holder Identifier', type="text", flag=(Qt.DisplayRole,)
            ): 'holder_identifier'
        },
        {
            Column(
                name='Date of Birth', type="date", flag=(Qt.DisplayRole,)
            ): 'date_of_birth'
        },
        {
            Column(
                name='Name of Juristic Person', type="text", flag=(Qt.DisplayRole,)
            ): 'name_of_juristic_person'
        },
        {
            Column(
                name='Reg. No. of Juristic Person', type="text", flag=(Qt.DisplayRole,)
            ): 'reg_no_of_juristic_person'
        },
        {
            Column(
                name='Marital Status', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_marital_status': 'value'}
        },
        {
            Column(
                name='Spouse Surname', type="text", flag=(Qt.DisplayRole,)
            ): 'spouse_surname'
        },
        {
            Column(
                name='Spouse First Name', type="text", flag=(Qt.DisplayRole,)
            ): 'spouse_first_name'
        },
        {
            Column(
                name='Spouse Gender', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_gender': 'value'}
        },
        {
            Column(
                name='Spouse Identifier', type="text", flag=(Qt.DisplayRole,)
            ): 'spouse_identifier'
        },
        {
            Column(
                name='Spouse Date of Birth', type="date", flag=(Qt.DisplayRole,)
            ): 'spouse_date_of_birth'
        },
        {
            Column(
                name='Disability Status', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_disability': 'value'}
        },
        {
            Column(
                name='Income Level', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_income_level': 'value'}
        },
        {
            Column(
                name='Occupation', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_occupation': 'value'}
        },
        {
            Column(
                name='Other Dependants', type="integer", flag=(Qt.DisplayRole,)
            ): 'other_dependants'
        },
    ],
    'holder_collections': ['cb_scheme_collection'],
    'holder_load_collections': ['cb_holder_collection'],
    'lookups': LookUp(
        APPROVAL_STATUS='check_lht_approval_status',
        WORKFLOW='check_lht_workflow',
        schemeLodgement=EntityRecordId(
            'check_lht_workflow', {'value': 'Lodgement'}
        ),
        schemeEstablishment=EntityRecordId(
            'check_lht_workflow', {'value': 'Establishment'}
        ),
        firstExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'First Assessment'}
        ),
        secondExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'Second Assessment'}
        ),
        thirdExamination=EntityRecordId(
            'check_lht_workflow', {'value': 'Third Assessment'}
        ),
        importPlot=EntityRecordId(
            'check_lht_workflow', {'value': 'Import Plot'}
        ),
        APPROVED=EntityRecordId(
            'check_lht_approval_status', {'value': 'Approved'}
        ),
        PENDING=EntityRecordId(
            'check_lht_approval_status', {'value': 'Pending'}
        ),
        DISAPPROVED=EntityRecordId(
            'check_lht_approval_status', {'value': 'Disapproved'}
        ),
        HELD=EntityRecordId(
            'check_lht_approval_status', {'value': 'Held'}
        ),
        WORKFLOW_COLUMN='workflow_id', APPROVAL_COLUMN='approval_id',
        SCHEME_COLUMN='scheme_id', SCHEME_NUMBER=1, CHECK=0, STATUS=2,
        COMMENT_COLUMN='comment', VIEW_PDF=5
    ),
    'scheme_columns': [
        {Column(name='', type="integer", flag=(Qt.ItemIsUserCheckable,)): '0'},
        {
            Column(
                name='Scheme Number', type="text", flag=(Qt.DisplayRole,)
            ): 'scheme_number'
        },
        {
            Column(
                name='Status', type="integer", flag=(Qt.DecorationRole,)
            ): {'approval_id': 'approval_id'}
        },
        {
            Column(
                name='Approval Date', type="date", flag=(Qt.DisplayRole,)
            ): 'date_of_approval'
        },
        {
            Column(
                name='Establishment Date', type="date", flag=(Qt.DisplayRole,)
            ): 'date_of_establishment'
        },
        {
            Column(
                name='Type of Relevant Authority', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_relevant_authority': 'value'}
        },
        {
            Column(
                name='Land Rights Office', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_land_rights_office': 'value'}
        },
        {
            Column(
                name='Region', type="text", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_region': 'value'}
        },
        {Column(name='Township', type="text", flag=(Qt.DisplayRole,)): 'township_name'},
        {
            Column(
                name='Registration Division', type="integer", flag=(Qt.DisplayRole,)
            ): {'cb_check_lht_reg_division': 'value'}
        },
        {Column(name='Block Area', type="float", flag=(Qt.DisplayRole,)): 'area'},
        {
            Column(
                name='Date/Time', type="datetime", flag=(Qt.DisplayRole,)
            ): {'timestamp': 'timestamp'}
        }
    ],
    'scheme_collections': ['cb_scheme_workflow_collection'],
    'plot_file_columns': [
        Column(
            name='Name', type="text", flag=(Qt.DisplayRole, Qt.TextColorRole,)
        ),
        Column(
            name='Import as', type="list", flag=(
                Qt.DisplayRole, Qt.TextColorRole, Qt.ItemIsEditable
            )
        ),
        Column(
            name='Delimiter', type="list", flag=(
                Qt.DisplayRole, Qt.TextColorRole, Qt.ItemIsEditable
            )
        ),
        Column(
            name='Header row', type="integer", flag=(
                Qt.DisplayRole, Qt.TextColorRole, Qt.ItemIsEditable
            )
        ),
        Column(
            name='CRS ID', type="text", flag=(Qt.DisplayRole, Qt.TextColorRole,)
        ),
        Column(
            name='Geometry field', type="list", flag=(
                Qt.DisplayRole, Qt.TextColorRole, Qt.ItemIsEditable
            )
        ),
        Column(
            name='Geometry Type', type="list", flag=(
                Qt.DisplayRole, Qt.TextColorRole, Qt.ItemIsEditable
            )
        )
    ],
    'plot_preview_columns': [
        Column(name='Parcel Number', type="text", flag=(Qt.DisplayRole,)),
        Column(name='UPI Number', type="text", flag=(Qt.DisplayRole,)),
        Column(name='Geometry', type="text", flag=(Qt.DisplayRole,)),
        Column(name='Area', type="float", flag=(Qt.DisplayRole,))
    ],
    'tab_icons': {
        'Holders': QIcon(":/plugins/stdm/images/icons/flts_scheme_holders.png"),
        'Documents': QIcon(":/plugins/stdm/images/icons/flts_scheme_documents.png"),
        'Comments': QIcon(":/plugins/stdm/images/icons/flts_scheme_comment.png"),
        'Hold': QIcon(":/plugins/stdm/images/icons/flts_scheme_withdraw.png"),
        'Scheme': QIcon(":/plugins/stdm/images/icons/flts_scheme.png")
    },
    'table_model_icons': {
        1: QIcon(":/plugins/stdm/images/icons/flts_approve.png"),
        2: QIcon(":/plugins/stdm/images/icons/flts_pending.png"),
        3: QIcon(":/plugins/stdm/images/icons/flts_disapprove.png"),
        4: QIcon(":/plugins/stdm/images/icons/flts_withdraw.png"),
        'View': QIcon(":/plugins/stdm/images/icons/flts_document_view.png"),
        'Warning': QIcon(":/plugins/stdm/images/icons/warning.png")
    },
    'toolbar_buttons': {
        'sharedButtons': [
            buttonConfig(
                name="Holders",
                label="Holders",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_holders.png"),
                size=QSize(24, 24),
                enable=False

            ),
            buttonConfig(
                name="Documents",
                label="Documents",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_documents.png"),
                size=QSize(24, 24),
                enable=False
            ),
            buttonConfig(
                name="Comments",
                label="Comments",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_comment.png"),
                size=QSize(24, 24),
                enable=False
            )
        ],
        'searchButton': [
            buttonConfig(
                name="searchButton",
                label="Search",
                icon=QIcon(":/plugins/stdm/images/icons/flts_search.png"),
                size=QSize(24, 24),
                enable=False
            )
        ],
        'schemeLodgement': [
            buttonConfig(
                name="approveButton",
                label="Pass",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_approve.png"),
                size=QSize(24, 24),
                enable=False
            ),
            buttonConfig(
                name="holdButton",
                label="Hold",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_withdraw.png"),
                size=QSize(24, 24),
                enable=False
            )
        ],
        'schemeExamination': [
            buttonConfig(
                name="approveButton",
                label="Pass",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_approve.png"),
                size=QSize(24, 24),
                enable=False
            ),
            buttonConfig(
                name="disapproveButton",
                label="Reject",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_disapprove.png"),
                size=QSize(24, 24),
                enable=False
            )
        ],
        'thirdExamination': [
            buttonConfig(
                name="Plots",
                label="Plots",
                icon=QIcon(":/plugins/stdm/images/icons/flts_plot_module_cropped.png"),
                size=QSize(24, 24),
                enable=False
            )
        ],
        'importPlot': [
            buttonConfig(
                name="plotsImportButton",
                label="Import",
                icon=QIcon(":/plugins/stdm/images/icons/flts_import_plot_cropped.png"),
                size=QSize(24, 24),
                enable=False
            ),
            buttonConfig(
                name="Plots",
                label="Plots",
                icon=QIcon(":/plugins/stdm/images/icons/flts_plot_module_cropped.png"),
                size=QSize(24, 24),
                enable=False
            ),
        ]
    },
    'pagination_buttons': {
        'previousButtons': [
            buttonConfig(
                name="First",
                label="First",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_first_record.png"),
                size=QSize(24, 24),
                enable=True
            ),
            buttonConfig(
                name="Previous",
                label="Previous",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_previous_record.png"),
                size=QSize(24, 24),
                enable=True
            )
        ],
        'nextButtons': [
            buttonConfig(
                name="Next",
                label="Next",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_next_record.png"),
                size=QSize(24, 24),
                enable=True
            ),
            buttonConfig(
                name="Last",
                label="Last",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_last_record.png"),
                size=QSize(24, 24),
                enable=True
            )
        ]
    },
    'plot_import_buttons': {
        'toolbar': [
            buttonConfig(
                name="addFiles",
                label="Add file(s)...",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_docs_dir.png"),
                size=None,
                enable=True
            ),
            buttonConfig(
                name="removeFiles",
                label="Remove file(s)",
                icon=QIcon(":/plugins/stdm/images/icons/flts_disapprove.png"),
                size=None,
                enable=False
            ),
            buttonConfig(
                name="setCRS",
                label="Set CRS",
                icon=QIcon(":/plugins/stdm/images/icons/flts_scheme_crs"),
                size=None,
                enable=False
            ),
            buttonConfig(
                name="Preview",
                label="Preview",
                icon=QIcon(":/plugins/stdm/images/icons/flts_document_view.png"),
                size=None,
                enable=False
            ),
            buttonConfig(
                name="Import",
                label="Import",
                icon=QIcon(":/plugins/stdm/images/icons/flts_import_plot_cropped.png"),
                size=None,
                enable=False
            )
        ]
    },
    'message_box': {
        'approveButton': [
            MessageBox(
                name='approveMsgButton',
                label="Pass",
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_approve.png")
            ),
            MessageBox(
                name=None,
                label="Cancel",
                role=QMessageBox.RejectRole,
                icon=None
            )
        ],
        'disapproveButton': [
            MessageBox(
                name='disapproveMsgButton',
                label="Reject",
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_disapprove.png")
            ),
            MessageBox(
                name='commentDisapproveMsgButton',
                label="Comment && Reject",
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_comment_reply_2.png")
            ),
            MessageBox(
                name=None,
                label="Cancel",
                role=QMessageBox.RejectRole,
                icon=None
            )
        ],
        'holdButton': [
            MessageBox(
                name='holdMsgButton',
                label="Hold",
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_withdraw.png")
            ),
            MessageBox(
                name='commentHoldMsgButton',
                label="Comment && Hold",
                role=QMessageBox.YesRole,
                icon=QIcon(":/plugins/stdm/images/icons/flts_comment_reply_2.png")
            ),
            MessageBox(
                name=None,
                label="Cancel",
                role=QMessageBox.RejectRole,
                icon=None
            )
        ]
    },
    'update_columns': {
        'scheme_update': [
            UpdateColumn(column={'approval_id': 'approval_id'}, value=None)
            # UpdateColumn(column={'timestamp': 'timestamp'}, value=datetime.now())
        ]
    },
    'save_columns': {
        'scheme_save': [
            SaveColumn(
                column={'scheme_id': 'scheme_id'}, value=None, entity=None
            ),
            SaveColumn(
                column={'workflow_id': 'workflow_id'}, value=None, entity=None
            ),
            SaveColumn(
                column={'approval_id': 'approval_id'}, value=None, entity=None
            )
        ],
        'comment_save': [
            SaveColumn(
                column='comment', value=None, entity='Comment'
            )
            # SaveColumn(
            #     column='user_id', value=1, entity='Comment'
            # )
            # SaveColumn(
            #     column='timestamp', value=datetime.now(), entity='Comment'
            # )
        ]
    }
}
