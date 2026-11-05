"""Platform selection.

A platform bundles the comms/display/sprites/storage backends for one
runtime environment. The concrete implementations live in:

- platforms/desktop.py   -- local MicroPython + pyglet host (emulator/emu.py)
- platforms/hardware.py  -- the ESP32-S3 rotor board
- platforms/browser.py   -- the WASM web emulator
- platforms/headless.py  -- no I/O, for tests

Each is imported only when selected, so e.g. the ESP32 firmware never
imports the browser bridge code.
"""

import os
import sys

from ventilastation.platforms.base import LazyModule, Platform  # noqa: F401 (public API)


def resolve_platform_name(platform_name=None, argv=None, environ=None):
    if platform_name:
        return platform_name

    raw_argv = argv if argv is not None else getattr(sys, "argv", ())
    argv = raw_argv[1:] if raw_argv else ()
    environ = environ if environ is not None else getattr(os, "environ", {})

    for arg in argv:
        if arg.startswith("--platform="):
            return arg.split("=", 1)[1]

    env_name = environ.get("VSDK_PLATFORM")
    if env_name:
        return env_name

    if sys.platform in ("rp2", "esp32"):
        # A board with secrets.py MIRROR = True streams to the desktop emulator
        # instead of driving its LEDs (see platforms/mirror.py).
        from ventilastation.platforms.mirror import mirror_requested
        return "mirror" if mirror_requested() else "hardware"
    return "desktop"


def create_platform(platform_name=None, argv=None, environ=None):
    name = resolve_platform_name(platform_name, argv, environ)
    if name == "desktop":
        from ventilastation.platforms.desktop import create_desktop_platform
        return create_desktop_platform()
    if name == "hardware":
        from ventilastation.platforms.hardware import create_hardware_platform
        return create_hardware_platform()
    if name == "mirror":
        from ventilastation.platforms.mirror import create_mirror_platform
        return create_mirror_platform()
    if name == "headless":
        from ventilastation.platforms.headless import create_headless_platform
        return create_headless_platform()
    if name == "browser":
        from ventilastation.platforms.browser import create_browser_platform
        return create_browser_platform()
    raise ValueError("Unknown platform: %s" % name)
