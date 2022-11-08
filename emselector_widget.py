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

    btnAllText = '   Все   '

    def __init__(self, isMultiselectable = True):
        super(EMSelector, self).__init__()

        # Main params
        self._isMultiselectable = isMultiselectable
        self._sorter = lambda sign: sign[0]

        # Signs properties
        # signs: [ name/str ]
        self._signs = []
        # colors: { name/str: { backcolor/str, textcolor/str, textcolor_0/str } }
        self._usercolors = {}
        # quantities: { name/str: quantity/int }
        self._quantities = {}
        # selections: { name/str: isSelected/bool }
        self._selections = {}

        # Runtime variables
        # signRects: [ { name/str, quantity/str, mainRect/QRect, textRect/QRect, powRect/QRect,
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
        # signs: [ name/str ]

        self.clearAll()
        self._signs = signs

        for sign in self._signs:
            self._selections[sign] = False

    def setSignsColors(self, colors):
        # colors: { name/str: color/str }

        self._usercolors = colors

    def setQuantity(self, quantities):
        # quantities: { name/str: quantity/int }

        self._quantities = quantities

        for sign in self._signs:
            if not(sign in self._quantities):
                self._quantities[sign] = 0

    def setSorter(self, sorter):
        # sorter/lambda
        self._sorter = sorter

    def clearSignsColors(self):
        self._usercolors.clear()

    def getSelected(self):
        res = []

        # res: [ name/str ]
        return res

    def clearAll(self):
        self._signs.clear()
        self._selections.clear()
        self._usercolors.clear()
        self._quantities.clear()
        self._signsRects.clear()

    def paintEvent(self, event):
        self._isAllSelected = True
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

        # Creation of rects
        if len(self._signs) > 0:
            self._signsRects.clear()

            # Creation of sign rects
            for sign in self._signs:
                # Check if any sign with positive amount is unselected
                if not self._selections[sign] and (self._quantities[sign] > 0):
                    self._isAllSelected = False

                # Determination of sign colors
                if self._selections[sign]:
                    self._selectedAmount += 1

                    # If alternative background color is set
                    if (sign in self._usercolors) and ('backcolor' in self._usercolors[sign]):
                        backcolor = self._usercolors[sign]['backcolor']
                    else:
                        backcolor = EMSelector.colors['sign_enabled']
                else:
                    backcolor = EMSelector.colors['sign_disabled']

                if self._quantities[sign] > 0:
                    # If alternative text color is set
                    if (sign in self._usercolors) and ('textcolor' in self._usercolors[sign]):
                        textcolor = self._usercolors[sign]['textcolor']
                    else:
                        textcolor = EMSelector.colors['text_enabled']
                else:
                    # If alternative inactive text color is set
                    if (sign in self._usercolors) and ('textcolor_0' in self._usercolors[sign]):
                        textcolor = self._usercolors[sign]['textcolor_0']
                    else:
                        textcolor = EMSelector.colors['text_disabled']

                # Create sign rect
                signRect = self._createSignRect(sign, self._quantities[sign], backcolor, textcolor, False)

                if self._quantities[sign] > 0:
                    active.append(signRect)
                else:
                    inactive.append(signRect)

            # Create button 'all' rect
            if self._isMultiselectable and (len(active) > 0):
                backcolor = EMSelector.colors['sign_all_enabled'] if self._isAllSelected \
                    else EMSelector.colors['sign_disabled']

                self._signsRects.append(self._createSignRect(EMSelector.btnAllText, None, backcolor,
                                                               EMSelector.colors['text_enabled'], True))

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

    def _createSignRect(self, text, quantity, backcolor, textcolor, isService = False):
        # signRect: { name/str, quantity/str, mainRect/QRect, textRect/QRect, powRect/QRect,
        #             backColor/str, textColor/str }

        if quantity is None:
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

        return { 'name': text, 'quantity': quantity, 'mainRect': mainQRect, 'textRect': textRect,
                'powRect': powRect, 'backColor': backcolor, 'textColor': textcolor, 'isService': isService }

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
        painter.drawText(signRect['textRect'], 0, signRect['name'])

        painter.setFont(self.powFont)
        painter.drawText(signRect['powRect'], 0, str(signRect['quantity']))

    # ****************************** Click Press handlers ******************************

    def multi(self, state):
        self._isMultiselect = state

    def keyPressEvent(self, event):
        # Check Ctrl pressed
        if event.key() == 0x01000021:
            self._isMultiselect = True

    def keyReleaseEvent(self, event):
        # Check Ctrl released
        if event.key() == 0x01000021:
            self._isMultiselect = False

    def mousePressEvent(self, event):
        for signRect in self._signsRects:
            if signRect['mainRect'].contains(event.pos()):
                # If it is btn 'All'
                if (signRect['name'] == EMSelector.btnAllText) and (signRect['isService'] is True):
                    # If all selected -> unselect all
                    if self._isAllSelected:
                        for sign in self._signs:
                            self._selections[sign] = False
                    # Otherwise select all
                    else:
                        for sign in self._signs:
                            self._selections[sign] = self._quantities[sign] > 0

                    self._isAllSelected = not self._isAllSelected

                # If quantity less or equal 0 - unselect (selection of such items is not allowed)
                elif self._quantities[signRect['name']] <= 0:
                    self._selections[signRect['name']] = False

                # If multiselect -> just add(rem) selection
                elif self._isMultiselectable and self._isMultiselect:
                    self._selections[signRect['name']] = not self._selections[signRect['name']]

                # If common item clicked and not multiselect
                else:
                    # If only this one is selected -> diselect it
                    if (self._selectedAmount == 1) and self._selections[signRect['name']]:
                        self._selections[signRect['name']] = False

                    # If there are any items selected, select just this one
                    elif self._selectedAmount >= 1:
                        for sign in self._signs:
                            self._selections[sign] = False
                        self._selections[signRect['name']] = True

                    # Else -> mirror state of selection
                    else:
                        self._selections[signRect['name']] = not self._selections[signRect['name']]

                self.repaint()

