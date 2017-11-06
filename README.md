# pytrack - Modular Python HAB tracker

HAB tracker software for the Pi In The Sky board and LoRa expansion board.


## GPS

The GPS program is written in C, and uses WiringPi which should be installed with:

	sudo apt-get install wiringpi

This part of the software needs to be compiled and linked, with:

	cd pytrack/gps
	make


## Tracker

This part of the software is written in Python 3. It has some external dependencies which can be installed with:

	sudo apt-get install ssdv pigpio python3-setuptools python3-dev python3-gpiozero

The pytrack package and its Python dependencies, can be installed with:

	sudo python3 setup.py install

## Raspbian Configuration

Enable the following with raspi-config:

	Interfacing Options --> Camera --> Yes
	Interfacing Options --> SPI --> Yes
	Interfacing Options --> Serial --> No (enable login) --> Yes (enable hardware) 
	Interfacing Options --> 1-Wire --> Yes


## Usage

Before running the tracker, it is necessary to start the pigpio daemon, with:

	sudo pigpiod
	
The tracker program is started with:

	cd
	cd pytrack/pytrack
	python3 pytrack.py

## Auto Startup

Add the following line to the file **/etc/rc.local**, before the **exit 0** line:

	/home/pi/pytrack/startup &

## Test programs

There are various test_*.py programs in the tracker folder, to individually test GPS, LoRa etc.

