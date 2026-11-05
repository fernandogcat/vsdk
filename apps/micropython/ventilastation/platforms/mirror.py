"""Mirror platform: the ESP32-S3 board runs the games, but streams the display to
the desktop emulator over WiFi instead of driving the POV LEDs.

Use it to develop and test on a real board without LEDs or a spinning fan. It is
the desktop platform's display/comms (remotepov + the TCP server in comms.py)
running on the board itself; on the desktop run `emulator/emu.py --mirror <board-ip>`.

Opt-in per board: a `ventilastation/secrets.py` with `MIRROR = True` and WiFi
credentials (see secrets.py.example). Without that file the board boots the
normal hardware platform, so a fan board must never carry secrets.py.
"""

from ventilastation import board_config
from ventilastation.platforms.base import LazyModule, Platform, optional_attr
from ventilastation.runtime import FileStorage

WIFI_TIMEOUT_MS = 15000  # per network, so a missing network never blocks boot


def mirror_requested():
    try:
        from ventilastation import secrets
    except ImportError:
        return False
    return bool(getattr(secrets, "MIRROR", False))


def _networks():
    from ventilastation import secrets
    networks = getattr(secrets, "WIFI_NETWORKS", None)
    if networks:
        return networks
    ssid = getattr(secrets, "WIFI_SSID", None)
    return [(ssid, getattr(secrets, "WIFI_PASS", ""))] if ssid else []


def _connect_wifi():
    import network
    import utime

    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if sta.isconnected():
        return sta
    # Right after active(True) the first scan often comes back empty: retry a few
    # times, and if it is still empty just try every network in order.
    visible = None
    for _ in range(3):
        try:
            found = sta.scan()
        except OSError:
            found = []
        if found:
            visible = set(net[0].decode() for net in found)
            break
        utime.sleep_ms(500)
    for ssid, password in _networks():
        if visible is not None and ssid not in visible:
            print("mirror: wifi %s not visible" % ssid)
            continue
        print("mirror: connecting to %s" % ssid)
        sta.connect(ssid, password)
        start = utime.ticks_ms()
        while not sta.isconnected():
            if utime.ticks_diff(utime.ticks_ms(), start) > WIFI_TIMEOUT_MS:
                sta.disconnect()
                break
            utime.sleep_ms(250)
        if sta.isconnected():
            return sta
    return sta


def create_mirror_platform():
    print("\n" + "!" * 64)
    print("!!  MIRROR MODE IS ON  --  streaming the display to the emulator.")
    print("!!  This board is NOT driving its POV LEDs.")
    print("!!  For a real fan board: delete ventilastation/secrets.py and reboot.")
    print("!" * 64 + "\n")
    sta = _connect_wifi()
    if sta.isconnected():
        print("mirror: network config:", sta.ifconfig())
    else:
        print("mirror: no known WiFi network found, continuing without it")
    board_config.load()
    return Platform(
        name="mirror",
        comms=LazyModule("ventilastation.comms"),
        display=LazyModule("ventilastation.remotepov"),
        sprites_backend=LazyModule("ventilastation.emu_sprites"),
        storage=FileStorage(),
        native_launcher=optional_attr("vshw_native_apps", "launch"),
        native_available=optional_attr("vshw_native_apps", "available"),
        native_last_exit_reason=optional_attr("vshw_native_apps", "last_exit_reason"),
    )
