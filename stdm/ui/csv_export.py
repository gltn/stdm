from qgis.PyQt.QtWidgets import (
    QDialog,
    QMessageBox,
    QFileDialog,
    QListWidgetItem
)

from qgis.PyQt.QtCore import (
    Qt,
    QDir
)

from qgis.PyQt import uic

from stdm.ui.gui_utils import GuiUtils

WIDGET, BASE = uic.loadUiType(
    GuiUtils.get_ui_file_path('ui_csv_export.ui')
)

class CSVExportDialog(WIDGET, BASE):
    def __init__(self, iface, export_entity: dict):
        QDialog.__init__(self, iface.mainWindow())
        self.setupUi(self)
        self.iface = iface
        self._export_entity = export_entity

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Export Data as CSV")

        entity_name_short = f"{self._export_entity['entity_name']}"
        entity_name_long = (
            f"{entity_name_short} ({len(self._export_entity['data'])} records)" 
              )
        self.lblEntity.setText(entity_name_long)

        self.btnFileBrowse.clicked.connect(self.browse_file)
        self.btnExport.clicked.connect(self.export_to_csv)
        self.btnClose.clicked.connect(self.close)

        csv_file = f"{QDir.homePath()}/Documents/{entity_name_short}.csv" 
        self.edtFilename.setText(csv_file)

        self.cbAll.setChecked(Qt.Checked)
        self.cbAll.stateChanged.connect(self._on_state_changed)

        self._show_entity_columns()

    def _on_state_changed(self, state: int):
        if state == 0:
            self._check_columns(Qt.Unchecked)
        if state == 2:
            self._check_columns(Qt.Checked)

    def _show_entity_columns(self):
        for index, header in enumerate(self._export_entity['headers']):
            lw_item = QListWidgetItem(header)
            lw_item.setCheckState(Qt.Checked)
            lw_item.setData(Qt.UserRole, self._export_entity['columns'][index])
            self.lwColumns.addItem(lw_item)

    def _check_columns(self, state: 'Qt.CheckState'):
        for index in range(self.lwColumns.count()):
            lw_item = self.lwColumns.item(index)
            lw_item.setCheckState(state)

    def browse_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", 
                                                "CSV Files (*.csv);;")
        if file_name:
            self.edtFilename.setText(file_name)

    def export_to_csv(self):
        if self.edtFilename.text().strip() == "":
           msg = f"Please enter CSV output file"
           self.show_message(msg, QMessageBox.Critical)
           return

        data = self._export_entity['data']
        if len(data) == 0:
            msg = f"No data in the entity to export!"
            self.show_message(msg)
            return

        export_record = []
        headers = []
        for record in data:
            row = []
            for index, field_value in enumerate(record):
                lw_item = self.lwColumns.item(index)
                if lw_item.checkState() == Qt.Checked:
                    col_name = lw_item.data(Qt.UserRole)
                    col_fmt = self._export_entity['formatters'].get(col_name, None)
                    if isinstance(field_value, int):
                        col_value = str(field_value)
                    elif not isinstance(field_value, str):
                        col_value = str(field_value)
                    else:
                        col_value = field_value

                    row.append(col_value)
                    header = self._export_entity['headers'][index]
                    if header not in headers:
                        headers.append(header)

            if len(row) > 0:
                export_record.append(row)
        
        if len(export_record) == 0:
            msg = f"Please select columns to export"
            self.show_message(msg, QMessageBox.Critical)
            return

        result = self.write_to_csv(export_record, headers)
        if result:
            self.show_message("Data exported successfully.")

    def write_to_csv(self, data: list[list], headers:list ) -> bool:
        try:
            printed_header = False
            with open(self.edtFilename.text(), 'w') as CSV:
                for record in data:
                    if not printed_header:
                        row = ",".join(headers)
                        CSV.write(row)
                        CSV.write('\n')
                        printed_header = True
                    row = ",".join(record)
                    CSV.write(row)
                    CSV.write('\n')
        except IOError as e:
            msg = f"I/O error {e.errno} : {e.strerror}"
            self.show_message(msg, QMessageBox.Critical)
            return False

        return True

    def show_message(self, msg: str, icon_type:'QMessageBox.Icon'=QMessageBox.Information):
        msg_box = QMessageBox()
        msg_box.setText(msg)
        msg_box.setIcon(icon_type)
        msg_box.exec_()
        
