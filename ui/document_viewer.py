"""
/***************************************************************************
Name                 : Document Viewer
Description          : GUI classes for managing and viewing supporting
                       documents.
Date                 : 8/September/2014
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from __future__ import division

import os

import logging

from PyQt4.QtGui import (
    QMdiSubWindow,
    QMdiArea,
    QApplication,
    QMessageBox,
    QLabel,
    QImage,
    QPixmap,
    QWidget,
    QPalette,
    QSizePolicy,
    QScrollArea,
    QIcon,
    QAction,
    QPrintDialog,
    QPrinter,
    QDialog,
    QPainter,
    QWheelEvent,
    QMainWindow,
    QMenu,
    QDesktopWidget,
    QResizeEvent
)
from PyQt4.QtCore import (
    Qt,
    pyqtSignal,
    QSignalMapper,
    QFile,
    QFileInfo,
    QSize,
    QSettings
)

from stdm.utils.util import (
    guess_extension
)

from stdm.settings import current_profile

LOGGER = logging.getLogger('stdm')

class PhotoViewer(QScrollArea):
    """
    Widget for viewing images by incorporating basic navigation options.
    """
    def __init__(self, parent=None, photo_path=""):
        QScrollArea.__init__(self, parent)
        self.setBackgroundRole(QPalette.Dark)

        self._printer = QPrinter()

        self._lbl_photo = QLabel()
        self._lbl_photo.setBackgroundRole(QPalette.Base)
        self._lbl_photo.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
        self._lbl_photo.setScaledContents(True)

        self.setWidget(self._lbl_photo)

        self._photo_path = photo_path
        self._ph_image = None
        self._scale_factor = 1.0
        self._aspect_ratio = -1

        self._create_actions()

        if self._photo_path:
            self.load_document(self._photo_path)


    def _create_actions(self):
        """
        Create actions for basic image navigation.
        """
        self._zoom_in_act = QAction(
            QApplication.translate("PhotoViewer","Zoom &In (25%)"), self)
        self._zoom_in_act.setShortcut(
            QApplication.translate("PhotoViewer","Ctrl++"))
        self._zoom_in_act.setEnabled(False)
        self._zoom_in_act.triggered.connect(self.zoom_in)

        self._zoom_out_act = QAction(
            QApplication.translate("PhotoViewer","Zoom &Out (25%)"), self)
        self._zoom_out_act.setShortcut(
            QApplication.translate("PhotoViewer","Ctrl+-"))
        self._zoom_out_act.setEnabled(False)
        self._zoom_out_act.triggered.connect(self.zoom_out)

        self._normal_size_act = QAction(
            QApplication.translate("PhotoViewer","&Normal Size"), self)
        self._normal_size_act.setShortcut(
            QApplication.translate("PhotoViewer","Ctrl+S"))
        self._normal_size_act.setEnabled(False)
        self._normal_size_act.triggered.connect(self.normal_size)

        self._fit_to_window_act = QAction(
            QApplication.translate("PhotoViewer","&Fit to Window"), self)
        self._fit_to_window_act.setShortcut(
            QApplication.translate("PhotoViewer","Ctrl+F"))
        self._fit_to_window_act.setEnabled(False)
        self._fit_to_window_act.setCheckable(True)
        self._fit_to_window_act.triggered.connect(self.fit_to_window)

        self._print_act = QAction(
            QApplication.translate("PhotoViewer","&Print"), self)
        self._print_act .setShortcut(
            QApplication.translate("PhotoViewer","Ctrl+P"))
        self._print_act .setEnabled(False)
        self._print_act .triggered.connect(self.print_photo)

    def zoom_in(self):
        self.scale_photo(1.25)

    def zoom_out(self):
        self.scale_photo(0.8)

    def normal_size(self):
        self._lbl_photo.adjustSize()
        self._scale_factor = 1.0

    def fit_to_window(self):
        fit_to_win = self._fit_to_window_act.isChecked()
        self.setWidgetResizable(fit_to_win)

        if not fit_to_win:
            self.normal_size()

        self.update_actions()

    def print_photo(self):
        print_dialog = QPrintDialog(self._printer,self)

        if print_dialog.exec_() == QDialog.Accepted:
            painter = QPainter(self._printer)
            rect = painter.viewport()
            size = self._lbl_photo.pixmap().size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self._lbl_photo.pixmap().rect())
            painter.drawPixmap(0, 0, self._lbl_photo.pixmap())

    def wheelEvent(self, event):
        """
        Zoom the image based on the mouse wheel rotation action.
        :param event: Event containing the wheel rotation info.
        :type event: QWheelEvent
        """
        degrees = event.delta() / 8
        num_steps = degrees / 15

        if num_steps < 0:
            abs_num_steps = abs(num_steps)
            zoom_factor  = 1 + (abs_num_steps * 0.25)

        else:
            zoom_factor = 1 - (num_steps * 0.2)

        self.scale_photo(zoom_factor)

    def heightForWidth(self, width):
        if self._aspect_ratio != -1:
            return width / self._aspect_ratio

        else:
            return -1

    def resizeEvent(self, event):
        """
        Event for resizing the widget based on the pixmap's aspect ratio.
        :param event: Contains event parameters for the resize event.
        :type event: QResizeEvent
        """
        super(PhotoViewer, self).resizeEvent(event)

    def update_actions(self):
        self._zoom_out_act.setEnabled(not self._fit_to_window_act.isChecked())
        self._zoom_in_act.setEnabled(not self._fit_to_window_act.isChecked())
        self._normal_size_act.setEnabled(not self._fit_to_window_act.isChecked())

    def scale_photo(self,factor):
        """
        :param factor: Value by which the image will be increased/decreased in the view.
        :type factor: float
        """
        if not self._lbl_photo.pixmap().isNull():
            self._scale_factor *= factor
            self._lbl_photo.resize(self._scale_factor * self._lbl_photo.pixmap().size())

            self._adjust_scroll_bar(self.horizontalScrollBar(), factor)
            self._adjust_scroll_bar(self.verticalScrollBar(), factor)

            self._zoom_in_act.setEnabled(self._scale_factor < 3.0)
            self._zoom_out_act.setEnabled(self._scale_factor > 0.333)

    def _adjust_scroll_bar(self, scroll_bar, factor):
        scroll_bar.setValue(int(factor * scroll_bar.value()
                + ((factor - 1) * scroll_bar.pageStep()/2)))

    def load_document(self, photo_path):
        if photo_path:
            self._ph_image = QImage(photo_path)

            if self._ph_image.isNull():
                return False

            self._photo_path = photo_path

            ph_pixmap = QPixmap.fromImage(self._ph_image)

            self._lbl_photo.setPixmap(ph_pixmap)
            self._scale_factor = 1.0

            self._aspect_ratio = ph_pixmap.width() / ph_pixmap.height()

            self._fit_to_window_act.setEnabled(True)
            self._print_act.setEnabled(True)
            self._fit_to_window_act.trigger()

            self.update_actions()
            return ph_pixmap

        return True

    def photo_location(self):
        """
        :returns: Absolute path of the photo in the central document repository.
        """
        return self._photo_path

    def set_actions(self,menu):
        """
        Add custom actions to the sub-window menu
        """
        menu.addSeparator()
        menu.addAction(self._zoom_in_act)
        menu.addAction(self._zoom_out_act)
        menu.addAction(self._normal_size_act)
        menu.addAction(self._fit_to_window_act)
        menu.addSeparator()
        menu.addAction(self._print_act)

class DocumentViewer(QMdiSubWindow):
    """
    Widget for rendering supporting documents within an MDI area.
    """
    closed = pyqtSignal(str)

    def __init__(self, parent=None, file_identifier=""):
        QMdiSubWindow.__init__(self, parent)
        self.setWindowIcon(QIcon(":/plugins/stdm/images/icons/photo.png"))
        self._file_identifier = file_identifier
        self._view_widget = None
        self.mdi_area = parent

        self.doc_width = None
        self.doc_height = None

    def file_identifier(self):
        """
        :return: Unique identifier of the file whose contents are displayed
        by this widget.
        :rtype: str
        """
        return self._file_identifier

    def set_file_identifier(self,file_identifier):
        """
        :param file_identifier: Unique identifier of the file being displayed
        by the widget.
        :type file_identifier: str
        """
        self._file_identifier = file_identifier

    def view_widget(self):
        """
        :return: Configured widget for displaying supporting document.
        """
        return self._view_widget

    def set_view_widget(self, v_widget):
        """
        :param v_widget: Widget for displaying supporting document.
        :type v_widget: QWidget
        """
        self._view_widget = v_widget
        self._view_widget.set_actions(self.systemMenu())
        self.setWidget(self._view_widget)

    def sizeHint(self):
        #Reset size hint of the document viewer.
        return QSize(400, 300)

    def load_document(self, doc_path):
        """
        Displays the document content using the specified document path.
        :param doc_path: Path to the document resource.
        :type doc_path: str
        """
        if not self._view_widget is None:
            photo_obj = self._view_widget.load_document(doc_path)
            try:
                self.doc_width = photo_obj.width()
                self.doc_height = photo_obj.height()

                self.update_size(self.doc_width, self.doc_height)
            except Exception as message:
                LOGGER.debug(unicode(message))

    def update_size(self, doc_width, doc_height):
        """
        Updates the size of the image contain
        based on the document viewer size.
        :param doc_width: The width of the image
        :type doc_width: Integer
        :param doc_height: The height of the image
        :type doc_height: Integer
        :return: None
        :rtype: NoneType
        """
        par_height = self.mdi_area.height()
        par_width = self.mdi_area.width()
        ratio_list = [par_width / doc_width, par_height / doc_height]
        ratio = min(ratio_list)
        if par_height > doc_height and par_width > doc_width:
            self.resize(doc_width, doc_height)
        else:
            self.resize(doc_width * ratio, doc_height * ratio)

    def closeEvent(self, event):
        """
        Raise signal that contains the file ID of the sub window.
        """
        self.closed.emit(self._file_identifier)
        event.accept()

class DocumentViewManager(QMainWindow):
    """
    MDI area for displaying supporting documents within a given context e.g.
    supporting documents for a specific household based on the lifetime of the
    'SourceDocumentManager' instance.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowFlags(Qt.Window)

        self._mdi_area = QMdiArea()
        self._mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self._mdi_area)
        # set the size of mid_area and DocumentViewManager based on the
        # screen size.
        screen = QDesktopWidget().availableGeometry()
        self._mdi_area.resize(screen.width() - 30, screen.height() - 80)
        self.resize(self._mdi_area.size())
        self._mdi_area.subWindowActivated.connect(self.update_actions)
        self._viewer_mapper = QSignalMapper(self)
        self._viewer_mapper.mapped[QWidget].connect(self.set_active_sub_window)

        win_title = QApplication.translate(
            "DocumentViewManager",
            "Document Viewer"
        )
        self.setWindowTitle(win_title)
        self.setUnifiedTitleAndToolBarOnMac(True)
        self.statusBar().showMessage(
            QApplication.translate(
                "DocumentViewManager",
                "Ready"
            )
        )
        self._doc_viewers = {}

        self._create_menu_actions()
        self.update_actions()

    def center(self):
        """
        Move the Document viewer to the center of the screen.
        """
        # Get the current screens' dimensions...
        screen = QDesktopWidget().availableGeometry()
        # ... and get this windows' dimensions
        mdi_area_size = self.frameGeometry()
        # The horizontal position
        hpos = (screen.width() - mdi_area_size.width()) / 2
        # vertical position
        vpos = (screen.height() - mdi_area_size.height()) / 2
        # repositions the window
        self.move(hpos, vpos)

    def _create_menu_actions(self):
        self._window_menu = self.menuBar().addMenu(
            QApplication.translate(
                "DocumentViewManager","&Windows"))

        self._close_act = QAction(
            QApplication.translate("DocumentViewManager",
                                                         "Cl&ose"), self)
        self._close_act.setStatusTip(
            QApplication.translate("DocumentViewManager",
                                   "Close the active document viewer"))
        self._close_act.triggered.connect(self._mdi_area.closeActiveSubWindow)

        self._close_all_act = QAction(QApplication.translate(
            "DocumentViewManager",
            "Close &All"), self
        )
        self._close_all_act.setStatusTip(
            QApplication.translate("DocumentViewManager",
                                   "Close all the document viewers")
        )
        self._close_all_act.triggered.connect(
            self._mdi_area.closeAllSubWindows
        )

        self._tile_act = QAction(QApplication.translate(
            "DocumentViewManager",
            "&Tile"), self
        )
        self._tile_act.setStatusTip(
            QApplication.translate("DocumentViewManager",
                                   "Tile the document viewers"))
        self._tile_act.triggered.connect(self.tile_windows)

        self._cascade_act = QAction(QApplication.translate(
            "DocumentViewManager",
            "&Cascade"), self)
        self._cascade_act.setStatusTip(QApplication.translate(
            "DocumentViewManager",
            "Cascade the document viewers"))
        self._cascade_act.triggered.connect(self.cascade_windows)

        self._next_act = QAction(QApplication.translate(
            "DocumentViewManager",
            "Ne&xt"), self)
        self._next_act.setStatusTip(
            QApplication.translate(
                "DocumentViewManager",
                "Move the focus to the next document viewer"
            )
        )
        self._next_act.triggered.connect(self._mdi_area.activateNextSubWindow)

        self._previous_act = QAction(QApplication.translate(
            "DocumentViewManager",
            "Pre&vious"), self)
        self._previous_act.setStatusTip(
            QApplication.translate(
                "DocumentViewManager",
                "Move the focus to the previous document viewer"
            )
        )
        self._previous_act.triggered.connect(
            self._mdi_area.activatePreviousSubWindow
        )

        self._separator_act = QAction(self)
        self._separator_act.setSeparator(True)

        self.update_window_menu()
        self._window_menu.aboutToShow.connect(self.update_window_menu)

    def cascade_windows(self):
        #Cascade document windows
        self._mdi_area.cascadeSubWindows()

    def tile_windows(self):
        #Arrange document windows to occupy the available space in mdi area
        self._mdi_area.tileSubWindows()

    def update_actions(self):
        if self._mdi_area.activeSubWindow():
            has_mdi_child = True

        else:
            has_mdi_child = False

        self._close_act.setEnabled(has_mdi_child)
        self._close_all_act.setEnabled(has_mdi_child)
        self._tile_act.setEnabled(has_mdi_child)
        self._cascade_act.setEnabled(has_mdi_child)
        self._previous_act.setEnabled(has_mdi_child)
        self._next_act.setEnabled(has_mdi_child)
        self._separator_act.setVisible(has_mdi_child)

    def update_window_menu(self):
        self._window_menu.clear()
        self._window_menu.addAction(self._close_act)
        self._window_menu.addAction(self._close_all_act)
        self._window_menu.addSeparator()
        self._window_menu.addAction(self._tile_act)
        self._window_menu.addAction(self._cascade_act)
        self._window_menu.addSeparator()
        self._window_menu.addAction(self._next_act)
        self._window_menu.addAction(self._previous_act)
        self._window_menu.addAction(self._separator_act)

        windows = self._mdi_area.subWindowList()
        self._separator_act.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            text = "%d. %s" % (i + 1, window.windowTitle())

            win_action = self._window_menu.addAction(text)
            win_action.setCheckable(True)
            win_action.setChecked(window is self._mdi_area.activeSubWindow())
            win_action.triggered.connect(self._viewer_mapper.map)
            self._viewer_mapper.setMapping(win_action, window)

    def load_viewer(self, document_widget, visible=True):
        """
        Open a new instance of the viewer or activate an existing one if the
        document had been previously loaded.
        :param document_widget: Contains all the necessary information required
        to load the specific document.
        :type document_widget: DocumentWidget
        :param visible: True to show the view manager after the viewer has
        been loaded, otherwise it will be the responsibility of the caller to
        enable visibility.
        :type visible: bool
        :returns: True if the document was successfully loaded, else False.
        :rtype: bool
        """
        doc_identifier = document_widget.file_identifier()

        if doc_identifier in self._doc_viewers:

            doc_sw = self._doc_viewers[doc_identifier]

            self._mdi_area.setActiveSubWindow(doc_sw)
            doc_sw.showNormal()

        else:
            abs_doc_path = self.absolute_document_path(document_widget)

            if not QFile.exists(abs_doc_path):
                msg = QApplication.translate(
                    "DocumentViewManager",
                    "The selected document does not exist."
                    "\nPlease check the supporting documents' "
                    "repository setting."
                )
                QMessageBox.critical(
                    self,
                    QApplication.translate(
                        "DocumentViewManager","Invalid Document"
                    ),
                    msg
                )

                return False

            file_info = QFileInfo(abs_doc_path)
            ext = file_info.suffix().lower()
            if ext == 'pdf':
                os.startfile(abs_doc_path)
                return True

            if ext in ['mp4', 'mp4a', 'mp3']:
                reg_entry = QSettings("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Active Setup\\Installed Components",
                                QSettings.NativeFormat)
                reg_entry.beginGroup("{22d6f312-b0f6-11d0-94ab-0080c74c7e95}") 
                is_installed = reg_entry.value("IsInstalled")
                reg_entry.endGroup()

                if is_installed == 1:
                    os.startfile(abs_doc_path)
                    return True

            doc_viewer = self._create_viewer(document_widget)

            doc_viewer.load_document(abs_doc_path)

            self._doc_viewers[doc_identifier] = doc_viewer

            self._mdi_area.addSubWindow(doc_viewer)

            doc_viewer.show()

        if not self.isVisible() and visible:
            self.setVisible(True)

        if self.isMinimized():
            self.showNormal()

        self.center()

        return True

    def set_active_sub_window(self, viewer):
        if viewer:
            self._mdi_area.setActiveSubWindow(viewer)

    def absolute_document_path(self, document_widget):
        """
        Build the absolute document path using info from the document widget.
        :param document_widget: Instance of document widget.
        :return: Absolute path of the supporting document.
        :rtype: str
        """
        abs_path = ''

        file_manager = document_widget.fileManager
        if not file_manager is None:
            network_repository = file_manager.networkPath
            file_id = document_widget.file_identifier()
            source_entity = document_widget.doc_source_entity()
            profile_name = current_profile().name
            doc_type = document_widget.doc_type_value().lower().replace(
                ' ', '_'
            )
            file_name, file_extension = guess_extension(
                document_widget.displayName()
            )

            abs_path = network_repository + '/' + profile_name + '/' +\
                       unicode(source_entity) + "/" + unicode(doc_type) + "/" +\
                       unicode(file_id) + unicode(file_extension)

        return abs_path

    def reset(self):
        """
        Removes all document viewers in the view area.
        The QCloseEvent sent to each sub-window will decrement the register.
        """
        self._mdi_area.closeAllSubWindows()

    def _create_viewer(self, document_widget):
        """
        Creates a new instance of a document viewer.
        :param document_widget: Contains all
        the necessary information required
        to load the specific document.
        :return: Document viewer object
        :rtype: DocumentViewer
        """
        doc_viewer = DocumentViewer(
            self._mdi_area, document_widget.file_identifier()
        )
        doc_viewer.setAttribute(Qt.WA_DeleteOnClose)
        doc_viewer.setWindowTitle(
            document_widget.displayName()
        )

        # TODO: Incorporate logic for determining
        # TODO: viewer based on document type
        ph_viewer = PhotoViewer()

        # v_layout = QVBoxLayout()
        # v_layout.addWidget(ph_viewer)
        # doc_viewer.setLayout(v_layout)

        doc_viewer.set_view_widget(ph_viewer)

        doc_viewer.closed.connect(self._on_viewer_closed)

        return doc_viewer

    def remove_viewer(self, viewer_id):
        """
        Close and remove the viewer with the specified viewer ID.
        """
        if viewer_id in self._doc_viewers:
            viewer = self._doc_viewers[viewer_id]
            self._mdi_area.setActiveSubWindow(viewer)
            self._mdi_area.closeActiveSubWindow()

        self._on_viewer_closed(viewer_id)

    def _on_viewer_closed(self,file_id):
        """
        Slot raised when a document viewer is closed.
        """
        if file_id in self._doc_viewers:
            del self._doc_viewers[file_id]
