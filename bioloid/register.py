"""Contains the Register class and derived classes."""

import sys
from bioloid.parse_utils import parse_int, parse_float
from bioloid import packet


def get_register_class(reg_type):
    """Returns the derived register class for the indicated type."""
    reg_class_name = "Register" + reg_type
    try:
        reg_class = getattr(sys.modules[__name__], reg_class_name)
    except AttributeError:
        return None
    return reg_class


class Register(object):
    """The Register class represents a single register contained within
    a device type, and may be a base class. Derived classes will typically
    override the fmt_derived and parse_derived methods.

    """

    def __init__(self, offset, name, size, access, min_raw, max_raw):
        self.reg_offset = offset
        self.reg_name = name
        self.reg_size = size
        self.reg_access = access
        self.reg_min_raw = min_raw
        self.reg_max_raw = max_raw

    def name(self):
        """Returns the name of the register."""
        return self.reg_name

    def offset(self):
        """Returns the offset of the register within the control table."""
        return self.reg_offset

    def size(self):
        """Returns the size of the register, in bytes."""
        return self.reg_size

    def access(self):
        """Returns 'ro' or 'rw' depending on whether the register is
        read-only or writable.

        """
        return self.reg_access

    def is_writable(self):
        """An alternative accessor to determine if the register is
        writable.

        """
        return self.reg_access == "rw"

    def min_raw(self):
        """Returns the minimum allowed raw value that the register is
        allowed.

        """
        return self.reg_min_raw

    def max_raw(self):
        """Returns the maximum allowed raw value that the register is
        allowed.

        """
        return self.reg_max_raw

    def type(self):
        """Returns the type of the register."""
        # Strip off "Register" from the class name
        return self.__class__.__name__[8:]

    def fmt_raw(self, raw_val):
        """Converts a number into a raw formatted value."""
        if raw_val is None:
            return ""
        return str(raw_val)

    def fmt(self, raw_val):
        """Converts a number into a formatted value based on the type of the
        register.

        """
        if raw_val is None:
            return ""
        return self.raw_to_str(raw_val)

    def parse_raw(self, string):
        """Parses a string to convert it into a raw register value."""
        raw_val = parse_int(string, "value")
        self.check_range(raw_val, string)
        return raw_val

    def parse(self, string):
        """Parses a string from its typed numeric value and converts it
        into a raw value.

        """
        raw_val = self.str_to_raw(string)
        self.check_range(raw_val, string)
        return raw_val

    def check_range(self, raw_val, string):
        """Verifies that raw_val is within the range of allowed values
        for the register.

        Returns an error string if raw_val is out of range, or None
        if raw_val is within range.

        """
        if (self.reg_min_raw is not None and self.reg_max_raw is not None and
                (raw_val < self.reg_min_raw or raw_val > self.reg_max_raw)):
            raise ValueError("%s %s is out of the allowed of range %s to %s"
                             % (self.type(),
                                string,
                                self.fmt(self.reg_min_raw),
                                self.fmt(self.reg_max_raw)))

    def raw_to_val(self, raw_val):
        """Converts a raw value into its value representation.

        This function will normally be overridden by a derived class.
        Raises a ValueError exception if an error occurs.

        """
        return int(raw_val)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        This function will normally be overridden by a derived class.
        Raises a ValueError exception if an error occurs.

        """
        return int(val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        This function will normally be overridden by a derived class.
        Raises a ValueError exception if an error occurs.

        """
        return str(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        This function will normally be overridden by a derived class.
        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_int(string))

    def from_raw(self, raw_val):
        """Converts a raw value into its baud rate representation."""
        return int(raw_val)


class RegisterBaudRate(Register):
    """Implements the BaudRate register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its baud rate  representation.

        Raises a ValueError exception if an error occurs.

        """
        return int(2000000 / (raw_val + 1))

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        if val:
            return int((2000000 / val) - 1)
        raise ValueError("Expecting non-zero baudrate")

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%d bps" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_int(string, "baud rate"))


class RegisterRDT(Register):
    """Implements the RDT (Return Delay Time) register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its RDT representation.

        Raises a ValueError exception if an error occurs.

        """
        return int(raw_val * 2)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return int(val / 2)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%d usec" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_int(string, "RDT"))


class RegisterAngle(Register):
    """Implements the Angle register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its angle representation.

        Raises a ValueError exception if an error occurs.

        """
        return float((raw_val * 300.0) / 1023.0)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return int((val * 1023.0) / 300.0)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%.1f deg" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_float(string, "angle"))


class RegisterTemperature(Register):
    """Implements the Temperature register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its angle representation.

        Raises a ValueError exception if an error occurs.

        """
        return int(raw_val)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return int(val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%dC" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_int(string, "temperature"))


class RegisterVoltage(Register):
    """Implements the Voltage register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its voltage representation.

        Raises a ValueError exception if an error occurs.

        """
        return float(raw_val / 10.0)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return int(val * 10.0)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%.1fV" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_float(string, "voltage"))


class RegisterStatusRet(Register):
    """Implements the StatusRet (Status Return) register type."""

    lookup = ['none', 'read', 'all']

    def raw_to_val(self, raw_val):
        """Converts a raw value into its StatusRet representation.

        Raises a ValueError exception if an error occurs.

        """
        if raw_val < len(RegisterStatusRet.lookup):
            return RegisterStatusRet.lookup[raw_val]
        return str(raw_val)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        val = val.lower()
        if val in RegisterStatusRet.lookup:
            return RegisterStatusRet.lookup.index(val)
        raise ValueError("Unrecognized StatusRet: '%s'" % val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)


class RegisterAlarm(Register):
    """Implements the Alarm register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its StatusRet representation.

        Raises a ValueError exception if an error occurs.

        """
        if raw_val == 0x7f:
            return "All"
        return str(packet.ErrorCode(raw_val))

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return packet.ErrorCode.parse(val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)


class RegisterOnOff(Register):
    """Implements the OnOff register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its OnOff representation.

        Raises a ValueError exception if an error occurs.

        """
        return "on" if raw_val else "off"

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        if isinstance(val, str):
            val = val.lower()
            if val == "on" or val == "1":
                return 1
            if val == "off" or val == "0":
                return 0
        else:
            if val == 0 or val == 1:
                return val
        raise ValueError("Invalid OnOff value '%s'" % val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)


class RegisterDirection(Register):
    """Implements the OnOff register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its Direction representation.

        Raises a ValueError exception if an error occurs.

        """
        return "output" if raw_val else "input"

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        if isinstance(val, str):
            val = val.lower()
            if val == "output" or val == "1":
                return 1
            if val == "input" or val == "0":
                return 0
        else:
            if val == 0 or val == 1:
                return val
        raise ValueError("Invalid Register value '%s'" % val)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)


class RegisterAngularVelocity(Register):
    """Implements the AngularVelocity (RPM) register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its anglular velocity representation.

        Raises a ValueError exception if an error occurs.

        """
        return float((raw_val * 114.0) / 1023.0)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        return int((val / 114.0) * 1023.0)

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return "%.1f RPM" % self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(parse_float(string, "anglular velocity"))


class RegisterLoad(Register):
    """Implements the Load register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its voltage representation.

        Raises a ValueError exception if an error occurs.

        """
        val = int(raw_val)
        if raw_val & 0x400:
            return -(val & 0x3ff)
        return val

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        if val < 0:
            return -int(val) | 0x400
        return int(val) & 0x3ff

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        val = int(raw_val)
        if val & 0x400:
            return "CW %d" % (val & 0x3ff)
        return "CCW %d" % (val & 0x3ff)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        raise ValueError("Parsing a load not supported yet.")


class RegisterPin(Register):
    """Implements the Pin register type."""

    def raw_to_val(self, raw_val):
        """Converts a raw value into its Pin representation.

        Raises a ValueError exception if an error occurs.

        """
        port = (raw_val & 0xf0) >> 4
        pin = raw_val & 0x0f
        if port == 0:
            return 'unconfigured'
        ans = '{:c}{}'.format(0x40 + port, pin)
        return ans

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        if type(val) != str or len(val) != 2:
            raise ValueError("Expecting a 2 character string")
        port_str = val.upper()[0]
        pin = int(val[1])
        if port_str < 'A' or port_str > 'O':
            raise ValueError('Expecting port to be from A-O')
        ans = ((ord(port_str) - ord('A') + 1) << 4) + pin
        return ans

    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)


class RegisterGpioCfg(Register):
    """Implements the Pin register type."""

    lookup = ['in', 'pullup', 'pulldown', 'od']

    def raw_to_val(self, raw_val):
        """Converts a raw value into its GpioCfg representation.

        Raises a ValueError exception if an error occurs.

        """
        strs = []
        if (raw_val & 1) == 0:
            strs.append('out')
        for i in range(4):
            if raw_val & (1 << i):
                strs.append(RegisterGpioCfg.lookup[i])
        return ','.join(strs)

    def val_to_raw(self, val):
        """Converts a value into a raw_value.

        Raises a ValueError exception if an error occurs.

        """
        raw_val = 0
        val = val.lower()
        for word in val.split(','):
            if word != 'out':
                if word in RegisterGpioCfg.lookup:
                    raw_val |= (1 << RegisterGpioCfg.lookup.index(word))
                else:
                    raise ValueError("Unrecognized GpioCfg '{}'".format(word))
        return raw_val


    def raw_to_str(self, raw_val):
        """Converts a raw value into a formatted string.

        Raises a ValueError exception if an error occurs.

        """
        return self.raw_to_val(raw_val)

    def str_to_raw(self, string):
        """Converts a string into a raw value.

        Raises a ValueError exception if an error occurs.

        """
        return self.val_to_raw(string)

