"""
/***************************************************************************
Name                 : SchemeSummaryWidget
Description          : A table widget that provides a quick access menus for
                       uploading and viewing supporting documents.
Date                 : 16/July/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QWidget
)
from PyQt4.QtCore import (
    Qt
)


class SchemeSummaryWidget(QTreeWidget):
    """
    A widget for displaying scheme summary information after lodgement
    """

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.setHeaderHidden(True)
        self.setColumnCount(2)
        self.setColumnWidth(0, 300)
        self.setColumnWidth(1, 200)
        self._scheme = None
        self._documents = None
        self._holder = None

        # Widget items
        self.scheme_info = QTreeWidgetItem()
        self.supporting_document = QTreeWidgetItem()
        self.holders_info = QTreeWidgetItem()
        self.scm_num = QTreeWidgetItem()
        self.scm_name = QTreeWidgetItem()
        self.scm_date_apprv = QTreeWidgetItem()
        self.scm_date_est = QTreeWidgetItem()
        self.scm_ra_type = QTreeWidgetItem()
        self.scm_ra_name = QTreeWidgetItem()
        self.scm_sg_num = QTreeWidgetItem()
        self.scm_lro = QTreeWidgetItem()
        self.scm_region = QTreeWidgetItem()
        self.scm_township = QTreeWidgetItem()
        self.scm_reg_div = QTreeWidgetItem()
        self.scm_blk_area = QTreeWidgetItem()
        self.doc_notice_establish = QTreeWidgetItem()
        self.doc_explanatory = QTreeWidgetItem()
        self.doc_council_res = QTreeWidgetItem()
        self.doc_blockerf_title = QTreeWidgetItem()
        self.doc_cover_cert = QTreeWidgetItem()
        self.doc_potential_hld = QTreeWidgetItem()
        self.doc_trans_contract = QTreeWidgetItem()
        self.doc_imposing_condition = QTreeWidgetItem()
        self.doc_layout_plan = QTreeWidgetItem()
        self.doc_field_book = QTreeWidgetItem()

        self._initialize_view()

    def _initialize_view(self):
        """
        Set scheme details to be shown in a summary as collapsed items.
        """
        # call label
        # Define top-level items
        self.scheme_info.setText(0, self.tr('Scheme Information'))
        self.supporting_document.setText(0, self.tr('Supporting Documents'))
        self.holders_info.setText(0, '{0}'.format(
            self.tr('List of Holders: ')))
        self.addTopLevelItems([self.scheme_info, self.supporting_document,
                               self.holders_info])

        # Add child elements items to categories
        self.scheme_info.addChildren(
            [self.scm_num,
             self.scm_name,
             self.scm_date_apprv,
             self.scm_date_est,
             self.scm_ra_type,
             self.scm_ra_name,
             self.scm_sg_num,
             self.scm_lro,
             self.scm_region,
             self.scm_township,
             self.scm_reg_div,
             self.scm_blk_area]
        )

        self.supporting_document.addChildren(
            [self.doc_explanatory,
             self.doc_council_res,
             self.doc_cover_cert,
             self.doc_blockerf_title,
             self.doc_field_book,
             self.doc_imposing_condition,
             self.doc_layout_plan,
             self.doc_notice_establish,
             self.doc_potential_hld,
             self.doc_trans_contract]
        )

        # Expand top-level items
        self.scheme_info.setExpanded(True)
        self.supporting_document.setExpanded(True)

        # Static children items
        # Scheme
        self.scm_region.setText(0,
                                self.tr('Region ')
                                )
        self.scm_ra_type.setText(0,
                                 self.tr('Type of Relevant Authority ')
                                 )
        self.scm_ra_name.setText(0,
                                 self.tr('Name of Relevant Authority ')
                                 )
        self.scm_sg_num.setText(0,
                                self.tr('SG/General Plan Number ')
                                )
        self.scm_num.setText(0,
                             self.tr('Number of Scheme ')
                             )
        self.scm_name.setText(0,
                              self.tr('Name of Scheme ')
                              )
        self.scm_date_apprv.setText(0,
                                    self.tr('Date of Approval')
                                    )
        self.scm_date_est.setText(0,
                                  self.tr('Date of Establishment ')
                                  )
        self.scm_lro.setText(0,
                             self.tr('Land Rights Office ')
                             )
        self.scm_township.setText(0,
                                  self.tr('Township ')
                                  )
        self.scm_reg_div.setText(0,
                                 self.tr('Registration Division ')
                                 )
        self.scm_blk_area.setText(0,
                                  self.tr('Block Area ')
                                  )

        view_str = self.tr('View')
        lbl_view_holders = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.holders_info, 1, lbl_view_holders)

        # Supporting Documents

        self.doc_cover_cert.setText(0, self.tr('Cover Certificate: '))
        lbl_view_cover_cert = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_cover_cert, 1, lbl_view_cover_cert)

        self.doc_council_res.setText(0, self.tr('Council Resolution: '))
        lbl_view_doc_council = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_council_res, 1, lbl_view_doc_council)

        self.doc_layout_plan.setText(0, self.tr('Digital Layout Plan: '))
        lbl_view_doc_layout_plan = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_layout_plan, 1, lbl_view_doc_layout_plan)

        self.doc_imposing_condition.setText(0, self.tr('Document Imposing '
                                                       'Conditions: '))
        lbl_view_doc_imposing = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_imposing_condition, 1,
                           lbl_view_doc_imposing)

        self.doc_explanatory.setText(0, self.tr('Explanatory Report: '))
        lbl_view_doc_explanatory = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_explanatory, 1, lbl_view_doc_explanatory)

        self.doc_field_book.setText(0, self.tr('Field Book: '))
        lbl_view_doc_fieldbk = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_field_book, 1, lbl_view_doc_fieldbk)

        self.doc_potential_hld.setText(0, self.tr('List of Potential '
                                                  'Holders: '))
        lbl_view_doc_potential_hld = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_potential_hld, 1,
                           lbl_view_doc_potential_hld)

        self.doc_notice_establish.setText(0, self.tr('Notice of Establishment '
                                                     'of Scheme: '))
        lbl_view_doc_notice = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_notice_establish, 1, lbl_view_doc_notice)

        self.doc_blockerf_title.setText(0, self.tr('Title Deed of Blockerf: ')
                                        )
        lbl_view_blockerf_title = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_blockerf_title, 1,
                           lbl_view_blockerf_title)

        self.doc_trans_contract.setText(0, self.tr('Transfer Contract: '))
        lbl_view_doc_trans = self.create_hyperlink_widget(view_str)
        self.setItemWidget(self.doc_trans_contract, 1, lbl_view_doc_trans)

    def create_hyperlink_widget(self, name):
        """
        Creates a clickable QLabel widget that appears like a hyperlink.
        :param name: Display name of the hyperlink.
        :type name: str
        :param document_info: Container for document information that is
        embedded as a property in the label.
        :type document_info: DocumentRowInfo
        :return: Returns the QLabel widget with appearance of a hyperlink.
        :rtype: QLabel
        """
        lbl_link = QLabel()
        lbl_link.setAlignment(Qt.AlignLeft)
        lbl_link.setText(u'<a href=\'placeholder\'>{0}</a>'.format(name))
        lbl_link.setTextInteractionFlags(Qt.TextBrowserInteraction)

        return lbl_link
