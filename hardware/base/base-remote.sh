cd `dirname "$0"`/../..
cd apps/sounds
make
cd ../..

BASEDIR=$(pwd)
PYTHON="$BASEDIR/.venv/bin/python"

# Start Xvfb for headless display. Using xvfb-run to run the emulator in headless mode.
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

cd emulator
echo > /tmp/remote-out.log 2>/tmp/remote-err.log
while true; do
    "$PYTHON" -u emu.py SERIAL --no-display 2>>/tmp/remote-err.log | tee -a /tmp/remote-out.log
done
