import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout,
    QPushButton, QColorDialog, QComboBox, QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor
from pyqt5_svg_widgets.QAbstract import SvgButton, SvgLabel, SvgRadioButton, SvgToolButton, ToggleSwitchGroup, \
    SwitchButton


class SvgWidgetsExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SVG Widgets Example")
        self.setMinimumSize(600, 400)
        
        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # Создаем панель управления
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Добавляем выбор темы
        theme_combo = QComboBox()
        theme_combo.addItems(["Светлая", "Темная", "Синяя", "Зеленая"])
        theme_combo.currentTextChanged.connect(self.changeTheme)
        control_layout.addWidget(theme_combo)
        
        # Добавляем кнопку выбора цвета
        color_button = QPushButton("Выбрать цвет")
        color_button.clicked.connect(self.changeColor)
        control_layout.addWidget(color_button)
        
        main_layout.addWidget(control_panel)
        
        # Создаем контейнер для виджетов
        widgets_container = QWidget()
        widgets_layout = QVBoxLayout(widgets_container)
        widgets_layout.setSpacing(20)
        
        # Создаем SVG кнопку
        self.button = SvgButton(svg_path="x.svg", text="Кнопка с SVG", parent=self)
        self.button.setIconSize(QSize(22, 22))
        widgets_layout.addWidget(self.button)
        
        # Создаем SVG метку
        self.label = SvgLabel(svg_path="x.svg", text="Метка с SVG", parent=self)
        self.label.setIconSize(QSize(32, 32))
        widgets_layout.addWidget(self.label)
        
        # Создаем контейнер для радио-кнопок
        radio_container = QWidget()
        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setSpacing(10)
        
        # Создаем первую радио-кнопку
        self.radio1 = SvgRadioButton(svg_path="x.svg", text="Опция 1", parent=self)
        self.radio1.setIconSize(QSize(22, 22))
        radio_layout.addWidget(self.radio1)
        
        # Создаем вторую радио-кнопку
        self.radio2 = SvgRadioButton(svg_path="x.svg", text="Опция 2", parent=self)
        self.radio2.setIconSize(QSize(32, 32))
        radio_layout.addWidget(self.radio2)
        
        widgets_layout.addWidget(radio_container)
        
        # Создаем инструментальную кнопку
        self.tool_button = SvgToolButton(svg_path="x.svg", text="Инструмент", parent=self)
        self.tool_button.setIconSize(QSize(32, 32))
        widgets_layout.addWidget(self.tool_button)

        toggle = ToggleSwitchGroup(["Off", "Yes", "Auto", "Custom"])
        toggle.toggled.connect(lambda idx, text: print(f"Выбрано: {text}"))
        widgets_layout.addWidget(toggle)

        # --- Пример SwitchButton ---
        self.switch_label = QLabel("Выкл")
        self.switch_label.setAlignment(Qt.AlignCenter)
        self.switch = SwitchButton()
        self.switch.setChecked(False)
        self.switch.setFixedWidth(80)
        self.switch.setStyleSheet('''
            SwitchButton[checked="true"] {
                background: #16e085;
            }
            SwitchButton[checked="false"] {
                background: #39394a;
            }
        ''')
        widgets_layout.addWidget(self.switch, alignment=Qt.AlignCenter)
        # --- конец SwitchButton ---

        main_layout.addWidget(widgets_container)
        
        # Применяем начальную тему
        self.changeTheme("Светлая")
        
    def changeTheme(self, theme_name: str):
        if theme_name == "Светлая":
            self.applyLightTheme()
        elif theme_name == "Темная":
            self.applyDarkTheme()
        elif theme_name == "Синяя":
            self.applyBlueTheme()
        elif theme_name == "Зеленая":
            self.applyGreenTheme()
            
    def applyLightTheme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            QPushButton, QToolButton {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 16px;
                color: #333333;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #e0e0e0;
                border-color: #999999;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #d0d0d0;
                border-color: #666666;
            }
            QLabel {
                background-color: #f8f8f8;
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 16px;
                color: #333333;
            }
            QLabel:hover {
                background-color: #f0f0f0;
                border-color: #cccccc;
            }
            QRadioButton {
                color: #333333;
                spacing: 8px;
            }
            QRadioButton:hover {
                color: #666666;
            }
            QComboBox {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 16px;
                color: #333333;
            }
        """)
        
    def applyDarkTheme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton, QToolButton {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #4d4d4d;
                border-color: #666666;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #5d5d5d;
                border-color: #777777;
            }
            QLabel {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
            }
            QLabel:hover {
                background-color: #4d4d4d;
                border-color: #666666;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
            }
            QRadioButton:hover {
                color: #cccccc;
            }
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                color: #ffffff;
            }
        """)
        
    def applyBlueTheme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #e6f3ff;
                color: #003366;
            }
            QPushButton, QToolButton {
                background-color: #cce5ff;
                border: 1px solid #99ccff;
                border-radius: 4px;
                padding: 8px 16px;
                color: #003366;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #b3d9ff;
                border-color: #66b3ff;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #99ccff;
                border-color: #3399ff;
            }
            QLabel {
                background-color: #d9ecff;
                border: 1px solid #99ccff;
                border-radius: 4px;
                padding: 8px 16px;
                color: #003366;
            }
            QLabel:hover {
                background-color: #cce5ff;
                border-color: #66b3ff;
            }
            QRadioButton {
                color: #003366;
                spacing: 8px;
            }
            QRadioButton:hover {
                color: #0066cc;
            }
            QComboBox {
                background-color: #cce5ff;
                border: 1px solid #99ccff;
                border-radius: 4px;
                padding: 4px 8px;
                color: #003366;
            }
        """)
        
    def applyGreenTheme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #e6ffe6;
                color: #003300;
            }
            QPushButton, QToolButton {
                background-color: #ccffcc;
                border: 1px solid #99ff99;
                border-radius: 4px;
                padding: 8px 16px;
                color: #003300;
            }
            QPushButton:hover, QToolButton:hover {
                background-color: #b3ffb3;
                border-color: #66ff66;
            }
            QPushButton:pressed, QToolButton:pressed {
                background-color: #99ff99;
                border-color: #33ff33;
            }
            QLabel {
                background-color: #d9ffd9;
                border: 1px solid #99ff99;
                border-radius: 4px;
                padding: 8px 16px;
                color: #003300;
            }
            QLabel:hover {
                background-color: #ccffcc;
                border-color: #66ff66;
            }
            QRadioButton {
                color: #003300;
                spacing: 8px;
            }
            QRadioButton:hover {
                color: #006600;
            }
            QComboBox {
                background-color: #ccffcc;
                border: 1px solid #99ff99;
                border-radius: 4px;
                padding: 4px 8px;
                color: #003300;
            }
        """)
        
    def changeColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # Создаем палитру с выбранным цветом
            palette = QPalette()
            palette.setColor(QPalette.Window, color.lighter(150))
            palette.setColor(QPalette.WindowText, color.darker(200))
            palette.setColor(QPalette.Button, color.lighter(120))
            palette.setColor(QPalette.ButtonText, color.darker(200))
            palette.setColor(QPalette.Highlight, color)
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
            # Применяем палитру
            QApplication.setPalette(palette)
            
            # Обновляем стили для корректного отображения
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {color.lighter(150).name()};
                    color: {color.darker(200).name()};
                }}
                QPushButton, QToolButton {{
                    background-color: {color.lighter(120).name()};
                    border: 1px solid {color.name()};
                    border-radius: 4px;
                    padding: 16px;
                    color: {color.darker(200).name()};
                }}
                QPushButton:hover, QToolButton:hover {{
                    background-color: {color.lighter(100).name()};
                    border-color: {color.darker(120).name()};
                }}
                QPushButton:pressed, QToolButton:pressed {{
                    background-color: {color.name()};
                    border-color: {color.darker(150).name()};
                }}
                QLabel {{
                    background-color: {color.lighter(130).name()};
                    border: 1px solid {color.name()};
                    border-radius: 4px;
                    padding: 8px 16px;
                    color: {color.darker(200).name()};
                }}
                QLabel:hover {{
                    background-color: {color.lighter(120).name()};
                    border-color: {color.darker(120).name()};
                }}
                QRadioButton {{
                    color: {color.darker(200).name()};
                    spacing: 8px;
                }}
                QRadioButton:hover {{
                    color: {color.darker(150).name()};
                }}
                QComboBox {{
                    background-color: {color.lighter(120).name()};
                    border: 1px solid {color.name()};
                    border-radius: 4px;
                    padding: 4px 8px;
                    color: {color.darker(200).name()};
                }}
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SvgWidgetsExample()
    window.setObjectName(u"mainWidget")
    window.show()
    sys.exit(app.exec())
