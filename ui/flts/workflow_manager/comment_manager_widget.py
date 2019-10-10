from datetime import datetime
from PyQt4.QtGui import *
from sqlalchemy import exc
from stdm.ui.flts.workflow_manager.config import CommentButtonIcons
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

    def __init__(self, widget_properties, profile, scheme_id, parent=None):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)
        self._comments = []
        self._load_collections = widget_properties["load_collections"]
        self._data_service = widget_properties["data_service"]
        self._data_service = self._data_service(profile, scheme_id)
        self._scheme_query_objs = widget_properties["scheme_query"]
        self.model = WorkflowManagerModel(self._data_service)
        self.setObjectName("Comments")
        self.oldCommentTextEdit.setReadOnly(True)
        self._set_button_icons()
        self._parent = parent
        self._parent.paginationFrame.hide()
        self.paginationFrame.setLayout(PaginationWidget().pagination_layout)
        self.submitButton.clicked.connect(self._on_submit)
        self._initial_load()
        self._get_comments()
        self._populate_comments()

    def _set_button_icons(self):
        """
        Sets QPushButton icons
        """
        icons = CommentButtonIcons(self)
        buttons = icons.buttons
        for button, options in buttons.iteritems():
            button.setIcon(options.icon)
            button.setIconSize(options.size)

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

    def _on_submit(self):
        """
        Submit new comment
        """
        save_items = self._save_items()
        if not save_items:
            msg = "Comment is empty. Kindly type your comments to submit."
            self._notification_warning(msg)
            return
        try:
            saved_comments = 0
            msg = "Submit comments?"
            if self._show_question_message(msg):
                saved_comments = self.model.save_collection(
                    save_items, self._scheme_query_objs
                )
        except (AttributeError, exc.SQLAlchemyError, Exception) as e:
            raise e
        else:
            if saved_comments > 0:
                self.newCommentTextEdit.document().clear()
                msg = "Comment submitted. Thank you."
                self._notification_information(msg)

    def _save_items(self):
        """
        Returns save items
        :return save_items: Save items; columns, values and entity
        :rtype save_items: Dictionary
        """
        new_comment = self.newCommentTextEdit.toPlainText()
        if not new_comment.strip():
            return
        columns = {}
        save_items = {}
        lookup = self._data_service.lookups
        save_columns = self._data_service.save_columns
        for option in self._get_config_option(save_columns):
            if option.column == lookup.COMMENT_COLUMN:
                columns[option.column] = new_comment
            elif type(option.value) is datetime:
                columns[option.column] = datetime.now()
            else:
                columns[option.column] = option.value
        entity_name = save_columns[0].entity
        save_items[entity_name] = [columns]
        return save_items

    @ staticmethod
    def _get_config_option(config):
        """
        Returns save/update configuration options
        :param config: Save/update configuration options
        :type config: Named
        :return option: Save/update configuration option
        :rtype option: named tuple
        """
        for option in config:
            yield option

    def _show_question_message(self, msg):
        """
        Message box to communicate a question
        :param msg: Message to be communicated
        :type msg: String
        """
        if QMessageBox.question(
            self,
            self.tr('Comment Manager'),
            self.tr(msg),
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
            return False
        return True

    def _notification_warning(self, msg):
        """
        Shows warning notification
        :param msg: Warning message
        :type msg: Warning message
        """
        self._parent.notif_bar.clear()
        self._parent.notif_bar.insertWarningNotification(msg)

    def _notification_information(self, msg):
        """
        Shows warning notification
        :param msg: Warning message
        :type msg: Warning message
        """
        self._parent.notif_bar.clear()
        self._parent.notif_bar.insertInformationNotification(msg)





