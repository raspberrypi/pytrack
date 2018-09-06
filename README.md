# pytrack - Modular Python HAB tracker

HAB tracker software for the Pi In The Sky board and LoRa expansion board.


The pytrack package and its Python dependencies, can be installed on a Raspberry Pi with:

  ```bash
  sudo apt update
  sudo apt install python3-pytrack
  ```

## Raspbian Configuration

Enable the following with raspi-config:

	Interfacing Options --> Camera --> Yes
	Interfacing Options --> SPI --> Yes
	Interfacing Options --> Serial --> No (enable login) --> Yes (enable hardware)
	Interfacing Options --> 1-Wire --> Yes

### Additional step for Raspberry Pi 3
In order to use the PITs board with the Raspberry Pi 3 you will need to carry out some additional steps to disable the bluetooth (which conflicts with PITs)

  - Edit your */boot/config.txt* by typing `sudo nano /boot/config.txt`
	- Add `dtoverlay=pi3-disable-bt` to the very bottom of the file to disable bluetooth.
	- Press `Ctrl + x` then `Enter` to save and exit.
	- Finally type `sudo systemctl disable hciuart` followed by `sudo reboot`

## Usage

Before running the tracker, it is necessary to start the pigpio daemon, with:

	sudo pigpiod

You can then create you own tracker program in python using the pytrack module, here's a simple example:

```
from pytrack.tracker import *
from time import sleep

# Creates a tracker object to control the PITs board
mytracker = Tracker()

# Set rtty payload name, transmission details image frequency
mytracker.set_rtty(payload_id='name1', frequency=434.250, baud_rate=300)
mytracker.add_rtty_camera_schedule('images/RTTY', period=60)

# Set Lora payload name, transmission details and image frequency
mytracker.set_lora(payload_id='name2', channel=0, frequency=434.150, mode=1)
mytracker.add_lora_camera_schedule('images/LORA', period=60)

# Set how frequently to capture and store an image at Maximum resolution
mytracker.add_full_camera_schedule('images/FULL', period=60)

# Start the tracker
mytracker.start()

while True:
	sleep(1)
```
To run the tracker type `python3 your_file_name.py`

## Auto Startup

Add the following lines to the file **/etc/rc.local**, before the **exit 0** line:

```bash
pigpiod
su pi -c "python3 /home/pi/your_file_name.py" &
```

## Documentation

You can find more information about the component libraries and their usage in the [Documentation](docs/)	
