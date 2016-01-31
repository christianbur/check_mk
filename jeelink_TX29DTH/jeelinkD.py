#!/usr/bin/env python

#http://fredboboss.free.fr/articles/tx29.php/

#https://github.com/rufik/LaCrosse_ITPlus_Reader/blob/master/jeelink_stuff/arduino_project/projects/LaCrosseITPlusReader/LaCrosseITPlusReader.ino

import serial, sys, time, pprint

sensor_dict = {
                "AC":{"1":{"sensor_name":"KS_Kuehlschrank"},
                      "2":{"sensor_name":"KS_Gefrierfach"},
                     },
                "8C":{"1":{"sensor_name":"Schlafzimmer_Fenster"}},
                "38":{"1":{"sensor_name":"Schlafzimmer_Bett"}},
                "B4":{"1":{"sensor_name":"Wohnzimmer"}},
                "D0":{"1":{"sensor_name":"Kueche"}},
                "20":{"1":{"sensor_name":"Bad"}},
                }


def is_valid_frame(frame):
        if len(frame) == 7:
                if frame[0] == "OK" and frame[1] == "9":
                        return True
        return False

def decode_battery_new(frame_3):
	battery_new_flag = "{0:08b}".format(int(frame_3))[0]

	if battery_new_flag == "1":
		return "NEW"
	else:
		return "-"

def decode_battery_weak(frame_6):
        battery_weak_flag = "{0:08b}".format(int(frame_6))[0]

        if battery_weak_flag == "1":
                return "WEAK"
        else:
                return "-"

def decode_humidity(frame_6):
        humidity_byte = "{0:08b}".format(int(frame_6))[1:8]
	humidity = int(humidity_byte, 2)

	if humidity <= 100:
		return humidity
	elif humidity == 106 or humidity == 125:
		return 0
	else:
		return "UNKNOWN"


def decode_temperature(frame_4,frame_5):
	return (int(frame_4) * 256 + int(frame_5) - 1000) / float(10)

def decode_sensor_id(frame_2):
	sensor_id = "{0:02X}".format(int(frame_2) * 4)
	return sensor_id

def decode_sensor_type(frame_3):
        sensor_type_byte = "{0:08b}".format(int(frame_3))[1:8]
	sensor_type = str(int(sensor_type_byte, 2))
        return sensor_type


def get_sensor_name(frame_2, frame_3):
	sensor_type = decode_sensor_type(frame_3)
	sensor_id   = decode_sensor_id(frame_2)

	if sensor_id in sensor_dict:
		if sensor_type in sensor_dict[sensor_id]:
			return sensor_dict[sensor_id][sensor_type]["sensor_name"]

	return "SENSOR (ID: %s (%s), type: %s)" % (sensor_id, str(frame_2), sensor_type)

def update_sensor_dict(sensor_id, sensor_type, temperature, humidity, battery_new, battery_weak):

	data_changed = False

        if sensor_id in sensor_dict:
                if sensor_type in sensor_dict[sensor_id]:

			if "last_update" not in sensor_dict[sensor_id][sensor_type]:
                        	sensor_dict[sensor_id][sensor_type]["temperature"] = temperature
                        	sensor_dict[sensor_id][sensor_type]["humidity"] = humidity
                        	sensor_dict[sensor_id][sensor_type]["battery_weak"] = battery_weak
                        	sensor_dict[sensor_id][sensor_type]["battery_new"] = battery_new
                                sensor_dict[sensor_id][sensor_type]["counter"] = -1
				data_changed = True
			else:
				if sensor_dict[sensor_id][sensor_type]["temperature"] != temperature:
					sensor_dict[sensor_id][sensor_type]["temperature"] = temperature
					data_changed = True
                                if sensor_dict[sensor_id][sensor_type]["humidity"] != humidity:
                                        sensor_dict[sensor_id][sensor_type]["humidity"] = humidity
                                        data_changed = True
                                if sensor_dict[sensor_id][sensor_type]["battery_weak"] != battery_weak:
                                        sensor_dict[sensor_id][sensor_type]["battery_weak"] = battery_weak
                                        data_changed = True
				if sensor_dict[sensor_id][sensor_type]["battery_new"] != battery_new:
                                        sensor_dict[sensor_id][sensor_type]["battery_new"] = battery_new
                                        data_changed = True

			if data_changed == True:
				sensor_dict[sensor_id][sensor_type]["last_update"] = int(time.time())

			sensor_dict[sensor_id][sensor_type]["last_seen"] = int(time.time())
                        sensor_dict[sensor_id][sensor_type]["counter"] += 1

	else:
		sensor_dict[sensor_id] = {}
		sensor_dict[sensor_id][sensor_type] = {"sensor_name":"UNKNOWN_ID:" + sensor_id + "_TYPE:" + sensor_type}

	return data_changed

def save_data():
        file = open("/root/python/jeelink.data", "w")
	for sensor_id in sensor_dict:
        	for sensor_type in sensor_dict[sensor_id]:
                	if "last_update" in sensor_dict[sensor_id][sensor_type]:
				minute_2 = 2 * 60
				if sensor_dict[sensor_id][sensor_type]["last_seen"] < int(time.time()) - minute_2:
					continue
                        	data = "%s;%s;%s;%s;%s;%s;%s;%s" % (
                                                                        sensor_dict[sensor_id][sensor_type]["sensor_name"],
                                                                        sensor_dict[sensor_id][sensor_type]["temperature"],
                                                                        sensor_dict[sensor_id][sensor_type]["humidity"],
                                                                        sensor_dict[sensor_id][sensor_type]["battery_weak"],
                                                                        sensor_dict[sensor_id][sensor_type]["battery_new"],
                                                                        sensor_dict[sensor_id][sensor_type]["counter"],
									sensor_dict[sensor_id][sensor_type]["last_update"],
									sensor_dict[sensor_id][sensor_type]["last_seen"],
                                                                )
                                file.write(data + "\n")
				#print data
	file.close()

jeelink = serial.Serial('/dev/ttyUSB0', 57600)
#jeelink.open()
time.sleep(10)
jeelink.write("0a\r\n")
print "blue LED deactivate"

while True:
	try:
		frame = jeelink.readline().split()

		if not is_valid_frame(frame):
			continue

        	sensor_type = decode_sensor_type(frame[3])
        	sensor_id   = decode_sensor_id(frame[2])
		sensor_name = get_sensor_name(frame[2], frame[3])
		temperature = decode_temperature(frame[4],frame[5])
		humidity = decode_humidity(frame[6])
		battery_weak = decode_battery_weak(frame[6])
		battery_new = decode_battery_new(frame[3])

		if update_sensor_dict(sensor_id, sensor_type, temperature, humidity, battery_new, battery_weak):
			save_data()
		#data = "ID: %-20s ;T: %-5s ;H: %-4s ;B_n: %s ;B_w: %s\n" % (sensor_name, temperature, humidity, battery_new, battery_weak)
		#print data
    	except KeyboardInterrupt:
        	jeelink.close()
        	break
