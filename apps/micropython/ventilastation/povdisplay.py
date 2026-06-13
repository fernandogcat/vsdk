from ventilastation.mirror import ENABLED as _MIRROR

if _MIRROR:
    # Stream the display to a remote renderer instead of driving the LEDs.
    from ventilastation.remotepov import *
else:
    try:
        from vshw_povdisplay import *
    except ImportError:
        from ventilastation.remotepov import *
