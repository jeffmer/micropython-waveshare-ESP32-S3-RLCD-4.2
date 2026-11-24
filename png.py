import framebuf
import pngdec

png = pngdec.PNG()

def getPNG(fn,key=0xFFFF):
    png.open_file(fn)
    w,h = png.width, png.height
    buf = bytearray(w * h * 2)  # RGB565
    png.decode(buf)
    fbuf = framebuf.FrameBuffer(buf, w, h, framebuf.RGB565)
    f = framebuf.FrameBuffer(bytearray(w*((h+7)//8)), w, h, framebuf.MONO_VLSB)
    for r in range(0,h):
        for c in range(0,w):
            if fbuf.pixel(c,r) == key:
                f.pixel(c, r, 0)
            else:
                f.pixel(c,r,1)
    return (w, h, f, 0xFFFF)

def drawPNG(g,im, x, y):
    g.updateMod(x, y, x + im[0] - 1, y + im[1] - 1)
    g.blit(im[2], x, y, im[3])