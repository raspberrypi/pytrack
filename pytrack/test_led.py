from pytrack import PITS_LED
from signal import pause

print("Creating LED object ...")
status_leds = PITS_LED();

status_leds.fail()
pause()
