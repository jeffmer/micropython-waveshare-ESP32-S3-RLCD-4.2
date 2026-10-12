import framebuf
from micropython import const
from fonts import glcdfont
import math

BLACK = const(0)
WHITE = const(1)


def rotate(coord, theta):
    "rotates an integer array of coordinates by angle theta"
    sinr = math.sin(theta)
    cosr = math.cos(theta)
    for i in range(0, len(coord), 2):
        x, y = coord[i], coord[i + 1]
        coord[i] = math.ceil(x * cosr - y * sinr)
        coord[i + 1] = math.ceil(x * sinr + y * cosr)
    return coord

class Graphics(framebuf.FrameBuffer):
    def __init__(self, buf, w, h, mode):
        self.width = w
        self.height = h
        self._font = glcdfont
        self._align = (-1, -1)  # top left
        self._buf = buf
        super().__init__(buf, w, h, mode)

    def poly(self, x, y, coord, c, f=False, theta=None):
        if theta is not None:
            coord = rotate(coord, theta)
        super().poly(x, y, coord, c, f)

    def setfont(self, font):
        self._font = font

    def getfont(self):
        return self._font

    def setfontalign(self, xalign, yalign):
        self._align = (xalign, yalign)

    def text_dim(self, str):
        return self._font.get_width(str), self._font.height()

    def text(self, str, x, y, c):
        "write a string of text.  c ic color of letters"
        str_w, str_h = self.text_dim(str)
        x_a, y_a = self._align
        x = x if x_a == -1 else x - str_w if x_a == 1 else x - str_w // 2
        y = y if y_a == -1 else y - str_h if y_a == 1 else y - str_h // 2
        div, rem = divmod(str_h, 8)
        nbytes = div + 1 if rem else div
        buf = bytearray(str_w * nbytes)
        pos = 0
        for ch in str:
            glyph, char_w = self._font.get_ch(ch)
            for row in range(nbytes):
                index = row * str_w + pos
                for i in range(char_w):
                    buf[index + i] = glyph[nbytes * i + row]
            pos += char_w
        fb = framebuf.FrameBuffer(buf, str_w, str_h, framebuf.MONO_VLSB)
        self.blit(fb, x, y)
        return str_w

    def wordwraptext(self, str, x, y, w, c):
        "write a string of text of color c. Automatically wrap text if the width is larger than w"
        curx = x
        cury = y
        char_h = self._font.height()
        char_w = self._font.max_width()
        lines = str.split("\n")
        for line in lines:
            words = line.split(" ")
            for word in words:
                ww = self._font.get_width(word)
                if curx + ww >= w:
                    curx = x
                    cury += char_h
                    while ww > w:
                        self.text(word[: w // char_w], curx, cury, c)
                        word = word[w // char_w :]
                        cury += char_h
                if len(word) > 0:
                    curx += self.text(word + " ", curx, cury, c)
            curx = x
            cury += char_h

    def screendump(self, name):
        with open(name + ".raw", "wb") as f:
            f.write(bytes(self._buf))
            f.close()
