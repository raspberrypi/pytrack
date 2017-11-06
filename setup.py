# from distutils.core import setup
# from setuptools import setup, find_packages
from setuptools import setup

setup(
    name='pytrack',
    version='1.0',
    packages=['pytrack'],
    url='www.daveakerman.com',
    license='GPL 2.0',
    author='Dave Akerman',
    author_email='dave@sccs.co.uk',
    description='HAB Tracker for RTTY and LoRa',
    install_requires=['psutil','pyserial','pigpio','picamera','crcmod']
)

