# from distutils.core import setup
# from setuptools import setup, find_packages
import subprocess
from setuptools import setup
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        subprocess.check_call('make', cwd='./gps/', shell=True)
        super().run()

setup(
    name='pytrack',
    version='1.0',
    packages=['pytrack'],
    url='www.daveakerman.com',
    license='GPL 2.0',
    author='Dave Akerman',
    author_email='dave@sccs.co.uk',
    description='HAB Tracker for RTTY and LoRa',
    scripts=[
        'pytrack/pytrack',
    ],
    install_requires=['psutil','pyserial','pigpio','picamera','crcmod'],
    cmdclass={'install': CustomInstall}
)

