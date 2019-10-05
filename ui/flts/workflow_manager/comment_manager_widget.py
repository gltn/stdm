from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.pagination_widget import PaginationWidget
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel
from stdm.ui.flts.workflow_manager.ui_comment_manager import Ui_CommentManagerWidget


class Comment(object):
    """
    Comment factory
    """
    def __init__(self, comment):
        self.comment,  self.user_name, self.first_name, \
        self.last_name, self.timestamp = comment


class CommentManagerWidget(QWidget, Ui_CommentManagerWidget):
    """
    Manages scheme user comments in the Scheme Lodgment, Scheme Establishment
    and First, Second and Third Examination FLTS modules
    """
    DATE_FORMAT = "ddd MMM dd yyyy"
    TIME_FORMAT = "hh:mm ap"

    def __init__(self, detail_service, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self._comments = []
        self._parent = parent
        self._load_collections = detail_service['load_collections']
        data_service = detail_service['data_service']
        data_service = data_service(profile, scheme_id)
        self.model = WorkflowManagerModel(data_service)
        self.setObjectName("Comments")
        # TODO: Start refactor icons and size
        pagination = PaginationWidget()
        pagination.first_button.setIcon(QIcon(":/plugins/stdm/images/icons/flts_scheme_first_record.png"))
        pagination.first_button.setIconSize(QSize(24, 24))
        pagination.previous_button.setIcon(QIcon(":/plugins/stdm/images/icons/flts_scheme_previous_record.png"))
        pagination.previous_button.setIconSize(QSize(24, 24))
        pagination.next_button.setIcon(QIcon(":/plugins/stdm/images/icons/flts_scheme_next_record.png"))
        pagination.next_button.setIconSize(QSize(24, 24))
        pagination.last_button.setIcon(QIcon(":/plugins/stdm/images/icons/flts_scheme_last_record.png"))
        pagination.last_button.setIconSize(QSize(24, 24))
        self.submitButton.setIcon(QIcon(":/plugins/stdm/images/icons/flts_comment_reply.png"))
        self.submitButton.setIconSize(QSize(24, 24))
        # TODO: End refactor
        self._parent.paginationFrame.hide()
        self.paginationFrame.setLayout(pagination.pagination_layout)
        self._initial_load()
        self._get_comments()
        self._populate_comments()

    def _initial_load(self):
        """
        Initial table view data load
        """
        try:
            if self._load_collections:
                self.model.load_collection()
            else:
                self.model.load()
        except (exc.SQLAlchemyError, Exception) as e:
            QMessageBox.critical(
                self,
                self.tr('{} Entity Model'.format(self.model.entity_name)),
                self.tr("{0} failed to load: {1}".format(
                    self.model.entity_name, e
                ))
            )

    def _get_comments(self):
        """
        Get comments from the model
        """
        for row in self.model.results:
            comment = Comment(
                [value for column, value in row.iteritems() if column != "data"]
            )
            self._comments.append(comment)

    def _populate_comments(self):
        """
        Populates Scheme user comments as HTML
        """
        html = u""
        font = (
            'font-weight:normal;'
            'font-size:14px;'
            'font-family:"Segoe UI",Roboto,Ubuntu,"Helvetica Neue",sans-serif;'
            'color:#008080;'
        )
        for comment in self._comments:
            html += (
                "<p style='{0} margin-right:10px;margin-left:10px;margin-bottom:0px;color:#14171a;'>"
                "<span style='font-weight:bold;color:#385898'>{1} {2}</span>"
                "<span style='font-weight:lighter;'>&nbsp;&nbsp;{3} at {4}</span>"
                "</p>"
                "<p style='{0} margin-top:5px;margin-right:10px;margin-left:10px;color:#14171a;'>"
                "{5}"
                "</p><hr>".format(
                    font,
                    comment.first_name,
                    comment.last_name,
                    comment.timestamp.toString(CommentManagerWidget.DATE_FORMAT),
                    comment.timestamp.toString(CommentManagerWidget.TIME_FORMAT),
                    comment.comment
                ))
        self.oldCommentTextEdit.setHtml(html)





