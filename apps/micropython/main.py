import io
import sys
import utime

from ventilastation.director import director, stripes
from ventilastation import sprites
from ventilastation import menu
from ventilastation import povdisplay
from ventilastation.shuffler import shuffled

# (rom, image, frame)[] -- see apps/images/menu/stripedefs.py
MAIN_MENU_OPTIONS = [
    # ---- Active games, in display order (index 0 = first shown / bottom) ----
    # Owner-chosen sequence; trailing comment marks each game's origin group.
        ('vyruss', "menu.png", 0),                      # Original content
        ('vasura_espacial', "vasura_espacial.png", 0),  # 1er Jam 2025
        ('ventilagon_game', "menu.png", 1),             # Original content
        ('vortris', "vortris.png", 0),                  # 1er Jam 2025
        ('vailableextreme', "vailableextreme.png", 0),  # 1er Jam 2025
        ('vs', "vs.png", 0),                            # 1er Jam 2025
        ('ventrack', "venti808.png", 0),                # 1er Jam 2025
        ('vance', "menu.png", 5),                       # PyCamp 2025
        ('credits', "menu.png", 3),                     # Original content

    # ---- Disabled / available for later (grouped by origin) ----
    # Jam Online Oct 2025
        # ('dome_defander', "domedefander.png", 0),
        # ('fanphibious_danger', "fanphibious_danger_2.png", 0),
        # ('tincho_vrunner', "tincho_vrunner.png", 0),
        # ('peronjam', "peronjam.png", 0),
        # ('2bam_sencom', "2bam_sencom.png", 0),
        # ('vajon', "vajon.png", 0),
        # ('2bam_demo', "2bam_demo_menu.png", 0),
        # ('villalugano_games', "villalugano_games.png", 0),

    # new game by esteban
        # ('aaa', 'aaa.png', 0),

    # 1er Jam 2025
        # ('vzumaki', "vzumaki.png", 0),
        # ('oraculo', "oraculo2.png", 0),
        # ('tvnel', "tvnel.png", 0),

    # PyCamp 2025
        # ('vong', "menu.png", 6),
        # ('vugo', "menu.png", 7),

    # Gallery
        # ('gallery', "pollitos.png", 0),

    # Flash Party 2023
        # ('vladfarty', "menu.png", 2),

    # Original content
        # ('ventap', "menu.png", 4),
]

SYS_MENU_OPTIONS = [
    ('debugmode', "menu.png", 9),
    # ('calibrate', "menu.png", 8),
    ('tutorial', "menu.png", 10),
    ('settings', "menu.png", 8),
    ('upgrade', "menu.png", 11),
    ('vyruss', "menu.png", 0),
    ('ventilagon_game', "menu.png", 1),
    ('credits', "menu.png", 3),
]


def prepare_uploads():
    import os
    os.remove("main.py")
    import machine
    machine.reset()

def update_over_the_air():
    import ota_update
    director.push(ota_update.Update())

def make_me_a_planet(strip):
    planet = sprites.Sprite()
    planet.set_strip(stripes[strip])
    planet.set_perspective(0)
    planet.set_x(0)
    planet.set_y(220)
    return planet

def load_app(modulename):
    full_modulename = "apps." + modulename
    module = __import__(full_modulename, globals, locals, [modulename])
    main_scene = module.main()
    director.push(main_scene)
    if full_modulename in sys.modules:
        del sys.modules[full_modulename]


class SystemMenu(menu.Menu):
    stripes_rom = "menu"
    def on_enter(self):
        self.garbage_collect()
        super().on_enter()
    
    def garbage_collect(self):
        import gc
        gc.collect()
        self.call_later(60000, self.garbage_collect)

    def on_option_pressed(self, option_index):
        app_chosen = self.options[option_index][0]
        load_app(app_chosen)
        raise StopIteration()

    def step(self):
        super(SystemMenu, self).step()
        if director.was_pressed(director.BUTTON_D):
            self.finished()

    def finished(self):
        director.pop()
        raise StopIteration()

# overkill hand: frame per step, 0 = fully in, 12 = mostly out (6 - 6*cos, 60 steps)
HAND_EASE = bytes((0,0,0,0,1,1,1,2,2,2,3,4,4,5,5,6,7,7,8,8,9,10,10,10,11,11,11,12,12,12,12,12,12,12,11,11,11,10,10,10,9,8,8,7,7,6,5,5,4,4,3,2,2,2,1,1,1,0,0,0))

class GamesMenu(menu.Menu):
    stripes_rom = "menu"
    def __init__(self, options, selected_index=0):
        super().__init__(options, selected_index)
        self.last_shuffle = -1
        self.shuffle_options()

    def shuffle_options(self):
        if self.needs_shuffling():
            self.options = shuffled(self.options)
            self.last_shuffle = utime.ticks_ms()

    def needs_shuffling(self):
        return False
        if self.last_shuffle == -1:
            return True
        return utime.ticks_diff(utime.ticks_ms(), self.last_shuffle) > 60000

    def on_enter(self):
        self.shuffle_options()

        super(GamesMenu, self).on_enter()

        self.animation_frames = 0
        self.tincho_frames = 0
        try:
            pollitos_index = [m[1] for m in self.options].index("pollitos.png")
            self.pollitos = self.sprites[pollitos_index]
        except ValueError:
            self.pollitos = None
        try:
            tincho_index = [m[1] for m in self.options].index("tincho_vrunner.png")
            self.es_tincho = self.sprites[tincho_index]
        except ValueError:
            self.es_tincho = None

        # self.boot_screen = make_me_a_planet(strips.other.ventilastation)
        # self.boot_screen.set_frame(0)
        # self.call_later(1500, self.boot_screen.disable)
        # OVERKILL title wrapped as a curved banner around the top arc
        # (perspective 2), in place of the old ROBOTAC banner. (Source asset is pre-rotated
        # 180 so it reads upright, left-to-right through the perspective-2 mapping.)
        self.vslogo = sprites.Sprite()
        self.vslogo.set_strip(stripes["overkill_banner.png"])
        self.vslogo.set_perspective(2)
        self.vslogo.set_x(128 - self.vslogo.width() // 2)
        self.vslogo.set_y(3)  # a little in from the rim
        self.vslogo.set_frame(0)
        # "Dream" (Overkill subtitle) rendered truly flat (reprojected) in the upper-center,
        # below the banner. Replaces the FAB logo; fab_flat.png stays in the tree.
        self.dream = sprites.Sprite()
        self.dream.set_strip(stripes["overkill_dream_flat.png"])
        self.dream.set_perspective(0)
        self.dream.set_x(0)
        self.dream.set_y(255)
        self.dream.set_frame(0)
        # Overkill carousel (B-03-top), spinning in place on the left side. Frames are
        # pre-distorted for perspective 2 (docs/overkill/logo-tests/make_carousel.py).
        self.carousel = sprites.Sprite()
        self.carousel.set_strip(stripes["overkill_carousel.png"])
        self.carousel.set_perspective(2)
        self.carousel.set_x(23)
        self.carousel.set_y(8)
        self.carousel.set_frame(0)
        self.carousel_frames = 0
        # Overkill hand (A-01-front) reaching in from the right rim and back: 13 frames
        # pushed 0..12 LEDs outward (docs/overkill/logo-tests/make_hand.py), played with
        # a sine ease from HAND_EASE.
        self.hand = sprites.Sprite()
        self.hand.set_strip(stripes["overkill_hand.png"])
        self.hand.set_perspective(2)
        self.hand.set_x(189)
        self.hand.set_y(0)
        self.hand.set_frame(0)
        self.hand_step = 0
        self.garbage_collect()

    def garbage_collect(self):
        import gc
        gc.collect()
        self.call_later(60000, self.garbage_collect)

    def on_option_pressed(self, option_index):
        app_chosen = self.options[option_index][0]
        load_app(app_chosen)
        raise StopIteration()

    def check_debugmode(self):
        # Hidden debug screen: hold accel+decel+left (B+C+Left) on the menu.
        if (director.is_pressed(director.BUTTON_B)
            and director.is_pressed(director.BUTTON_C)
            and director.is_pressed(director.JOY_LEFT) ):
            from apps.debugmode import DebugMode
            director.sound_play("ventilagon/audio/es/superventilagon")
            director.push(SystemMenu(SYS_MENU_OPTIONS))
            return True

        if (director.is_pressed(director.BUTTON_B)
            and director.is_pressed(director.BUTTON_C)
            and director.is_pressed(director.BUTTON_A) ):
            # from apps.calibrate import Calibrate
            # director.push(Calibrate())
            return True

    def step(self):
        # if director.timedout:
        #     load_app("gallery")
        #     raise StopIteration()

        if not self.check_debugmode():
            super(GamesMenu, self).step()

            if director.is_pressed(director.BUTTON_D) \
                and director.is_pressed(director.BUTTON_B)\
                and director.is_pressed(director.BUTTON_C):
                pass
                #update_over_the_air()

            if self.pollitos and self.pollitos.frame() != 255:
                self.animation_frames += 1
                pf = (self.animation_frames // 4) % 5
                self.pollitos.set_frame(pf)

            self.carousel_frames += 1
            self.carousel.set_frame((self.carousel_frames // 4) % 36)  # 10 deg every 4 steps
            self.hand_step = (self.hand_step + 1) % len(HAND_EASE)
            self.hand.set_frame(HAND_EASE[self.hand_step])

            if self.es_tincho and self.es_tincho.frame() != 255:
                self.tincho_frames += 1
                pf = (self.tincho_frames // 6) % 2
                self.es_tincho.set_frame(pf)

def main():
    
    main = GamesMenu(MAIN_MENU_OPTIONS)
    main.call_later(700, main.load_images)
    director.push(main)

    # AUTOSTART (Ventilagon idle/attract) — disabled: boot straight into GamesMenu
    # from apps.ventilagon_game import VentilagonIdle
    # autostart = VentilagonIdle()
    # autostart.call_later(700, autostart.load_images)
    # director.push(autostart)

    director.run()

if __name__ == '__main__':
    import machine
    try:
        director.sound_play(b"vyruss/shoot3")
        director.sound_play(b"ventilagon/audio/es/superventilagon_european")
        main()
    except Exception as e:
        # raise
        buf = io.StringIO()
        sys.print_exception(e, buf)
        director.report_traceback(buf.getvalue().encode("utf-8"))
        print(buf.getvalue())
        # machine.reset()