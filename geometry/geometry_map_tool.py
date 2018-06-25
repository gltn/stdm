from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QPixmap, QCursor

from qgis.gui import QgsMapToolIdentify, QgsMapTool
from qgis.utils import iface


class GeometryMapTool(QgsMapToolIdentify, QgsMapTool):

    geomIdentified = pyqtSignal(list)
    # canvasClicked = pyqtSignal(['QgsPoint', 'Qt::MouseButton'])

    def __init__(self, canvas):
        self.canvas = canvas
        # QgsMapToolIdentify.__init__(self, canvas)
        QgsMapTool.__init__(self, canvas)
        # First we have to load the pixmap for the cursor
        # self.cursor_pixmap = QPixmap(
        #     '":/plugins/stdm/images/icons/geometry_map_tool.png'
        # )
        self.feature_ids = []
        self.feature_id = None
        # Now we create a QCursor with the pixmap
        # self.cursor = QCursor(self.cursor_pixmap, 1, 1)
        self.widget = None
        self.setCursor(Qt.PointingHandCursor)

    def setWidget(self, widget):
        self.widget = widget

    def canvasReleaseEvent(self, mouseEvent):

        results = self.identify(
            mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer
        )
        # print 'released ', mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer
        # if len(results) > 0:
        #     feature_id = results[0].mFeature.id()
        #     results[0].mLayer.selectByIds([feature_id])
        #     print feature_id
        #     # results[0].mLayer.selectByIds(results[0].mFeature)
        #     self.geomIdentified.emit(feature_id)

    def canvasPressEvent(self, mouseEvent):
        # print 'clicked '
        # Just set the mapTool's parent cursor to
        # the previous cursor
        # self.parent().setCursor(self.stdCursor)

        # pnt = self.toMapCoordinates(mouseEvent.pos())
        # self.canvasClicked.emit(pnt, mouseEvent.button())
        results = self.identify(
            mouseEvent.x(), mouseEvent.y(), self.ActiveLayer, self.VectorLayer
        )
        if len(results) > 0:
            # if self.feature_id != results[0].mFeature.id():
            iface.mainWindow().blockSignals(True)
            results[0].mLayer.selectByIds([results[0].mFeature.id()])
            iface.mainWindow().blockSignals(False)
            self.feature_ids.append(results[0].mFeature.id())
            # self.feature_id = results[0].mFeature.id()
            results[0].mLayer.selectionChanged.emit(
                self.feature_ids,
                [self.feature_id],
                True
            )

            self.feature_id = results[0].mFeature.id()

                # self.widget.on_feature_selected([self.feature_id])
                # results[0].mLayer.selectByIds(results[0].mFeature)
                # self.geomIdentified.emit([self.feature_id])
