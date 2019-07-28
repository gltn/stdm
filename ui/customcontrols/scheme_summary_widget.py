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

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import (
    QTreeWidget,
    QTreeWidgetItem,
    QDesktopServices
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
        self.scm_num = QTreeWidgetItem()
        self.scm_name = QTreeWidgetItem()
        self.scm_date_apprv = QTreeWidgetItem()
        self.scm_date_est = QTreeWidgetItem()
        self.scm_ra_type = QTreeWidgetItem()
        self.scm_ra_name = QTreeWidgetItem()
        self.scm_lro = QTreeWidgetItem()
        self.scm_region = QTreeWidgetItem()
        self.scm_township = QTreeWidgetItem()
        self.scm_reg_div = QTreeWidgetItem()
        self.scm_blk_area = QTreeWidgetItem()
        self.doc_link = QTreeWidgetItem()
        self.hld_link = QTreeWidgetItem()

        self._initialize_view()

    def _initialize_view(self):
        """
        Set scheme details to be shown in a summary as collapsed items.
        """
        # call label
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
        self.scm_date_apprv.setText(0, self.tr('Date of Approval'))
        self.scm_date_est.setText(0, self.tr('Date of Establishment '
                                             ''))
        self.scm_ra_type.setText(0, self.tr('Type of Relevant Authority '))
        self.scm_ra_name.setText(0, self.tr('Name of Relevant Authority '))
        self.scm_lro.setText(0, self.tr('Land Rights Office '))
        self.scm_region.setText(0, self.tr('Region '))
        self.scm_township.setText(0, self.tr('Township '))
        self.scm_reg_div.setText(0, self.tr('Registration Division '))
        self.scm_blk_area.setText(0, self.tr('Block Area '))
        # Supporting Documents
        self.doc_link.setText(0, '{0} {1}'.format(
            self.tr('Holders'),
            ': ' + self.tr('link')
        )
                              )
        # Holders
        self.hld_link.setText(0, '{0} {1}'.format(
            self.tr('Holders'),
            ': ' + self.tr('link'))
                              )

        # Add child elements items to categories
        self.scheme_info.addChildren([self.scm_num,
                                      self.scm_name,
                                      self.scm_date_apprv,
                                      self.scm_date_est,
                                      self.scm_ra_type,
                                      self.scm_ra_name,
                                      self.scm_lro,
                                      self.scm_region,
                                      self.scm_township,
                                      self.scm_reg_div,
                                      self.scm_blk_area])

        self.supporting_document.addChildren([self.doc_link])

        self.holders_info.addChildren([self.hld_link])

        # Expand top-level items
        self.scheme_info.setExpanded(True)
        self.supporting_document.setExpanded(True)
        self.holders_info.setExpanded(True)
