from functools import lru_cache
from functools import lru_cache
from typing import Optional, Union, Dict

from PyQt5.QtCore import Qt, QSize, QEvent, pyqtProperty, QRect, pyqtSignal, QPropertyAnimation, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor, QPalette, QImage, QFont, QBrush, QPen
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QPushButton, QWidget, QLabel, QStyle, QStyleOption,
    QRadioButton, QToolButton, QStyleOptionButton, QSizePolicy, QFrame, QStyleOptionFrame, QStyleOptionToolButton, QHBoxLayout, QAbstractButton
)

# Константы
DEFAULT_SIZE = 25
SCALE_FACTOR = 10

class StyleManager:
    """Менеджер стилей для обработки и кэширования стилей виджетов"""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def parse_style_sheet(style_sheet: str) -> Dict[str, Dict[str, str]]:
        """Парсит таблицу стилей и возвращает словарь с правилами"""
        if not style_sheet:
            return {}
            
        result = {}
        blocks = style_sheet.split('}')
        
        for block in blocks:
            if not block.strip():
                continue

            selector, rules = block.split('{', 1)
            selector = selector.strip()
            rules = rules.strip()
            
            if selector not in result:
                result[selector] = {}
                
            for rule in rules.split(';'):
                if ':' in rule:
                    prop, value = rule.split(':', 1)
                    result[selector][prop.strip()] = value.strip()
                    
        return result

    @staticmethod
    def get_effective_style(widget: QWidget, state: str = '') -> Dict[str, str]:
        """Получает эффективные стили для виджета с учетом родительских стилей"""
        styles = {}
        current = widget
        
        while current:
            if not current.styleSheet():
                current = current.parentWidget()
            continue

            parsed = StyleManager.parse_style_sheet(current.styleSheet())
            widget_name = type(widget).__name__
            
            # Проверяем специфичные состояния
            if state:
                state_selector = f"{widget_name}:{state}"
                if state_selector in parsed:
                    styles.update(parsed[state_selector])
                    
            # Базовые стили
            if widget_name in parsed:
                styles.update(parsed[widget_name])
                
            current = current.parentWidget()
            
        return styles

class SvgRenderer:
    """Класс для рендеринга SVG с кэшированием"""
    def __init__(self, svg_path: str):
        self._renderer = QSvgRenderer(svg_path)
        self._cache = {}
        
    def render(self, size: QSize, color: QColor) -> QPixmap:
        """Рендерит SVG с заданным размером и цветом"""
        key = (size.width(), size.height(), color.name())
        if key in self._cache:
            return self._cache[key]
            
        image = QImage(size, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Рендерим SVG
        self._renderer.render(painter)
        painter.end()
        
        # Применяем цвет
        if color != Qt.black:
            image = self._apply_color(image, color)
            
        pixmap = QPixmap.fromImage(image)
        self._cache[key] = pixmap
        return pixmap
        
    def _apply_color(self, image: QImage, color: QColor) -> QImage:
        """Применяет цвет к изображению"""
        for x in range(image.width()):
            for y in range(image.height()):
                pixel = image.pixelColor(x, y)
                if pixel.alpha() > 0:
                    pixel.setRed(color.red())
                    pixel.setGreen(color.green())
                    pixel.setBlue(color.blue())
                    image.setPixelColor(x, y, pixel)
        return image

class SvgWidget(QWidget):
    """Базовый класс для SVG виджетов"""
    def __init__(self, svg_path: str, parent=None):
        super().__init__(parent)
        self._renderer = SvgRenderer(svg_path)
        self._size = QSize(24, 24)
        self._color = QColor(Qt.black)
        self._is_hovered = False
        self._is_pressed = False
        self._text = ""
        self._text_color = QColor(Qt.black)
        self._font = QFont()
        
        self.setAttribute(Qt.WA_Hover)
        self.setMouseTracking(True)
        self.setFixedSize(self._size)
        
    def setSvg(self, svg_path: str):
        """Устанавливает новый SVG файл"""
        self._renderer = SvgRenderer(svg_path)
        self.update()
        
    def setIconSize(self, size: QSize):
        """Устанавливает размер иконки"""
        self._size = size
        self.setFixedSize(size)
        self.update()
        
    def setText(self, text: str):
        """Устанавливает текст"""
        self._text = text
        self.update()
        
    def setTextColor(self, color: QColor):
        """Устанавливает цвет текста"""
        self._text_color = color
        self.update()
        
    def setFont(self, font: QFont):
        """Устанавливает шрифт"""
        self._font = font
        self.update()
        
    def _getColor(self) -> QColor:
        """Получает текущий цвет с учетом состояния"""
        if self._is_pressed:
            return self.palette().color(QPalette.ButtonText)
        elif self._is_hovered:
            return self.palette().color(QPalette.Highlight)
        return self.palette().color(QPalette.WindowText)
        
    def paintEvent(self, event):
        """Отрисовка виджета"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Рисуем фон
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        
        # Рисуем SVG
        pixmap = self._renderer.render(self._size, self._getColor())
        painter.drawPixmap(0, 0, pixmap)
        
        # Рисуем текст
        if self._text:
            painter.setPen(self._text_color)
            painter.setFont(self._font)
            text_rect = QRect(self._size.width() + 5, 0, 
                            self.width() - self._size.width() - 5, 
                            self.height())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self._text)
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)
        
    def event(self, event):
        if event.type() == QEvent.StyleChange:
            self.update()
        return super().event(event)

class SvgButton(QPushButton):
    """Кнопка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(text, parent)
        self._renderer = SvgRenderer(svg_path)
        self._icon_size = QSize(24, 24)
        self._is_hovered = False
        self._is_pressed = False
        
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    def setIconSize(self, size: QSize):
        self._icon_size = size
        self.updateGeometry()
        self.update()
        
    def sizeHint(self) -> QSize:
        """Возвращает рекомендуемый размер виджета"""
        # Получаем размер текста
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        
        # Получаем отступы из стиля
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.text = self.text()
        opt.iconSize = self._icon_size
        opt.features = QStyleOptionButton.ButtonFeatures()
        
        # Получаем отступы из стиля
        margins = self.style().pixelMetric(QStyle.PM_ButtonMargin, opt, self)
        padding = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self) * 2
        
        # Вычисляем общую ширину
        width = self._icon_size.width() + text_width + margins * 2 + padding * 2
        if text_width > 0:
            width += 10  # Дополнительный отступ между иконкой и текстом
            
        # Вычисляем высоту
        height = max(self._icon_size.height(), fm.height()) + margins * 2 + padding * 2
        
        return QSize(width, height)
        
    def minimumSizeHint(self) -> QSize:
        """Возвращает минимальный размер виджета"""
        return self.sizeHint()
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)
        
    def _getColor(self) -> QColor:
        """Получает текущий цвет с учетом состояния"""
        if self._is_pressed:
            return self.palette().color(QPalette.ButtonText)
        elif self._is_hovered:
            return self.palette().color(QPalette.Highlight)
        return self.palette().color(QPalette.WindowText)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Рисуем фон
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.text = ""  # Убираем текст из опций, так как будем рисовать его сами
        opt.iconSize = self._icon_size
        opt.features = QStyleOptionButton.ButtonFeatures()
        if self.isDown():
            opt.state |= QStyle.State_Sunken
        if self.isChecked():
            opt.state |= QStyle.State_On
        if self._is_hovered:
            opt.state |= QStyle.State_MouseOver
            
        self.style().drawControl(QStyle.CE_PushButton, opt, painter, self)
        
        # Получаем отступы из стиля
        margins = self.style().pixelMetric(QStyle.PM_ButtonMargin, opt, self)
        padding = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self)
        
        # Рисуем SVG
        pixmap = self._renderer.render(self._icon_size, self._getColor())
        icon_rect = QRect(margins + padding, 
                         (self.height() - self._icon_size.height()) // 2,
                         self._icon_size.width(), 
                         self._icon_size.height())
        painter.drawPixmap(icon_rect, pixmap)
        
        # Рисуем текст
        if self.text():
            text_rect = QRect(icon_rect.right() + 10, 0,
                            self.width() - icon_rect.right() - margins - padding,
                            self.height())
            painter.setPen(self._getColor())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

class SvgLabel(QLabel):
    """Метка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(text, parent)
        self._renderer = SvgRenderer(svg_path)
        self._icon_size = QSize(24, 24)
        self._is_hovered = False
        
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    def setIconSize(self, size: QSize):
        self._icon_size = size
        self.updateGeometry()
        self.update()
        
    def sizeHint(self) -> QSize:
        """Возвращает рекомендуемый размер виджета"""
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        
        opt = QStyleOption()
        opt.initFrom(self)
        margins = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self) * 2
        
        width = self._icon_size.width() + text_width + margins * 2
        if text_width > 0:
            width += 10
            
        height = max(self._icon_size.height(), fm.height()) + margins * 2
        
        return QSize(width, height)
        
    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def _getColor(self) -> QColor:
        if self._is_hovered:
            return self.palette().color(QPalette.Highlight)
        return self.palette().color(QPalette.WindowText)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        opt = QStyleOptionFrame()
        opt.initFrom(self)
        opt.frameShape = QFrame.StyledPanel
        opt.lineWidth = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self)
        opt.midLineWidth = 0
        opt.state |= QStyle.State_Sunken
        
        self.style().drawPrimitive(QStyle.PE_Frame, opt, painter, self)
        
        margins = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self)
        
        # Рисуем SVG
        pixmap = self._renderer.render(self._icon_size, self._getColor())
        icon_rect = QRect(margins, 
                         (self.height() - self._icon_size.height()) // 2,
                         self._icon_size.width(), 
                         self._icon_size.height())
        painter.drawPixmap(icon_rect, pixmap)
        
        # Рисуем текст
        if self.text():
            text_rect = QRect(icon_rect.right() + 10, 0,
                            self.width() - icon_rect.right() - margins,
                            self.height())
            painter.setPen(self._getColor())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

class SvgRadioButton(QRadioButton):
    """Радио-кнопка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(text, parent)
        self._renderer = SvgRenderer(svg_path)
        self._icon_size = QSize(24, 24)
        self._is_hovered = False
        
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    def setIconSize(self, size: QSize):
        self._icon_size = size
        self.updateGeometry()
        self.update()
        
    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.text = ""
        opt.iconSize = self._icon_size
        
        indicator_width = self.style().pixelMetric(QStyle.PM_ExclusiveIndicatorWidth, opt, self)
        indicator_height = self.style().pixelMetric(QStyle.PM_ExclusiveIndicatorHeight, opt, self)
        spacing = self.style().pixelMetric(QStyle.PM_RadioButtonLabelSpacing, opt, self)
        
        width = indicator_width + spacing + self._icon_size.width() + text_width
        if text_width > 0:
            width += 10
            
        height = max(indicator_height, self._icon_size.height(), fm.height())
        
        return QSize(width, height)
        
    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def _getColor(self) -> QColor:
        if self._is_hovered:
            return self.palette().color(QPalette.Highlight)
        return self.palette().color(QPalette.WindowText)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        opt = QStyleOptionButton()
        opt.initFrom(self)
        opt.text = ""
        opt.iconSize = self._icon_size
        if self.isChecked():
            opt.state |= QStyle.State_On
        if self._is_hovered:
            opt.state |= QStyle.State_MouseOver
            
        # Рисуем индикатор
        indicator_rect = self.style().subElementRect(QStyle.SE_RadioButtonIndicator, opt, self)
        self.style().drawPrimitive(QStyle.PE_IndicatorRadioButton, opt, painter, self)
        
        # Рисуем SVG
        pixmap = self._renderer.render(self._icon_size, self._getColor())
        icon_rect = QRect(indicator_rect.right() + 5,
                         (self.height() - self._icon_size.height()) // 2,
                         self._icon_size.width(),
                         self._icon_size.height())
        painter.drawPixmap(icon_rect, pixmap)
        
        # Рисуем текст
        if self.text():
            text_rect = QRect(icon_rect.right() + 10, 0,
                            self.width() - icon_rect.right() - 5,
                            self.height())
            painter.setPen(self._getColor())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

class SvgToolButton(QToolButton):
    """Инструментальная кнопка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(parent)
        self._renderer = SvgRenderer(svg_path)
        self._icon_size = QSize(24, 24)
        self._is_hovered = False
        self._is_pressed = False
        
        self.setText(text)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
    def setIconSize(self, size: QSize):
        self._icon_size = size
        self.updateGeometry()
        self.update()
        
    def sizeHint(self) -> QSize:
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        
        opt = QStyleOptionToolButton()
        opt.initFrom(self)
        opt.text = self.text()
        opt.iconSize = self._icon_size
        opt.toolButtonStyle = Qt.ToolButtonTextBesideIcon
        
        margins = self.style().pixelMetric(QStyle.PM_ButtonMargin, opt, self)
        padding = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self) * 2
        
        width = self._icon_size.width() + text_width + margins * 2 + padding * 2
        if text_width > 0:
            width += 10
            
        height = max(self._icon_size.height(), fm.height()) + margins * 2 + padding * 2
        
        return QSize(width, height)
        
    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self._is_pressed = True
        self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._is_pressed = False
        self.update()
        super().mouseReleaseEvent(event)
        
    def _getColor(self) -> QColor:
        if self._is_pressed:
            return self.palette().color(QPalette.ButtonText)
        elif self._is_hovered:
            return self.palette().color(QPalette.Highlight)
        return self.palette().color(QPalette.WindowText)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        opt = QStyleOptionToolButton()
        opt.initFrom(self)
        opt.text = ""
        opt.iconSize = self._icon_size
        opt.toolButtonStyle = Qt.ToolButtonTextBesideIcon
        if self.isDown():
            opt.state |= QStyle.State_Sunken
        if self.isChecked():
            opt.state |= QStyle.State_On
        if self._is_hovered:
            opt.state |= QStyle.State_MouseOver
            
        self.style().drawComplexControl(QStyle.CC_ToolButton, opt, painter, self)
        
        margins = self.style().pixelMetric(QStyle.PM_ButtonMargin, opt, self)
        padding = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth, opt, self)
        
        # Рисуем SVG
        pixmap = self._renderer.render(self._icon_size, self._getColor())
        icon_rect = QRect(margins + padding,
                         (self.height() - self._icon_size.height()) // 2,
                         self._icon_size.width(),
                         self._icon_size.height())
        painter.drawPixmap(icon_rect, pixmap)
        
        # Рисуем текст
        if self.text():
            text_rect = QRect(icon_rect.right() + 10, 0,
                            self.width() - icon_rect.right() - margins - padding,
                            self.height())
            painter.setPen(self._getColor())
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())

class ToggleSwitchButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(36)
        self.setStyleSheet(self._get_style(False))

    def setChecked(self, checked):
        super().setChecked(checked)
        self.setStyleSheet(self._get_style(checked))

    def _get_style(self, checked):
        if checked:
            return """
                QPushButton {
                    background-color: #22c55e;
                    color: #fff;
                    border-radius: 18px;
                    font-weight: bold;
                    padding: 0 24px;
                    border: none;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #e5e7eb;
                    color: #444;
                    border-radius: 18px;
                    font-weight: normal;
                    padding: 0 24px;
                    border: none;
                }
            """

class ToggleSwitchGroup(QWidget):
    toggled = pyqtSignal(int, str)  # индекс, текст

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._buttons = []
        self._current = 0
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        for i, text in enumerate(options):
            btn = ToggleSwitchButton(text)
            btn.clicked.connect(lambda checked, idx=i: self.setChecked(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)
        if self._buttons:
            self._buttons[0].setChecked(True)

    def setChecked(self, idx):
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == idx)
        self._current = idx
        self.toggled.emit(idx, self._buttons[idx].text())

    def currentIndex(self):
        return self._current

    def currentText(self):
        return self._buttons[self._current].text()

class SwitchButton(QAbstractButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._offset = 1.0 if self.isChecked() else 0.0
        self.setCheckable(True)
        self.setMinimumSize(64, 36)
        self._animation = QPropertyAnimation(self, b"offset", self)
        self._icon_size = 20
        self._duration = 180
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty('checked', self.isChecked())
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked):
        self.setProperty('checked', checked)
        self.style().unpolish(self)
        self.style().polish(self)
        self._start_anim(checked)

    def _start_anim(self, checked):
        self._animation.stop()
        start = self._offset
        end = 1.0 if checked else 0.0
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.setDuration(self._duration)
        self._animation.start()

    def _get_offset(self):
        return getattr(self, "_offset", 0.0)

    def _set_offset(self, value):
        self._offset = value
        self.update()

    offset = pyqtProperty(float, _get_offset, _set_offset)

    def sizeHint(self):
        return QSize(64, 36)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 4
        radius = h / 2
        # Получаем цвета из стиля
        bg_color = self._getStyleColor('background', '#16e085' if self.isChecked() else '#39394a')
        thumb_color = self._getStyleColor('thumb', '#e5e7eb')
        check_color = self._getStyleColor('check', '#fff')
        cross_color = self._getStyleColor('cross', '#fff')
        # Фон
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, w, h), radius, radius)
        # Кружок
        x = margin + (w - 2 * margin - h + 2 * margin) * self._offset
        thumb_rect = QRectF(x, margin, h - 2 * margin, h - 2 * margin)
        painter.setBrush(QBrush(thumb_color))
        painter.drawEllipse(thumb_rect)
        # Иконки внутри кружка
        icon_rect = thumb_rect.adjusted(4, 4, -4, -4)
        # Крестик (затухает вправо)
        painter.save()
        painter.setOpacity(1.0 - self._offset)
        self._draw_cross(painter, icon_rect, cross_color)
        painter.restore()
        # Галочка (появляется справа)
        painter.save()
        painter.setOpacity(self._offset)
        self._draw_check(painter, icon_rect, check_color)
        painter.restore()

    def _getStyleColor(self, role, default):
        # role: 'background', 'thumb', 'check', 'cross'
        # Чтение из palette или property
        if role == 'background':
            if self.property('checked'):
                return self.palette().color(QPalette.Highlight)
            else:
                return self.palette().color(QPalette.Mid)
        elif role == 'thumb':
            return self.palette().color(QPalette.Base)
        elif role == 'check':
            return QColor(self.property('checkColor')) if self.property('checkColor') else QColor(default)
        elif role == 'cross':
            return QColor(self.property('crossColor')) if self.property('crossColor') else QColor(default)
        return QColor(default)

    def _draw_check(self, painter, rect, color):
        pen = QPen(color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        # Галочка
        x1, y1 = rect.left() + rect.width() * 0.15, rect.top() + rect.height() * 0.55
        x2, y2 = rect.left() + rect.width() * 0.45, rect.bottom() - rect.height() * 0.2
        x3, y3 = rect.right() - rect.width() * 0.15, rect.top() + rect.height() * 0.25
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y2, x3, y3)

    def _draw_cross(self, painter, rect, color):
        pen = QPen(color, 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        # Крестик
        x1, y1 = rect.left() + rect.width() * 0.25, rect.top() + rect.height() * 0.25
        x2, y2 = rect.right() - rect.width() * 0.25, rect.bottom() - rect.height() * 0.25
        x3, y3 = rect.right() - rect.width() * 0.25, rect.top() + rect.height() * 0.25
        x4, y4 = rect.left() + rect.width() * 0.25, rect.bottom() - rect.height() * 0.25
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x3, y3, x4, y4)

