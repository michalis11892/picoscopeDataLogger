import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

channels = ['A', 'B', 'C', 'D']

def channel_config(chandle, status, enable, channels_, coupling, cranges_, offset):
    for i in range(len(channels_)):
        indx = "setCh"+channels[channels_[i]]
        status[indx] = ps.ps2000aSetChannel(chandle, channels_[i], enable, coupling, cranges_[i], offset)
        assert_pico_ok(status[indx])

def timebase_block_config(chandle, status, timebase, totalSamples):
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(0) #Not Used - Residual function from older scopes
    cTotalSamples = ctypes.c_int32(totalSamples)
    status["getTimebase2"] = ps.ps2000aGetTimebase2(chandle, timebase, totalSamples, ctypes.byref(timeIntervalns), oversample, ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status["getTimebase2"])
    return np.linspace(0, (cTotalSamples.value) * timeIntervalns.value, cTotalSamples.value)

def timebase_stream_config(totalSamples, sampleInterval, sampleUnits):
    actualSampleIntervalNs = sampleInterval * 1000**(sampleUnits-2)
    print("Capturing at sample interval %s ns" % actualSampleIntervalNs)
    return np.linspace(0, (totalSamples) * actualSampleIntervalNs, totalSamples)

def buffer_block_config(chandle, status, channels_, totalSamples, segments, downsampling_ratio_mode):
    buffersMax = []
    buffersMin = []
    for channel in range(len(channels_)):
        indx = "setDataBuffers"+channels[channels_[channel]]
        buffersMax.append([])
        buffersMin.append([])
        for segment in range(segments):
            buffersMax[channel].append((ctypes.c_int16 * totalSamples)())
            buffersMin[channel].append((ctypes.c_int16 * totalSamples)())
            status[indx] = ps.ps2000aSetDataBuffers(chandle, channel, ctypes.byref(buffersMax[channel][segment]), ctypes.byref(buffersMin[channel][segment]), totalSamples, segment, downsampling_ratio_mode)
            assert_pico_ok(status[indx])
    return buffersMax, buffersMin

def buffer_stream_config(chandle, status, channels_, totalSamples, sizeOfOneBuffer, segments, downsampling_ratio_mode):
    numBuffersToCapture = totalSamples/sizeOfOneBuffer
    if numBuffersToCapture != int(numBuffersToCapture):
        print('Number of nuffers to capture is not integer!\n-> numBuffersToCapture =', numBuffersToCapture)
        exit()
    buffersComplete = []
    buffersMax = []
    buffersMin = []
    for channel in range(len(channels_)):
        indx = "setDataBuffers"+channels[channels_[channel]]
        buffersComplete.append(np.zeros(shape=totalSamples, dtype=np.int16))
        buffersMax.append(np.zeros(shape=sizeOfOneBuffer, dtype=np.int16))
        buffersMin.append(np.zeros(shape=sizeOfOneBuffer, dtype=np.int16))
        for segment in range(segments):
            status[indx] = ps.ps2000aSetDataBuffers(chandle, channel, buffersMax[channel].ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), buffersMin[channel].ctypes.data_as(ctypes.POINTER(ctypes.c_int16)), totalSamples, segment, downsampling_ratio_mode)
            assert_pico_ok(status[indx])
    return buffersComplete, buffersMax, buffersMin

def segment_capture_config(chandle, status, segments, captures, totalSamples):
    cTotalSamples = ctypes.c_int32(totalSamples)
    status["MemorySegments"] = ps.ps2000aMemorySegments(chandle, segments, ctypes.byref(cTotalSamples))
    assert_pico_ok(status["MemorySegments"])

    # sets number of captures
    status["SetNoOfCaptures"] = ps.ps2000aSetNoOfCaptures(chandle, captures)
    assert_pico_ok(status["SetNoOfCaptures"])
