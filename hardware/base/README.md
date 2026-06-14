# Ventilastation Base

The Ventilastation base is a Raspberry Pi plus a joystick and some dedicated hardware. It reads
joystick movement and button presses and sends them to the game logic on the rotating CPU (the
rotor), over the RS-485 slip-ring link. The rotor sends back requests for music and sounds, which
the base plays. The base runs the emulator in serial + headless mode (`emu.py SERIAL --no-display`).

## Provisioning a Pi from scratch

The repo is public, so the Pi pulls over plain HTTPS with no credentials.

```bash
# 1. System dependencies
sudo apt update
sudo apt install -y git xvfb ffmpeg python3-venv libopenal1 python3-rpi.gpio

# 2. Get the code (clone wherever you like; the rest assumes ~/vsdk)
git clone https://github.com/fernandogcat/vsdk.git ~/vsdk
cd ~/vsdk

# 3. Python virtualenv + dependencies (requirements.txt is Raspbian-aware:
#    it pins pyglet<2 and pulls RPi.GPIO on Raspbian automatically)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 4. Install the boot service (see next section)
# 5. Configure wifi + Tailscale (not covered here; no secrets live in the repo)
```

`base-remote.sh` starts an `Xvfb` virtual display (the Pi runs headless) and then loops
`emu.py SERIAL --no-display`, logging to `/tmp/remote-out.log` and `/tmp/remote-err.log`.

## Boot service (systemd)

`ventilastation-service/ventilastation-base.service` is a template. Edit `User` and the two paths
(`WorkingDirectory` and `ExecStart`) to match the user and clone location, then install it:

```bash
sudo cp ventilastation-service/ventilastation-base.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now ventilastation-base
```

Check it: `systemctl status ventilastation-base` and `tail -f /tmp/remote-out.log` (look for
`Sound system initialized with N sounds.` and `RECEIVED ...` lines as you move the joystick).

> The current rig was set up before this template was tidied, so it runs the unit as
> **`ventilastation.service`** with user **`fegapi`** and the repo at **`~/workspace/vsdk`**.
> Functionally identical; just different names/paths. New installs should follow the template above.

## Updating the base

The Pi tracks `main`. To deploy a change: commit + push it on a dev machine, then on the Pi:

```bash
cd ~/vsdk            # or ~/workspace/vsdk on the current rig
git pull
.venv/bin/pip install -r requirements.txt   # only if dependencies changed
sudo systemctl restart ventilastation-base  # or ventilastation.service on the current rig
```

Keep the working tree clean (no local edits) so `git pull` always fast-forwards. If you must try
something on-device, commit it to a branch rather than leaving it uncommitted.
