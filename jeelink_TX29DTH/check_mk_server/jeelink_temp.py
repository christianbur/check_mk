factory_settings["jeelink_default_levels"] = {
    "levels"                    : (70, 80),
    "device_levels_handling"    : "devdefault",
}



def inventory_jeelink_temp(info):
   inventory = []
   for sensor in info:
	sensor_name = sensor[0].split(";")[0]
	inventory.append( (sensor_name, None) )

   return inventory

def check_jeelink_temp(item, params, info):

        dev_warn = 1
        dev_crit = 1

	for sensor in info:
		sensor_name = sensor[0].split(";")[0]
		if sensor_name == item:
			temperature = savefloat(sensor[0].split(";")[1])
			humidity = saveint(sensor[0].split(";")[2])
			battery_weak = sensor[0].split(";")[3]
			battery_new = sensor[0].split(";")[4]
			counter = saveint(sensor[0].split(";")[5])
			last_update = saveint(sensor[0].split(";")[6])
			last_seen = saveint(sensor[0].split(";")[7])

			minute_2 = 2 * 60
			if last_seen < int(time.time()) - minute_2:
				return 1, "received data older than 2 minutes (!)"

			if humidity == 0:
                                t_status, t_infotext, t_perfdata = check_temperature(temperature, params)
				status   = t_status
                                infotext = "T: %s" % t_infotext
				perfdata = t_perfdata

			else:
				h_status, h_infotext, h_perfdata = check_humidity(humidity, params)
				t_status, t_infotext, t_perfdata = check_temperature(temperature, params)
				status   = t_status
				infotext = "T: %s, H: %s" % (t_infotext, h_infotext)
				perfdata = t_perfdata + h_perfdata

			infotext += ", (Counter: %s)" % (counter)
			if battery_weak != "-":
				infotext += " - (!) Battery weak"
				status = 1
			if battery_new != "-":
                                infotext += " -(!) Battery New"

			return status, infotext, perfdata


# declare the check to Check_MK
check_info["jeelink_temp"] = {
    'check_function':            check_jeelink_temp,
    'has_perfdata':              True,
    'inventory_function':        inventory_jeelink_temp,
    'service_description':       'jeelink %s',
    "includes"                : [ "temperature.include" , "humidity.include"],
    "group"                   : "temperature",
    "default_levels_variable" : "jeelink_temp_default_levels",
}
