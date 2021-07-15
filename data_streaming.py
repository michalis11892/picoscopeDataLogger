import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import time

nextSample = 0
autoStopOuter = False
wasCalledBack = False

def data_streaming(chandle, status, channel, coupling, crange, offset,
                sizeOfOneBuffer, numBuffersToCapture, sampleUnits, downsampling_ratio_mode, downsampling_ratio):
    '''
    chandle -> Picoscope handle
    status, coupling, crange, offset -> Lists,
        list[0] -> A channel
        list[1] -> B channel
    channel, sizeOfOneBuffer, numBuffersToCapture, sampleUnits, downsampling_ratio_mode, downsampling_ratio -> Variables

    channel:
        'AB' OR 'A' OR 'B' (Any valid permutation of the used channels)
    status:
        Empty list
    coupling:
        AC -> 0
        DC -> 1
    crange:
        10 mV -> 0
        20 mV -> 1
        50 mV -> 2
        100 mV -> 3
        200 mV -> 4
        500 mV -> 5
        1 V -> 6
        2 V -> 7
        5 V -> 8
        10 V -> 9
        20 V -> 10
        50 V -> 11
        MAX RANGE  -> 12
    offset:
        Any offset, same units as range
    sizeOfOneBuffer:
        Number of samples to keep per buffer
    numBuffersToCapture:
        Number of buffers have
    sampleUnits:
        Femptoseconds -> 0
        Picoseconds -> 1
        Nanoseconds -> 2
        Microseconds -> 3
        Milliseconds -> 4
        Seconds -> 5
    downsampling_ratio_mode:
        None -> 0 (No downsampling)
        Aggregate -> 1 (Keep only block Max and Min)
        Average -> 2 (Keep block Average)
        Decimate -> 3 (Keep only first measured block value)
    downsampling_ratio:
        Samples per data block for downsampling
    '''
    enabled = 1
    disabled = 0
    memory_segment = 0
    totalSamples = sizeOfOneBuffer * numBuffersToCapture

    if 'A' in channel:
        # Set up channel
        status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, coupling[0], crange[0], offset[0])
        assert_pico_ok(status["setChA"])
        # Create buffers ready for assigning pointers for data collection
        bufferAMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
        # Set data buffer location for data collection from channel A
        status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,
                                                             0,
                                                             bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                             None,
                                                             sizeOfOneBuffer,
                                                             memory_segment,
                                                             downsampling_ratio_mode)
        assert_pico_ok(status["setDataBuffersA"])
    if 'B' in channel:
        # Set up channel
        status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, coupling[1], crange[1], offset[1])
        assert_pico_ok(status["setChB"])
        # Create buffers ready for assigning pointers for data collection
        bufferBMax = np.zeros(shape=sizeOfOneBuffer, dtype=np.int16)
        # Set data buffer location for data collection from channel B
        status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,
                                                             1,
                                                             bufferBMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                             None,
                                                             sizeOfOneBuffer,
                                                             memory_segment,
                                                             downsampling_ratio_mode)
        assert_pico_ok(status["setDataBuffersB"])

    # Begin streaming mode:
    sampleInterval = ctypes.c_int32(250)
    # We are not triggering:
    maxPreTriggerSamples = 0
    autoStopOn = 1
    status["runStreaming"] = ps.ps2000aRunStreaming(chandle,
                                                    ctypes.byref(sampleInterval),
                                                    sampleUnits,
                                                    maxPreTriggerSamples,
                                                    totalSamples,
                                                    autoStopOn,
                                                    downsampling_ratio,
                                                    downsampling_ratio_mode,
                                                    sizeOfOneBuffer)
    assert_pico_ok(status["runStreaming"])

    actualSampleInterval = sampleInterval.value
    actualSampleIntervalNs = actualSampleInterval * 1000**(sampleUnits-2)

    print("Capturing at sample interval %s ns" % actualSampleIntervalNs)

    # We need a big buffer, not registered with the driver, to keep our complete capture in.
    if 'A' in channel:
        bufferCompleteA = np.zeros(shape=totalSamples, dtype=np.int16)
    if 'B' in channel:
        bufferCompleteB = np.zeros(shape=totalSamples, dtype=np.int16)

    global nextSample, autoStopOuter, wasCalledBack

    def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
        global nextSample, autoStopOuter, wasCalledBack
        wasCalledBack = True
        destEnd = nextSample + noOfSamples
        sourceEnd = startIndex + noOfSamples
        if 'A' in channel:
            bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
        if 'B' in channel:
            bufferCompleteB[nextSample:destEnd] = bufferBMax[startIndex:sourceEnd]
        nextSample += noOfSamples
        if autoStop:
            autoStopOuter = True

    # Convert the python function into a C function pointer.
    cFuncPtr = ps.StreamingReadyType(streaming_callback)

    # Fetch data from the driver in a loop, copying it out of the registered buffers and into our complete one.
    while nextSample < totalSamples and not autoStopOuter:
        wasCalledBack = False
        status["getStreamingLastestValues"] = ps.ps2000aGetStreamingLatestValues(chandle, cFuncPtr, None)
        if not wasCalledBack:
            # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
            # again.
            time.sleep(0.01)

    print("Done grabbing values.")

    # Find maximum ADC count value
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # Create time data
    time_ = np.linspace(0, (totalSamples) * actualSampleIntervalNs, totalSamples)
    results = [[], []] #In mV

    # Convert ADC counts data to mV
    if 'A' in channel:
        results[0] = [time_, adc2mV(bufferCompleteA, crange[0], maxADC)]
    if 'B' in channel:
        results[1] = [time_, adc2mV(bufferCompleteB, crange[1], maxADC)]

    return results
