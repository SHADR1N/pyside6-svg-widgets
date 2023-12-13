## SVG Widgets for PySide6

SVG widgets for PySide6
Such as QCustomAbstractButton, QIconSvg, QDropButton

Widgets do not use strict rules for palettes, but take colors from the application's QCSS table, which allows them to be used as standard widgets

## Requirements
PySide6>=6.4.0

## Setup
python -m pip install git+https://github.com/SHADR1N/pyside6-svg-widgets.git

## Usage for QIconSvg

- ```svgIcon = QIconSvg(svg_path: Optional[str] = None)``` - Accepts an optional parameter with an image in the svg
- ```svgIcon.setObjectName(object_name: str)``` - Changes the name of the object through which we will then set the style for the image.
- ```svgIcon.setIcon(path_to_svg: str)``` - If you didn't pass the image or want to replace it, you can use setIcon, takes the path to the image.
- ```svgIcon.setIconSize(width: int, height: int)``` - Changes the image size.

## Usage for QCustomAbstractButton

- ```abstractButton = QCustomAbstractButton(svg_path: Optional[str] = None)``` - Accepts an optional parameter with an image in the svg
- ```abstractButton.setObjectName(object_name: str)``` - Changes the name of the object through which we will then set the style for the image.
- ```abstractButton.setSvg(path_to_svg: str)``` - Accepts an optional parameter with an image in the svg
- ```abstractButton.setSvgSize(width: int, height: int)``` - Changes the image size.
- ```abstractButton.setText(text: str)``` - Any text.

## Usage for QDropButton

```py 
dropButton = QDropButton(
            text: str, 
            left_svg: str, 
            right_svg: str, 
            minus_svg: Optional[str] = None, 
            only_click: bool = False,
            save_state: bool = False,
            text_alignment: Optional[str] = "left"  # left, right, center
)
dropButton.setObjectName(object_name: str)
dropButton.setIconSize(width: int, height: int)
dropButton.setCursor(type_cursor: QCursor)
dropButton.layout().setSpacing(space: int)
```
- text - Sets the button text
- left_svg - Path to the SVG image for the button.
- right_svg - If you use a drop-down menu button, you can put a swg icon on the right.
- minus_svg - For the menu opening and closing state, add another SVG icon, it will be replaced with the primary one and back.
- only_click - If you only want to open and change the state of the button otherwise it will change the image on hover.
- save_state - If you want to leave the state pressed after clicking, then pass True.
- text_alignment - Set the text position on the button, left, right, center are available.
- `` dropButton.layout().setSpacing(space: int) `` You can also change the distance between the images and the button, to do this change the space.
- The widget accepts all settings as for QWidget!

## Usage QCSS

```css
#nameYourWidget {
    color: white; /* Sets the text color if the widget has one. */
    icon-color: white; /* Sets the color of the image. */
}

#nameYourWidget:hover {
    color: blue;
    icon-color: blue;
}

#nameYourWidget:pressed {
    color: blue;
    icon-color: blue;
}
```

# Example
```py
import sys

from pyside6_svg_widgets import QCustomAbstractButton, QIconSvg, QDropButton

from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor


STYLE_WIDGET = """
* {
    background: #1E293B;
    font: 12pt;
}
#svgWidget {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    icon-color: #CCD5E1;
    background: #1E293B;
    border: 0px solid transparent;
    border-radius: 5%;
    color: #fff;
}

#svgWidget:hover {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    icon-color: #496EF6;
    color: #496EF6;
    background: #344254;
}
#svgWidget:pressed {
    padding:  5px;
    padding-left: 10px;
    padding-right: 10px;
    icon-color: #3276C3;
    color: #3276C3;
}
"""


class SvgButtonExample(QWidget):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 200)
        self.setStyleSheet(STYLE_WIDGET)
        self.__initUi()

    def __initUi(self):
        newButton = QCustomAbstractButton()
        newButton.setObjectName(u"svgWidget")
        newButton.setSvg('icons/message.svg')
        newButton.setText("  Message")

        svgIcon = QIconSvg('icons/message.svg')
        svgIcon.setObjectName(u"svgWidget")
        svgIcon.setIconSize(19, 19)

        dropButton = QDropButton(
            "Message",
            'icons/message.svg',
            'icons/right_arrow.svg',
            'icons/minus.svg',
            False,
            True,
            "left"
        )
        dropButton.setObjectName(u"svgWidget")
        dropButton.setIconSize(22, 22)
        dropButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

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
```

# Result

![](https://github.com/SHADR1N/pyside6-svg-widgets/blob/master/example/example.gif?raw=true)

