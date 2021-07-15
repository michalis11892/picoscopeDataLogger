import ctypes
import numpy as np
from matplotlib import pyplot as plt
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok
import time
from data_block import data_block
from data_rapid_block import data_rapid_block
from data_streaming import data_streaming
from sigGen_stndrd import sigGen_stndrd
from power_operations_scope import *

'''Autodetect driver version for single connected picoscope
from picosdk.discover import find_all_units
scopes = find_all_units() #Will contain infomration on all connected picoscopes
str(scopes[0].info.driver).split(' ')[1]
'''

chandle = ctypes.c_int16()
status = {}

start_scope([chandle, status])

#TEST sigGen_stndrd()
sigGen_stndrd(chandle, status, 0, 1000000, 0, 100, 10000, 100, 0.1, 0, 0, 0, 0, 0, 0, 1)
#time.sleep(60)

#TEST data_block()
buff = []
for i in range(10):
    buff.append(data_block(chandle, status, 'A', [0,0], [6,0], [0,0], True, [[1, 0, 0, 0, 0, 0, 0, 0]], 'A', 1024, 2, 0, 1000, 2500, 2500, 32, 0, 1)[0])
f = open('test.txt', 'w')
for run in buff:
    if True: #True for plots
        plt.plot(run[0], run[1])
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    if False: #True for file writing
        for axis in run:
            f.write('--------------------------------------------------------------------\n')
            for element in axis:
                f.write(str(element)+'\n')
f.close()

'''#TEST data_rapid_block() #Measured deadtime between calls ~3/160000 seconds/totalSamples (in data) [Rule of thumb]
buff = []
for i in range(10):
    buff.append(data_rapid_block(chandle, status, 'A', 0, 6, 0, False, [], 1024, 2, 0, 1000, 1600, 1600, 32, 6, 6, 0, 1))
    #restart_scope()
f = open('test.txt', 'w')
for run in buff:
    print('NEW RUN')
    if True: #True for plots
        for list in run:
            plt.plot(list[0], list[1])
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    if False: #True for file writing
        for list in run:
            f.write('--------------------------------------------------------------------=[List]=--------------------------------------------------------------------\n')
            for axis in list:
                f.write('--------------------------------------------------------------------=[Axis]=--------------------------------------------------------------------\n')
                for element in axis:
                    f.write(str(element)+'\n')
f.close()'''

'''#TEST data_streaming()
f = open('test.txt', 'w')
for axis in data_streaming(chandle, status, 'A', [0,0], [6,0], [0,0], 500, 10, 2, 0, 1)[0]:
    f.write('--------------------------------------------------------------------\n')
    for element in axis:
        f.write(str(element)+'\n')
f.close()'''

stop_scope([chandle, status])
