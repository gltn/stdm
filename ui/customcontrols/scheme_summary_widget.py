"""
/***************************************************************************
Name                 : SchemeSummaryWidget
Description          : A tree summary view of the scheme details.
Date                 : 07/July/2019
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

from PyQt4.QtGui import (
    QTreeWidget,
    QTreeWidgetItem
)


class SchemeSummaryWidget(QTreeWidget):
    """
    A widget for displaying scheme summary information after lodgement
    """

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)

        # List of static items
        self._scheme_info_items = []
        self._document_info_items = []
        self._holder_info_items = []

        self.set_scheme()

    def set_scheme(self):
        """
        Set scheme details to be shown in a summary as collapsed items.
        """
        # Define top-level items
        self.scheme_info = QTreeWidgetItem(['Scheme Information', 'SCI'])
        self.supporting_document = QTreeWidgetItem(['Supporting Documents',
                                                    'SDC'])
        self.holders_info = QTreeWidgetItem(['Holder Information', 'HLD'])
        self.addTopLevelItems([self.scheme_info, self.supporting_document,
                               self.holders_info])

        # Static children items
        # Scheme
        self.scm_num = QTreeWidgetItem(self.tr('Number of Scheme: '))
        self.scm_name = QTreeWidgetItem(self.tr('Name of Scheme: '))
        self.scm_date_apprv = QTreeWidgetItem(self.tr('Date of Approval: '))
        self.scm_date_est = QTreeWidgetItem(self.tr('Date of Establishment: '
                                                    ''))
        self.scm_ra = QTreeWidgetItem(self.tr('Relevant Authority: '))
        self.scm_lro = QTreeWidgetItem(self.tr('Land Rights Office: '))
        self.scm_region = QTreeWidgetItem(self.tr('Region: '))
        self.scm_township = QTreeWidgetItem(self.tr('Townshipe: '))
        self.scm_reg_dev = QTreeWidgetItem(self.tr('Registration Division: '))
        self.scm_blk_area = QTreeWidgetItem(self.tr('Block Area: '))
        # Supporting Documents
        self.doc_notice = QTreeWidgetItem(self.tr("Notice of Establishment of"
                                                  " a Scheme: "))
        self.doc_explanatory = QTreeWidgetItem(self.tr("Explanatory Report: "))
        self.doc_council_res = QTreeWidgetItem(self.tr("Council Resolution: "))
        self.doc_title_deed = QTreeWidgetItem(self.tr("Title Deed of the "
                                                      "Blockerf:"))
        self.doc_covcert = QTreeWidget(self.tr("Cover Certificate: "))
        self.doc_lst_holders = QTreeWidgetItem(self.tr("List of Potential "
                                                       "Holders: "))
        self.doc_tr_contract = QTreeWidgetItem(self.tr("Transfer Contract: "))
        self.doc_conditions = QTreeWidgetItem(self.tr("Document Imposing "
                                                      "Conditions: "))
        self.doc_digital_layout = QTreeWidgetItem(self.tr("Digital Layout Plan: "))
        # Holders
        self.hld_num = QTreeWidgetItem(self.tr('Number of Holders'))

        # Append items to categories
        self.scheme_info.addChildren([self.scm_num, self.scm_name,
                                      self.scm_date_apprv,
                                      self.scm_date_est,
                                      self.scm_ra, self.scm_lro,
                                      self.scm_region,
                                      self.scm_township,
                                      self.scm_reg_dev,
                                      self.scm_blk_area])

        self.supporting_document.addChildren([self.doc_notice,
                                              self.doc_explanatory,
                                              self.doc_council_res,
                                              self.doc_title_deed,
                                              self.doc_covcert,
                                              self.doc_lst_holders,
                                              self.doc_tr_contract,
                                              self.doc_conditions,
                                              self.doc_digital_layout])

        self.holders_info.addChild(self.hld_num)

        # Expand top-level items
        self.scheme_info.setExpanded(True)
        self.supporting_document.setExpanded(True)
        self.holders_info.setExpanded(True)

    def refresh(self):
        pass
