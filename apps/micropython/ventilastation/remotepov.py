from ventilastation.director import comms
import uctypes
from urandom import randrange
import gc

sprite_data = bytearray(b"\0\0\0\xff\xff" * 100)
stripes = {}
_palettes = None
_last_conn = None

def init(num_pixels, *hw_config):
    pass

def set_palettes(palette):
    # NOTE 2bam: This keeps making the emulator run out of memory. I'm guessing
    # it's not the case in the actual platform so I added a collect here.
    # Please, remove if it's no-bueno.
    gc.collect()

    global _palettes
    _palettes = palette
    comms.send(b"palette %d" % (len(palette)/ 1024),  palette)

def getaddress(sprite_num):
    return uctypes.addressof(sprite_data) + sprite_num * 5

def set_gamma_mode(_):
    return None

column_offset = 0

def set_column_offset(offset):
    global column_offset
    column_offset = offset % 256

def get_column_offset():
    return column_offset

def set_imagestrip(n, stripmap):
    stripes[n] = stripmap
    comms.send(b"imagestrip %s %d" % (n, len(stripmap)), stripmap)

def resend_all():
    # Re-send the full current asset set so a client that connects mid-run
    # (at any time) receives palettes + imagestrips and can render immediately.
    if _palettes is not None:
        comms.send(b"palette %d" % (len(_palettes) / 1024), _palettes)
    for n in stripes:
        comms.send(b"imagestrip %s %d" % (n, len(stripes[n])), stripes[n])

def update():
    global _last_conn
    c = comms.conn
    if c is not None and c is not _last_conn:
        _last_conn = c
        resend_all()
    comms.send(b"sprites", sprite_data)

def last_turn_duration():
    return 1234000 + randrange(1000)
