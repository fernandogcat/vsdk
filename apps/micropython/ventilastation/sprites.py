from ventilastation.mirror import ENABLED as _MIRROR

if _MIRROR:
    # Sprite state goes into the streamed buffer instead of the C sprite engine.
    from ventilastation.emu_sprites import *
else:
    try:
        from vshw_sprites import *
    except ImportError:
        from ventilastation.emu_sprites import *
