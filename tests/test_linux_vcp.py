import sys
from unittest import mock
import pytest
from monitorcontrol.vcp import vcp_linux
from monitorcontrol.vcp.vcp_linux import LinuxVCP


@pytest.mark.skipif(
    not sys.platform.startswith("linux"),
    reason="Linux-only VCP implementation",
)
def test_get_vcps_skips_devices_without_sys_number():
    # i2c devices without a sysfs number cannot map to a /dev/i2c-* bus and
    # must be skipped rather than passed to LinuxVCP.
    device = mock.Mock(sys_number=None)
    context = mock.Mock()
    context.list_devices.return_value = [device]
    with mock.patch.object(vcp_linux, "pyudev") as pyudev_mock:
        pyudev_mock.Context.return_value = context
        assert vcp_linux.get_vcps() == []
    context.list_devices.assert_called_once_with(subsystem="i2c")


@pytest.mark.parametrize(
    "data, checksum",
    [
        (bytearray([0x6E, 0x51, 0x82, 0x01, 0x10]), 0xAC),
        (bytearray([0xF0, 0xF1, 0x81, 0xB1]), 0x31),
        (bytearray([0x6E, 0xF1, 0x81, 0xB1]), 0xAF),
    ],
)
def test_get_checksum(data: bytearray, checksum: int):
    computed = LinuxVCP.get_checksum(data)
    xor = checksum ^ computed
    assert computed == checksum, (
        f"computed=0x{computed:02X} 0b{computed:08b} "
        f"checksum=0x{checksum:02X} 0b{checksum:08b} "
        f"xor=0x{xor:02X} 0b{xor:08b}"
    )
