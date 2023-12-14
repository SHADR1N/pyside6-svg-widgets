import re
from functools import partial
from typing import Optional

from functools import lru_cache

from PySide6.QtWidgets import (
    QPushButton, QWidget,
    QLabel, QHBoxLayout, QStyle, QStyleOption,
    QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QTimer, QSize, Signal


@lru_cache()
def get_color(init_widget, style_sheet, hover=False, pressed=False, style_filter="icon-color", string_widget=None):
    if string_widget:
        object_name = string_widget
    else:
        object_name = init_widget.objectName()

    style_blocks = style_sheet.split('}')
    for block in style_blocks:

        if not object_name:
            continue

        if not any([hover, pressed]) and object_name in block.strip():
            style_rules = block.split('{')[-1].strip()

        elif hover and f'{object_name}:hover' in block.strip():
            style_rules = block.split('{')[-1].strip()

        elif pressed and f'{object_name}:pressed' in block.strip():
            style_rules = block.split('{')[-1].strip()

        else:
            continue

        style_string = "\n".join(
            [i.strip() for i in style_rules.split("\n") if i.strip().startswith(style_filter)])

        if style_string:
            pattern = style_filter + r":\s*([^;]+);"
            matches = re.findall(pattern, style_string)
            _match = matches[0] if matches else None
            return _match, style_sheet

    if string_widget:
        return None, None
    else:
        return get_color(init_widget=init_widget, style_sheet=style_sheet, hover=hover, pressed=pressed,
                         style_filter=style_filter,
                         string_widget=type(init_widget).__name__)


def get_effective_style(init_widget: QWidget, hover=False, pressed=False, style_filter="icon-color",
                        string_widget=None):
    """Get the effective style of a widget, considering parent styles."""

    if string_widget:
        object_name = string_widget
    else:
        object_name = init_widget.objectName()

    current_widget = init_widget
    while current_widget:
        style_sheet = current_widget.styleSheet()
        if style_sheet and object_name in style_sheet:
            x, y = get_color(init_widget, style_sheet, hover, pressed, style_filter)
            if x and y:
                return x, y

        # Move to the parent widget
        current_widget = current_widget.parentWidget()

    if string_widget:
        return None, None
    else:
        return get_effective_style(init_widget=init_widget, hover=hover, pressed=pressed, style_filter=style_filter,
                                   string_widget=type(init_widget).__name__)


class QDropButton(QWidget):
    changeState = Signal(bool)
    clicked = Signal()

    def __init__(
            self,
            text: str,
            left_svg: str,
            right_svg: str,
            minus_svg: Optional[str] = None,
            only_click: bool = False,
            save_state: bool = False,
            text_alignment: Optional[str] = "left",
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.text = text
        self.left_svg = left_svg
        self.right_svg = right_svg
        self.minus_svg = minus_svg
        self.only_click = only_click
        self.save_state = save_state
        self.text_alignment = text_alignment
        self.stylecode = None

        if not self.minus_svg:
            self.save_state = False

        if self.save_state:
            self.only_click = True

        self.state_release = False
        self.size = (20, 20)
        self.initWidget()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)

        style = self.style()
        style.drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)

    def setIconSize(self, width: int, height: int):
        self.size = (width, height)
        self.right.setIconSize(*self.size)
        self.left.setIconSize(*self.size)

    def initWidget(self):
        """Initialize the widget."""
        layout = QHBoxLayout()
        layout.setSpacing(0)

        self.left = self.createButton(self.left_svg)
        self.label = self.createLabel(self.text)
        self.right = self.createButton(self.right_svg)

        layout.addWidget(self.left, alignment=Qt.AlignmentFlag.AlignLeft)
        if self.text_alignment == "right":
            layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)
        if self.text_alignment == "left":
            layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addWidget(self.right, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.setStyleSheet("QLabel {background: transparent;}")
        QTimer.singleShot(100, partial(self.leaveEvent, None))

    def createButton(self, svg_path):
        """Create and return a button with an icon."""
        button = QIconSvg(svg_path)
        button.setObjectName(self.objectName())
        button.setDisabledAnim(True)
        button.setIconSize(*self.size)
        return button

    def createLabel(self, text):
        """Create and return a label."""
        label = QLabel(text)
        return label

    def updateIcon(self, color, hover=False):
        """Update the color of the icons."""
        if not color:
            return

        svgs = [self.left_svg, self.right_svg if not hover and not self.state_release else self.minus_svg]
        for svg, button in zip(svgs, [self.left, self.right]):
            pixmap = self.generateColoredPixmap(svg, color)
            button.setPixmap(pixmap)

    def generateColoredPixmap(self, svg_path, color):
        """Generate a colored pixmap from an SVG."""
        renderer = QSvgRenderer(svg_path)
        pixmap = QPixmap(*self.size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        self.label.setStyleSheet("* {color: {COLOR};}".replace("{COLOR}", color))
        return pixmap

    def setPixmap(self, icon, pixmap):
        icon.setPixmap(pixmap)

    def enterEvent(self, event):
        hover = False
        if (self.minus_svg and not self.only_click):
            hover = True
            self.right.setIcon(self.minus_svg)

        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self, hover=True)
        else:
            effective_style, _ = get_color(self, self.stylecode, hover=True)
        self.updateIcon(effective_style, hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.minus_svg:
            self.right.setIcon(self.right_svg)

        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self)
        else:
            effective_style, _ = get_color(self, self.stylecode)
        self.updateIcon(effective_style, self.state_release)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        hover = False
        if self.minus_svg:
            hover = True
            self.right.setIcon(self.minus_svg)

        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self, pressed=True)
        else:
            effective_style, _ = get_color(self, self.stylecode, pressed=True)
        self.updateIcon(effective_style, hover)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event=None):
        self.clicked.emit()
        hover = False
        if self.save_state:
            self.state_release = not self.state_release
            self.changeState.emit(self.state_release)

        if self.underMouse():
            """ If cursor on  widget """
            if (self.minus_svg and not self.only_click) or self.state_release:
                """ If widget have open svg and not active only_click """
                hover = True
                self.right.setIcon(self.minus_svg)

            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, hover=True)
            else:
                effective_style, _ = get_color(self, self.stylecode, hover=True)
        else:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, hover=False)
            else:
                effective_style, _ = get_color(self, self.stylecode, hover=True)

        self.updateIcon(effective_style, hover)
        if event:
            super().mouseReleaseEvent(event)


class QIconSvg(QLabel):
    clicked = Signal()

    def __init__(self, svg_path: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.svg_path = svg_path
        self.size = (20, 20)
        self.disable = False
        self.stylecode = None
        if self.svg_path:
            self.setIcon(self.svg_path)

    def setDisabledAnim(self, disable: bool):
        self.disable = disable

    def setIconSize(self, width: int, height: int):
        self.size = (width, height)
        self.leaveEvent(None)

    def setIcon(self, icon):
        self.svg_path = icon
        self.icon = QIcon(self.svg_path)
        self.setPixmap(self.icon.pixmap(QSize(*self.size)))
        QTimer.singleShot(100, partial(self.leaveEvent, None))

    def updateIcon(self, color):
        if not color or not self.svg_path:
            return

        # Render SVG with the specified color
        renderer = QSvgRenderer(self.svg_path)
        pixmap = QPixmap(*self.size)  # Set desired icon size
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        self.setPixmap(pixmap)

    def enterEvent(self, event):
        if not self.disable:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, hover=True)
            else:
                effective_style, _ = get_color(self, self.stylecode, hover=True)
            self.updateIcon(effective_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.disable:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self)
            else:
                effective_style, _ = get_color(self, self.stylecode)
            self.updateIcon(effective_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self.disable:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, pressed=True)
            else:
                effective_style, _ = get_color(self, self.stylecode, pressed=True)
            self.updateIcon(effective_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, hover=True)
            else:
                effective_style, _ = get_color(self, self.stylecode, hover=True)
        else:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self)
            else:
                effective_style, _ = get_color(self, self.stylecode)

        if not self.disable:
            self.updateIcon(effective_style)

        self.clicked.emit()
        super().mouseReleaseEvent(event)


class QSvgButton(QPushButton):
    def __init__(self, svg_path: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = (20, 20)
        self.svg_path = svg_path
        self.stylecode = None
        if self.svg_path:
            self.setSvg(self.svg_path)

    def setSvgSize(self, width: int, height: int):
        self.size = (width, height)
        self.leaveEvent(None)

    def setSvg(self, icon):
        self.svg_path = icon
        QTimer.singleShot(100, partial(self.leaveEvent, None))

    def updateIcon(self, color):
        if not color or not self.svg_path:
            return

        # Render SVG with the specified color
        renderer = QSvgRenderer(self.svg_path)
        pixmap = QPixmap(*self.size)  # Set desired icon size
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        self.setIcon(QIcon(pixmap))

    def enterEvent(self, event):
        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self, hover=True)
        else:
            effective_style, _ = get_color(self, self.stylecode, hover=True)
        self.updateIcon(effective_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self)
        else:
            effective_style, _ = get_color(self, self.stylecode)
        self.updateIcon(effective_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self.stylecode:
            effective_style, self.stylecode = get_effective_style(self, pressed=True)
        else:
            effective_style, _ = get_color(self, self.stylecode, pressed=True)
        self.updateIcon(effective_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self, hover=True)
            else:
                effective_style, _ = get_color(self, self.stylecode, hover=True)
        else:
            if not self.stylecode:
                effective_style, self.stylecode = get_effective_style(self)
            else:
                effective_style, _ = get_color(self, self.stylecode)

        self.updateIcon(effective_style)
        super().mouseReleaseEvent(event)
