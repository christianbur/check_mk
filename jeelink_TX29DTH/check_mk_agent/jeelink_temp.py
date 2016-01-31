#!/usr/bin/env python
# -*- coding: utf-8 -*-


# import sys module
import sys

file = open('/root/python/jeelink.data')
jeelink_data = file.readlines()
file.close()

print( '<<<jeelink_temp>>>' )
for line in jeelink_data:
	print line.strip()
