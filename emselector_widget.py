from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import pyqtSignal, QPainter, QColor, QBrush, QFont, QFontMetrics, QRect, QKeyEvent, QSizePolicy, Qt

class EMSelector(QWidget):
    signalValuesChanged = pyqtSignal()
    signalNewValueSelected = pyqtSignal()

    globalDeltas = { 'margin': 3, 'startx': 10, 'starty': 10 }

    signDeltas = { 'txt_bottom': 3, 'txt_left': 3, 'txt_pow_vertical': -8, 'txt_pow_horizontal': 2,
                   'pow_top': 3, 'pow_right': 2 }

    colors = { 'sign_enabled': '#67BDFF', 'sign_disabled': '#F6F6F6', 'sign_all_enabled': '#88CC66',
               'text_enabled': '#000000', 'text_disabled': '#808080', 'background': '#FFFFFF' }

    def __init__(self, isMultiselectable = True):
        super(EMSelector, self).__init__()

        # Main params
        self._isMultiselectable = isMultiselectable
        self._sorter = lambda sign: sign[0]

        # Signs properties
        # signs: [ (id/int, name/str) ]
        self._signs = []
        # colors: { id/int: { backcolor/str, textcolor/str, textcolor_0/str } }
        self._usercolors = {}
        # quantities: { id/int: quantity/int }
        self._quantities = {}
        # selections: { id/int: isSelected/bool }
        self._selections = {}

        # Runtime variables
        # signRects: [ { id/int|str, name/str, quantity/str, mainRect/QRect, textRect/QRect, powRect/QRect,
        #                backColor/str, textColor/str } ]
        self._signsRects = []
        self._isMultiselect = False
        self._isAllSelected = False
        self._selectedAmount = 0

        self.setFocusPolicy(Qt.NoFocus)
        self.setMinimumHeight(100)
        self.setMinimumWidth(100)

        self.mainFont = QFont()
        self.textFontMetrics = QFontMetrics(self.mainFont)

        self.powFont = QFont()
        self.powFont.setPointSize(7)
        self.powFontMetrics = QFontMetrics(self.powFont)

    def setSigns(self, signs):
        # signs: [ (id/int, name/str) ]

        self.clearAll()
        self._signs = signs

        for sign in self._signs:
            self._selections[sign[0]] = False

    def setSignsColors(self, colors):
        # colors: { id/int: color/str }

        self._usercolors = colors

    def setQuantity(self, quantities):
        # quantities: { id/int: quantity/int }

        self._quantities = quantities

        for sid, sname in self._signs:
            if not(sid in self._quantities):
                self._quantities[sid] = 0

    def setSorter(self, sorter):
        # sorter/lambda
        self._sorter = sorter

    def clearSignsColors(self):
        self._usercolors.clear()

    def getSelected(self):
        res = []

        # res: [ id/int ]
        return res

    def clearAll(self):
        self._signs.clear()
        self._selections.clear()
        self._usercolors.clear()
        self._quantities.clear()
        self._signsRects.clear()

    def paintEvent(self, event):
        self._isAllSelected = True
        self._signsRects.clear()
        self._selectedAmount = 0

        # Painter setup
        painter = QPainter(self)
        painter.setRenderHint(painter.Antialiasing)
        painter.save()

        # Drawing widget background
        painter.setBrush(QColor(EMSelector.colors['background']))
        painter.setPen(QColor(EMSelector.colors['background']))
        painter.drawRect(self.rect())

        active = []
        inactive = []

        # Gen value rects
        if len(self._signs) > 0:

            # Creation of sign rects
            for sid, sname in self._signs:
                # Check if any sign with positive amount is unselected
                if not self._selections[sid] and (self._quantities[sid] > 0):
                    self._isAllSelected = False

                # Determination of sign colors
                if self._selections[sid]:
                    # If alternative background color is set
                    if (sid is self._usercolors) and ('backcolor' in self._usercolors[sid]):
                        backcolor = self._usercolors[sid]
                    else:
                        backcolor = EMSelector.colors['sign_enabled']
                else:
                    backcolor = EMSelector.colors['sign_disabled']

                if self._quantities[sid] > 0:
                    # If alternative text color is set
                    if (sid is self._usercolors) and ('textcolor' in self._usercolors[sid]):
                        textcolor = self._usercolors[sid]
                    else:
                        textcolor = EMSelector.colors['text_enabled']
                else:
                    # If alternative inactive text color is set
                    if (sid is self._usercolors) and ('textcolor_0' in self._usercolors[sid]):
                        textcolor = self._usercolors[sid]
                    else:
                        textcolor = EMSelector.colors['text_disabled']

                # Create sign rect
                signRect = self._createSignRect(sid, sname, self._quantities[sid], backcolor, textcolor)

                if self._quantities[sid] > 0:
                    active.append(signRect)
                else:
                    inactive.append(signRect)

            # Create button 'all' rect
            if self._isMultiselectable and (len(active) > 0):
                backcolor = EMSelector.colors['sign_all_enabled'] if self._isAllSelected \
                    else EMSelector.colors['sign_disabled']

                self._signsRects.append(self._createSignRect('ALL', '   Все   ', None, backcolor,
                                                               EMSelector.colors['text_enabled']))

            # TODO: sort?
            self._signsRects += active
            self._signsRects += inactive

            # Rendering sign rects
            currx = EMSelector.globalDeltas['startx']
            curry = EMSelector.globalDeltas['starty']

            for signRect in self._signsRects:
                if currx + signRect['mainRect'].width() + EMSelector.globalDeltas['margin'] > self.width():
                    # Next row
                    currx = EMSelector.globalDeltas['startx']
                    curry += signRect['mainRect'].height() + EMSelector.globalDeltas['margin']

                    self.setMinimumHeight(curry + EMSelector.globalDeltas['margin'] + signRect['mainRect'].height())

                self._moveSignRect(signRect, currx, curry)
                self._renderSignRect(signRect, painter)

                currx += signRect['mainRect'].width() + EMSelector.globalDeltas['margin']

        painter.restore()

    # +++++++++++++++++++++++++++++ Sign rects interaction +++++++++++++++++++++++++++++

    def _createSignRect(self, id, text, quantity, backcolor, textcolor):
        # signRect: { id/int|str, name/str, quantity/str, mainRect/QRect, textRect/QRect, powRect/QRect,
        #             backColor/str, textColor/str }

        if quantity == None:
            quantity = ''

        textRect = QRect(EMSelector.signDeltas['txt_left'],
                         EMSelector.signDeltas['txt_pow_vertical'] + EMSelector.signDeltas['pow_top'] +
                         self.powFontMetrics.height(),
                         self.textFontMetrics.horizontalAdvance(text),
                         self.textFontMetrics.height())

        powRect = QRect(textRect.width() + EMSelector.signDeltas['txt_left'] +
                        EMSelector.signDeltas['txt_pow_horizontal'],
                        EMSelector.signDeltas['pow_top'],
                        self.powFontMetrics.horizontalAdvance(str(quantity)),
                        self.powFontMetrics.height())

        mainQRect = QRect(0, 0,
                          textRect.width() + powRect.width() + EMSelector.signDeltas['txt_left'] +
                          EMSelector.signDeltas['txt_pow_horizontal'] + EMSelector.signDeltas['pow_right'],
                          textRect.height() + powRect.height() + EMSelector.signDeltas['txt_pow_vertical'] +
                          EMSelector.signDeltas['txt_bottom'] + EMSelector.signDeltas['pow_top'])

        return { 'id': id, 'text': text, 'quantity': quantity, 'mainRect': mainQRect, 'textRect': textRect,
                'powRect': powRect, 'backColor': backcolor, 'textColor': textcolor}

    def _moveSignRect(self, signRect, x, y):
        currx = signRect['mainRect'].x()
        curry = signRect['mainRect'].y()

        signRect['mainRect'].moveTo(x, y)

        signRect['textRect'].translate(x - currx, y - curry)

        signRect['powRect'].translate(x - currx, y - curry)

    def _renderSignRect(self, signRect, painter):
        # Draw sign background
        painter.setPen(QColor(signRect['backColor']))
        painter.setBrush(QColor(signRect['backColor']))
        painter.drawRect(signRect['mainRect'])

        # Write text
        painter.setFont(self.mainFont)

        painter.setPen(QColor(signRect['textColor']))
        painter.drawText(signRect['textRect'], 0, signRect['text'])

        painter.setFont(self.powFont)
        painter.drawText(signRect['powRect'], 0, str(signRect['quantity']))

    # ****************************** Click Press handlers ******************************

    def keyPressEvent(self, event):
        # Check Ctrl pressed
        if event.key() == 0x01000021:
            self._isMultiselect = True

    def keyReleaseEvent(self, event):
        # Check Ctrl released
        if event.key() == 0x01000021:
            self._isMultiselect = False

    def mousePressEvent(self, event):
        pass
