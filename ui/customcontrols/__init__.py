'''
from .validating_line_edit import ValidatingLineEdit
from .combobox_with_other import ComboBoxWithOther
from .coordinates_editor import CoordinatesWidget
from .model_attributes_view import ModelAtrributesView
from .checkable_combo import MultipleChoiceCombo
from .list_pair_table_view import ListPairTableView
from .notification_widget import NotificationWidget
from .scheme_summary_widget import SchemeSummaryWidget
from documents_table_widget import DocumentTableWidget
'''

TABLE_STYLE_SHEET = 'QTableWidget { border:2px groove #96A8A8; ' \
                    'border-radius:3px;selection-background-color: ' \
                    'qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: ' \
                    '0 #D7F4F7, stop: 0.4 #CEECF0,stop: 0.6 #C5E4E8, ' \
                    'stop: 1.0 #D7F4F7); selection-color:black;} ' \
                    'QTableWidget QHeaderView::section { ' \
                    'border-bottom:0px groove #8BA6D9; ' \
                    'border-left:0px groove #8BA6D9; border-right:' \
                    '2px groove #8BA6D9; border-top:0px; padding:5px; ' \
                    'background:qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, ' \
                    'stop: 0 #F8FCFE, stop: 0.4 #EBEEF2, ' \
                    'stop: 0.5 #E0E5EA, ' \
                    'stop: 1.0 #DADEEA); ' \
                    'color:black; outline:0px; } ' \
                    'QHeaderView::section:checked { color: green;}' \
                    'QTableWidget::item { padding:5px; outline:0px; }'
