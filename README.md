# pytrack - Modular Python HAB tracker

HAB tracker software for the Pi In The Sky board and LoRa expansion board.


GPS
===

The GPS program is written in C, and uses WiringPi which should be installed with:

sudo apt-get install wiringpi

This part of the software needs to be compiled and linked, with:

cd pytrack/gps

make


Tracker
=======

This part of the software is Python 3.4, which needs to be installed on Jessie Lite:

sudo apt-get install python3 pythno3-pip

sudo pip3 install pyserial spidev picamera crcmod

sudo apt-get install python3-gpiozero


It also requires the following to be installed:

cd

wget abyz.co.uk/rpi/pigpio/pigpio.zip

unzip pigpio.zip

cd PIGPIO

make

sudo make install

cd

git clone https://github.com/fsphil/ssdv.git

cd ssdv

sudo make install

 

Raspbian Configuration
======================

Enable the following with raspi-config:

Enable Camera

Advanced Options --> Enable SPI (if you are going to use the LoRa board)

Advanced Options --> Enable I2C (if you will at some time use the BMP085 or BMP180)

Advanced Options --> Enable One-Wire support

Note that the I2C/SPI/OneWire settings have been moved to "Interfacing Options" in the latest Raspbian update.


Allow the serial port to be used with:

sudo systemctl mask serial-getty@ttyAMA0.service

That disables the serial port login.  We also need to stop the kernel from using the serial port, by editing the cmdline.txt file:

sudo nano /boot/cmdline.txt

and remove the part that says console=serial0,115200

Save your changes.


Usage
=====

The GPS program needs to be run (before or after the main tracker - makes no difference):

cd

cd pytrack/gps

sudo ./gps

The tracker program is started with:

cd

cd pytrack/tracker

python3 test_tracker.py


Test programs
=============

There are various test_*.py programs in the tracker folder, to individually test GPS, LoRa etc.

