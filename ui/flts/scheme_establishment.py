"""
/***************************************************************************
Name                 : Scheme Establishment Dialog
Description          : Dialog for establishing a new scheme.
Date                 : 01/Aug/2019
copyright            : (C) 2019 by Joseph Kariuki
email                : joehene@gmail.com
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
from time import strftime
from PyQt4.QtGui import (
    QDialog,
    QMessageBox,
    QTreeWidget
)

from stdm.data.pg_utils import (
    export_data,
    export_data_from_columns
)

from stdm.settings import current_profile
from stdm.data.configuration import entity_model
from stdm.data.mapping import MapperMixin
from ui_scheme_establishment import Ui_scheme_establish_dialog
from notification import NotificationDialog
from ..notification import NotificationBar, ERROR
from ..customcontrols.scheme_summary_widget import SchemeSummaryWidget


class EstablishmentDialog(QDialog, Ui_scheme_establish_dialog, MapperMixin):
    """
    Dialog that provides shortcut actions upon loading the establishment dialog.
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.sc_summary = SchemeSummaryWidget()

        self._checkbox_color()

        # Current profile
        self.curr_profile = current_profile()

        # Check if the current profile exists
        if self.curr_profile is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Profile'),
                self.tr("No profile has been specified")
            )
            self.reject()

        # Entity
        self._sch_entity = self.curr_profile.entity('Scheme')
        self._sch_apprv_entity = self.curr_profile.entity('Scheme_approval')
        self._notif_entity = self.curr_profile.entity('Notification')
        self._apprv_entity = self.curr_profile.entity('Approval')
        self._chk_apprv_entity = self.curr_profile.entity('check_lht_approval_status')

        # Check if entities exist
        if self._sch_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Scheme Entity'),
                self.tr("The scheme entity is missing in the profile.")
            )
            self.reject()

        if self._sch_apprv_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Scheme Approval Entity'),
                self.tr("The scheme entity approval is missing in the profile.")
            )
            self.reject()

        if self._notif_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Notification Entity'),
                self.tr("The notification entity approval is missing in the profile.")
            )
            self.reject()

        if self._apprv_entity is None:
            QMessageBox.critical(
                self,
                self.tr('Missing Approval Entity'),
                self.tr("The approval entity approval is missing in the profile.")
            )
            self.reject()

        # Entities model
        self.scheme_model = entity_model(self._sch_entity)
        self.notif_model = entity_model(self._notif_entity)
        self.apprv_model = entity_model(self._apprv_entity)

        # Check if entity model exist
        if self.scheme_model is None:
            QMessageBox.critical(
                self,
                self.tr('Scheme Entity Model'),
                self.tr("The scheme entity model could not be generated.")
            )
            self.reject()

        if self.notif_model is None:
            QMessageBox.critical(
                self,
                self.tr('Notification Entity Model'),
                self.tr("The notification entity model could not be generated.")
            )
            self.reject()

        if self.apprv_model is None:
            QMessageBox.critical(
                self,
                self.tr('Approval Entity Model'),
                self.tr("The approval entity model could not be generated.")
            )
            self.reject()

        # Entities objects
        self.scheme_obj = self.scheme_model()
        self.notif_obj = self.notif_model()
        self.apprv_obj = self.apprv_model()

        # Initializing mappermixin for saving attribute data
        MapperMixin.__init__(self, self.apprv_model, self._apprv_entity)

        # Configure notification bar
        self.notif_bar = NotificationBar(self.vlNotification)

        # Connecting signals to slots
        self.chk_approve.toggled.connect(self.on_approve_action)
        self.chk_disapprove.toggled.connect(self.on_disapprove_action)
        self.btnSubmit.clicked.connect(self.on_validate_all)

        # self.tvw_notification.notif_detail.setSelected = False

        # item_selected = self.tvw_notification.setItemSelected

        # if self.tvw_notification.notif_detail.setSelected:
        #     self.on_notif_clicked()

        self.approved = self.chk_approve.isChecked()
        self.disapproved = self.chk_disapprove.isChecked()

        # self.tw_lodgement_details.setEnabled(False)

        # self._load_notification()

        self.load_scheme_details()

    # def _load_notification(self):
    #     """
    #     Load notification data from the database
    #     """
    #     # Querying for notification
    #     res = self.notif_obj.queryObject().all()
    #
    #     for r in res:
    #         n_status = r.status
    #         n_content = r.content
    #         n_time = r.timestamp
    #
    #         self.tvw_notification.notif_detail.setText(0, str(n_content))
    #         self.tvw_notification.notif_detail.setText(1, str(n_status))
    #         self.tvw_notification.notif_detail.setText(2, str(n_time))

    def on_notif_clicked(self):
        """
        Slot raised when a notification is clicked
        """
        # Close the notification widget
        self.tvw_notification.close()
        self.tw_lodgement_details.setEnabled(True)

    def load_scheme_details(self):
        """
        Load details of lodged scheme on widget
        """
        # Query scheme entity model
        res = self.scheme_obj.queryObject().all()

        # Loop through the scheme
        for rs in res:
            sc_name = rs.scheme_name
            sc_apprv = rs.date_of_approval
            sc_est = rs.date_of_establishment
            sc_relv_auth = rs.relevant_authority
            sc_lro = rs.land_rights_office
            sc_rgn = rs.region
            sc_townshp = rs.township_name
            sc_reg_div = rs.registration_division
            sc_area = rs.area
            sc_schm_no = rs.scheme_number

            self.sc_summary.scm_num.setText(2, sc_schm_no)
            self.sc_summary.scm_name.setText(1, sc_name)
            self.sc_summary.scm_date_apprv.setText(1, str(sc_apprv))
            self.sc_summary.scm_date_est.setText(1, str(sc_est))
            self.sc_summary.scm_lro.setText(1, str(sc_lro))
            self.sc_summary.scm_township.setText(1, sc_townshp)
            # self.sc_summary.scm_reg_div.setText(1, sc_reg_div)
            # self.sc_summary.scm_ra_name.setText(1, sc_relv_auth)
            self.sc_summary.scm_blk_area.setText(1, str(sc_area))
            # self.sc_summary.scm_region.setText(1, sc_rgn)

    def _checkbox_color(self):
        """
        Give the checkbox labels color to distinguish
        between the functions.
        """
        self.chk_approve.setStyleSheet("QWidget { color: green}")
        self.chk_disapprove.setStyleSheet("QWidget { color: red}")

    def on_validate_all(self):
        # Clear notification bar
        self.notif_bar.clear()
        txt_comments = self.txtEdit_disApprv.toPlainText()

        # Checks if checkbox is selected
        if not self.chk_approve.isChecked() and not self.chk_disapprove.isChecked():
            self.notif_bar.insertWarningNotification(
                self.tr(
                    'Please check a checkbox option. '
                )
            )

        elif self.chk_disapprove.isChecked() and not self.chk_approve.isChecked() and len(txt_comments) == 0:
            self.notif_bar.insertWarningNotification(
                self.tr(
                    'Please add comments. '
                )
            )
        else:
            self.submit()
            self.create_notification()
            self.close_dialog()

    def on_approve_action(self):
        """
        Slot raised when the user selects the approve checkbox.
        """
        # self.btnSubmit.setEnabled(True)
        self.chk_disapprove.setChecked(False)
        self.txtEdit_disApprv.clear()
        self.txtEdit_disApprv.setReadOnly(True)

    def on_disapprove_action(self):
        """
        Slot raised when the user selects the disapprove checkbox.
        """
        self.chk_approve.setChecked(False)
        self.txtEdit_disApprv.setEnabled(True)
        self.txtEdit_disApprv.setReadOnly(False)

    def col_widgets(self):
        """
        Register column widgets
        """
        # Get the table columns and add mapping
        self.addMapping(
            'comments',
            self.txtEdit_disApprv,
            pseudoname='Comments'
        )

    def create_notification(self):
        """
        Populate notification table
        """
        # Get the table columns and add mapping
        self.notif_obj.status = 1
        self.notif_obj.source_user_id = 2
        self.notif_obj.target_user_id = 3
        self.notif_obj.content = 'Establishment done'
        self.notif_obj.timestamp = strftime("%m-%d-%Y %H:%M:%S")
        self.notif_obj.save()

    def close_dialog(self):
        """
        On clicking submit
        """
        self.close()
