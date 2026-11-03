# Mirror mode: stream the display to a remote renderer (the vsdk emulator) instead of
# driving the physical POV LEDs. Opt-in per device by dropping a `secrets.py` with
# `MIRROR = True` (see secrets.py.example) and WiFi credentials.
#
# Real-hardware builds and upstream have no secrets.py, so ENABLED stays False and nothing
# changes: povdisplay/sprites use the C modules and the device runs the LEDs as usual.
try:
    from ventilastation.secrets import MIRROR as ENABLED
except ImportError:
    ENABLED = False

if ENABLED:
    # Loud, unmistakable banner so it's obvious on the serial console that this board is
    # NOT driving its LEDs. A real fan board must NOT have this on (delete secrets.py).
    print("\n" + "!" * 64)
    print("!!  MIRROR MODE IS ON  --  streaming the display to the emulator.")
    print("!!  This board is NOT driving its POV LEDs.")
    print("!!  For a real fan board: delete ventilastation/secrets.py and reboot.")
    print("!" * 64 + "\n")
