"""
/***************************************************************************
Name                 : ProfileTenureView
Description          : A widget for rendering a profile's social tenure
                       relationship.
Date                 : 9/October/2016
copyright            : John Kahiu
email                : gkahiu at gmail dot com
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
import math

from qgis.PyQt.QtCore import (
    pyqtSignal,
    QFile,
    QIODevice,
    QLineF,
    QPointF,
    QRect,
    QRectF,
    QSize,
    QSizeF,
    Qt
)
from qgis.PyQt.QtGui import (
    QBrush,
    QColor,
    QCursor,
    QFont,
    QFontMetrics,
    QIcon,
    QImage,
    QLinearGradient,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QTextLayout
)
from qgis.PyQt.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QWidget
)

from stdm.ui.gui_utils import GuiUtils
from stdm.ui.image_export_settings import ImageExportSettings


class Arrow(QGraphicsLineItem):
    """
    Renders an arrow object (with line and arrow head) from one item to
    another. The arrow head size can be customized by specifying the angle
    and width of the arrow base.
    """

    def __init__(self, start_item, end_item, base_width=None,
                 tip_angle=None, fill_arrow_head=False,
                 parent_item=None):
        """
        Class constructor
        :param start_point: Arrow start item.
        :type start_point: BaseTenureItem
        :param end_point: Arrow end item.
        :type end_point: BaseTenureItem
        :param base_width: Width (in pixels) of the arrow base. If not
        specified, it defaults to 9.0.
        :type base_width: float
        :param tip_angle: Angle (in radians) between the two line components
        at the tip of the arrow. If not specified, it defaults to
        math.radians(50.0).
        Minimum math.radians(10.0)
        Maximum math.radians(<90.0)
        :type tip_angle: float
        :param fill_arrow_head: True to close and fill the arrow head with
        the specified pen and brush settings. Defaults to False.
        :type fill_arrow_head: bool
        :param parent_item: Parent item.
        :type parent_item: QGraphicsItem
        :param scene: Scene object.
        :type scene: QGraphicsScene
        """
        super(Arrow, self).__init__(parent_item)

        self._start_item = start_item
        self._end_item = end_item

        self.base_width = base_width
        if self.base_width is None:
            self.base_width = 9.0

        self._angle = tip_angle
        if tip_angle is None:
            self._angle = math.radians(50.0)

        self.fill_arrow_head = fill_arrow_head

        self.setPen(
            QPen(
                Qt.black,
                1,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.MiterJoin
            )
        )
        self.brush = QBrush(Qt.black)

        self._arrow_head_points = []

    @property
    def start_item(self):
        """
        :return: Returns the start item for the arrow.
        :rtype: BaseTenureItem
        """
        return self._start_item

    @property
    def end_item(self):
        """
        :return: Returns the end item for the arrow.
        :rtype: BaseTenureItem
        """
        return self._end_item

    @property
    def start_point(self):
        """
        :return: Returns the arrow start point.
        :rtype: QPointF
        """
        return self._start_item.pos()

    @property
    def end_point(self):
        """
        :return: Returns the arrow end point.
        :rtype: QPointF
        """
        return self._end_item.pos()

    def boundingRect(self):
        extra = (self.base_width + self.pen().widthF()) / 2.0
        p1 = self.line().p1()
        p2 = self.line().p2()

        rect = QRectF(
            p1, QSizeF(p2.x() - p1.x(), p2.y() - p1.y())
        ).normalized().adjusted(-extra, -extra, extra, extra)

        return rect

    def arrow_head_polygon(self):
        """
        :return: Returns the arrow head as a QPolygonF object.
        :rtype: QPolygonF
        """
        return QPolygonF(self._arrow_head_points)

    def shape(self):
        path = super(Arrow, self).shape()
        path.addPolygon(self.arrow_head_polygon())

        return path

    @property
    def angle(self):
        """
        :return: Returns the value of the angle at the tip in radians.
        :rtype: float
        """
        return self._angle

    @angle.setter
    def angle(self, angle):
        """
        Sets the value of the angle to be greater than or equal to
        math.radians(10.0) and less than math.radians(90).
        :param angle: Angle at the tip of the arrow in radians.
        :type angle: float
        """
        min_angle = math.radians(10.0)
        max_angle = math.radians(90)

        if angle < min_angle:
            self._angle = min_angle
        elif angle > max_angle:
            self._angle = max_angle
        else:
            self._angle = angle

        self.update()

    @property
    def arrow_points(self):
        """
        :return: Returns a collection of points used to draw the arrow head.
        :rtype: list(QPointF)
        """
        return self._arrow_head_points

    def update_position(self):
        """
        Updates the position of the line and arrowhead when the positions of
        the start and end items change.
        """
        line = QLineF(
            self.mapFromScene(self.start_item.center()),
            self.mapFromScene(self.end_item.center())
        )
        self.setLine(line)

    def _intersection_point(self, item, reference_line):
        # Computes the intersection point between the item's line segments
        # with the reference line.
        intersect_point = QPointF()

        for l in item.line_segments():
            intersect_type = l.intersect(reference_line, intersect_point)
            if intersect_type == QLineF.BoundedIntersection:
                return intersect_point

        return None

    def paint(self, painter, option, widget):
        """
        Draw the arrow item.
        """
        if self._start_item.collidesWithItem(self._end_item):
            return

        painter.setPen(self.pen())

        center_line = QLineF(self.start_item.center(), self.end_item.center())

        # Get intersection points
        start_intersection_point = self._intersection_point(
            self._start_item,
            center_line
        )
        end_intersection_point = self._intersection_point(
            self._end_item,
            center_line
        )

        # Do not draw if there are no intersection points
        if start_intersection_point is None or end_intersection_point is None:
            return

        arrow_line = QLineF(start_intersection_point, end_intersection_point)
        self.setLine(arrow_line)

        arrow_length = arrow_line.length()

        # Setup computation parameters
        cnt_factor = (self.base_width / 2.0) / (
                math.tan(self._angle / 2.0) * arrow_length
        )
        cnt_point_delta = (self.base_width / 2.0) / arrow_length

        # Get arrow base along the line
        arrow_base_x = end_intersection_point.x() - (arrow_line.dx() * cnt_factor)
        arrow_base_y = end_intersection_point.y() - (arrow_line.dy() * cnt_factor)

        # Get deltas to arrow points from centre point of arrow base
        cnt_point_dx = -(arrow_line.dy() * cnt_point_delta)
        cnt_point_dy = arrow_line.dx() * cnt_point_delta

        # Compute absolute arrow positions
        A1 = QPointF(arrow_base_x - cnt_point_dx, arrow_base_y - cnt_point_dy)
        A2 = QPointF(arrow_base_x + cnt_point_dx, arrow_base_y + cnt_point_dy)

        # Update arrow points
        self._arrow_head_points = [A1, A2, end_intersection_point]

        # Draw main arrow line
        painter.drawLine(arrow_line)

        # Draw arrow head
        if not self.fill_arrow_head:
            painter.drawLine(A1, end_intersection_point)
            painter.drawLine(end_intersection_point, A2)

        else:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.brush)
            painter.drawPolygon(self.arrow_head_polygon())


class BaseIconRender(object):
    """Renders an icon on the tenure item's header section. This icon can be
    can be used to visually depict the nature of the context of the tenure
    item. See bounding_rect function for positioning of the icon in the
    tenure item. This is an abstract class and needs to be sub-classed for
    custom renderers."""

    def __init__(self):
        # Icon area is 16px by 16px
        # TODO: Set location based on screen resolution
        self.upper_left = QPointF(142.5, 14.0)
        self.bottom_right = QPointF(158.5, 30.0)

    def bounding_rect(self):
        """
        :return: Returns the bounds of the icon and does not factor in the
        pen width.
        :rtype: QRectF
        """
        return QRectF(self.upper_left, self.bottom_right)

    @property
    def width(self):
        """
        :return: Returns the width of the icon plane area.
        :rtype: float
        """
        return self.bottom_right.x() - self.upper_left.x()

    @property
    def height(self):
        """
        :return: Returns the height of the icon plane area.
        :rtype: float
        """
        return self.bottom_right.y() - self.upper_left.y()

    @property
    def pen(self):
        """
        :return: Returns a default pen for use in the renderer's painter.
        :rtype: QPen
        """
        return QPen(Qt.black, 1.0, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin)

    def draw(self, painter, item):
        """
        Custom code for rendering the icon. To be implemented by subclasses.
        :param painter: Painter object
        :type painter: QPainter
        :param item: Tenure item object.
        :type item: BaseTenureItem
        """
        raise NotImplementedError


class EntityIconRenderer(BaseIconRender):
    """Renderer for an icon depicting a data table."""

    def draw(self, p, item):
        # Save painter state
        p.save()

        p.setPen(self.pen)

        # Draw outline
        # Define gradient
        grad = QLinearGradient(self.upper_left, self.bottom_right)
        grad.setColorAt(0.0, Qt.white)
        grad.setColorAt(0.65, QColor('#D2F6FC'))
        grad.setColorAt(1.0, QColor('#50E3FC'))

        grad_bush = QBrush(grad)
        p.setBrush(grad_bush)
        p.drawRect(self.bounding_rect())

        # Draw column header
        cols_header_rect = QRectF(
            self.upper_left.x() + 0.5,
            self.upper_left.y() + 0.5,
            self.width - 1.0,
            3.5
        )
        p.setBrush(QColor('#1399FC'))
        p.setPen(Qt.NoPen)
        p.drawRect(cols_header_rect)

        # Draw horizontal separators
        h1_start_point = self.upper_left + QPointF(0, 4.0)
        h1_end_point = self.upper_left + QPointF(self.width, 4.0)
        h1_sep = QLineF(h1_start_point, h1_end_point)
        p.setPen(self.pen)
        p.drawLine(h1_sep)

        h_col_pen = QPen(self.pen)
        h_col_pen.setColor(QColor('#32A7BB'))
        p.setPen(h_col_pen)

        delta_v = 12 / 3.0
        y = 4.0 + delta_v

        for i in range(2):
            h_start_point = self.upper_left + QPointF(1.0, y)
            h_end_point = self.upper_left + QPointF(self.width - 1.0, y)
            h_sep = QLineF(h_start_point, h_end_point)

            y += delta_v

            p.drawLine(h_sep)

        # Draw vertical column separator
        v_start_point = self.upper_left + QPointF(8.0, 0)
        v_end_point = self.upper_left + QPointF(8.0, 16.0)
        col_vertical_sep = QLineF(v_start_point, v_end_point)
        p.setPen(self.pen)
        p.drawLine(col_vertical_sep)

        p.restore()


class DocumentIconRenderer(BaseIconRender):
    """Renderer for document icon."""

    def draw(self, p, item):
        p.save()

        # Draw primary folder
        outline = QPen(self.pen)
        outline.setColor(QColor('#1399FC'))
        p.setPen(outline)

        back_leaf_brush = QBrush(QColor('#C2E4F8'))
        p.setBrush(back_leaf_brush)

        leaf_1 = QPainterPath()
        leaf_1.moveTo(self.upper_left + QPointF(0, (self.height - 1.5)))
        leaf_1.lineTo(self.upper_left + QPointF(0, 5.0))
        leaf_1.lineTo(self.upper_left + QPointF(2.0, 5.0))
        leaf_1.lineTo(self.upper_left + QPointF(4.0, 2.5))
        leaf_1.lineTo(self.upper_left + QPointF(8.0, 2.5))
        leaf_1.lineTo(self.upper_left + QPointF(10.0, 5.0))
        leaf_1.lineTo(self.upper_left + QPointF(13.0, 5.0))
        leaf_1.lineTo(self.upper_left + QPointF(13.0, self.height - 1.5))
        leaf_1.closeSubpath()
        p.drawPath(leaf_1)

        # Front folder leaf
        p.setBrush(QBrush(Qt.white))
        leaf_2 = QPainterPath()
        leaf_2.moveTo(self.upper_left + QPointF(0.5, (self.height - 0.5)))
        leaf_2.lineTo(self.upper_left + QPointF(3.0, 8.5))
        leaf_2.lineTo(self.upper_left + QPointF(15.5, 8.5))
        leaf_2.lineTo(self.upper_left + QPointF(13.0, self.height - 0.5))
        leaf_2.closeSubpath()
        p.drawPath(leaf_2)

        p.restore()


class TenureLinkRenderer(BaseIconRender):
    """Renders an icon depicting a link between the party and
    spatial unit."""

    def draw(self, p, item):
        p.save()

        outline = QPen(self.pen)
        outline.setColor(QColor('#1399FC'))
        outline.setCapStyle(Qt.RoundCap)
        outline.setWidthF(1.6)
        p.setPen(outline)

        # Set segment fill brush
        seg_brush = QBrush(QColor('#ECF8FF'))
        p.setBrush(seg_brush)

        # Draw link segment
        link_path = QPainterPath()
        link_path.moveTo(self.upper_left + QPointF(2.0, 5.0))
        rect_pos = self.upper_left + QPointF(0.5, 5.0)
        arc_rect = QRectF(rect_pos, QSizeF(3.0, 6.0))
        link_path.arcTo(arc_rect, 90, 180.0)
        link_path.lineTo(self.upper_left + QPointF(5.5, 11.0))
        rect_pos_2 = self.upper_left + QPointF(4.0, 5.0)
        arc_rect_2 = QRectF(rect_pos_2, QSizeF(3.0, 6.0))
        link_path.arcTo(arc_rect_2, -90, 180)
        link_path.closeSubpath()
        p.drawPath(link_path)

        # Draw 2nd segment
        p.translate(8.5, 0)
        p.drawPath(link_path)

        # Draw segment connector
        p.translate(-8.5, 0)
        start_p = self.upper_left + QPointF(5.0, 8.0)
        end_p = self.upper_left + QPointF(11.0, 8.0)
        p.drawLine(QLineF(start_p, end_p))

        p.restore()


class BaseTenureItem(QGraphicsItem):
    """Abstract class that provides core functionality for rendering entity and
    social tenure relationship objects corresponding to the entities in a
    given profile."""
    Type = QGraphicsItem.UserType + 1

    def __init__(self, parent=None, **kwargs):
        super(BaseTenureItem, self).__init__(parent)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        # Renderer for header icon
        self.icon_renderer = kwargs.get('icon_renderer', None)

        self.arrows = []

        self.pen = QPen(
            Qt.black,
            0.9,
            Qt.SolidLine,
            Qt.RoundCap,
            Qt.RoundJoin
        )

        # Display properties
        self._default_header = QApplication.translate(
            'ProfileTenureView',
            'Not Defined'
        )
        self.header = self._default_header
        self.items_title = ''
        self.icon_painter = kwargs.pop('icon_painter', None)
        self.items = []
        self.font_name = 'Consolas'
        self._entity = None

        # Distance between the primary shape and its shadow
        self.shadow_thickness = 4

        self._side = 156
        self._height = self._side
        self._start_pos = 10

        # The start and stop positions match the size of the item
        stop_position = self._start_pos + self._side

        # Main item gradient
        self._gradient = QLinearGradient(
            self._start_pos,
            self._start_pos,
            stop_position,
            stop_position
        )

        self._gradient_light = QColor('#fcf2e3')
        self._gradient_dark = QColor('#e9dac2')
        self._gradient.setColorAt(0.0, self._gradient_light)
        self._gradient.setColorAt(1.0, self._gradient_dark)
        self._brush = QBrush(self._gradient)

        # Shadow gradient
        # The start and stop positions match the size of the item
        shadow_start_pos = self._start_pos + self.shadow_thickness
        shadow_stop_pos = self._start_pos + self._side + self.shadow_thickness
        self._shadow_gradient = QLinearGradient(
            shadow_start_pos,
            shadow_start_pos,
            shadow_stop_pos,
            shadow_stop_pos
        )
        self._shadow_gradient.setColorAt(0.0, QColor('#f7f8f9'))
        self._shadow_gradient.setColorAt(1.0, QColor('#d1d1d1'))
        self._brush = QBrush(self._gradient)

        self._text_highlight_color = QColor('#E74C3C')
        self._text_item_color = QColor('#CC0000')
        self._normal_text_color = Qt.black

    def type(self):
        return BaseTenureItem.Type

    def remove_arrow(self, arrow):
        """
        Removes an arrow from the collection.
        :param arrow: Arrow item.
        :type arrow: Arrow
        """
        try:
            self.arrows.remove(arrow)
        except ValueError:
            pass

    def remove_arrows(self):
        """
        Removes all arrows associated with this item and related item.
        """
        for ar in self.arrows[:]:
            ar.start_item.remove_arrow(ar)
            ar.end_item.remove_arrow(ar)
            self.scene().removeItem(ar)

    def add_arrow(self, arrow):
        """
        Adds arrow item to the collection.
        :param arrow: Arrow item.
        :type arrow: Arrow
        """
        self.arrows.append(arrow)

    def boundingRect(self):
        extra = self.pen.widthF() / 2.0

        return QRectF(
            self._start_pos - extra,
            self._start_pos - extra,
            self.width + self.shadow_thickness + extra,
            self.height + self.shadow_thickness + extra
        )

    def invalidate(self):
        """
        Reset the title and items.
        """
        self.header = self._default_header
        self.items = []

        self.update()

    @property
    def brush(self):
        """
        :return: Returns the brush used for rendering the entity item.
        :rtype: QBrush
        """
        return self._brush

    @property
    def header_font(self):
        """
        :return: Returns the font object used to render the header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 10, 63)

    @property
    def items_title_font(self):
        """
        :return: Returns the font object used to render the items header text.
        :rtype: QFont
        """
        return QFont(self.font_name, 10)

    @property
    def items_font(self):
        """
        :return: Returns the font object used to render multiline items.
        :rtype: QFont
        """
        return QFont(self.font_name, 9)

    @property
    def entity(self):
        """
        :return: Returns the entity associated with the rendered.
        :rtype: Entity
        """
        return self._entity

    def auto_adjust_height(self):
        """
        :return: True if the height should be automatically adjusted to fit
        the number of items specified. Otherwise, False; in this case, the
        height is equal to the default height of the item. Items that exceed
        the height of the items area will not be shown.
        To be overridden by sub-classes.
        :rtype: bool
        """
        return True

    @entity.setter
    def entity(self, entity):
        """
        Sets the current entity object.
        :param entity: Entity object.
        :type entity: Entity
        """
        self._entity = entity
        self.prepareGeometryChange()
        self._on_set_entity()

    def _on_set_entity(self):
        """
        Update attributes based on the entity's attributes. To be implemented
        by subclasses.
        """
        raise NotImplementedError

    @property
    def width(self):
        """
        :return: Returns the logical width of the item.
        :rtype: float
        """
        return float(self._side + self.shadow_thickness)

    @property
    def height(self):
        """
        :return: Returns the logical height of the item. If
        auto_adjust_height is True then the height will be automatically
        adjusted to match number of items, else it will be equal to the width
        of the item.
        """
        return float(self._height + self.shadow_thickness)

    def scene_bounding_rect(self):
        """
        :return: Returns the bounding rect of the primary item in scene
        coordinates, this does not include the shadow thickness.
        :rtype: QRectF
        """
        local_start_point = QPointF(self._start_pos, self._start_pos)
        scene_start_point = self.mapToScene(local_start_point)

        return QRectF(scene_start_point, QSizeF(self._side, self._height))

    def center(self):
        """
        :return: Returns the center point of the item in scene coordinates.
        :rtype: QPointF
        """
        return self.scene_bounding_rect().center()

    def line_segments(self):
        """
        :return: Returns a list of QLineF objects that constitute the scene
        bounding rect. The line segments are in scene coordinates.
        :rtype: QRectF
        """
        lines = []

        rect = self.scene_bounding_rect()
        poly = QPolygonF(rect)

        for i, p in enumerate(poly):
            if i == len(poly) - 1:
                break

            p1 = poly[i]

            # Close to first point if the last item is reached
            if i + 1 == len(poly):
                p2 = poly[0]
            else:
                p2 = poly[i + 1]

            # Construct line object
            line = QLineF(p1, p2)
            lines.append(line)

        return lines

    def _elided_text(self, font, text, width):
        # Returns elided version of the text if greater than the width
        fm = QFontMetrics(font)

        return str(fm.elidedText(text, Qt.ElideRight, width))

    def _elided_items(self, font, width):
        # Formats each item text to incorporate an elide if need be and
        # return the items in a list.
        return [self._elided_text(font, item, width) for item in self.items]

    def items_size(self, items):
        """
        Computes an appropriate width and height of an items' text separated
        by a new line.
        :param items: Iterable containing string items for which the size
        will be computed.
        :type items: list
        :return: Returns a size object that fits the items' text in the list.
        :rtype: QSize
        """
        fm = QFontMetrics(self.items_font)

        return fm.size(Qt.TextWordWrap, '\n'.join(items))

    def items_by_height(self, height, items):
        """
        :param height: Height in pixels in which the subset of items will fit.
        :type height: int
        :return: Returns a subset of items which fit the specified height.
        :rtype: list
        """
        items_sub = []

        fm = QFontMetrics(self.items_font)

        for i in items:
            sz = self.items_size(items_sub)
            if sz.height() > height:
                break

            items_sub.append(i)

        return items_sub

    def _font_height(self, font, text):
        """
        Computes the height for the given font object.
        :param font: Font object.
        :type font: QFont
        :param text: Text
        :type text: str
        :return: Returns the minimum height for the given font object.
        :rtype: int
        """
        fm = QFontMetrics(font)

        return fm.size(Qt.TextSingleLine, text).height()

    def draw_text(self, painter, text, font, bounds, alignment=Qt.AlignCenter):
        """
        Provides a device independent mechanism for rendering fonts
        regardless of the device's resolution. By default, the text will be
        centred. This is a workaround for the font scaling issue for devices
        with different resolutions.
        :param painter: Painter object.
        :type painter: QPainter
        :param text: Text to be rendered.
        :type text: str
        :param font: Font for rendering the text.
        :type font: QFont
        :param bounds: Rect object which will provide the reference point for
        drawing the text.
        :type bounds: QRectF
        :param alignment: Qt enums used to describe alignment. AlignCenter is
        the default. Accepts bitwise OR for horizontal and vertical flags.
        :type alignment: int
        """
        layout = QTextLayout(text, font)

        layout.beginLayout()
        # Create the required number of lines in the layout
        while layout.createLine().isValid():
            pass
        layout.endLayout()

        y = 0
        max_width = 0

        # Set line positions relative to the layout
        for i in range(layout.lineCount()):
            line = layout.lineAt(i)
            max_width = max(max_width, line.naturalTextWidth())
            line.setPosition(QPointF(0, y))
            y += line.height()

        # Defaults
        start_x = bounds.left()
        start_y = bounds.top()

        # Horizontal flags
        if (alignment & Qt.AlignLeft) == Qt.AlignLeft:
            start_x = bounds.left()
        elif (alignment & Qt.AlignCenter) == Qt.AlignCenter or \
                (alignment & Qt.AlignHCenter) == Qt.AlignHCenter:
            start_x = bounds.left() + (bounds.width() - max_width) / 2.0

        # Vertical flags
        if (alignment == Qt.AlignTop) == Qt.AlignTop:
            start_y = bounds.top()
        elif (alignment & Qt.AlignCenter) == Qt.AlignCenter or \
                (alignment & Qt.AlignVCenter) == Qt.AlignVCenter:
            start_y = bounds.top() + (bounds.height() - y) / 2.0

        layout.draw(painter, QPointF(start_x, start_y))

    def paint(self, painter, option, widget=None):
        """
        Performs the painting of the tenure item based on the object's
        attributes.
        :param painter: Performs painting operation on the item.
        :type painter: QPainter
        :param option: Provides style option for the item.
        :type option: QStyleOptionGraphicsItem
        :param widget: Provides points to the widget that is being painted on.
        :type widget: QWidget
        """
        shadow_start_pos = self._start_pos + self.shadow_thickness

        # Use height of subsections to compute the appropriate height
        header_height = self._font_height(self.header_font, self.header) + 7

        items_title_height = self._font_height(
            self.items_title_font,
            self.items_title
        )
        margin = 1

        fixed_height = header_height + items_title_height + (6 * margin)

        if self.auto_adjust_height():
            items_height = self.items_size(self.items).height() + 2
            main_item_height = max(self._side, fixed_height + items_height)

        else:
            items_height = self._side - fixed_height
            main_item_height = self._side

        self._height = main_item_height

        shadow_rect = QRect(
            shadow_start_pos,
            shadow_start_pos,
            self._side,
            main_item_height
        )

        main_item_rect = QRect(
            self._start_pos,
            self._start_pos,
            self._side,
            main_item_height
        )

        painter_pen = painter.pen()
        painter_pen.setColor(self._normal_text_color)
        painter_pen.setWidth(0)

        # Create shadow effect using linear gradient
        painter.setBrush(self._shadow_gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRect(shadow_rect)

        painter.setPen(self.pen)
        painter.setBrush(self._brush)

        # Main item outline
        painter.drawRect(main_item_rect)
        line_y_pos = header_height + margin * 2
        painter.drawLine(
            self._start_pos,
            self._start_pos + line_y_pos,
            self._start_pos + self._side,
            self._start_pos + line_y_pos
        )

        # Draw header text
        header_start_pos = self._start_pos + margin
        header_rect = QRect(
            header_start_pos,
            header_start_pos,
            self._side - (margin * 2),
            header_height
        )

        # Adjust header text area if there is an icon renderer
        if not self.icon_renderer is None:
            init_width = header_rect.width()
            adj_width = init_width - (self.icon_renderer.width + 6)
            header_rect.setWidth(int(adj_width))

        # Draw header icon if renderer is available
        if not self.icon_renderer is None:
            if isinstance(self.icon_renderer, BaseIconRender):
                self.icon_renderer.draw(painter, self)

        painter.setFont(self.header_font)

        if self.header == self._default_header:
            painter.setPen(self._text_highlight_color)
        else:
            painter.setPen(self._normal_text_color)

        elided_header = self._elided_text(
            self.header_font,
            self.header,
            header_rect.width()
        )
        # print(elided_header)
        self.draw_text(painter, elided_header, self.header_font, header_rect)

        # Draw items header
        items_title_rect = QRect(
            header_start_pos + 1,
            header_height + items_title_height - 1,
            self._side - (margin * 4),
            items_title_height
        )
        painter.setFont(self.items_title_font)
        painter.setPen(QColor('#c3b49c'))
        items_title_brush = QBrush(self._gradient_dark)
        painter.setBrush(items_title_brush)
        painter.drawRect(items_title_rect)

        # Adjust left margin of items title
        items_title_rect.adjust(1, 0, 0, 0)
        painter.setPen(self._normal_text_color)
        self.draw_text(
            painter,
            self.items_title,
            self.items_title_font,
            items_title_rect
        )

        # Items listing
        items_margin = 6
        items_vertical_pos = header_height + items_title_height + 16
        items_w = self._side - (items_margin * 2)
        items_rect = QRect(
            header_start_pos + items_margin,
            items_vertical_pos,
            items_w,
            items_height
        )

        # Draw if there are items
        if len(self.items) > 0:
            painter.setFont(self.items_font)
            painter.setPen(self._text_item_color)
            multiline_items = self._elided_items(self.items_font, items_w)

            # If auto-adjust is disabled then extract subset that will fit
            if not self.auto_adjust_height():
                multiline_items = self.items_by_height(
                    items_height,
                    multiline_items
                )

            # QTextLayout requires the unicode character of the line separator
            multiline_items = '\u2028'.join(multiline_items)
            self.draw_text(
                painter,
                multiline_items,
                self.items_font,
                items_rect,
                Qt.AlignLeft | Qt.AlignTop
            )


class EntityItem(BaseTenureItem):
    """
    Represents a Party or a SpatialUnit items in a profile's social tenure
    relationship.
    """
    Type = QGraphicsItem.UserType + 2

    def __init__(self, *args, **kwargs):
        super(EntityItem, self).__init__(*args, **kwargs)
        columns = QApplication.translate(
            'ProfileTenureView',
            'columns'
        )
        self.items_title = '<<{0}>>'.format(columns)

        # Use default renderer if none is specified
        if self.icon_renderer is None:
            self.icon_renderer = EntityIconRenderer()

    def type(self):
        return EntityItem.Type

    def _on_set_entity(self):
        if not self._entity is None:
            self.header = self.entity.short_name
            self.items = list(self.entity.columns.keys())
            self.update()


def _updated_code_values(value_list):
    vl = []

    # Use updated values in the value list
    for cd in value_list.values.values():
        lk_value = cd.value
        if cd.updated_value:
            lk_value = cd.updated_value

        vl.append(lk_value)

    return vl


class TenureRelationshipItem(BaseTenureItem):
    """
    Renders the profile's tenure relationship by listing the tenure types.
    """
    Type = QGraphicsItem.UserType + 3

    def __init__(self, *args, **kwargs):
        super(TenureRelationshipItem, self).__init__(*args, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'tenure types'
        )
        self.items_title = '<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Social Tenure'
        )

        # Use default renderer if none is specified
        if self.icon_renderer is None:
            self.icon_renderer = TenureLinkRenderer()

    def type(self):
        return TenureRelationshipItem.Type

    def auto_adjust_height(self):
        # Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            self.items = _updated_code_values(
                self.entity.tenure_type_lookup.value_list
            )
            self.update()


class TenureDocumentItem(BaseTenureItem):
    """
    Renders the document types for the social tenure relationship.
    """
    Type = QGraphicsItem.UserType + 4

    def __init__(self, *args, **kwargs):
        super(TenureDocumentItem, self).__init__(*args, **kwargs)
        tenure_types = QApplication.translate(
            'ProfileTenureView',
            'document types'
        )
        self.items_title = '<<{0}>>'.format(tenure_types)
        self.header = QApplication.translate(
            'ProfileTenureView',
            'Documents'
        )

        # Use default renderer if none is specified
        if self.icon_renderer is None:
            self.icon_renderer = DocumentIconRenderer()

    def type(self):
        return TenureDocumentItem.Type

    def auto_adjust_height(self):
        # Base class override
        return False

    def _on_set_entity(self):
        if not self._entity is None:
            supporting_doc = self.entity.supporting_doc
            self.items = _updated_code_values(
                supporting_doc.doc_type.value_list
            )
            self.update()


class Annotation(QGraphicsTextItem):
    """Add major or minor annotation item to the view. The only difference
    between major and minor annotations is the font size and underline
    (for the former)."""
    Minor, Major = list(range(2))

    lost_focus = pyqtSignal(QGraphicsTextItem)

    def __init__(self, parent=None, size=0):
        super(Annotation, self).__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.size = size
        self.setDefaultTextColor(Qt.black)

        font = 'Consolas'

        # Set font size
        if self.size == Annotation.Minor:
            self.setFont(QFont(font, 10, 50))

        else:
            font = QFont(font, 14, 75)
            font.setUnderline(True)
            self.setFont(font)

    def focusOutEvent(self, event):
        # Disable text interaction
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.lost_focus.emit(self)
        super(Annotation, self).focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        # Enable text interaction
        if self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)

        super(Annotation, self).mouseDoubleClickEvent(event)


class ProfileTenureScene(QGraphicsScene):
    """
    Custom scene for handling annotation items.
    """
    InsertMajorAnnotation, InsertMinorAnnotation, MoveItem = list(range(3))

    annotation_inserted = pyqtSignal(QGraphicsTextItem)

    def __init__(self, parent=None):
        super(ProfileTenureScene, self).__init__(parent)

        self.mode = ProfileTenureScene.MoveItem

    def editor_lost_focus(self, item):
        """
        Check if the annotation item is empty and delete if it is.
        :param item: Annotation item.
        :type item: QGraphicsTextItem
        """
        cursor = item.textCursor()
        cursor.clearSelection()
        item.setTextCursor(cursor)

        if not item.toPlainText():
            self.removeItem(item)
            item.deleteLater()

    def mousePressEvent(self, event):
        """
        Handles insert of annotation item.
        :param event: Mouse press event.
        :type event: QGraphicsSceneMouseEvent
        """
        if event.button() != Qt.LeftButton:
            return

        if self.mode == ProfileTenureScene.InsertMajorAnnotation:
            sz = Annotation.Major
            self._insert_annotation_item(sz, event.scenePos())
        elif self.mode == ProfileTenureScene.InsertMinorAnnotation:
            sz = Annotation.Minor
            self._insert_annotation_item(sz, event.scenePos())

        super(ProfileTenureScene, self).mousePressEvent(event)

    def _insert_annotation_item(self, size, scene_pos):
        # Insert major or minor annotation based on size
        annotation = Annotation(size=size)
        annotation.setTextInteractionFlags(Qt.TextEditorInteraction)
        annotation.setZValue(1000.0)
        annotation.lost_focus.connect(self.editor_lost_focus)
        self.addItem(annotation)
        annotation.setPos(scene_pos)
        self.annotation_inserted.emit(annotation)


class ProfileTenureView(QGraphicsView):
    """
    A widget for rendering a profile's social tenure relationship. It also
    includes functionality for saving the view as an image.
    """
    MIN_DPI = 72
    MAX_DPI = 600

    # Enums for add party policy
    ADD_TO_EXISTING, REMOVE_PREVIOUS = list(range(2))

    def __init__(self, parent=None, profile=None):
        super(ProfileTenureView, self).__init__(parent)

        # Specify STR graphic items adding policy
        self.add_party_policy = ProfileTenureView.ADD_TO_EXISTING
        self.add_spatial_unit_policy = ProfileTenureView.ADD_TO_EXISTING

        # Init items
        # Container for party entities and corresponding items
        self._default_party_item = EntityItem()
        self._party_items = {}
        self._sp_unit_items = {}
        self._default_sp_item = EntityItem()
        self._str_item = TenureRelationshipItem()
        self._supporting_doc_item = TenureDocumentItem()

        self.profile = profile

        scene_rect = QRectF(0, 0, 960, 540)
        scene = ProfileTenureScene(self)
        scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        scene.setSceneRect(scene_rect)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        self.setScene(scene)

        # Connect signals
        scene.annotation_inserted.connect(self.annotation_inserted)

        # Add items to view
        self.scene().addItem(self._default_party_item)
        self.scene().addItem(self._str_item)
        self.scene().addItem(self._default_sp_item)
        self.scene().addItem(self._supporting_doc_item)

        # Position items
        self._default_party_item.setPos(210, 20)
        self._str_item.setPos(400, 20)
        self._default_sp_item.setPos(590, 20)
        self._supporting_doc_item.setPos(400, 220)

        # Ensure vertical scroll is at the top
        self.centerOn(490.0, 20.0)

        # Link social tenure item to supporting documents item
        self.add_arrow(self._supporting_doc_item, self._str_item)

    def annotation_inserted(self, item):
        """
        Slot raised when an annotation item has been inserted.
        :param item: Annotation item.
        :type item: Annotation
        """
        self.scene().mode = ProfileTenureScene.MoveItem

    @property
    def profile(self):
        """
        :return: The profile object being rendered.
        :rtype: Profile
        """
        return self._profile

    def _update_profile(self):
        # Update profile objects and render
        if self._profile is None:
            return

        # Remove existing party items
        party_items = list(self._party_items.keys())
        for p in party_items:
            self.remove_party(p)

        # Remove spatial unit items
        spatial_unit_items = list(self._sp_unit_items.keys())
        for sp in spatial_unit_items:
            self.remove_spatial_unit(sp)

        str_ent = self._profile.social_tenure
        # Set renderer entities
        self._str_item.entity = str_ent
        self._supporting_doc_item.entity = str_ent

        # Add party entities
        parties = str_ent.parties
        if len(parties) == 0:
            self._default_party_item.show()
        else:
            self.add_parties(parties)

        # Add spatial unit entities
        sp_units = str_ent.spatial_units
        if len(sp_units) == 0:
            self._default_sp_item.show()
        else:
            self.add_spatial_units(sp_units)

    def add_parties(self, parties):
        """
        Add party items to the view.
        :param parties: List of party entities.
        :type parties: list
        """
        for p in parties:
            self.add_party_entity(p)

    def add_spatial_units(self, spatial_units):
        """
        Add spatial unit items to the view.
        :param spatial_units: List of spatial unit entities.
        :type spatial_units: list
        """
        for sp in spatial_units:
            self.add_spatial_unit_entity(sp)

    @profile.setter
    def profile(self, profile):
        """
        Sets the profile object whose STR view is to rendered.
        :param profile: Profile object to be rendered.
        :type profile: Profile
        """
        self._profile = profile

        self._update_profile()

    def _highest_party_z_order(self):
        # Returns the highest z-order of party graphic items.
        return self._highest_item_z_order(list(self._party_items.values()))

    def _highest_sp_unit_z_order(self):
        # Returns the highest z-order of spatial unit graphic items.
        return self._highest_item_z_order(list(self._sp_unit_items.values()))

    def _highest_item_z_order(self, items):
        # Get the highest z-order of the graphic items in the list.
        z = 0
        for gi in items:
            if gi.zValue() > z:
                z = gi.zValue()

        return z

    def add_party_entity(self, party):
        """
        Adds a party entity to the view. If there is a existing one with the
        same name then it will be removed before adding this party.
        :param party: Party entity.
        :type party: Entity
        """
        if party.short_name in self._party_items:
            self.remove_party(party.short_name)

        # Remove previous if set in the policy
        if self.add_party_policy == ProfileTenureView.REMOVE_PREVIOUS:
            for p in self._party_items.keys():
                self.remove_party(p)

        # Hide default party placeholder
        self._default_party_item.hide()

        p_item = EntityItem()
        p_item.entity = party

        # Set z-order
        z = self._highest_party_z_order()
        if z == 0:
            z = 1.0
        else:
            z = z + 1.1
        p_item.setZValue(z)

        self.scene().addItem(p_item)

        if len(self._party_items) == 0:
            p_item.setPos(210, 20)
        else:
            self.auto_position(p_item)

        # Add to collection
        self._party_items[party.short_name] = p_item

        # Add connection arrow to social tenure item
        self.add_arrow(p_item, self._str_item)

    def add_spatial_unit_entity(self, spatial_unit):
        """
        Adds a spatial unit entity to the view. If there is a existing one
        with the same name then it will be removed before adding this spatial
        unit.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity.
        :type spatial_unit: Entity
        """
        if spatial_unit.short_name in self._sp_unit_items:
            self.remove_spatial_unit(spatial_unit.short_name)

        # Remove previous if specified in the policy
        if self.add_spatial_unit_policy == ProfileTenureView.REMOVE_PREVIOUS:
            for sp in self._sp_unit_items.keys():
                self.remove_spatial_unit(sp)

        # Hide default spatial unit placeholder
        self._default_sp_item.hide()

        sp_item = EntityItem()
        sp_item.entity = spatial_unit

        # Set z-order
        z = self._highest_sp_unit_z_order()
        if z == 0:
            z = 1.0
        else:
            z = z + 1.1
        sp_item.setZValue(z)

        self.scene().addItem(sp_item)

        if len(self._sp_unit_items) == 0:
            sp_item.setPos(590, 20)
        else:
            self.auto_position_spatial_unit(sp_item)

        # Add to collection
        self._sp_unit_items[spatial_unit.short_name] = sp_item

        # Add connection arrow to social tenure item
        self.add_arrow(self._str_item, sp_item)

    def auto_position(self, item):
        """
        Automatically positions the party item to prevent it from overlapping
        the others.
        :param item: Party entity item.
        :type item: EntityItem
        """
        item_count = len(self._party_items)

        # Just in case it is called externally
        if item_count == 0:
            return

        factor = item_count + 1
        dx, dy = 5 * factor, 10 * factor

        pos_x, pos_y = 205 + dx, 10 + dy
        item.setPos(pos_x, pos_y)

    def auto_position_spatial_unit(self, item):
        """
        Automatically positions the spatial unit item to prevent it from
        overlapping the others.
        .. versionadded:: 1.7
        :param item: Spatial unit entity item.
        :type item: EntityItem
        """
        item_count = len(self._sp_unit_items)

        # Just in case it is called externally
        if item_count == 0:
            return

        factor = item_count + 1
        dx, dy = 5 * factor, 10 * factor

        pos_x, pos_y = 585 + dx, 10 + dy
        item.setPos(pos_x, pos_y)

    def remove_party(self, name):
        """
        Removes the party with the specified name from the collection.
        :param name: Party name
        :type name: str
        :return: Returns True if the operation succeeded, otherwise False if
        the party with the specified name does not exist in the collection.
        :rtype: bool
        """
        if not name in self._party_items:
            return False

        p_item = self._party_items.pop(name)
        p_item.remove_arrows()
        self.scene().removeItem(p_item)

        del p_item

        # Show default party item
        if len(self._party_items) == 0:
            self._default_party_item.show()

        return True

    def remove_spatial_unit(self, name):
        """
        Removes the spatial unit graphics item with the specified name from
        the collection.
        .. versionadded:: 1.7
        :param name: Spatial unit name
        :type name: str
        :return: Returns True if the operation succeeded, otherwise False if
        the spatial unit item with the specified name does not exist in the
        collection.
        :rtype: bool
        """
        if not name in self._sp_unit_items:
            return False

        sp_item = self._sp_unit_items.pop(name)
        sp_item.remove_arrows()
        self.scene().removeItem(sp_item)

        del sp_item

        # Show default spatial unit item
        if len(self._sp_unit_items) == 0:
            self._default_sp_item.show()

        return True

    def invalidate_spatial_unit(self):
        """
        Clears the spatial unit entity.
        .. deprecated:: 1.7
        """
        pass

    def set_spatial_unit(self, spatial_unit):
        """
        Set the spatial unit entity.
        .. deprecated:: 1.7
        :param spatial_unit: Entity corresponding to a spatial unit in a
        profile's STR relationship.
        :type spatial_unit: Entity
        """
        pass

    def add_arrow(self, start_item, end_item, **kwargs):
        """
        Adds an arrow item running from the start to the end item.
        :param start_item: Start item for the arrow.
        :type start_item: BaseTenureItem
        :param end_item: End item for the arrow.
        :type end_item: BaseTenureItem
        :param kwargs: Optional arrow arguments such as angle, base width
        etc. See arguments for the Arrow class.
        :type kwargs: dict
        """
        arrow = Arrow(start_item, end_item, **kwargs)
        start_item.add_arrow(arrow)
        end_item.add_arrow(arrow)

        # Set z-value
        ref_z = end_item.zValue()
        if start_item.zValue() > end_item.zValue():
            ref_z = start_item.zValue()
        arrow.setZValue(ref_z + 1.0)
        self.scene().addItem(arrow)
        arrow.update_position()

    def keyPressEvent(self, event):
        """
        Capture delete key to remove selected annotation items.
        :param event: Key event.
        :type event: QKeyEvent
        """
        if event.key() == Qt.Key_Delete:
            self._delete_selected_annotation_items()

        super(ProfileTenureView, self).keyPressEvent(event)

    def deselect_items(self):
        """
        Deselects all graphic items in the scene.
        """
        for item in self.scene().selectedItems():
            item.setSelected(False)

    def _delete_selected_annotation_items(self):
        # Deletes selected annotation items in the scene
        for item in self.scene().selectedItems():
            if isinstance(item, Annotation):
                # Only remove if item is not on interactive text edit mode
                if item.textInteractionFlags() == Qt.NoTextInteraction:
                    self.scene().removeItem(item)
                    item.deleteLater()

    def save_image_to_file(self, path, resolution=96, background=Qt.white):
        """
        Saves the profile tenure view image to file using A4 paper size.
        :param path: Absolute path where the image will be saved.
        :type path: str
        :param resolution: Resolution in dpi. Default is 96.
        :type resolution: int
        :param background: Background color of the image:
        :type background: QColor
        :return: Returns True if the operation succeeded, otherwise False. If
        False then a corresponding message is returned as well.
        :rtype: (bool, str)
        """
        image = self.image(resolution, background)

        if image.isNull():
            msg = self.tr('Constructed image is null.')

            return False, msg

        # Test if file is writeable
        fl = QFile(path)
        if not fl.open(QIODevice.WriteOnly):
            msg = self.tr('The image file cannot be saved in the '
                          'specified location.')

            return False, msg

        # Attempt to save to file
        save_op = image.save(fl)

        if not save_op:
            msg = self.tr('Image operation failed.')

            return False, msg

        return True, ''

    def _resolution_in_mm(self, resolution):
        # Calculates the resolution in mm
        return resolution / 25.4

    def _resolution_in_m(self, resolution):
        # Calculates the resolution in mm
        return self._resolution_in_mm(resolution) * 1000

    def image_size(self, resolution):
        """
        Computes the image size from the given resolution in dpi.
        :param resolution: Resolution in dpi.
        :type resolution: int
        :return: Image size in pixels.
        :rtype: QSize
        """
        res = resolution / 25.4

        # A4 landscape size
        width = 297 * res
        height = 210 * res

        return QSize(int(width), int(height))

    def image(self, resolution, background=Qt.white):
        """
        Renders the view onto a QImage object.
        :param resolution: Resolution of the image in dpi.
        :type resolution: int
        :param background: Set background color of the image. Default is a
        white background.
        :type background: QColor
        :return: Returns a QImage object corresponding to the profile STR
        view.
        :rtype: QImage
        """
        # Ensure resolution is within limits
        if resolution < ProfileTenureView.MIN_DPI:
            resolution = ProfileTenureView.MIN_DPI
        if resolution > ProfileTenureView.MAX_DPI:
            resolution = ProfileTenureView.MAX_DPI

        # In metres
        dpm = self._resolution_in_m(resolution)

        image_size = self.image_size(resolution)

        img = QImage(
            image_size.width(),
            image_size.height(),
            QImage.Format_ARGB32
        )
        img.setDotsPerMeterX(int(dpm))
        img.setDotsPerMeterY(int(dpm))
        img.fill(background)

        # Deselect selected items
        self.deselect_items()

        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        self.scene().render(painter)
        painter.end()

        return img

    def valid(self):
        """
        :return: Returns False if the respective party and spatial unit
        entities have not been set. Otherwise True.
        :rtype: bool
        """
        if len(self._party_items) == 0:
            return False

        if len(self._sp_unit_items) == 0:
            return False

        return True

    def minimumSizeHint(self):
        return QSize(480, 270)

    def sizeHint(self):
        return QSize(560, 315)


class ProfileTenureDiagram(QWidget):
    """
    Widget for visualizing a profile's social tenure relationship definition.
    It provides controls for zooming, adding text and exporting the view to
    an image file, and wraps most of the ProfileTenureView functionality.
    """

    def __init__(self, parent=None, profile=None):
        super(ProfileTenureDiagram, self).__init__(parent)

        self._profile_view = ProfileTenureView(self, profile)
        self.set_scene_mode(ProfileTenureScene.MoveItem)
        self._profile_view.scene().annotation_inserted.connect(
            self.on_annotation_inserted
        )

        self._setup_widgets()
        self._current_zoom_factor = 1.0

        # Image export options
        self._path = ''
        self._resolution = 96
        self._bg_color = Qt.transparent

    def scene_mode(self):
        """
        :return: Returns the current state of the scene.
        :rtype: int
        """
        return self._profile_view.scene().mode

    def set_scene_mode(self, mode):
        """
        Sets the current state of the scene.
        :param mode: Scene mode i.e. move item, insert major or minor
        annotation.
        :type mode: int
        """
        if self.scene_mode() != mode:
            self._profile_view.scene().mode = mode

    def _setup_widgets(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(2, 4, 2, 9)

        self.minor_annotation = QToolButton(self)
        self.minor_annotation.setMaximumSize(QSize(24, 24))
        minor_icon = QIcon()
        minor_icon.addPixmap(
            GuiUtils.get_icon_pixmap('minor_annotation.png')
        )
        self.minor_annotation.setIcon(minor_icon)
        self.minor_annotation.setCheckable(True)
        self.minor_annotation.setToolTip(self.tr('Add Minor Annotation'))
        self.minor_annotation.toggled.connect(self.on_minor_annotation_toggled)
        self.layout.addWidget(self.minor_annotation, 0, 0, 1, 1)

        self.major_annotation = QToolButton(self)
        self.major_annotation.setMinimumSize(QSize(24, 24))
        major_icon = QIcon()
        major_icon.addPixmap(
            GuiUtils.get_icon_pixmap('major_annotation.png')
        )
        self.major_annotation.setIcon(major_icon)
        self.major_annotation.setCheckable(True)
        self.major_annotation.setToolTip(self.tr('Add Major Annotation'))
        self.major_annotation.toggled.connect(self.on_major_annotation_toggled)
        self.layout.addWidget(self.major_annotation, 0, 1, 1, 1)

        self.export_image = QToolButton(self)
        self.export_image.setMinimumSize(QSize(24, 24))
        export_image_icon = QIcon()
        export_image_icon.addPixmap(
            GuiUtils.get_icon_pixmap('save_image.png')
        )
        self.export_image.setIcon(export_image_icon)
        self.export_image.setToolTip(self.tr('Save Image...'))
        self.export_image.clicked.connect(self.on_image_export_settings)
        self.layout.addWidget(self.export_image, 0, 2, 1, 1)

        spacer_item = QSpacerItem(
            288,
            20,
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )
        self.layout.addItem(spacer_item, 0, 3, 1, 1)

        self.label = QLabel(self)
        self.label.setText(self.tr('Zoom'))
        self.layout.addWidget(self.label, 0, 4, 1, 1)

        self.zoom_cbo = QComboBox(self)
        self.zoom_cbo.addItem(self.tr('50%'), 50 / 100.0)
        self.zoom_cbo.addItem(self.tr('75%'), 75 / 100.0)
        self.zoom_cbo.addItem(self.tr('100%'), 100 / 100.0)
        self.zoom_cbo.addItem(self.tr('125%'), 125 / 100.0)
        self.zoom_cbo.addItem(self.tr('150%'), 150 / 100.0)
        self.zoom_cbo.setCurrentIndex(2)
        self.zoom_cbo.currentIndexChanged.connect(self.on_zoom_changed)
        self.layout.addWidget(self.zoom_cbo, 0, 5, 1, 1)

        self.layout.addWidget(self._profile_view, 1, 0, 1, 6)

    def minimumSizeHint(self):
        return QSize(500, 320)

    def sizeHint(self):
        return QSize(600, 360)

    def image_size(self, resolution):
        """
        Computes the image size based on the specified resolution.
        :param resolution: Resolution in dpi.
        :type resolution: int
        :return: Returns a QSize object containing the width and height of
        the image.
        :rtype: QSize
        """
        return self._profile_view.image_size(resolution)

    def on_image_export_settings(self):
        """
        Slot raised to show the dialog for image export settings.
        """
        img_export = ImageExportSettings(
            self,
            image_path=self._path,
            resolution=self._resolution,
            background=self._bg_color
        )

        if img_export.exec_() == QDialog.Accepted:
            self._path = img_export.path
            self._resolution = img_export.resolution
            self._bg_color = img_export.background_color

            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            # Attempt to save the image
            status, msg = self.save_image_to_file(
                self._path,
                self._resolution,
                self._bg_color
            )

            QApplication.restoreOverrideCursor()

            if status:
                QMessageBox.information(
                    self,
                    self.tr('Profile Tenure View'),
                    self.tr('Image successfully saved.')
                )
            else:
                QMessageBox.critical(
                    self,
                    self.tr('Profile Tenure View'),
                    msg
                )

    def on_major_annotation_toggled(self, state):
        """
        Slot raised when the major annotation tool button has been toggled.
        :param state: Button state
        :type state: bool
        """
        if not state and self.scene_mode() != ProfileTenureScene.MoveItem:
            self.set_scene_mode(ProfileTenureScene.MoveItem)

        if state:
            if self.minor_annotation.isChecked():
                self.minor_annotation.setChecked(False)
            self.set_scene_mode(ProfileTenureScene.InsertMajorAnnotation)

    def on_minor_annotation_toggled(self, state):
        """
        Slot raised when the minor annotation tool button has been toggled.
        :param state: Button state
        :type state: bool
        """
        if not state and self.scene_mode() != ProfileTenureScene.MoveItem:
            self.set_scene_mode(ProfileTenureScene.MoveItem)

        if state:
            if self.major_annotation.isChecked():
                self.major_annotation.setChecked(False)
            self.set_scene_mode(ProfileTenureScene.InsertMinorAnnotation)

    def on_annotation_inserted(self, item):
        """
        Slot raised when an annotation item has been inserted. It unchecks
        the correct tool button based on the annotation type.
        :param item: Annotation item.
        :type item: Annotation
        """
        if not isinstance(item, Annotation):
            return

        anno_type = item.size
        if anno_type == Annotation.Minor:
            self.minor_annotation.setChecked(False)
        elif anno_type == Annotation.Major:
            self.major_annotation.setChecked(False)

    def on_zoom_changed(self, idx):
        """
        Slot raised when the zoom level changes to change the scale of the
        view.
        :param idx: Item index for the combo.
        :type idx: int
        """
        if idx == -1:
            return

        factor = self.zoom_cbo.itemData(idx)

        # Compute relative scale
        scale = factor / self._current_zoom_factor
        self.scale(scale)
        self._current_zoom_factor = factor

    def scale(self, factor):
        """
        Scales the view by the given scale factor.
        :param factor: Scale factor
        :type factor: float
        """
        if factor <= 0:
            return

        self._profile_view.scale(factor, factor)

    def valid(self):
        """
        :return: Returns False if the respective party and spatial unit
        entities have not been set. Otherwise True.
        :rtype: bool
        """
        return self._profile_view.valid()

    def save_image_to_file(self, path, resolution, background=Qt.white):
        """
        Saves the profile tenure view image to file using A4 paper size.
        :param path: Absolute path where the image will be saved.
        :type path: str
        :param resolution: Resolution in dpi. Default is 96.
        :type resolution: int
        :param background: Background color of the image.
        :type background: QColor
        :return: Returns True if the operation succeeded, otherwise False. If
        False then a corresponding message is returned as well.
        :rtype: (bool, str)
        """
        return self._profile_view.save_image_to_file(
            path,
            resolution,
            background
        )

    def set_spatial_unit(self, spatial_unit):
        """
        Set the spatial unit entity.
        .. deprecated:: 1.7
        :param spatial_unit: Entity corresponding to a spatial unit in a
        profile's STR relationship.
        :type spatial_unit: Entity
        """
        self._profile_view.set_spatial_unit(spatial_unit)

    def invalidate_spatial_unit(self):
        """
        Clears the spatial unit entity.
        .. deprecated:: 1.7
        """
        self._profile_view.invalidate_spatial_unit()

    def add_parties(self, parties):
        """
        Add party items to the view.
        :param parties: List of party entities.
        :type parties: list
        """
        for p in parties:
            self.add_party_entity(p)

    def add_party_entity(self, party):
        """
        Adds a party entity to the view. If there is a existing one with the
        same name then it will be removed before adding this party.
        :param party: Party entity.
        :type party: Entity
        """
        self._profile_view.add_party_entity(party)

    def add_spatial_units(self, spatial_units):
        """
        Add spatial unit items to the view.
        .. versionadded:: 1.7
        :param spatial_units: List of spatial unit entities.
        :type spatial_units: list
        """
        for sp in spatial_units:
            self.add_spatial_unit_entity(sp)

    def add_spatial_unit_entity(self, spatial_unit):
        """
        Adds a spatial unit entity to the view. If there is a existing one
        with the same name then it will be removed before adding this
        spatial unit.
        .. versionadded:: 1.7
        :param spatial_unit: Spatial unit entity.
        :type spatial_unit: Entity
        """
        self._profile_view.add_spatial_unit_entity(spatial_unit)

    def remove_party(self, name):
        """
        Removes the party with the specified name from the collection.
        :param name: Party name
        :return: Returns True if the operation succeeded, otherwise False if
        the party with the specified name does not exist in the collection.
        :rtype: bool
        """
        return self._profile_view.remove_party(name)

    def remove_spatial_unit(self, name):
        """
        Removes the spatial unit with the specified name from the collection.
        .. versionadded:: 1.7
        :param name: Spatial unit name.
        :return: Returns True if the operation succeeded, otherwise False if
        the spatial unit with the specified name does not exist in the
        collection.
        :rtype: bool
        """
        return self._profile_view.remove_spatial_unit(name)

    @property
    def profile(self):
        """
        :return: The profile object being rendered.
        :rtype: Profile
        """
        return self._profile_view.profile

    @profile.setter
    def profile(self, profile):
        """
        Sets the profile object whose STR view is to rendered.
        :param profile: Profile object to be rendered.
        :type profile: Profile
        """
        self._profile_view.profile = profile
