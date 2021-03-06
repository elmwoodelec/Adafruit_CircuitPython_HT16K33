# The MIT License (MIT)
#
# Copyright (c) 2016 Radomir Dopieralski & Tony DiCola for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
`adafruit_ht16k33.ht16k33`
===========================

* Authors: Radomir Dopieralski & Tony DiCola for Adafruit Industries

"""

from adafruit_bus_device import i2c_device
from micropython import const


_HT16K33_BLINK_CMD = const(0x80)
_HT16K33_BLINK_DISPLAYON = const(0x01)
_HT16K33_CMD_BRIGHTNESS = const(0xE0)
_HT16K33_OSCILATOR_ON = const(0x21)


class HT16K33:
    """The base class for all displays. Contains common methods."""
    def __init__(self, i2c, address=0x70):
        self.i2c_device = i2c_device.I2CDevice(i2c, address)
        self._temp = bytearray(1)
        self._buffer = bytearray(17)
        self.fill(0)
        self._write_cmd(_HT16K33_OSCILATOR_ON)
        self._blink_rate = None
        self._brightness = None
        self.blink_rate(0)
        self.brightness(15)

    def _write_cmd(self, byte):
        self._temp[0] = byte
        with self.i2c_device:
            self.i2c_device.write(self._temp)

    def blink_rate(self, rate=None):
        """The blink rate. Range 0-3."""
        if rate is None:
            return self._blink_rate
        rate = rate & 0x03
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD |
                        _HT16K33_BLINK_DISPLAYON | rate << 1)
        return None

    def brightness(self, brightness):
        """The brightness. Range 0-15."""
        if brightness is None:
            return self._brightness
        brightness = brightness & 0x0F
        self._brightness = brightness
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | brightness)
        return None

    def show(self):
        """Refresh the display and show the changes."""
        with self.i2c_device:
            # Byte 0 is 0x00, address of LED data register. The remaining 16
            # bytes are the display register data to set.
            self.i2c_device.write(self._buffer)

    def fill(self, color):
        """Fill the whole display with the given color."""
        fill = 0xff if color else 0x00
        for i in range(16):
            self._buffer[i+1] = fill

    def _pixel(self, x, y, color=None):
        mask = 1 << x
        if color is None:
            return bool((self._buffer[y + 1] | self._buffer[y + 2] << 8) & mask)
        if color:
            self._buffer[(y * 2) + 1] |= mask & 0xff
            self._buffer[(y * 2) + 2] |= mask >> 8
        else:
            self._buffer[(y * 2) + 1] &= ~(mask & 0xff)
            self._buffer[(y * 2) + 2] &= ~(mask >> 8)
        return None

    def _set_buffer(self, i, value):
        self._buffer[i+1] = value  # Offset by 1 to move past register address.

    def _get_buffer(self, i):
        return self._buffer[i+1]   # Offset by 1 to move past register address.
