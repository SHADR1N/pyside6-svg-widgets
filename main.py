import sys

try:
    from .pyqt5_svg_widgets import QSvgButton, QIconSvg, QDropButton
except ImportError:
    from pyqt5_svg_widgets import QSvgButton, QIconSvg, QDropButton, QSvgButtonIcon, SVGRenderIcon

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor


STYLE_WIDGET = """
* {
    background: #1E293B;
    font: 12pt;
}
SVGRenderIcon, QIconSvg, QSvgButtonIcon {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    background: #1E293B;
    border: 0px solid transparent;
    border-radius: 5%;
    color: #fff;
/*  icon-color: #fff; */
}

SVGRenderIcon:hover, SVGRenderIcon:hover, SVGRenderIcon:hover {
    padding:  15px;
    color: #496EF6;
/*  icon-color: #496EF6; */
    background: #344254;
}
SVGRenderIcon:pressed, SVGRenderIcon:pressed {
    padding:  15px;
    color: #3276C3;
    /* icon-color: #3276C3; */
}
"""


class SvgButtonExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 200)
        self.__initUi()
        self.setStyleSheet(STYLE_WIDGET)

    def __initUi(self):
        img = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-folder-open-dot"><path d="m6 14 1.45-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.55 6a2 2 0 0 1-1.94 1.5H4a2 2 0 0 1-2-2V5c0-1.1.9-2 2-2h3.93a2 2 0 0 1 1.66.9l.82 1.2a2 2 0 0 0 1.66.9H18a2 2 0 0 1 2 2v2"/><circle cx="14" cy="15" r="1"/></svg>'
        svg = SVGRenderIcon(svg_string=img, size_ic=(25, 25))
        svg.setObjectName(u"svgWidget")
        svg.setFixedSize(150, 50)
        svg.setText("Test button")
        svg.clicked.connect(lambda: print("clicked"))

        # newButton = QSvgButton()
        # newButton.setSvg('icons/message.svg')
        # newButton.setText("  Message")
        # newButton.setSvgSize(45, 45)
        #
        # svgIcon = QIconSvg('icons/message.svg')
        # svgIcon.setObjectName(u"svgWidget")
        # svgIcon.setSvgSize(25, 25)
        #
        # dropButton = QDropButton(
        #     "Message",
        #     'icons/message.svg',
        #     'icons/right_arrow.svg',
        #     'icons/minus.svg',
        #     False,
        #     False,
        #     "left",
        # )
        # dropButton.setIconSize(22, 22)
        # dropButton.setObjectName(u"svgWidget")
        #
        # dropButton.setFixedSize(180, 40)
        # dropButton.layout().setSpacing(10)

        lay = QVBoxLayout()
        lay.addWidget(svg, alignment=Qt.AlignmentFlag.AlignCenter)
        # lay.addWidget(newButton, alignment=Qt.AlignmentFlag.AlignCenter)
        # lay.addWidget(svgIcon, alignment=Qt.AlignmentFlag.AlignCenter)
        # lay.addWidget(dropButton, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(lay)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SvgButtonExample()
    ex.setObjectName(u"mainWidget")
    ex.show()
    sys.exit(app.exec())
