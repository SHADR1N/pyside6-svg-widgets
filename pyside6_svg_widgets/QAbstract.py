import re
from functools import partial
from typing import Optional

from PySide6.QtWidgets import (
    QPushButton, QWidget,
    QLabel, QHBoxLayout, QStyle, QStyleOption,
    QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QPixmap, QPainter, QIcon
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QTimer, QSize, Signal


def get_effective_style(widget: QWidget, hover=False, pressed=False, _filter="icon-color") -> str:
    """Get the effective style of a widget, considering parent styles."""
    object_name = widget.objectName()
    current_widget = widget

    while current_widget:
        style_sheet = current_widget.styleSheet()
        if style_sheet:
            # Splitting the style sheet by '}' to get individual style blocks
            style_blocks = style_sheet.split('}')
            for block in style_blocks:
                # Check if this block contains the style for the specific widget\
                if not any([hover, pressed]) and block.strip().startswith(f'#{object_name}'):
                    style_rules = block.split('{')[-1].strip()

                elif hover and block.strip().startswith(f'#{object_name}:hover'):
                    style_rules = block.split('{')[-1].strip()

                elif pressed and block.strip().startswith(f'#{object_name}:pressed'):
                    style_rules = block.split('{')[-1].strip()

                else:
                    continue

                style_string = "\n".join(
                    [i.strip() for i in style_rules.split("\n") if i.strip().startswith(_filter)])
                if style_string:
                    pattern = _filter + r":\s*([^;]+);"
                    matches = re.findall(pattern, style_string)
                    return matches[0] if matches else None

        # Move to the parent widget
        current_widget = current_widget.parentWidget()

    return None


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

        effective_style = get_effective_style(self, hover=True)
        self.updateIcon(effective_style, hover)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.minus_svg:
            self.right.setIcon(self.right_svg)

        effective_style = get_effective_style(self)
        self.updateIcon(effective_style, self.state_release)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        hover = False
        if self.minus_svg:
            hover = True
            self.right.setIcon(self.minus_svg)

        effective_style = get_effective_style(self, pressed=True)
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

            effective_style = get_effective_style(self, hover=True)
        else:
            effective_style = get_effective_style(self, hover=False)

        self.updateIcon(effective_style, hover)
        if event:
            super().mouseReleaseEvent(event)


class QIconSvg(QLabel):
    def __init__(self, svg_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.svg_path = svg_path
        self.size = (20, 20)
        self.disable = False
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
            effective_style = get_effective_style(self, hover=True)
            self.updateIcon(effective_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self.disable:
            effective_style = get_effective_style(self)
            self.updateIcon(effective_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self.disable:
            effective_style = get_effective_style(self, pressed=True)
            self.updateIcon(effective_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.underMouse():
            effective_style = get_effective_style(self, hover=True)
        else:
            effective_style = get_effective_style(self)

        if not self.disable:
            self.updateIcon(effective_style)
        super().mouseReleaseEvent(event)


class QCustomAbstractButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.svg_path = None

    def setSvg(self, icon):
        self.svg_path = icon
        QTimer.singleShot(100, partial(self.leaveEvent, None))

    def updateIcon(self, color):
        if not color:
            return

        # Render SVG with the specified color
        renderer = QSvgRenderer(self.svg_path)
        pixmap = QPixmap(100, 100)  # Set desired icon size
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        self.setIcon(QIcon(pixmap))

    def enterEvent(self, event):
        effective_style = get_effective_style(self, hover=True)
        self.updateIcon(effective_style)
        super().enterEvent(event)

    def leaveEvent(self, event):
        effective_style = get_effective_style(self)
        self.updateIcon(effective_style)
        self.updateIcon(effective_style)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        effective_style = get_effective_style(self, pressed=True)
        self.updateIcon(effective_style)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        effective_style = get_effective_style(self)
        self.updateIcon(effective_style)
        super().mouseReleaseEvent(event)