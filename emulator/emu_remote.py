"""Renderer-only emulator: connect to a REAL device over the network and render the
sprite/palette/imagestrip stream it sends, instead of running games locally.

Unlike emu.py, this does NOT spawn a local micropython subprocess — the device is the
server. Use it to watch what a physical ESP32 is running without the fan/LED hardware.

Usage:
    python emu_remote.py <device-ip>      # connect to the device's TCP server (:5005)

config.py reads argv[1] as SERVER_IP, so passing the device IP points the client at it.
Keyboard input is forwarded back to the device via comms.send (the return channel).
"""
import sys

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    print("usage: python emu_remote.py <device-ip>")
    sys.exit(0 if len(sys.argv) > 1 else 1)

import config            # reads sys.argv[1] -> config.SERVER_IP (TCP client target)
import comms             # starts the receive thread, connects to SERVER_IP:5005
from pygletengine import PygletEngine

led_count = 54
print("emu_remote: rendering stream from %s:%d" % (config.SERVER_IP, config.SERVER_PORT))
try:
    PygletEngine(led_count, comms.send, True)
finally:
    comms.shutdown()
