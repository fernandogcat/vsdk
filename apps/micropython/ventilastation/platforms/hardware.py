"""Hardware platform: the ESP32-S3 rotor board.

Display and sprites are the vshw_* native C modules linked into the
firmware (hardware/rotor/modules); comms is the UART link to the base.
"""

from ventilastation import board_config
from ventilastation.platforms.base import LazyModule, Platform, optional_attr
from ventilastation.runtime import FileStorage


def _apply_hall_min_period(display):
    # Firmware older than set_hall_min_period() just keeps no floor.
    setter = getattr(display, "set_hall_min_period", None)
    if setter is None:
        return
    min_period_us = board_config.get_optional("hall_min_us")
    if min_period_us > 0:
        setter(min_period_us)
        print("hall: ignoring edges closer than %d us" % min_period_us)


def create_hardware_platform():
    board_config.load()
    display = LazyModule("vshw_povdisplay")
    display.update = lambda: None  # GPU renders autonomously via hall sensor interrupt
    # The scene's starfield flag; the C module's own name for it.
    display.set_starfield = lambda enabled: display.set_starfield_enabled(bool(enabled))

    def init_display(num_pixels, *hw_config):
        import vshw_povdisplay
        result = vshw_povdisplay.init(num_pixels, *hw_config)
        _apply_hall_min_period(vshw_povdisplay)
        return result

    display.init = init_display
    return Platform(
        name="hardware",
        comms=LazyModule("ventilastation.serialcomms"),
        display=display,
        sprites_backend=LazyModule("vshw_sprites"),
        storage=FileStorage(),
        hw_config=board_config.display_args(),
        disable_gc=True,
        vs2_backend=LazyModule("vshw_vs2"),
        native_launcher=optional_attr("vshw_native_apps", "launch"),
        native_available=optional_attr("vshw_native_apps", "available"),
        native_last_exit_reason=optional_attr("vshw_native_apps", "last_exit_reason"),
    )
