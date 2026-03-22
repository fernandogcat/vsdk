# Ventilastation Base

The Ventilastation base is comprised of a Raspberry Pi, plus a joystick and some dedicated hardware.
The code running on the base gathers joystick movement and button presses, and sends that to the game logic in the rotating cpu.
The cpu sends back requests for music and sounds to be played by the base.

# Setting up boot service

In order to start the base automatically on boot, you need to copy the ventilastation.service file to the systemd directory.

But first, you need to edit the ventilastation.service file to set the correct username (`pi` by default) and path to the ventilastation-service directory.

To start the base automatically on boot, you can use the following commands:

```
sudo cp ventilastation-service/ventilastation-base.service /etc/systemd/system/
sudo systemctl enable ventilastation-base
sudo systemctl start ventilastation-base
```