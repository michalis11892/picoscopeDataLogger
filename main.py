import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

def data_block(chandle, status, channel, coupling, range, offset,
                trig_channel, trig_adc_counts, trig_direction, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples,
                timebase, downsampling_ratio_mode, downsampling_ratio):
    #Set channels
    if 'A' in channel:
        status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, coupling[0], range[0], offset[0])
        assert_pico_ok(status["setChA"])
    if 'B' in channel:
        status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, coupling[1], range[1], offset[1])
        assert_pico_ok(status["setChB"])

    #Set triggers
    if trig_channel == 'A':
        status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, trig_adc_counts, trig_direction, trig_delay, trig_auto)
        assert_pico_ok(status["trigger"])
    else if trig_channel == 'B':
        status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 1, trig_adc_counts, trig_direction, trig_delay, trig_auto)
        assert_pico_ok(status["trigger"])
    else:
        return 'Error'

    totalSamples = preTriggerSamples + postTriggerSamples

    # Get timebase information
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(0)
    status["getTimebase2"] = ps.ps2000aGetTimebase2(chandle,
                                                    timebase,
                                                    totalSamples,
                                                    ctypes.byref(timeIntervalns),
                                                    oversample,
                                                    ctypes.byref(returnedMaxSamples),
                                                    0)
    assert_pico_ok(status["getTimebase2"])

    #Run block
    status["runBlock"] = ps.ps2000aRunBlock(chandle,
                                            preTriggerSamples,
                                            postTriggerSamples,
                                            timebase,
                                            oversample,
                                            None,
                                            0,
                                            None,
                                            None)
    assert_pico_ok(status["runBlock"])

    # Check for data collection to finish using ps2000aIsReady
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps2000aIsReady(chandle, ctypes.byref(ready))

    # Create buffers ready for assigning pointers for data collection && Set data buffer location for data collection
    if 'A' in channel:
        bufferAMax = (ctypes.c_int16 * totalSamples)()
        bufferAMin = (ctypes.c_int16 * totalSamples)()
        status["setDataBuffersA"] = ps.ps2000aSetDataBuffers(chandle,
                                                             0,
                                                             ctypes.byref(bufferAMax),
                                                             ctypes.byref(bufferAMin),
                                                             totalSamples,
                                                             0,
                                                             downsampling_ratio_mode)
        assert_pico_ok(status["setDataBuffersA"])
    if 'B' in channel:
        bufferBMax = (ctypes.c_int16 * totalSamples)()
        bufferBMin = (ctypes.c_int16 * totalSamples)()
        status["setDataBuffersB"] = ps.ps2000aSetDataBuffers(chandle,
                                                             1,
                                                             ctypes.byref(bufferBMax),
                                                             ctypes.byref(bufferBMin),
                                                             totalSamples,
                                                             0,
                                                             downsampling_ratio_mode)
        assert_pico_ok(status["setDataBuffersB"])

    # Create overflow location
    overflow = ctypes.c_int16()
    # create converted type totalSamples
    cTotalSamples = ctypes.c_int32(totalSamples)

    # Retried data from scope to buffers assigned above
    status["getValues"] = ps.ps2000aGetValues(chandle, 0, ctypes.byref(cTotalSamples), downsampling_ratio, downsampling_ratio_mode, 0, ctypes.byref(overflow))
    assert_pico_ok(status["getValues"])


    # find maximum ADC count value
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # Create time data
    time = np.linspace(0, (cTotalSamples.value) * timeIntervalns.value, cTotalSamples.value) #In nanoseconds
    results = [[], []] #In miliVolts

    # convert ADC counts data to mV
    if 'A' in channel:
        adc2mVChAMax =  adc2mV(bufferAMax, chARange, maxADC)
        results[0] = [time, adc2mVChAMax]
    if 'B' in channel:
        adc2mVChBMax =  adc2mV(bufferBMax, chBRange, maxADC)
        results[0] = [time, adc2mVChBMax]

    return results

chandle = ctypes.c_int16()
status = {}

status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

# Stop the scope
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

# Close unitDisconnect the scope
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# display status returns
print(status)
