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
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setColumnWidth(0, 500)
        self._scheme = None
        self._documents = None
        self._holder = None

        # Widget items
        self.scheme_info = QTreeWidgetItem()
        self.supporting_document = QTreeWidgetItem()
        self.holders_info = QTreeWidgetItem()
        self.holders_info = QTreeWidgetItem()
        self.scm_num = QTreeWidgetItem()
        self.scm_name = QTreeWidgetItem()
        self.scm_date_apprv = QTreeWidgetItem()
        self.scm_date_est = QTreeWidgetItem()
        self.scm_ra = QTreeWidgetItem()
        self.scm_lro = QTreeWidgetItem()
        self.scm_region = QTreeWidgetItem()
        self.scm_township = QTreeWidgetItem()
        self.scm_reg_div = QTreeWidgetItem()
        self.doc_notice = QTreeWidgetItem()
        self.scm_blk_area = QTreeWidgetItem()
        self.doc_explanatory = QTreeWidgetItem()
        self.doc_council_res = QTreeWidgetItem()
        self.doc_title_deed = QTreeWidgetItem()
        self.doc_covcert = QTreeWidgetItem()
        self.doc_lst_holders = QTreeWidgetItem()
        self.doc_tr_contract = QTreeWidgetItem()
        self.doc_digital_layout = QTreeWidgetItem()
        self.doc_conditions = QTreeWidgetItem()
        self.hld_num = QTreeWidgetItem()

        self._initialize_view()

    def _def_attr_names(self):
        pass

    def _initialize_view(self):
        """
        Set scheme details to be shown in a summary as collapsed items.
        """
        # Define top-level items
        self.scheme_info.setText(0, self.tr('Scheme Information'))
        self.supporting_document.setText(0, self.tr('Supporting Documents'))
        self.holders_info.setText(0, self.tr('Holder Information'))
        self.addTopLevelItems([self.scheme_info, self.supporting_document,
                               self.holders_info])

        # Static children items
        # Scheme
        self.scm_num.setText(0, self.tr('Number of Scheme '))
        self.scm_name.setText(0, self.tr('Name of Scheme '))
        self.scm_date_apprv.setText(0, self.tr('Date of Approval '))
        self.scm_date_est.setText(0, self.tr('Date of Establishment '
                                                    ''))

        self.scm_ra.setText(0, self.tr('Relevant Authority '))
        self.scm_lro.setText(0, self.tr('Land Rights Office '))
        self.scm_region.setText(0, self.tr('Region '))
        self.scm_township.setText(0,self.tr('Township '))
        self.scm_reg_div.setText(0, self.tr('Registration Division '))
        self.scm_blk_area.setText(0, self.tr('Block Area '))
        # Supporting Documents
        self.doc_notice.setText(0, self.tr('Notice of Establishment of'
                                                  ' a Scheme '))
        self.doc_explanatory.setText(0, self.tr('Explanatory Report '))
        self.doc_council_res.setText(0, self.tr('Council Resolution '))
        self.doc_title_deed.setText(0, self.tr('Title Deed of the '
                                                      'Blockerf '))
        self.doc_covcert.setText(0, self.tr('Cover Certificate '))
        self.doc_lst_holders.setText(0, self.tr('List of Potential '
                                                       'Holders '))
        self.doc_tr_contract.setText(0, self.tr('Transfer Contract '))
        self.doc_conditions.setText(0, self.tr('Document Imposing '
                                                      'Conditions '))
        self.doc_digital_layout.setText(0, self.tr('Digital Layout Plan '))
        # Holders
        self.hld_num.setText(0, self.tr('Number of Holders '))

        # Add child elements items to categories
        self.scheme_info.addChildren([self.scm_num, self.scm_name,
                                      self.scm_date_apprv,
                                      self.scm_date_est,
                                      self.scm_ra, self.scm_lro,
                                      self.scm_region,
                                      self.scm_township,
                                      self.scm_reg_div,
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

    def set_scheme(self, scheme):
        """
        Setting the scheme elements and updating in case of changes
        """
        self._scheme = scheme
        self.refresh()

    def refresh(self):
        """
        When input values are changed the summary updates the values based on
        user input
        """
        if self._scheme is None:
            return

        name = self._scheme.scheme_name
        number = self._scheme.scheme_number
        relevant_auth = '' # self._scheme.relevant_authority
        date_of_approval = self._scheme.date_of_approval
        date_of_establishment = self._scheme.date_of_establishment
        lro = '' #self._scheme.lro
        region = '' #self._scheme.region
        township_name = self._scheme.township_name
        registration_div = '' # self._scheme.registration_div
        block_area = str(self._scheme.area)

        # Capture the text values
        base_name = self.scm_name.text(0)
        base_num = self.scm_num.text(0)
        base_ra = self.scm_ra.text(0)
        base_doa = self.scm_date_apprv.text(0)
        base_doe = self.scm_date_est.text(0)
        base_lro = self.scm_lro.text(0)
        base_rgn = self.scm_region.text(0)
        base_twn = self.scm_township.text(0)
        base_reg_div = self.scm_reg_div.text(0)
        base_blk_area = self.scm_blk_area.text(0)

        # Set changed text

        self.scm_name.setText(0, '{0}:{1}'.format(base_name, name))
        self.scm_num.setText(0, '{0}:{1}'.format(base_num, number))
        self.scm_ra.setText(0, '{0}:{1}'.format(base_ra, relevant_auth))
        self.scm_date_apprv.setText(0, '{0}:{1}'.format(base_doa,
                                                        date_of_approval))
        self.scm_date_est.setText(0, '{0}:{1}'.format(base_doe,
                                                      date_of_establishment))
        self.scm_lro.setText(0, '{0}:{1}'.format(base_lro, lro))
        self.scm_region.setText(0, '{0}:{1}'.format(base_rgn, region))
        self.scm_township.setText(0, '{0}:{1}'.format(base_twn,
                                                      township_name))
        self.scm_reg_div.setText(0, '{0}:{1}'.format(base_reg_div,
                                                     registration_div))
        self.scm_blk_area.setText(0, '{0}:{1}'.format(base_blk_area,
                                                      block_area))
