import time, framebuf, graphics


FRAMERATE_1 = (0x39, 0x02) # (best quality) 0x39-LPM 0x02-HPM_16Hz_LPM_1Hz
FRAMERATE_8 = (0x39, 0x05) # (best quality) 0x39-LPM 0x05-HPM_16Hz_LPM_8Hz
FRAMERATE_16 = (0x38, 0x05) # (best quality) 0x38-HPM 0x05-HPM_16Hz_LPM_8Hz
FRAMERATE_32 = (0x38, 0x15) # (lower quality) 0x38-HPM 0x15-HPM_32Hz_LPM_8Hz

WIDTH = 400
HEIGHT = 300
BUFFER_HEIGHT = (HEIGHT + 7) // 8
NATIVE_WIDTH = HEIGHT
NATIVE_HEIGHT = WIDTH
NATIVE_COLUMN_GROUPS = NATIVE_WIDTH // 12
NATIVE_ROW_ADDRESSES = NATIVE_HEIGHT // 2
FRAMERATE_DEFAULT = (0x38, 0x02)

class ST7305(graphics.Graphics):
    """Waveshare 4.2-inch, 400x300 reflective LCD framebuffer."""
    def __init__(self, spi, cs_pin, dc_pin, res_pin, te_pin = None, framerate = FRAMERATE_DEFAULT):
        self.spi = spi
        self.cs = cs_pin
        self.dc = dc_pin
        self.rs = res_pin
        self.bs = bytearray(WIDTH * BUFFER_HEIGHT)
        super().__init__(self.bs, WIDTH, HEIGHT, framebuf.MONO_VLSB)
        # The controller packs each 4x2-pixel block into one byte.
        self.bt = bytearray((NATIVE_WIDTH * NATIVE_HEIGHT) // 8)
        self.interleave = bytearray(256)
        for first_nibble in range(16):
            for second_nibble in range(16):
                packed = 0
                for pixel in range(4):
                    packed |= ((first_nibble >> (3 - pixel)) & 1) << (7 - pixel * 2)
                    packed |= ((second_nibble >> (3 - pixel)) & 1) << (6 - pixel * 2)
                self.interleave[(first_nibble << 4) | second_nibble] = packed
        # cache
        self.cmd = bytearray(1)
        self.caset = bytearray([0x12, 0x12 + NATIVE_COLUMN_GROUPS - 1])
        self.raset = bytearray([0x00, NATIVE_ROW_ADDRESSES - 1])
        # start
        self._init(framerate)
    
    def _send(self, command, data = None):
        self.cmd[0] = command
        self.dc.value(0)  # Command mode
        self.cs.value(0)
        self.spi.write(self.cmd)
        self.cs.value(1)
        self.dc.value(1) # Data mode
        if data:
            self.cs.value(0)
            if isinstance(data, bytearray) or isinstance(data, memoryview):
                self.spi.write(data)
            else:
                self.spi.write(bytearray(data))
            self.cs.value(1)
    
    def _init(self, framerate):
        # reset
        time.sleep_ms(50)
        self.rs.value(0)
        time.sleep_ms(100)
        self.rs.value(1)
        
        # (command, data...)
        commands = [
            (0xD6, [0x13, 0x02]), # NVM Load Control (0x17 0xXX Enable VS/ID, 0x13 0xXX Enable ID)
            (0xD1, [0x01]), # Booster Enable 
            (0xC0, [0x11, 0x04]), # Gate Voltage Setting
            (0xC1, [0x69, 0x69, 0x69, 0x69]), # VSHP Setting
            (0xC2, [0x19, 0x19, 0x19, 0x19]), # VSLP Setting
            (0xC4, [0x4B, 0x4B, 0x4B, 0x4B]), # VSHN Setting
            (0xC5, [0x19, 0x19, 0x19, 0x19]), # VSLN Setting
            (0xD8, [0x80, 0xE9]), # Oscillator Setting
            (0xB2, [framerate[1]]), # Frame Rate Control
            (0xB3, [0xE5, 0xF6, 0x17, 0x77, 0x77, 0x77, 0x77, 0x77, 0x77, 0x71]), # Update Period Gate EQ Control in HPM
            (0xB4, [0x05, 0x46, 0x77, 0x77, 0x77, 0x77, 0x76, 0x45]), # Update Period Gate EQ Control in LPM
            (0x62, [0x32, 0x03, 0x1F]), # Gate Timing Control
            (0xB7, [0x13]), # Source EQ Enable
            (0xB0, [NATIVE_HEIGHT // 4]), # Gate Line Setting in 4-line units
            
            (0x11, []), # Sleep out
            100, # delay 100ms
            (0xC9, [0x00]), # Source Voltage Select: VSHP1; VSLP1 ; VSHN1 ; VSLN1
            (0x36, [0x48]), # Memory Data Access Control
            (0x3A, [0x11]), # Data Format Select: 10:4write for 24bit ; 11: 3write for 24bit
            (0xB9, [0x20]), # Gamma Mode Setting: 20: Mono; 00:4GS
            (0xB8, [0x29]), # Panel Setting: 0x29: 1-Dot inversion, Frame inversion, One Line Interlace
            (0x2A, [self.caset[0], self.caset[1]]), # Column Address Setting
            (0x2B, [self.raset[0], self.raset[1]]), # Row Address Setting
            (0x35, [0x00]), # TE
            (0xD0, [0xFF]), # Auto power down
            (framerate[0], []), # 0x38 HPM; 0x39 LPM
            (0x29, []), # Display on
            (0x20, []), # Display inversion off
            (0xBB, [0x4F]), # Clear controller RAM
            100, # delay 100ms
        ]       
        for command in commands:
            if isinstance(command, tuple):
                self._send(command[0], command[1])
            else:
                time.sleep_ms(command)

    @micropython.viper
    def _convert_chunk(self, xs: int, xe: int, ys: int, ye: int):
        # xs - start horizontal pixel (0..399)
        # xe - last horizontal pixel (0..399)
        # ys - start vertical pixel (0..299)
        # ye - last vertical pixel (0..299)
        if xs < 0:
            xs = 0
        if xe > 399:
            xe = 399
        if ys < 0:
            ys = 0
        if ye > 299:
            ye = 299
        if xs > xe or ys > ye:
            return

        # Align horizontal coordinates to 8-pixel boundaries (within 0..400)
        x_start = xs & ~7
        x_end = (xe + 8) & ~7
        if x_end > 400:
            x_end = 400

        # In ST7305 native mapping:
        # column = 299 - y0, stepping by 4 pixels downwards in y.
        # Aligning to 8-pixel boundaries ensures column aligns to 8 pixels.
        # col_start corresponds to ye (the largest y):
        col_start = (299 - ye) & ~7
        # col_end corresponds to ys (the smallest y):
        col_end = ((299 - ys) & ~7) + 8
        if col_end > 300:
            col_end = 300

        s = ptr8(self.bs)
        t = ptr8(self.bt)
        lut = ptr8(self.interleave)

        for x0 in range(x_start, x_end, 2):
            x1 = x0 + 1
            k_base = (x0 >> 1) * 75
            for column in range(col_start, col_end, 4):
                y0 = 299 - column
                page = (y0 >> 3) * 400
                shift = (y0 & 7) - 3
                first_nibble = (s[page + x0] >> shift) & 0x0F
                second_nibble = (s[page + x1] >> shift) & 0x0F
                t[k_base + (column >> 2)] = lut[(first_nibble << 4) | second_nibble]

    def show(self):
        xs,xe,ys,ye = self.getMod()
        self._convert_chunk(xs,xe,ys,ye)
        self._send(0x2A, self.caset)
        self._send(0x2B, self.raset)
        self._send(0x2C, self.bt)
