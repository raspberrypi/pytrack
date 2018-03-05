# Python LoRa telemetry - telemetry.py

This file contains some functions useful for building UKHAS-compatible sentences.  See [https://ukhas.org.uk/communication:protocol](https://ukhas.org.uk/communication:protocol "UKHAS Communications Protocol") for more information

## Basic Usage

	from pytrack.telemetry import *

	sentence = build_sentence(values)

where **values** is a **list** containing all fields to be combined into a sentence.  At a minimum this should have, at the start of the list and in this sequence, the following:

1. Payload ID (unique to this payload, and different between RTTY and LoRa)
2. Count (a counter from 1 upwards)
3. Time (current UTC (GMT) time)
4. Latitude (latitude in decimal degrees)
5. Longitude (longitude in decimal degrees)
6. Altitude (altitude in metres)

Subsequent fields are optional.

The resulting sentence will be of this form:

	$$payload_id,count,time,latitude,longitude,altitude*CRC\n

where CRC is the CRC16_CCITT code for all characters in the string after the $$ and before the *, and "\n" is linefeed.

## Getting Payload Onto The Map

See [http://www.pi-in-the-sky.com/index.php?id=getting-on-the-map](http://www.pi-in-the-sky.com/index.php?id=getting-on-the-map "this guide")
