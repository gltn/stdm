# QRCode for Python
#
# Ported from the Javascript library by Sam Curren
# ReportLab module by German M. Bravo
#
# QRCode for Javascript
# http://d-project.googlecode.com/svn/trunk/misc/qrcode/js/qrcode.js
#
# Copyright (c) 2009 Kazuhiko Arase
#
# URL: http://www.d-project.com/
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php
#
# The word "QR Code" is registered trademark of
# DENSO WAVE INCORPORATED
#   http://www.denso-wave.com/qrcode/faqpatent-e.html

__all__=(
        'QrCodeWidget',
        )
import math, re
from reportlab.graphics.shapes import Group, Rect
from reportlab.lib import colors
from reportlab.lib.validators import isNumber, isColor, isString, Validator
from reportlab.lib.attrmap import *
from reportlab.graphics.charts.areas import PlotArea
from reportlab.lib.units import mm

class isLevel(Validator):
    def test(self,x):
        # level L : About 7% or less errors can be corrected.
        # level M : About 15% or less errors can be corrected.
        # level Q : About 25% or less errors can be corrected.
        # level H : About 30% or less errors can be corrected.
        return type(x) is str and len(x)==1 and x in ['L', 'M', 'Q', 'H']
isLevel = isLevel()

class QrCodeWidget(PlotArea):
    codeName = "QR"
    _attrMap = AttrMap(BASE=PlotArea,
        value = AttrMapValue(isString, desc='the text'),
        x = AttrMapValue(isNumber, desc='x-coord'),
        y = AttrMapValue(isNumber, desc='y-coord'),
        barFillColor = AttrMapValue(isColor, desc='bar color'),
        barWidth = AttrMapValue(isNumber, desc='Width of bars.'), # maybe should be named just width?
        barHeight = AttrMapValue(isNumber, desc='Height of bars.'), # maybe should be named just height?
        barStrokeWidth = AttrMapValue(isNumber, desc='Width of bar borders.'), # maybe removed?
        barStrokeColor = AttrMapValue(isColor, desc='Color of bar borders.'), # maybe removed?
        barBorder = AttrMapValue(isNumber, desc='Width of QR border.'), # maybe should be named qrBorder?
        barLevel = AttrMapValue(isLevel, desc='QR Code level.'), # maybe should be named qrLevel
        )
    x = 0
    y = 0
    barFillColor = colors.black
    barStrokeColor = None
    barStrokeWidth = 0
    barHeight = 32*mm
    barWidth = 32*mm
    barBorder = 4
    barLevel = 'L'

    def __init__(self,value='Hello World',**kw):
        self.value=value
        for k, v in kw.iteritems():
            setattr(self, k, v)

    def wrap(self,aW,aH):
        return self.width,self.height


    def draw(self):
        g = Group()
        gAdd = g.add
        barWidth = self.barWidth
        barHeight = self.barHeight
        x = self.x
        y = self.y
        gAdd(Rect(x,y,barWidth,barHeight,fillColor=None,strokeColor=None,strokeWidth=0))

        barFillColor = self.barFillColor
        barStrokeWidth = self.barStrokeWidth
        barStrokeColor = self.barStrokeColor
        barBorder = self.barBorder

        correctLevel = {
            'L': QRErrorCorrectLevel.L,
            'M': QRErrorCorrectLevel.M,
            'Q': QRErrorCorrectLevel.Q,
            'H': QRErrorCorrectLevel.H,
        }[self.barLevel]

        qr = QRCode(None, correctLevel)

        qr.addData(self.value)
        qr.make()

        moduleCount = qr.getModuleCount()
        boxsize = min(barWidth, barHeight) / (moduleCount + barBorder * 2)
        offsetX = (barWidth - min(barWidth, barHeight)) / 2
        offsetY = (min(barWidth, barHeight) - barHeight) / 2

        for r in xrange(moduleCount):
            for c in xrange(moduleCount):
                if (qr.isDark(r, c) ):
                    x = (c + barBorder) * boxsize
                    y = (r + barBorder+1) * boxsize
                    qrect = Rect(offsetX+x,offsetY+barHeight-y,boxsize,boxsize,fillColor=barFillColor,strokeWidth=barStrokeWidth,strokeColor=barStrokeColor)
                    gAdd(qrect)

        return g

class QRMode:
    MODE_NUMBER = 1 << 0
    MODE_ALPHA_NUM = 1 << 1
    MODE_8BIT_BYTE = 1 << 2
    MODE_KANJI = 1 << 3

class QR:
    def __init__(self, data):
        if self.valid:
            if not re.search('^[%s]+$' % self.valid, data):
                raise ValueError
        else:
            self.valid = ''.join(chr(c) for c in range(256))
        self.data = data

    def getLength(self):
        return len(self.data)

    def __repr__(self):
        return self.data

    def write(self, buffer):
        for g in map(None, *[iter(self.data)] * self.group):
            bits = 0
            n = 0
            for i in range(self.group):
                if g[i] is not None:
                    n *= len(self.valid)
                    n += self.valid.index(g[i])
                    bits += self.bits[i]
            buffer.put(n, bits)

class QRNumber(QR):
    valid = '0123456789'
    bits = (4,3,3)
    group = 3
    mode = QRMode.MODE_NUMBER

class QRAlphaNum(QR):
    valid = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:'
    bits = (6,5)
    group = 2
    mode = QRMode.MODE_ALPHA_NUM

class QR8bitByte(QR):
    valid = None #''.join(chr(c) for c in range(256))
    bits = (8,)
    group = 1
    mode = QRMode.MODE_8BIT_BYTE

    def write(self, buffer):
        for c in self.data:
            buffer.put(ord(c), 8)

class QRKanji(QR):
    valid = None
    bits = (8,)
    group = 1
    mode = QRMode.MODE_KANJI

class QRCode:
    def __init__(self, typeNumber, errorCorrectLevel):
        self.typeNumber = typeNumber
        self.errorCorrectLevel = errorCorrectLevel
        self.modules = None
        self.moduleCount = 0
        self.dataCache = None
        self.dataList = []

    def addData(self, data):
        try :
            newData = QRNumber(data)
        except ValueError:
            try:
                newData = QRAlphaNum(data)
            except ValueError:
                try:
                    newData = QR8bitByte(data)
                except ValueError:
                    try:
                        newData = QRKanji(data)
                    except:
                        raise
        self.dataList.append(newData)
        self.dataCache = None

    def isDark(self, row, col):
        if (row < 0 or self.moduleCount <= row or col < 0 or self.moduleCount <= col):
            raise Exception("%s,%s - %s" % (row, col, self.moduleCount))
        return self.modules[row][col]

    def getModuleCount(self):
        return self.moduleCount

    def make(self):
        if self.typeNumber is None:
            # Calculate typeNumber for data to fit the QR Code capacity
            errorCorrectLevel = self.errorCorrectLevel
            for typeNumber in xrange(1, 40):
                rsBlocks = QRRSBlock.getRSBlocks(typeNumber, errorCorrectLevel)
                totalDataCount = 0;
                for i in xrange(len(rsBlocks)):
                    totalDataCount += rsBlocks[i].dataCount
                length = 0
                for i in xrange(len(self.dataList)):
                    data = self.dataList[i]
                    length += 4
                    length += QRUtil.getLengthInBits(data.mode, typeNumber)
                    length += len(data.data) * 8
                if length <= totalDataCount * 8:
                    break
            self.typeNumber = typeNumber
        self.makeImpl(False, self.getBestMaskPattern())

    def makeImpl(self, test, maskPattern):
        self.moduleCount = self.typeNumber * 4 + 17
        self.modules = [None for x in xrange(self.moduleCount)]
        for row in xrange(self.moduleCount):
            self.modules[row] = [None for x in xrange(self.moduleCount)]
            for col in xrange(self.moduleCount):
                self.modules[row][col] = None #(col + row) % 3;
        self.setupPositionProbePattern(0, 0)
        self.setupPositionProbePattern(self.moduleCount - 7, 0)
        self.setupPositionProbePattern(0, self.moduleCount - 7)
        self.setupPositionAdjustPattern()
        self.setupTimingPattern()
        self.setupTypeInfo(test, maskPattern)
        if (self.typeNumber >= 7):
            self.setupTypeNumber(test)
        if (self.dataCache == None):
            self.dataCache = QRCode.createData(self.typeNumber, self.errorCorrectLevel, self.dataList)
        self.mapData(self.dataCache, maskPattern)

    def setupPositionProbePattern(self, row, col):
        for r in xrange(-1, 8):
            if (row + r <= -1 or self.moduleCount <= row + r): continue
            for c in xrange(-1, 8):
                if (col + c <= -1 or self.moduleCount <= col + c): continue
                if ( (0 <= r and r <= 6 and (c == 0 or c == 6) )
                        or (0 <= c and c <= 6 and (r == 0 or r == 6) )
                        or (2 <= r and r <= 4 and 2 <= c and c <= 4) ):
                    self.modules[row + r][col + c] = True;
                else:
                    self.modules[row + r][col + c] = False;

    def getBestMaskPattern(self):
        minLostPoint = 0
        pattern = 0
        for i in xrange(8):
            self.makeImpl(True, i);
            lostPoint = QRUtil.getLostPoint(self);
            if (i == 0 or minLostPoint > lostPoint):
                minLostPoint = lostPoint
                pattern = i
        return pattern

    def setupTimingPattern(self):
        for r in xrange(8, self.moduleCount - 8):
            if (self.modules[r][6] != None):
                continue
            self.modules[r][6] = (r % 2 == 0)
        for c in xrange(8, self.moduleCount - 8):
            if (self.modules[6][c] != None):
                continue
            self.modules[6][c] = (c % 2 == 0)

    def setupPositionAdjustPattern(self):
        pos = QRUtil.getPatternPosition(self.typeNumber)
        for i in xrange(len(pos)):
            for j in xrange(len(pos)):
                row = pos[i]
                col = pos[j]
                if (self.modules[row][col] != None):
                    continue
                for r in xrange(-2, 3):
                    for c in xrange(-2, 3):
                        if (r == -2 or r == 2 or c == -2 or c == 2 or (r == 0 and c == 0) ):
                            self.modules[row + r][col + c] = True
                        else:
                            self.modules[row + r][col + c] = False

    def setupTypeNumber(self, test):
        bits = QRUtil.getBCHTypeNumber(self.typeNumber)
        for i in xrange(18):
            mod = (not test and ( (bits >> i) & 1) == 1)
            self.modules[i // 3][i % 3 + self.moduleCount - 8 - 3] = mod;
        for i in xrange(18):
            mod = (not test and ( (bits >> i) & 1) == 1)
            self.modules[i % 3 + self.moduleCount - 8 - 3][i // 3] = mod;

    def setupTypeInfo(self, test, maskPattern):
        data = (self.errorCorrectLevel << 3) | maskPattern
        bits = QRUtil.getBCHTypeInfo(data)
        # vertical
        for i in xrange(15):
            mod = (not test and ( (bits >> i) & 1) == 1)
            if (i < 6):
                self.modules[i][8] = mod
            elif (i < 8):
                self.modules[i + 1][8] = mod
            else:
                self.modules[self.moduleCount - 15 + i][8] = mod
        # horizontal
        for i in xrange(15):
            mod = (not test and ( (bits >> i) & 1) == 1);
            if (i < 8):
                self.modules[8][self.moduleCount - i - 1] = mod
            elif (i < 9):
                self.modules[8][15 - i - 1 + 1] = mod
            else:
                self.modules[8][15 - i - 1] = mod
        # fixed module
        self.modules[self.moduleCount - 8][8] = (not test)

    def mapData(self, data, maskPattern):
        inc = -1
        row = self.moduleCount - 1
        bitIndex = 7
        byteIndex = 0
        for col in xrange(self.moduleCount - 1, 0, -2):
            if (col == 6): col-=1
            while (True):
                for c in xrange(2):
                    if (self.modules[row][col - c] == None):
                        dark = False
                        if (byteIndex < len(data)):
                            dark = ( ( (data[byteIndex] >> bitIndex) & 1) == 1)
                        mask = QRUtil.getMask(maskPattern, row, col - c)
                        if (mask):
                            dark = not dark
                        self.modules[row][col - c] = dark
                        bitIndex-=1
                        if (bitIndex == -1):
                            byteIndex+=1
                            bitIndex = 7
                row += inc
                if (row < 0 or self.moduleCount <= row):
                    row -= inc
                    inc = -inc
                    break
    PAD0 = 0xEC
    PAD1 = 0x11

    @staticmethod
    def createData(typeNumber, errorCorrectLevel, dataList):
        rsBlocks = QRRSBlock.getRSBlocks(typeNumber, errorCorrectLevel)
        buffer = QRBitBuffer();
        for i in xrange(len(dataList)):
            data = dataList[i]
            buffer.put(data.mode, 4)
            buffer.put(data.getLength(), QRUtil.getLengthInBits(data.mode, typeNumber) )
            data.write(buffer)
        # calc num max data.
        totalDataCount = 0;
        for i in xrange(len(rsBlocks)):
            totalDataCount += rsBlocks[i].dataCount
        if (buffer.getLengthInBits() > totalDataCount * 8):
            raise Exception("code length overflow. (%d > %d)" % (buffer.getLengthInBits(), totalDataCount * 8))
        # end code
        if (buffer.getLengthInBits() + 4 <= totalDataCount * 8):
            buffer.put(0, 4)
        # padding
        while (buffer.getLengthInBits() % 8 != 0):
            buffer.putBit(False)
        # padding
        while (True):
            if (buffer.getLengthInBits() >= totalDataCount * 8):
                break
            buffer.put(QRCode.PAD0, 8)
            if (buffer.getLengthInBits() >= totalDataCount * 8):
                break
            buffer.put(QRCode.PAD1, 8)
        return QRCode.createBytes(buffer, rsBlocks)

    @staticmethod
    def createBytes(buffer, rsBlocks):
        offset = 0
        maxDcCount = 0
        maxEcCount = 0
        dcdata = [0 for x in xrange(len(rsBlocks))]
        ecdata = [0 for x in xrange(len(rsBlocks))]
        for r in xrange(len(rsBlocks)):
            dcCount = rsBlocks[r].dataCount
            ecCount = rsBlocks[r].totalCount - dcCount
            maxDcCount = max(maxDcCount, dcCount)
            maxEcCount = max(maxEcCount, ecCount)
            dcdata[r] = [0 for x in xrange(dcCount)]
            for i in xrange(len(dcdata[r])):
                dcdata[r][i] = 0xff & buffer.buffer[i + offset]
            offset += dcCount
            rsPoly = QRUtil.getErrorCorrectPolynomial(ecCount)
            rawPoly = QRPolynomial(dcdata[r], rsPoly.getLength() - 1)
            modPoly = rawPoly.mod(rsPoly)
            ecdata[r] = [0 for x in xrange(rsPoly.getLength()-1)]
            for i in xrange(len(ecdata[r])):
                modIndex = i + modPoly.getLength() - len(ecdata[r])
                if (modIndex >= 0):
                    ecdata[r][i] = modPoly.get(modIndex)
                else:
                    ecdata[r][i] = 0
        totalCodeCount = 0
        for i in xrange(len(rsBlocks)):
            totalCodeCount += rsBlocks[i].totalCount
        data = [None for x in xrange(totalCodeCount)]
        index = 0
        for i in xrange(maxDcCount):
            for r in xrange(len(rsBlocks)):
                if (i < len(dcdata[r])):
                    data[index] = dcdata[r][i]
                    index+=1
        for i in xrange(maxEcCount):
            for r in xrange(len(rsBlocks)):
                if (i < len(ecdata[r])):
                    data[index] = ecdata[r][i]
                    index+=1
        return data


class QRErrorCorrectLevel:
    L = 1
    M = 0
    Q = 3
    H = 2

class QRMaskPattern:
    PATTERN000 = 0
    PATTERN001 = 1
    PATTERN010 = 2
    PATTERN011 = 3
    PATTERN100 = 4
    PATTERN101 = 5
    PATTERN110 = 6
    PATTERN111 = 7

class QRUtil(object):
    PATTERN_POSITION_TABLE = [
        [],
        [6, 18],
        [6, 22],
        [6, 26],
        [6, 30],
        [6, 34],
        [6, 22, 38],
        [6, 24, 42],
        [6, 26, 46],
        [6, 28, 50],
        [6, 30, 54],
        [6, 32, 58],
        [6, 34, 62],
        [6, 26, 46, 66],
        [6, 26, 48, 70],
        [6, 26, 50, 74],
        [6, 30, 54, 78],
        [6, 30, 56, 82],
        [6, 30, 58, 86],
        [6, 34, 62, 90],
        [6, 28, 50, 72, 94],
        [6, 26, 50, 74, 98],
        [6, 30, 54, 78, 102],
        [6, 28, 54, 80, 106],
        [6, 32, 58, 84, 110],
        [6, 30, 58, 86, 114],
        [6, 34, 62, 90, 118],
        [6, 26, 50, 74, 98, 122],
        [6, 30, 54, 78, 102, 126],
        [6, 26, 52, 78, 104, 130],
        [6, 30, 56, 82, 108, 134],
        [6, 34, 60, 86, 112, 138],
        [6, 30, 58, 86, 114, 142],
        [6, 34, 62, 90, 118, 146],
        [6, 30, 54, 78, 102, 126, 150],
        [6, 24, 50, 76, 102, 128, 154],
        [6, 28, 54, 80, 106, 132, 158],
        [6, 32, 58, 84, 110, 136, 162],
        [6, 26, 54, 82, 110, 138, 166],
        [6, 30, 58, 86, 114, 142, 170]
    ]

    G15 = (1 << 10) | (1 << 8) | (1 << 5) | (1 << 4) | (1 << 2) | (1 << 1) | (1 << 0)
    G18 = (1 << 12) | (1 << 11) | (1 << 10) | (1 << 9) | (1 << 8) | (1 << 5) | (1 << 2) | (1 << 0)
    G15_MASK = (1 << 14) | (1 << 12) | (1 << 10) | (1 << 4) | (1 << 1)

    @staticmethod
    def getBCHTypeInfo(data):
        d = data << 10;
        while (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15) >= 0):
            d ^= (QRUtil.G15 << (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G15) ) )
        return ( (data << 10) | d) ^ QRUtil.G15_MASK

    @staticmethod
    def getBCHTypeNumber(data):
        d = data << 12;
        while (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G18) >= 0):
            d ^= (QRUtil.G18 << (QRUtil.getBCHDigit(d) - QRUtil.getBCHDigit(QRUtil.G18) ) )
        return (data << 12) | d

    @staticmethod
    def getBCHDigit(data):
        digit = 0;
        while (data != 0):
            digit += 1
            data >>= 1
        return digit

    @staticmethod
    def getPatternPosition(typeNumber):
        return QRUtil.PATTERN_POSITION_TABLE[typeNumber - 1]

    @staticmethod
    def getMask(maskPattern, i, j):
        if maskPattern == QRMaskPattern.PATTERN000 : return (i + j) % 2 == 0
        if maskPattern == QRMaskPattern.PATTERN001 : return i % 2 == 0
        if maskPattern == QRMaskPattern.PATTERN010 : return j % 3 == 0
        if maskPattern == QRMaskPattern.PATTERN011 : return (i + j) % 3 == 0
        if maskPattern == QRMaskPattern.PATTERN100 : return (math.floor(i / 2) + math.floor(j / 3) ) % 2 == 0
        if maskPattern == QRMaskPattern.PATTERN101 : return (i * j) % 2 + (i * j) % 3 == 0
        if maskPattern == QRMaskPattern.PATTERN110 : return ( (i * j) % 2 + (i * j) % 3) % 2 == 0
        if maskPattern == QRMaskPattern.PATTERN111 : return ( (i * j) % 3 + (i + j) % 2) % 2 == 0
        raise Exception("bad maskPattern:" + maskPattern)

    @staticmethod
    def getErrorCorrectPolynomial(errorCorrectLength):
        a = QRPolynomial([1], 0);
        for i in xrange(errorCorrectLength):
            a = a.multiply(QRPolynomial([1, QRMath.gexp(i)], 0) )
        return a

    @staticmethod
    def getLengthInBits(mode, type):
        if 1 <= type and type < 10:
            # 1 - 9
            if mode == QRMode.MODE_NUMBER     : return 10
            if mode == QRMode.MODE_ALPHA_NUM     : return 9
            if mode == QRMode.MODE_8BIT_BYTE    : return 8
            if mode == QRMode.MODE_KANJI      : return 8
            raise Exception("mode:" + mode)
        elif (type < 27):
            # 10 - 26
            if mode == QRMode.MODE_NUMBER     : return 12
            if mode == QRMode.MODE_ALPHA_NUM     : return 11
            if mode == QRMode.MODE_8BIT_BYTE    : return 16
            if mode == QRMode.MODE_KANJI      : return 10
            raise Exception("mode:" + mode)
        elif (type < 41):
            # 27 - 40
            if mode == QRMode.MODE_NUMBER     : return 14
            if mode == QRMode.MODE_ALPHA_NUM    : return 13
            if mode == QRMode.MODE_8BIT_BYTE    : return 16
            if mode == QRMode.MODE_KANJI      : return 12
            raise Exception("mode:" + mode)
        else:
            raise Exception("type:" + type)

    @staticmethod
    def getLostPoint(qrCode):
        moduleCount = qrCode.getModuleCount();
        lostPoint = 0;
        # LEVEL1
        for row in xrange(moduleCount):
            for col in xrange(moduleCount):
                sameCount = 0;
                dark = qrCode.isDark(row, col);
                for r in xrange(-1, 2):
                    if (row + r < 0 or moduleCount <= row + r):
                        continue
                    for c in xrange(-1, 2):
                        if (col + c < 0 or moduleCount <= col + c):
                            continue
                        if (r == 0 and c == 0):
                            continue
                        if (dark == qrCode.isDark(row + r, col + c) ):
                            sameCount+=1
                if (sameCount > 5):
                    lostPoint += (3 + sameCount - 5)
        # LEVEL2
        for row in xrange(moduleCount - 1):
            for col in xrange(moduleCount - 1):
                count = 0;
                if (qrCode.isDark(row,     col    ) ): count+=1
                if (qrCode.isDark(row + 1, col    ) ): count+=1
                if (qrCode.isDark(row,     col + 1) ): count+=1
                if (qrCode.isDark(row + 1, col + 1) ): count+=1
                if (count == 0 or count == 4):
                    lostPoint += 3
        # LEVEL3
        for row in xrange(moduleCount):
            for col in xrange(moduleCount - 6):
                if (qrCode.isDark(row, col)
                        and not qrCode.isDark(row, col + 1)
                        and  qrCode.isDark(row, col + 2)
                        and  qrCode.isDark(row, col + 3)
                        and  qrCode.isDark(row, col + 4)
                        and not qrCode.isDark(row, col + 5)
                        and  qrCode.isDark(row, col + 6) ):
                    lostPoint += 40
        for col in xrange(moduleCount):
            for row in xrange(moduleCount - 6):
                if (qrCode.isDark(row, col)
                        and not qrCode.isDark(row + 1, col)
                        and  qrCode.isDark(row + 2, col)
                        and  qrCode.isDark(row + 3, col)
                        and  qrCode.isDark(row + 4, col)
                        and not qrCode.isDark(row + 5, col)
                        and  qrCode.isDark(row + 6, col) ):
                    lostPoint += 40
        # LEVEL4
        darkCount = 0;
        for col in xrange(moduleCount):
            for row in xrange(moduleCount):
                if (qrCode.isDark(row, col) ):
                    darkCount+=1
        ratio = abs(100 * darkCount / moduleCount / moduleCount - 50) / 5
        lostPoint += ratio * 10
        return lostPoint

class QRMath:
    @staticmethod
    def glog(n):
        if (n < 1):
            raise Exception("glog(" + n + ")")
        return LOG_TABLE[n];

    @staticmethod
    def gexp(n):
        while n < 0:
            n += 255
        while n >= 256:
            n -= 255
        return EXP_TABLE[n];

EXP_TABLE = [x for x in xrange(256)]
LOG_TABLE = [x for x in xrange(256)]
for i in xrange(8):
    EXP_TABLE[i] = 1 << i;
for i in xrange(8, 256):
    EXP_TABLE[i] = EXP_TABLE[i - 4] ^ EXP_TABLE[i - 5] ^ EXP_TABLE[i - 6] ^ EXP_TABLE[i - 8]
for i in xrange(255):
    LOG_TABLE[EXP_TABLE[i] ] = i

class QRPolynomial:
    def __init__(self, num, shift):
        if (len(num) == 0):
            raise Exception(num.length + "/" + shift)
        offset = 0
        while offset < len(num) and num[offset] == 0:
            offset += 1
        self.num = [0 for x in xrange(len(num)-offset+shift)]
        for i in xrange(len(num) - offset):
            self.num[i] = num[i + offset]

    def get(self, index):
        return self.num[index]

    def getLength(self):
        return len(self.num)

    def multiply(self, e):
        num = [0 for x in xrange(self.getLength() + e.getLength() - 1)];
        for i in xrange(self.getLength()):
            for j in xrange(e.getLength()):
                num[i + j] ^= QRMath.gexp(QRMath.glog(self.get(i) ) + QRMath.glog(e.get(j) ) )
        return QRPolynomial(num, 0);

    def mod(self, e):
        if (self.getLength() - e.getLength() < 0):
            return self;
        ratio = QRMath.glog(self.get(0) ) - QRMath.glog(e.get(0) )
        num = [0 for x in xrange(self.getLength())]
        for i in xrange(self.getLength()):
            num[i] = self.get(i);
        for i in xrange(e.getLength()):
            num[i] ^= QRMath.gexp(QRMath.glog(e.get(i) ) + ratio)
        # recursive call
        return QRPolynomial(num, 0).mod(e);

class QRRSBlock:
    RS_BLOCK_TABLE = [
        # L
        # M
        # Q
        # H

        # 1
        [1, 26, 19],
        [1, 26, 16],
        [1, 26, 13],
        [1, 26, 9],

        # 2
        [1, 44, 34],
        [1, 44, 28],
        [1, 44, 22],
        [1, 44, 16],

        # 3
        [1, 70, 55],
        [1, 70, 44],
        [2, 35, 17],
        [2, 35, 13],

        # 4
        [1, 100, 80],
        [2, 50, 32],
        [2, 50, 24],
        [4, 25, 9],

        # 5
        [1, 134, 108],
        [2, 67, 43],
        [2, 33, 15, 2, 34, 16],
        [2, 33, 11, 2, 34, 12],

        # 6
        [2, 86, 68],
        [4, 43, 27],
        [4, 43, 19],
        [4, 43, 15],

        # 7
        [2, 98, 78],
        [4, 49, 31],
        [2, 32, 14, 4, 33, 15],
        [4, 39, 13, 1, 40, 14],

        # 8
        [2, 121, 97],
        [2, 60, 38, 2, 61, 39],
        [4, 40, 18, 2, 41, 19],
        [4, 40, 14, 2, 41, 15],

        # 9
        [2, 146, 116],
        [3, 58, 36, 2, 59, 37],
        [4, 36, 16, 4, 37, 17],
        [4, 36, 12, 4, 37, 13],

        # 10
        [2, 86, 68, 2, 87, 69],
        [4, 69, 43, 1, 70, 44],
        [6, 43, 19, 2, 44, 20],
        [6, 43, 15, 2, 44, 16],

        # 11
        [4, 101, 81],
        [1, 80, 50, 4, 81, 51],
        [4, 50, 22, 4, 51, 23],
        [3, 36, 12, 8, 37, 13],

        # 12
        [2, 116, 92, 2, 117, 93],
        [6, 58, 36, 2, 59, 37],
        [4, 46, 20, 6, 47, 21],
        [7, 42, 14, 4, 43, 15],

        # 13
        [4, 133, 107],
        [8, 59, 37, 1, 60, 38],
        [8, 44, 20, 4, 45, 21],
        [12, 33, 11, 4, 34, 12],

        # 14
        [3, 145, 115, 1, 146, 116],
        [4, 64, 40, 5, 65, 41],
        [11, 36, 16, 5, 37, 17],
        [11, 36, 12, 5, 37, 13],

        # 15
        [5, 109, 87, 1, 110, 88],
        [5, 65, 41, 5, 66, 42],
        [5, 54, 24, 7, 55, 25],
        [11, 36, 12],

        # 16
        [5, 122, 98, 1, 123, 99],
        [7, 73, 45, 3, 74, 46],
        [15, 43, 19, 2, 44, 20],
        [3, 45, 15, 13, 46, 16],

        # 17
        [1, 135, 107, 5, 136, 108],
        [10, 74, 46, 1, 75, 47],
        [1, 50, 22, 15, 51, 23],
        [2, 42, 14, 17, 43, 15],

        # 18
        [5, 150, 120, 1, 151, 121],
        [9, 69, 43, 4, 70, 44],
        [17, 50, 22, 1, 51, 23],
        [2, 42, 14, 19, 43, 15],

        # 19
        [3, 141, 113, 4, 142, 114],
        [3, 70, 44, 11, 71, 45],
        [17, 47, 21, 4, 48, 22],
        [9, 39, 13, 16, 40, 14],

        # 20
        [3, 135, 107, 5, 136, 108],
        [3, 67, 41, 13, 68, 42],
        [15, 54, 24, 5, 55, 25],
        [15, 43, 15, 10, 44, 16],

        # 21
        [4, 144, 116, 4, 145, 117],
        [17, 68, 42],
        [17, 50, 22, 6, 51, 23],
        [19, 46, 16, 6, 47, 17],

        # 22
        [2, 139, 111, 7, 140, 112],
        [17, 74, 46],
        [7, 54, 24, 16, 55, 25],
        [34, 37, 13],

        # 23
        [4, 151, 121, 5, 152, 122],
        [4, 75, 47, 14, 76, 48],
        [11, 54, 24, 14, 55, 25],
        [16, 45, 15, 14, 46, 16],

        # 24
        [6, 147, 117, 4, 148, 118],
        [6, 73, 45, 14, 74, 46],
        [11, 54, 24, 16, 55, 25],
        [30, 46, 16, 2, 47, 17],

        # 25
        [8, 132, 106, 4, 133, 107],
        [8, 75, 47, 13, 76, 48],
        [7, 54, 24, 22, 55, 25],
        [22, 45, 15, 13, 46, 16],

        # 26
        [10, 142, 114, 2, 143, 115],
        [19, 74, 46, 4, 75, 47],
        [28, 50, 22, 6, 51, 23],
        [33, 46, 16, 4, 47, 17],

        # 27
        [8, 152, 122, 4, 153, 123],
        [22, 73, 45, 3, 74, 46],
        [8, 53, 23, 26, 54, 24],
        [12, 45, 15, 28, 46, 16],

        # 28
        [3, 147, 117, 10, 148, 118],
        [3, 73, 45, 23, 74, 46],
        [4, 54, 24, 31, 55, 25],
        [11, 45, 15, 31, 46, 16],

        # 29
        [7, 146, 116, 7, 147, 117],
        [21, 73, 45, 7, 74, 46],
        [1, 53, 23, 37, 54, 24],
        [19, 45, 15, 26, 46, 16],

        # 30
        [5, 145, 115, 10, 146, 116],
        [19, 75, 47, 10, 76, 48],
        [15, 54, 24, 25, 55, 25],
        [23, 45, 15, 25, 46, 16],

        # 31
        [13, 145, 115, 3, 146, 116],
        [2, 74, 46, 29, 75, 47],
        [42, 54, 24, 1, 55, 25],
        [23, 45, 15, 28, 46, 16],

        # 32
        [17, 145, 115],
        [10, 74, 46, 23, 75, 47],
        [10, 54, 24, 35, 55, 25],
        [19, 45, 15, 35, 46, 16],

        # 33
        [17, 145, 115, 1, 146, 116],
        [14, 74, 46, 21, 75, 47],
        [29, 54, 24, 19, 55, 25],
        [11, 45, 15, 46, 46, 16],

        # 34
        [13, 145, 115, 6, 146, 116],
        [14, 74, 46, 23, 75, 47],
        [44, 54, 24, 7, 55, 25],
        [59, 46, 16, 1, 47, 17],

        # 35
        [12, 151, 121, 7, 152, 122],
        [12, 75, 47, 26, 76, 48],
        [39, 54, 24, 14, 55, 25],
        [22, 45, 15, 41, 46, 16],

        # 36
        [6, 151, 121, 14, 152, 122],
        [6, 75, 47, 34, 76, 48],
        [46, 54, 24, 10, 55, 25],
        [2, 45, 15, 64, 46, 16],

        # 37
        [17, 152, 122, 4, 153, 123],
        [29, 74, 46, 14, 75, 47],
        [49, 54, 24, 10, 55, 25],
        [24, 45, 15, 46, 46, 16],

        # 38
        [4, 152, 122, 18, 153, 123],
        [13, 74, 46, 32, 75, 47],
        [48, 54, 24, 14, 55, 25],
        [42, 45, 15, 32, 46, 16],

        # 39
        [20, 147, 117, 4, 148, 118],
        [40, 75, 47, 7, 76, 48],
        [43, 54, 24, 22, 55, 25],
        [10, 45, 15, 67, 46, 16],

        # 40
        [19, 148, 118, 6, 149, 119],
        [18, 75, 47, 31, 76, 48],
        [34, 54, 24, 34, 55, 25],
        [20, 45, 15, 61, 46, 16]

    ]

    def __init__(self, totalCount, dataCount):
        self.totalCount = totalCount
        self.dataCount = dataCount

    @staticmethod
    def getRSBlocks(typeNumber, errorCorrectLevel):
        rsBlock = QRRSBlock.getRsBlockTable(typeNumber, errorCorrectLevel);
        if rsBlock == None:
            raise Exception("bad rs block @ typeNumber:" + typeNumber + "/errorCorrectLevel:" + errorCorrectLevel)
        length = len(rsBlock) / 3
        list = []
        for i in xrange(length):
            count = rsBlock[i * 3 + 0]
            totalCount = rsBlock[i * 3 + 1]
            dataCount  = rsBlock[i * 3 + 2]
            for j in xrange(count):
                list.append(QRRSBlock(totalCount, dataCount))
        return list;

    @staticmethod
    def getRsBlockTable(typeNumber, errorCorrectLevel):
        if errorCorrectLevel == QRErrorCorrectLevel.L:
            return QRRSBlock.RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 0];
        elif errorCorrectLevel == QRErrorCorrectLevel.M:
            return QRRSBlock.RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 1];
        elif errorCorrectLevel ==  QRErrorCorrectLevel.Q:
            return QRRSBlock.RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 2];
        elif errorCorrectLevel ==  QRErrorCorrectLevel.H:
            return QRRSBlock.RS_BLOCK_TABLE[(typeNumber - 1) * 4 + 3];
        else:
            return None;

class QRBitBuffer:
    def __init__(self):
        self.buffer = []
        self.length = 0

    def __repr__(self):
        return ".".join([str(n) for n in self.buffer])

    def get(self, index):
        bufIndex = math.floor(index / 8)
        val = ( (self.buffer[bufIndex] >> (7 - index % 8) ) & 1) == 1
        return ( (self.buffer[bufIndex] >> (7 - index % 8) ) & 1) == 1

    def put(self, num, length):
        for i in xrange(length):
            self.putBit( ( (num >> (length - i - 1) ) & 1) == 1)

    def getLengthInBits(self):
        return self.length

    def putBit(self, bit):
        bufIndex = self.length // 8
        if len(self.buffer) <= bufIndex:
            self.buffer.append(0)
        if bit:
            self.buffer[bufIndex] |= (0x80 >> (self.length % 8) )
        self.length += 1
