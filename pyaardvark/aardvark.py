# Copyright (c) 2014  Kontron Europe GmbH
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import time
import array
import logging
import sys

from .constants import *

if sys.platform.startswith('linux'):
    try:
        from .ext.linux32 import aardvark as api
    except ImportError:
        try:
            from .ext.linux64 import aardvark as api
        except:
            api = None
elif sys.platform.startswith('win32'):
    try:
        from .ext.win32 import aardvark as api
    except ImportError:
        try:
            from .ext.win64 import aardvark as api
        except:
            api = None
else:
    api = None

if not api:
    raise RuntimeError('Unable to find suitable binary interface. '
            'Unsupported platform?')

          
log = logging.getLogger(__name__)

def error_string(error_number):
    for k, v in globals().items():
        if k.startswith('ERR_') and v == error_number:
            return k
    else:
        return 'ERR_UNKNOWN_ERROR'

def _raise_error_if_negative(val):
    if val < 0:
        raise IOError(error_string(val))


        
def find_devices(filter_in_use=True):
    """Return a list of port numbers which can be used with :func:`open`.

    If *filter_in_use* parameter is `True` devices which are already opened
    will be filtered from the list. If set to `False`, the port numbers are
    still included in the returned list and the user may get an
    :class:`IOError` if the port number is used with :func:`open`.

    .. note::

       There is no guarantee, that the returned port numbers are still valid
       when you open the device with it. Eg. it may be disconnected from the
       machine after you call :func:`find_devices` but before you call
       :func:`open`.
    """
    
    # first fetch the number of attached devices, so we can create a buffer
    # with the exact amount of entries. api expects array of u16
    num_devices = api.py_aa_find_devices(0, array.array('H'))
    assert num_devices > 0
    devices = array.array('H', (0,) * num_devices)
    
    num_devices = api.py_aa_find_devices(len(devices), devices)
    assert num_devices > 0
    
    del devices[num_devices:]

    if filter_in_use:
        devices = [ d for d in devices if not d & PORT_NOT_FREE ]
    else:
        devices = [ d & ~PORT_NOT_FREE for d in devices]
        
    return devices

def open(port=None, serial_number=None):
    """Open an aardvark device and return an :class:`Aardvark` object. If the
    device cannot be opened an :class:`IOError` is raised.

    The `port` can be retrieved by :func:`find_devices`. Usually, the first
    device is 0, the second 1, etc.

    If you are using only one device, you can therefore omit the parameter
    in which case 0 is used.

    Another method to open a device is to use the serial number. You can either
    find the number on the device itself or in the in the corresponding USB
    property. The serial number is a string which looks like `NNNN-MMMMMMM`.

    Raises an :class:`IOError` if the port number (or serial number) does not
    exist, is already connected or an incompatible device is found.
    """
    if port is None and serial_number is None:
        dev = Aardvark(0)
    elif serial_number is not None:
        for port in find_devices(True):
            dev = Aardvark(port)
            if dev.unique_id_str() == serial_number:
                break
            dev.close()
        else:
            raise IOError(error_string(ERR_UNABLE_TO_OPEN))
    else:
        dev = Aardvark(port)

    return dev

class Aardvark(object):
    """Represents an Aardvark device."""
    BUFFER_SIZE = 65535

    def __init__(self, port=0):
        ret, ver = api.py_aa_open_ext(port)
            
        _raise_error_if_negative(ret)

        #: A handle which is used as the first paramter for all calls to the
        #: underlying API.
        self.handle = ret

        # assign some useful names
        version = dict(
            software = ver[0],
            firmware = ver[1],
            hardware = ver[2],
            sw_req_by_fw = ver[3],
            fw_req_by_sw = ver[4],
            api_req_by_sw = ver[5],
        )

        to_version_str = lambda v: '%d.%02d' % (v >> 8, v & 0xff)

        #: Hardware revision of the host adapter as a string. The format is
        #: ``M.NN`` where `M` is the major number and `NN` the zero padded
        #: minor number.
        self.hardware_revision = to_version_str(version['hardware'])

        #: Firmware version of the host adapter as a string. See
        #: :attr:`hardware_revision` for more information on the format.
        self.firmware_version = to_version_str(version['firmware'])

        #: Version of underlying C module (aardvark.so, aardvark.dll) as a
        #: string. See :attr:`hardware_revision` for more information on the
        #: format.
        self.api_version = to_version_str(version['software'])

        # version checks
        if version['firmware'] < version['fw_req_by_sw']:
            log.debug('The API requires a firmware version >= %s, but the '
                    'device has version %s',
                    to_version_str(version['fw_req_by_sw']),
                    to_version_str(version['firmware']))
            ret = ERR_INCOMPATIBLE_DEVICE
        elif version['software'] < version['sw_req_by_fw']:
            log.debug('The firmware requires an API version >= %s, but the '
                    'API has version %s',
                    to_version_str(version['sw_req_by_fw']),
                    to_version_str(version['software']))
            ret = ERR_INCOMPATIBLE_LIBRARY

        _raise_error_if_negative(ret)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()
        return False

    def close(self):
        """Close the device."""
        api.py_aa_close(self.handle)
        self.handle = None

    def unique_id(self):
        """Return the unique identifier of the device. The identifier is the
        serial number you can find on the adapter without the dash. Eg. the
        serial number 0012-345678 would be 12345678.
        """
        return api.py_aa_unique_id(self.handle)

    def unique_id_str(self):
        """Return the unique identifier. But unlike :func:`unique_id`, the ID
        is returned as a string which has the format NNNN-MMMMMMM.
        """
        unique_id = self.unique_id()
        id1 = unique_id / 1000000
        id2 = unique_id % 1000000
        return '%04d-%06d' % (id1, id2)

    def _interface_configuration(self, value):
        ret = api.py_aa_configure(self.handle, value)
        _raise_error_if_negative(ret)
        return ret

    @property
    def enable_i2c(self):
        """Set this to `True` to enable the hardware I2C interface. If set to
        `False` the hardware interface will be disabled and its pins (SDA and
        SCL) can be used as GPIOs.
        """
        config = self._interface_configuration(CONFIG_QUERY)
        return config == CONFIG_GPIO_I2C or config == CONFIG_SPI_I2C

    @enable_i2c.setter
    def enable_i2c(self, value):
        new_config = config = self._interface_configuration(CONFIG_QUERY)
        if value and config == CONFIG_GPIO_ONLY:
            new_config = CONFIG_GPIO_I2C
        elif value and config == CONFIG_SPI_GPIO:
            new_config = CONFIG_SPI_I2C
        elif not value and config == CONFIG_GPIO_I2C:
            new_config = CONFIG_GPIO_ONLY
        elif not value and config == CONFIG_SPI_I2C:
            new_config = CONFIG_SPI_GPIO
        if new_config != config:
            self._interface_configuration(new_config)

    @property
    def enable_spi(self):
        """Set this to `True` to enable the hardware SPI interface. If set to
        `False` the hardware interface will be disabled and its pins (MISO,
        MOSI, SCK and SS) can be used as GPIOs.
        """
        config = self._interface_configuration(CONFIG_QUERY)
        return config == CONFIG_SPI_GPIO or config == CONFIG_SPI_I2C

    @enable_spi.setter
    def enable_spi(self, value):
        new_config = config = self._interface_configuration(CONFIG_QUERY)
        if value and config == CONFIG_GPIO_ONLY:
            new_config = CONFIG_SPI_GPIO
        elif value and config == CONFIG_GPIO_I2C:
            new_config = CONFIG_SPI_I2C
        elif not value and config == CONFIG_SPI_GPIO:
            new_config = CONFIG_GPIO_ONLY
        elif not value and config == CONFIG_SPI_I2C:
            new_config = CONFIG_GPIO_I2C
        if new_config != config:
            self._interface_configuration(new_config)

    @property
    def i2c_bitrate(self):
        """I2C bitrate in kHz. Not every bitrate is supported by the host
        adapter. Therefore, the actual bitrate may be less than the value which
        is set.

        The power-on default value is 100 kHz.
        """
        ret = api.py_aa_i2c_bitrate(self.handle, 0)
        _raise_error_if_negative(ret)
        return ret

    @i2c_bitrate.setter
    def i2c_bitrate(self, value):
        ret = api.py_aa_i2c_bitrate(self.handle, value)
        _raise_error_if_negative(ret)

    @property
    def i2c_pullups(self):
        """Setting this to `True` will enable the I2C pullup resistors. If set
        to `False` the pullup resistors will be disabled.

        Raises an :exc:`IOError` if the hardware adapter does not support
        pullup resistors.
        """
        ret = api.py_aa_i2c_pullup(self.handle, I2C_PULLUP_QUERY)
        _raise_error_if_negative(ret)

    @i2c_pullups.setter
    def i2c_pullups(self, value):
        if value:
            pullup = I2C_PULLUP_BOTH
        else:
            pullup = I2C_PULLUP_NONE
        ret = api.py_aa_i2c_pullup(self.handle, pullup)
        _raise_error_if_negative(ret)

    @property
    def target_power(self):
        """Setting this to `True` will activate the power pins (4 and 6). If
        set to `False` the power will be deactivated.

        Raises an :exc:`IOError` if the hardware adapter does not support
        the switchable power pins.
        """
        ret = api.py_aa_target_power(self.handle, TARGET_POWER_QUERY)
        _raise_error_if_negative(ret)


    @target_power.setter
    def target_power(self, value):
        if value:
            power = TARGET_POWER_BOTH
        else:
            power = TARGET_POWER_NONE
        ret = api.py_aa_target_power(self.handle, power)
        _raise_error_if_negative(ret)

    def i2c_master_write(self, i2c_address, data, flags=I2C_NO_FLAGS):
        """Make an I2C write access.

        The given I2C device is addressed and data given as a string is
        written. The transaction is finished with an I2C stop condition unless
        I2C_NO_STOP is set in the flags.

        10 bit addresses are supported if the I2C_10_BIT_ADDR flag is set.
        """

        data = array.array('B', data)
        ret = api.py_aa_i2c_write(self.handle, i2c_address,
                flags, len(data), data)
        _raise_error_if_negative(ret)

    def i2c_master_read(self, addr, length, flags=I2C_NO_FLAGS):
        """Make an I2C read access.

        The given I2C device is addressed and clock cycles for `length` bytes
        are generated. A short read will occur if the device generates an early
        NAK.

        The transaction is finished with an I2C stop condition unless the
        I2C_NO_STOP flag is set.
        """

        data = array.array('B', (0,) * length)
        print length
        ret = api.py_aa_i2c_read(self.handle, addr, flags, length,
                data)
        _raise_error_if_negative(ret)
        print data
        del data[ret:]
        return data.tostring()

    def i2c_master_write_read(self, i2c_address, data, length):
        """Make an I2C write/read access.

        First an I2C write access is issued. No stop condition will be
        generated. Instead the read access begins with a repeated start.

        This method is useful for accessing most addressable I2C devices like
        EEPROMs, port expander, etc.

        Basically, this is just a convinient function which interally uses
        `i2c_master_write` and `i2c_master_read`.
        """

        self.i2c_master_write(i2c_address, data, I2C_NO_STOP)
        return self.i2c_master_read(i2c_address, length)

    def i2c_slave_enable(self, slave_address):
        """Enable slave mode.

        The device will respond to the specified slave_address if it is
        addressed.

        You can wait for the data with `poll` and get it with
        `i2c_slave_read`.
        """
        ret = api.py_aa_i2c_slave_enable(self.handle, slave_address,
                self.BUFFER_SIZE, self.BUFFER_SIZE)
        _raise_error_if_negative(ret)

    def poll(self, timeout_ms):
        """Wait for an event to occur.

        Returns a bitfield of event flags.
        """
        ret = api.py_aa_async_poll(self.handle, timeout_ms)
        _raise_error_if_negative(ret)
        return ret

    def i2c_slave_read(self):
        """Read the bytes from an I2C slave reception.

        The bytes are returns as an string object.
        """
        data = array.array('B', (0,) * self.BUFFER_SIZE)
        (ret, slave_addr) = api.py_aa_i2c_slave_read(self.handle, self.BUFFER_SIZE,
                data)
        _raise_error_if_negative(ret)
        del data[ret:]
        return (slave_addr, data.tostring())

    @property
    def spi_bitrate(self):
        """SPI bitrate in kHz. Not every bitrate is supported by the host
        adapter. Therefore, the actual bitrate may be less than the value which
        is set. The slowest bitrate supported is 125kHz. Any smaller value will
        be rounded up to 125kHz.

        The power-on default value is 1000 kHz.
        """
        ret = api.py_aa_spi_bitrate(self.handle, 0)
        _raise_error_if_negative(ret)
        return ret

    @spi_bitrate.setter
    def spi_bitrate(self, value):
        ret = api.py_aa_spi_bitrate(self.handle, value)
        _raise_error_if_negative(ret)

    def spi_configure(self, polarity, phase, bitorder):
        """Configure the SPI interface."""
        ret = api.py_aa_spi_configure(self.handle, polarity, phase, bitorder)
        _raise_error_if_negative(ret)

    def spi_configure_mode(self, spi_mode):
        """Configure the SPI interface by the well known SPI modes."""
        if spi_mode == SPI_MODE_0:
            self.spi_configure(SPI_POL_RISING_FALLING,
                    SPI_PHASE_SAMPLE_SETUP, SPI_BITORDER_MSB)
        elif spi_mode == SPI_MODE_3:
            self.spi_configure(SPI_POL_FALLING_RISING,
                    SPI_PHASE_SETUP_SAMPLE, SPI_BITORDER_MSB)
        else:
            raise RuntimeError('SPI Mode not supported')

    def spi_write(self, data):
        "Write a stream of bytes to a SPI device."""
        data_out = array.array('B', data)
        data_in = array.array('B', (0,) * len(data_out))
        ret = api.py_aa_spi_write(self.handle, len(data_out), data_out,
                len(data_in), data_in)
        _raise_error_if_negative(ret)
        return data_in.tostring()

    def spi_ss_polarity(self, polarity):
        """Change the ouput polarity on the SS line.

        Please note, that this only affects the master functions.
        """
        ret = api.py_aa_spi_master_ss_polarity(self.handle, polarity)
        _raise_error_if_negative(ret)
  