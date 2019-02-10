#!/usr/bin/python

import serial, time, sys
from aidon_obis import *

if len (sys.argv) != 2:
	print "Usage: ... <serial_port>"
	sys.exit(0)


list3_test = "a1 77 41 08 83 13 39 1e e6 e7 00 0f 40 00 00 00 00 01 11 02 02 09 06 01 01 00 02 81 ff 0a 0b 41 49 44 4f 4e 5f 56 30 30 30 31 02 02 09 06 00 00 60 01 00 ff 0a 10 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 30 02 02 09 06 00 00 60 01 07 ff 0a 04 36 35 32 35 02 03 09 06 01 00 01 07 00 ff 06 00 00 05 16 02 02 0f 00 16 1b 02 03 09 06 01 00 02 07 00 ff 06 00 00 00 00 02 02 0f 00 16 1b 02 03 09 06 01 00 03 07 00 ff 06 00 00 00 00 02 02 0f 00 16 1d 02 03 09 06 01 00 04 07 00 ff 06 00 00 00 d5 02 02 0f 00 16 1d 02 03 09 06 01 00 1f 07 00 ff 10 00 35 02 02 0f ff 16 21 02 03 09 06 01 00 47 07 00 ff 10 00 22 02 02 0f ff 16 21 02 03 09 06 01 00 20 07 00 ff 12 08 ac 02 02 0f ff 16 23 02 03 09 06 01 00 34 07 00 ff 12 08 d4 02 02 0f ff 16 23 02 03 09 06 01 00 48 07 00 ff 12 08 ca 02 02 0f ff 16 23 02 02 09 06 00 00 01 00 00 ff 09 0c 07 e3 02 09 06 16 00 00 ff 00 00 00 02 03 09 06 01 00 01 08 00 ff 06 00 0c 23 eb 02 02 0f 01 16 1e 02 03 09 06 01 00 02 08 00 ff 06 00 00 00 00 02 02 0f 01 16 1e 02 03 09 06 01 00 03 08 00 ff 06 00 00 00 46 02 02 0f 01 16 20 02 03 09 06 01 00 04 08 00 ff 06 00 01 b8 b6 02 02 0f 01 16 20 f1 db"

filter_keys = ["typecode", "obis_code", "unit_code", "scaler", "rawvalue"]

test_mode = False
debug = 0 # 0, 1, 2

def aidon_callback(cosem_objects):
	print "\nList with " + str(len(cosem_objects)) + " elements"
	for cosem_object in cosem_objects:
		out = {k: v for k, v in cosem_object.items() if k not in filter_keys}
		print cosem_object['obis_code'] + "\t: " + str(out)
	print

ser = serial.Serial(sys.argv[1], 2400, timeout=0.05, parity=serial.PARITY_NONE)
a = aidon(aidon_callback, debug = debug)

if test_mode:
	raw_test = list3_test.replace(" ", "").decode('hex')
	a.parse(raw_test)
else:
	while(1):
		while ser.inWaiting():
			a.decode(ser.read(1))
		time.sleep(0.01)

