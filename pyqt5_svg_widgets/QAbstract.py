from functools import lru_cache
from functools import lru_cache
from typing import Optional, Union, Dict

from PyQt5.QtCore import Qt, QSize, QEvent, pyqtProperty, QRect
from PyQt5.QtGui import QPixmap, QPainter, QIcon, QColor, QPalette, QImage, QFont
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import (
    QPushButton, QWidget, QLabel, QStyle, QStyleOption,
    QRadioButton, QToolButton, QStyleOptionButton, QSizePolicy
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
        super().__init__(text, parent)  # Сначала инициализируем базовый класс
        self._svg_widget = SvgWidget(svg_path, self)
        self._svg_widget.setFixedSize(self.size())
        self._svg_widget.setText(text)
        
    def setText(self, text: str):
        super().setText(text)
        self._svg_widget.setText(text)
        
    def setIconSize(self, size: QSize):
        self._svg_widget.setIconSize(size)
        self.setFixedSize(size)
        
    def resizeEvent(self, event):
        self._svg_widget.setFixedSize(self.size())
        super().resizeEvent(event)
        
    def paintEvent(self, event):
        # Рисуем стандартную метку
        super().paintEvent(event)
        # SVG отрисовывается автоматически через дочерний виджет

class SvgRadioButton(QRadioButton):
    """Радио-кнопка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(text, parent)  # Сначала инициализируем базовый класс
        self._svg_widget = SvgWidget(svg_path, self)
        self._svg_widget.setFixedSize(self.size())
        self._svg_widget.setText(text)
        
    def setText(self, text: str):
        super().setText(text)
        self._svg_widget.setText(text)
        
    def setIconSize(self, size: QSize):
        self._svg_widget.setIconSize(size)
        self.setFixedSize(size)
        
    def resizeEvent(self, event):
        self._svg_widget.setFixedSize(self.size())
        super().resizeEvent(event)
        
    def paintEvent(self, event):
        # Рисуем стандартную радио-кнопку
        super().paintEvent(event)
        # SVG отрисовывается автоматически через дочерний виджет

class SvgToolButton(QToolButton):
    """Инструментальная кнопка с SVG иконкой"""
    def __init__(self, svg_path: str, text: str = "", parent=None):
        super().__init__(parent)  # Сначала инициализируем базовый класс
        self.setText(text)  # Устанавливаем текст после инициализации
        self._svg_widget = SvgWidget(svg_path, self)
        self._svg_widget.setFixedSize(self.size())
        self._svg_widget.setText(text)
        
    def setText(self, text: str):
        super().setText(text)
        self._svg_widget.setText(text)
        
    def setIconSize(self, size: QSize):
        self._svg_widget.setIconSize(size)
        self.setFixedSize(size)
        
    def resizeEvent(self, event):
        self._svg_widget.setFixedSize(self.size())
        super().resizeEvent(event)
        
    def paintEvent(self, event):
        # Рисуем стандартную инструментальную кнопку
        super().paintEvent(event)
        # SVG отрисовывается автоматически через дочерний виджет
