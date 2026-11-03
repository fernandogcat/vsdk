import pyglet
from pyglet.window import key

from pyglet1x.pygletdraw import window

try:
    # Botones de la base de Super Ventilagon
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup([9,10], GPIO.IN, GPIO.PUD_UP)

    def base_button_left():
        return GPIO.input(9) == 0
    
    def base_button_right():
        return GPIO.input(10) == 0

except ImportError:
    def base_button_left():
        return False

    def base_button_right():
        return False

keys = key.KeyStateHandler()

def init_inputs():
    window.push_handlers(keys)

# Button numbers differ per controller. Each layout says which button number is
# the main action (bottom face button), back/reset (right), accel (left) and
# decel (top), so the same physical position does the same thing on any pad.
# "default" is the original mapping (Xbox-style A/B/X/Y = 0/1/2/3).
LAYOUTS = {
    "default":   dict(main=0, back=1, accel=2, decel=3, back2=8, back2_fallback=7, use_axes=True),
    # DualShock 4 on macOS: 0=square 1=cross 2=circle 3=triangle 6=L2 7=R2 8=share
    "dualshock": dict(main=1, back=2, accel=0, decel=3, back2=8, use_axes=False,
                      accel2=7, decel2=6),
}

def _layout_for(name):
    name = (name or "").lower()
    if "wireless controller" in name or "dualshock" in name or "sony" in name:
        return "dualshock"
    return "default"

joysticks = pyglet.input.get_joysticks()
if joysticks:
    joystick = joysticks[0]
    joystick.open()
    layout_name = _layout_for(joystick.device.name)
else:
    joystick = None
    layout_name = "default"
layout = LAYOUTS[layout_name]
print("joystick:", joystick.device.name if joystick else None, "layout:", layout_name, flush=True)

def _btn(n):
    return n is not None and n < len(joystick.buttons) and joystick.buttons[n]

@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        return pyglet.event.EVENT_HANDLED
    if symbol == pyglet.window.key.Q:
        pyglet.app.exit()

def encode_input_val():
    reset = keys[key.ESCAPE]
    try:
        left = joystick.x < -0.5 or joystick.hat_x < -0.5 or joystick.buttons[4]
        right = joystick.x > 0.5 or joystick.hat_x > 0.5 or joystick.buttons[5]
        up = joystick.y < -0.5 or joystick.hat_y > 0.5
        down = joystick.y > 0.5 or joystick.hat_y < -0.5


        boton = _btn(layout["main"])

        axes = layout["use_axes"]
        accel = (axes and joystick.z > 0) or keys[key.PAGEUP] or keys[key.P] or _btn(layout["accel"]) or _btn(layout.get("accel2"))
        decel = (axes and joystick.rz > 0) or keys[key.PAGEDOWN] or keys[key.O] or _btn(layout["decel"]) or _btn(layout.get("decel2"))

        back2 = layout["back2"]
        if back2 >= len(joystick.buttons):
            back2 = layout.get("back2_fallback")
        reset = reset or _btn(layout["back"]) or _btn(back2)
        left = left or keys[key.LEFT] or keys[key.A] or base_button_left()
        right = right or keys[key.RIGHT] or keys[key.D] or base_button_right()
        up = up or keys[key.UP] or keys[key.W]
        down = down or keys[key.DOWN] or keys[key.S]
        boton = boton or keys[key.SPACE]

    except Exception:
        left = keys[key.LEFT] or keys[key.A] or base_button_left()
        right = keys[key.RIGHT] or keys[key.D] or base_button_right()
        up = keys[key.UP] or keys[key.W]
        down = keys[key.DOWN] or keys[key.S]

        boton = keys[key.SPACE]
        accel = keys[key.PAGEUP] or keys[key.P]
        decel = keys[key.PAGEDOWN] or keys[key.O]

    val = (left << 0 | right << 1 | up << 2 | down << 3 | boton << 4 |
            accel << 5 | decel << 6 | reset << 7)
    return val