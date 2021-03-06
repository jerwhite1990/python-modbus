#!/usr/bin/env python

# Based on Morningstar documentation here
# http://www.morningstarcorp.com/wp-content/uploads/2014/02/TSMPPT.APP_.Modbus.EN_.10.2.pdf
# and heavily modified version of the script here
# http://www.fieldlines.com/index.php?topic=147639.0

# This is modified for the non-MPPT tri-stars without built-in network monitoring. It has different indices and different available data.

import sys
import re
import time
counter = 0

script = sys.argv[0]
host = re.sub(r".*tristar_monitoring_",'',script)

if len(sys.argv) == 2:
    if sys.argv[1] == "config":
#        print "host_name %s" % host
        print "graph_category power"
       	print "graph_title Solar Charge Controller Info"
	print "graph_vlabel A bit of all (V, A, C)"
	print "vPanel.label panel potential (V)"
	print "vPanel.max   80"
	print "vBattTerm.label battery potential at terminals (V)"
        print "vBattTerm.max 32"
        print "vBattTerm.warning 25:32"
        print "vBattTerm.critical 24:33"
#	print "vBattSense.label battery potential sensing (V)"
#	print "vBattSense.max 32"
	print "hsTemp.label heat sink temperature (C)"
	print "hsTemp.max 120"
        print "hsTemp.warning :60"
        print "hsTemp.critical :80"
	# print "battTemp.label battery temperature (C)"
	# print "battTemp.max 120"
        # print "battTemp.warning :80"
        # print "battTemp.critical :100"
	print "aPanel.label charge current (A)"
	print "aPanel.max 20"
#        print "aPanel.warning :15"
#        print "aPanel.critical :19"
#	print "aBatt.label battery current (A)"
#	print "aBatt.max 20"
#        print "aBatt.warning :15"
#        print "aBatt.critical :19"
        exit(0)
# import the server implementation
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# configure the client logging
import logging
logging.basicConfig()
log = logging.getLogger('./modbus.error')
log.setLevel(logging.ERROR)

client = ModbusClient(method='rtu',port='/dev/ttyUSB0', baudrate=9600, timeout=1)
client.connect()
log.debug(client)

# Define the State list
state = ['Start', 'Night Check', 'Disconnected', 'Night', 'Fault!', 'BulkCharge', 'Absorption', 'FloatCharge', 'Equalizing']

# read registers. Start at 0 for convenience
rr = client.read_holding_registers(0,37,1)
if rr == None:
    client.close()
    log.error("couldn't connect")
    exit(1)

# for all indexes, subtract 1 from what's in the manual
#V_PU_hi = rr.registers[0]
#V_PU_lo = rr.registers[1]
#I_PU_hi = rr.registers[2]
#I_PU_lo = rr.registers[3]

#V_PU = float(V_PU_hi) + float(V_PU_lo)
#I_PU = float(I_PU_hi) + float(I_PU_lo)

v_scale = 96.667 * 2**(-15)
i_scale = 66.667 * 2**(-15)
#p_scale = V_PU * I_PU * 2**(-17)
array_scale = 139.15 * 2**(-15)
# battery sense voltage, filtered
battsV = rr.registers[8] * v_scale
#battsV = ( rr.registers[8] * 96.667 ) / 32768
#battsSensedV = rr.registers[26] * v_scale
battsI = rr.registers[12] * i_scale * 4.75
arrayV = rr.registers[10] * array_scale
arrayI = rr.registers[11] * i_scale
statenum = rr.registers[27]
hsTemp = rr.registers[14] 
#rtsTemp = rr.registers[36]
#outPower = rr.registers[58] * p_scale
#inPower = rr.registers[59] * p_scale
#minVb_daily = rr.registers[64] * v_scale
#maxVb_daily = rr.registers[65] * v_scale
#minTb_daily = rr.registers[71]
#maxTb_daily = rr.registers[72]
dipswitches = bin(rr.registers[25])[::-1][:-2].zfill(8)
#led_state = rr.registers
print "vBattTerm.value %.2f" % battsV
#print "vBattSense.value %.2f" % battsSensedV
#print "aBatt.value %.2f" % battsI
#print "battery watts:   %.2f" % (battsV*battsI)
print "vPanel.value %.2f" % arrayV
print "aPanel.value %.2f" % arrayI
#print "array watts:     %.2f" % (arrayV*arrayI)
print "hsTemp.value %.2f" % hsTemp
#print "battTemp.value %.2f" % rtsTemp
print "state:           %s" % state[statenum]
#print "out power:       %0.2f" % outPower
#print "in Power:        %0.2f" % inPower
#print "min Vb daily:    %0.2f" % minVb_daily
#print "max Vb daily:    %0.2f" % maxVb_daily
#print "min Tb daily:    %0.2f" % minTb_daily
#print "max Tb daily:    %0.2f" % maxTb_daily
print "dipswitches:     %s" % dipswitches
print "dipswitches:     12345678"
#print ""
client.close()
