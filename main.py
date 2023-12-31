import sys

try:
    from .pyside6_svg_widgets import QSvgButton, QIconSvg, QDropButton
except ImportError:
    from pyside6_svg_widgets import QSvgButton, QIconSvg, QDropButton

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor


STYLE_WIDGET = """
* {
    background: #1E293B;
    font: 12pt;
}
QSvgButton, QIconSvg {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    background: #1E293B;
    border: 0px solid transparent;
    border-radius: 5%;
    color: #fff;
    icon-color: #fff;
}

QSvgButton:hover, QIconSvg:hover {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    color: #496EF6;
    icon-color: #496EF6;
    background: #344254;
}
QSvgButton:pressed, QIconSvg:pressed {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    color: #3276C3;
    icon-color: #3276C3;
}
"""


class SvgButtonExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 200)
        self.__initUi()
        self.setStyleSheet(STYLE_WIDGET)

    def __initUi(self):
        newButton = QSvgButton()
        newButton.setSvg('icons/message.svg')
        newButton.setText("  Message")
        newButton.setSvgSize(45, 45)

        svgIcon = QIconSvg('icons/message.svg')
        svgIcon.setObjectName(u"svgWidget")
        svgIcon.setSvgSize(25, 25)

        dropButton = QDropButton(
            "Message",
            'icons/message.svg',
            'icons/right_arrow.svg',
            'icons/minus.svg',
            False,
            False,
            "left",
        )
        dropButton.setIconSize(22, 22)
        dropButton.setObjectName(u"svgWidget")

        dropButton.setFixedSize(180, 40)
        dropButton.layout().setSpacing(10)

        lay = QVBoxLayout()
        lay.addWidget(newButton, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(svgIcon, alignment=Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(dropButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(lay)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SvgButtonExample()
    ex.setObjectName(u"mainWidget")
    ex.show()
    sys.exit(app.exec())
