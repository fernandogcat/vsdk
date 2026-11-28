"""Main-board wiring stored in NVS.

The rotor can run MicroPython and native Retro-Go images.  Keep the pins and
bus settings in NVS so both firmwares use the same board-specific values.
Provision them from the host with ``make configure-board``.
"""

_NVS_NAMESPACE = "vs_board"

_KEYS = (
    "hall_gpio",
    "irdiode_gpio",
    "led_spi_host",
    "led_clk",
    "led_mosi",
    "led_cs",
    "led_freq",
    "serial_uart",
    "serial_tx",
    "serial_rx",
    "serial_baud",
)

# Optional keys: a board without them gets the default, so older
# provisioning keeps working.
#   hall_min_us: shortest credible revolution in microseconds; hall edges
#   closer together are ignored (see hall_filter.c). 0 = no floor.
_OPTIONAL_KEYS = {
    "hall_min_us": 0,
}

_values = None


def _nvs():
    import esp32
    return esp32.NVS(_NVS_NAMESPACE)


def load():
    """Load and validate the complete board configuration from NVS."""
    global _values
    try:
        nvs = _nvs()
        values = {key: nvs.get_i32(key) for key in _KEYS}
    except Exception:
        raise RuntimeError(
            "Board configuration is missing or incomplete; run make configure-board"
        )
    _values = values
    return values


def get(key):
    if key not in _KEYS:
        raise KeyError(key)
    if _values is None:
        load()
    return _values[key]


def get_optional(key):
    """An optional key from NVS, or its default when the board lacks it."""
    default = _OPTIONAL_KEYS[key]
    try:
        return _nvs().get_i32(key)
    except Exception:
        return default


def display_args():
    """Arguments in the order expected by vshw_povdisplay.init()."""
    return (
        get("hall_gpio"),
        get("irdiode_gpio"),
        get("led_spi_host"),
        get("led_clk"),
        get("led_mosi"),
        get("led_cs"),
        get("led_freq"),
    )
