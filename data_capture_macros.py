import ctypes
import numpy as np
import time
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
from trig_config_macros import trig_logic_config
from trig_config_macros import trig_pwq_config

def data_block(chandle, status, preTriggerSamples, postTriggerSamples, timebase, downsampling_ratio_mode, downsampling_ratio):
    #Run block
    status["runBlock"] = ps.ps2000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, ctypes.c_int16(0), None, 0, None, None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps2000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps2000aIsReady(chandle, ctypes.byref(ready))

    # Create overflow location
    overflow = ctypes.c_int16()
    # create converted type totalSamples
    cTotalSamples = ctypes.c_int32(preTriggerSamples+postTriggerSamples)

    # Retried data from scope to buffers assigned above
    status["getValues"] = ps.ps2000aGetValues(chandle, 0, ctypes.byref(cTotalSamples), downsampling_ratio, downsampling_ratio_mode, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])


def data_rapid_block(chandle, status, preTriggerSamples, postTriggerSamples, timebase, segments, captures, downsampling_ratio_mode, downsampling_ratio): #Measured deadtime between calls ~~3/160000 seconds/totalSamples (in data) [Rule of thumb]
    # Starts the block capture
    status["runblock"] = ps.ps2000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
    assert_pico_ok(status["runblock"])

    # Creates a overlow location for data
    overflow = (ctypes.c_int16 * 10)()
    # Creates converted types maxsamples
    cTotalSamples = ctypes.c_int32(preTriggerSamples+postTriggerSamples)

    # Checks data collection to finish the capture
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps2000aIsReady(chandle, ctypes.byref(ready))

    status["GetValuesBulk"] = ps.ps2000aGetValuesBulk(chandle, ctypes.byref(cTotalSamples), 0, segments-1, downsampling_ratio, downsampling_ratio_mode, ctypes.byref(overflow))
    assert_pico_ok(status["GetValuesBulk"])

    Times = (ctypes.c_int16*10)()
    TimeUnits = ctypes.c_char()
    status["GetValuesTriggerTimeOffsetBulk"] = ps.ps2000aGetValuesTriggerTimeOffsetBulk64(chandle, ctypes.byref(Times), ctypes.byref(TimeUnits), 0, segments-1)
    assert_pico_ok(status["GetValuesTriggerTimeOffsetBulk"])


nextSample = 0
autoStopOuter = False
wasCalledBack = False

def data_streaming(chandle, status, sampleInterval, autoStopOn, buffersComplete, buffersMax, sizeOfOneBuffer, sampleUnits, preTriggerSamples, postTriggerSamples, downsampling_ratio_mode, downsampling_ratio):

    # Begin streaming mode:
    sampleInterval = ctypes.c_int32(sampleInterval)
    status["runStreaming"] = ps.ps2000aRunStreaming(chandle, ctypes.byref(sampleInterval), sampleUnits, preTriggerSamples, postTriggerSamples,
                                                    autoStopOn, downsampling_ratio, downsampling_ratio_mode, sizeOfOneBuffer)
    assert_pico_ok(status["runStreaming"])

    global nextSample, autoStopOuter, wasCalledBack
    #Reset their value in case of consecutive runs
    nextSample = 0
    autoStopOuter = False
    wasCalledBack = False

    def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
        global nextSample, autoStopOuter, wasCalledBack
        wasCalledBack = True
        destEnd = nextSample + noOfSamples
        sourceEnd = startIndex + noOfSamples
        for i in range(len(buffersComplete)):
            buffersComplete[i][nextSample:destEnd] = buffersMax[i][startIndex:sourceEnd]
        nextSample += noOfSamples
        if autoStop:
            autoStopOuter = True

    # Convert the python function into a C function pointer.
    cFuncPtr = ps.StreamingReadyType(streaming_callback)

    # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
    totalSamples = preTriggerSamples+postTriggerSamples
    while nextSample < totalSamples and not autoStopOuter:
        wasCalledBack = False
        status["getStreamingLastestValues"] = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
        if not wasCalledBack:
            # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
            # again.
            time.sleep(0.01)

    print("Stream Run Done")
