# Aidon AMS meter parser, specifically for OBIS messages used by Hafslund meters
# Needs crcmod (sudo pip install crcmod)

import struct, crcmod

# HDLC constants
FLAG = '\x7e'
ESCAPE = '\x7d'

# HDLC states	
WAITING = 0	
DATA = 1
ESCAPED = 2

# Number of objects in known frames
#LONG_FRAME_OBJECTS = 12

# OBIS types
TYPE_STRING = 0x0a
TYPE_UINT32 = 0x06
TYPE_INT16 = 0x10
TYPE_UINT16 = 0x12
TYPE_OCTET_STRING = 0x09

cosem_units = {
				27: "W",
				28: "VA",
				29: "var",
				30: "Wh",
				31: "VAh",
				32: "varh",
				33: "A",
				34: "C",
				35: "V"
				}

obis_shortname = {
				"1.1.0.2.129.255": "obis_list_id",
				"0.0.96.1.0.255": "meter_id",
				"0.0.96.1.7.255": "meter_type",
				"1.0.1.7.0.255": "p_act_in",
				"1.0.2.7.0.255": "p_act_out",
				"1.0.3.7.0.255": "p_react_in",
				"1.0.4.7.0.255": "p_react_out",
				"1.0.31.7.0.255": "il1",
				"1.0.51.7.0.255": "il2",
				"1.0.71.7.0.255": "il3",
				"1.0.32.7.0.255": "ul1",
				"1.0.52.7.0.255": "ul2",
				"1.0.72.7.0.255": "ul3",
				"0.0.1.0.0.255": "clockdate",
				"1.0.1.8.0.255": "e_act_in_cum_h",
				"1.0.2.8.0.255": "e_act_out_cum_h",
				"1.0.3.8.0.255": "e_react_in_cum_h",
				"1.0.4.8.0.255": "e_react_out_cum_h"
				}

def decode_obis_code(pkt):
	return ".".join("{:01d}".format(ord(c)) for c in pkt)

# Object     02 03 09 06 01 00 01 07 00 ff 06  = 01.00.01.07.00.255       1955
def print_object(pkt):
	return "T:" + str(ord(pkt[0])) + " Q:" + str(ord(pkt[1])) + " OBIS:" + decode_obis_code(pkt[4:10])

def decode_scale_struct(pkt):
	# if this isn't a two item struct somethings wrong
	#import pdb; pdb.set_trace()
	out = {}
	if not (pkt[0] == '\x02' and pkt[1] == '\x02'):
		out["err"] = "Cannot decode. Check Type. Expected struct with quantity 2. Got: " + " ".join("{:02}".format(ord(c)) for c in pkt)

	out["scaler"] = struct.unpack(">b", pkt[3])[0]
	out["unit_code"] =  struct.unpack(">b", pkt[5])[0]
	if out["unit_code"] in cosem_units:
		out["unit"] = cosem_units[out["unit_code"]]
	return out

def print_scale_struct(pkt):
	#import pdb; pdb.set_trace()
	scale_struct = decode_scale_struct(pkt)
	if 'err' in scale_struct:
		return scale_struct['err']
	return "Scaler:" + str((scale_struct['scaler'])) + "\tUnit:" + str((scale_struct['unit_code'])) + "(" + scale_struct['unit'] + ")" # +"\tRAW:" + " ".join("{:02}".format(ord(c)) for c in pkt)

class aidon:
	def __init__(self, callback, debug=False):
		self.state = WAITING
		self.pkt = ""
		self.crc_func = crcmod.mkCrcFun(0x11021, rev=True, initCrc=0xffff, xorOut=0x0000)
		self.callback = callback
		self.debug = debug

	# Does a lot of assumptions on Aidon/Hafslund COSEM format
	# Not a general parser! 
	def parse(self, pkt):
		# 0,1 frame format
		# 2 client address
		# 3,4 server address
		# 5 control
		# 6,7 HCS
		# 8,9,10 LLC
		#print("\n")
		if self.debug >= 2: print("Parser:: New Msg HexDump without 7E follows\n--------------------------------------------------")
		if self.debug >= 2: print " ".join("{:02x}".format(ord(c)) for c in pkt)
		if self.debug >= 2: print("--------------------------------------------------")

		frame_type = (ord(pkt[0]) & 0xf0) >> 4
		frame_length = ((ord(pkt[0]) & 0x07) << 8) + ord(pkt[1])
		object_count = ord(pkt[18])
		
		if self.debug >= 1: print "Header     " + " ".join("{:02x}".format(ord(c)) for c in pkt[0:11]) + " : FrameType: " + str(frame_type) + " FrameLength: " + str(frame_length)
		if self.debug >= 1: print "DataHeader " + " ".join("{:02x}".format(ord(c)) for c in pkt[11:17])
		if self.debug >= 1: print "Type & Len " + " ".join("{:02x}".format(ord(c)) for c in pkt[17:19])
		if self.debug >= 1: print

		pkt = pkt[19:] # Remove 18 first bytes to start with first object inside the first object

		#if (object_count == LONG_FRAME_OBJECTS):
		cosem_objects = []

		for j in range(0, object_count):
			msg_current_pos = 0
			msg_type = ord(pkt[0])		# Expect this to be 2 = struct
			msg_quantity = ord(pkt[1])   # Varies depending on which list we get. 1 for 2.5 update, 12 for 10 sec, 17 for hourly

			# First element we get is the obis octet
			obis_type = ord(pkt[2])
			obis_length = ord(pkt[3])
			obis_code = decode_obis_code(pkt[4:10])

			# Second element is the value
			value_type = ord(pkt[10])

			data = {}
			data['typecode'] = "{:02d}".format(value_type)
			data['obis_code'] = obis_code
			if obis_code in obis_shortname:
				data['obis_shortname'] = obis_shortname[obis_code]

			if self.debug >= 1: print "Object     " + print_object(pkt[0:11]),

			if (value_type == TYPE_STRING):
				strlen = ord(pkt[11])
				data['value'] = pkt[12:12+strlen]
				msg_current_pos = 12+strlen

			elif (value_type == TYPE_UINT32): 
				data['rawvalue'] = struct.unpack(">I", pkt[11:15])[0]
				msg_current_pos = 15

			elif (value_type == TYPE_INT16):
				data['rawvalue'] = struct.unpack(">h", pkt[11:13])[0]
				msg_current_pos = 13

			elif (value_type == TYPE_UINT16):
				data['rawvalue'] = struct.unpack(">H", pkt[11:13])[0]
				msg_current_pos = 13
			elif value_type == TYPE_OCTET_STRING:
				octets = ord(pkt[11])
				#print "\t= Octets:" + str(octets),
				if octets == 12: #DateTime
					year = struct.unpack(">H", pkt[12:14])[0]
					month = ord(pkt[14])
					dayofmonth = ord(pkt[15])
					dayofweek = ord(pkt[16])
					hour = ord(pkt[17])
					minute = ord(pkt[18])
					second = ord(pkt[19])
					seconds_houndred = ord(pkt[20])
					deviation = struct.unpack(">h", pkt[21:23])[0]
					clock_status = ord(pkt[23])

					datetime = str(year) + "." + "{:02}".format(month) + "." + "{:02}".format(dayofmonth) + "T" + "{:02}".format(hour) + ":" + "{:02}".format(minute) + ":" + "{:02}".format(second) 
					if not seconds_houndred == 255:
						datetime += "." + "{:02}".format(seconds_houndred)

					data['datetime'] = datetime
					data['deviation'] = deviation
					data['clock_status'] = clock_status
					#data += " deviation: " + str(deviation) + " clock_status:" + str(clock_status)
				msg_current_pos = octets * 2

			else:
				print " -- Unknown Type: " + str(data['typecode']) + " for OBIS Code: " + obis_code
				return # Unknown field - We need to return as we don't know the position to advance to
			
			# We assume the third message element is the scale_val structure we get with registers. This has length 6
			if msg_quantity == 3:
				scale_struct = decode_scale_struct(pkt[msg_current_pos:msg_current_pos+6])
				if 'err' in scale_struct:
					print "Error in parsing scaleval_struct: " + scale_struct['err']
				else:
					data.update(scale_struct)

				# Scaling with some checking in preparation for future cleanup
				if "scaler" in data:
					if data['scaler'] != 0:
						data['value'] = data['rawvalue'] * 10**data['scaler']
						if data['scaler'] > 0:
							data['value'] = int(data['value'])
						else:
							data['value'] = round(data['value'],3)
					else:
						data['value'] = data['rawvalue']
						del data['rawvalue']

				msg_current_pos += 6
			
			if self.debug >= 1: print "\t= " + str(data)
			cosem_objects.append(data)
			pkt = pkt[msg_current_pos:]

		self.callback(cosem_objects)

	# General HDLC decoder
	def decode(self, c):
		# Waiting for packet start
		if (self.state == WAITING): 
			if (c == FLAG):
				self.state = DATA
				self.pkt = ""

		elif (self.state == DATA):
			if (c == FLAG):
				# Minimum length check
				if (len(self.pkt) >= 19):
					# Check CRC
					crc = self.crc_func(self.pkt[:-2])
					crc ^= 0xffff
					if (crc == struct.unpack("<H", self.pkt[-2:])[0]):
						self.parse(self.pkt)
				self.pkt = ""
			elif (c == ESCAPE):
				self.state = ESCAPED
			else:
				self.pkt += c

		elif (self.state == ESCAPED):
			self.pkt += chr(ord(c) ^ 0x20)
			self.state = DATA

