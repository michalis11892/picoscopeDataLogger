import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

#-----------------------------------------[Functions]-----------------------------------------
def data_block(chandle, status, channel, coupling, range, offset,
                trig_channel, trig_adc_counts, trig_direction, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples,
                timebase, downsampling_ratio_mode, downsampling_ratio):
    '''
    chandle -> Picoscope handle
    status, coupling, range, offset -> Lists,
        list[0] -> A channel
        list[1] -> B channel
    channel, trig_channel, trig_adc_counts, trig_direction, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples, timebase, downsampling_ratio_mode, downsampling_ratio -> Variables

    channel:
        'AB' OR 'A' OR 'B' (Any valid permutation of the used channels)
    status:
        Empty list
    coupling:
        AC -> 0
        DC -> 1
    range:
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
    trig_channel:
        'A' OR 'B' (Single channel trigger only)
    trig_adc_counts:
        -32512 <= trig_adc_counts <= +32512 (trigger threshold),
            -32512  -> corresponds to the Minimum Range Voltage
            0 -> corresponds to 0 Volts
            +32512 -> corresponds to the Maximum Range Voltage
    trig_direction:
        Above -> 0
        Below -> 1
        Rising -> 2
        Falling -> 3
        Rising Or Falling -> 4
    trig_delay:
        Arbitrary trigger delay in ms
    trig_auto:
        Arbitrary number of milliseconds the device will wait if no trigger occurs in ms
    preTriggerSamples:
        Arbitrary number of samples to keep before trigger fire point
    postTriggerSamples:
        Arbitrary number of samples to keep after trigger fire point
    timebase:
        Let MSR be the Maximum Smapling Rate of the device and n be the timebase value,
        Timebase 0 to 2 correspond to a sample interval value of 2^n /MSR,
        Timebase 3 to 2^32 correspond to a sample interval value of (n-2)*8 /MSR
    downsampling_ratio_mode:
        None -> 0 (No downsampling)
        Aggregate -> 1 (Keep only block Max and Min)
        Average -> 2 (Keep block Average)
        Decimate -> 3 (Keep only first measured block value)
    downsampling_ratio:
        Samples per data block for downsampling
    '''
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
        return 'Invalid Trigger Channel'

    totalSamples = preTriggerSamples + postTriggerSamples

    # Get timebase information
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int32()
    oversample = ctypes.c_int16(0) #Not Used - Residual function from older scopes
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

#-----------------------------------------[Main Code]-----------------------------------------
chandle = ctypes.c_int16()
status = {}

print(data_block(chandle, status, 'A', ))

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
