import ctypes
import copy
import numpy as np
from matplotlib import pyplot as plt
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok
import time
'''from data_block import data_block
from data_rapid_block import data_rapid_block
from data_streaming import data_streaming'''
from data_capture_macros import *
from signal_generator_macros import *
from power_operation_macros import *
from capture_config_macros import *
from trig_config_macros import *
from data_processing_macros import *

'''Autodetect driver version for single connected picoscope
from picosdk.discover import find_all_units
scopes = find_all_units() #Will contain infomration on all connected picoscopes
str(scopes[0].info.driver).split(' ')[1]
'''

channels = ['A', 'B', 'C', 'D']

chandle = ctypes.c_int16()
status = {}

start_scope([chandle, status])

#TEST sigGen_stndrd()
sigGen_stndrd(chandle, status, 0, 1000000, 0, 100, 10000, 100, 0.1, 0, 0, 0, 0, 0, 0, 1)
#time.sleep(60)

#TEST data_block()
channels_ = [0, 1]
preTriggerSamples = 25000
postTriggerSamples = 25000
timebase = 8
totalSamples = preTriggerSamples+postTriggerSamples
segments = 1
channel_config(chandle, status, 1, channels_, 0, 7, 0) #Configure channel A
trig_simple_config(chandle, status, 1, 0, 1024, 2, 0, 1000) #Setup a simple trigger
time_ = timebase_block_config(chandle, status, timebase, totalSamples) #Setup timebase and time axis
buffersMax, buffersMin = buffer_block_config(chandle, status, channels_, totalSamples, segments, 0) #Setup buffer and segments
buff = []
for i in range(3):
    data_block(chandle, status, preTriggerSamples, postTriggerSamples, timebase, 0, 0) #Get data
    buff.append(copy.deepcopy(buffersMax))
for indx in range(len(buff)):
    run = buff[indx]
    run = run_to_mV(chandle, status, run, channels_, 7, totalSamples, segments)
    if True: #True for plots
        for i in range(len(channels_)):
            run_channel = run[i]
            for j in range(segments):
                run_channel_segment = run_channel[j]
                plt.plot(time_, run_channel_segment)
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    if True: #True for file writing
        run_to_file(time_, run, channels_, segments, indx, 'test.out')

#TEST data_rapid_block() #Measured deadtime between calls ~3/160000 seconds/totalSamples (in data) [Rule of thumb]
'''channels_ = [0, 1]
preTriggerSamples = 2500
postTriggerSamples = 2500
timebase = 8
totalSamples = preTriggerSamples+postTriggerSamples
segments = 3
captures = 3
channel_config(chandle, status, 1, channels_, 0, 7, 0) #Configure channels
trig_simple_config(chandle, status, 1, 0, 1024, 2, 0, 1000) #Setup a simple trigger
time_ = timebase_block_config(chandle, status, timebase, totalSamples) #Setup timebase and time axis
segment_capture_config(chandle, status, segments, captures, totalSamples) #Setup memory segmentation & capture configuration
buffersMax, buffersMin = buffer_block_config(chandle, status, channels_, totalSamples, segments, 0) #Setup buffer and segments
buff = []
for i in range(2):
    data_rapid_block(chandle, status, preTriggerSamples, postTriggerSamples, timebase, segments, captures, 0, 0) #Get data
    buff.append(copy.deepcopy(buffersMax))
for indx in range(len(buff)):
    print('NEW RUN')
    run = buff[indx]
    run = run_to_mV(chandle, status, run, channels_, 7, totalSamples, segments)
    if True: #True for plots
        for i in range(len(channels_)):
            run_channel = run[i]
            for j in range(segments):
                run_channel_segment = run_channel[j]
                plt.plot(time_, run_channel_segment)
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    if True: #True for file writing
        run_to_file(time_, run, channels_, segments, indx, 'test.out')'''

#TEST data_streaming()
'''channels_ = [0, 1]
preTriggerSamples = 0
postTriggerSamples = 5000
totalSamples = preTriggerSamples+postTriggerSamples #totalSamples = preTriggerSamples+postTriggerSamples = sizeOfOneBuffer * numBuffersToCapture
sizeOfOneBuffer = 500
totalRuntime = 12500000 #In sampleUnits
sampleInterval = int(totalRuntime/totalSamples)
sampleUnits = 2
segments = 1
channel_config(chandle, status, 1, channels_, 0, 7, 0) #Configure channels
#trig_simple_config(chandle, status, 1, 0, 1024, 2, 0, 1000) #Setup a simple trigger
time_ = timebase_stream_config(totalSamples, sampleInterval, sampleUnits) #Setup timebase and time axis
buffersComplete, buffersMax, buffersMin = buffer_stream_config(chandle, status, channels_, totalSamples, sizeOfOneBuffer, segments, 0) #Setup buffers
buff = []
for i in range(2):
    data_streaming(chandle, status, sampleInterval, 0, buffersComplete, buffersMax, sizeOfOneBuffer, sampleUnits, preTriggerSamples, postTriggerSamples, 0, 1) #Get data
    buff.append(copy.deepcopy(buffersComplete))
for indx in range(len(buff)):
    run = buff[indx]
    run = run_to_mV(chandle, status, run, channels_, 7, totalSamples, segments)
    if True: #True for plots
        for i in range(len(channels_)):
            for j in range(segments):
                plt.plot(time_, run[i][j])
        plt.xlabel('Time (ns)')
        plt.ylabel('Voltage (mV)')
        plt.show()
    if True: #True for file writing
        run_to_file(time_, run, channels_, segments, indx, 'test.out')'''

stop_scope([chandle, status])
