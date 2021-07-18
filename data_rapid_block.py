import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
from trig_config_macros import trig_logic_config
from trig_config_macros import trig_pwq_config

def data_rapid_block(chandle, status, channel, coupling, crange, offset,
                complxTrig, trig_conditions, trig_properties, trig_adc_counts, trig_directions, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples,
                timebase, segments, captures, downsampling_ratio_mode, downsampling_ratio): #Measured deadtime between calls ~~3/160000 seconds/totalSamples (in data) [Rule of thumb]
    '''
    chandle -> Picoscope handle
    All other parameters are single-valued variables

    channel:
        'A' OR 'B'
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
    complxTrig:
        No conditions -> False
        Logical conditions (AND, OR, etc...) -> True
    trig_conditions:
        List of lists, [list1, list2, list3, ...]
        where each list represents the parameters of a condition structure
        list1 = [channelA; channelB; channelC; channelD; external; aux; pulseWidthQualifier; digital]
        where channelA/B/C/D/etc:
            Don't care -> 0
            True -> 1
            False -> 2
        such that all parameters within a condition structure are ANDed (channelA AND channelB)
        and all condition structres are then ORed (struct_list1 OR struct_list2 OR struct_list3 OR ...)
    trig_properties:
        List of lists, [list1, list2, list3, ...]
        where each list represents the parameters of a property structure
        list1 = [thresholdUpper, thresholdUpperHysteresis, thresholdLower, thresholdLowerHysteresis, channel, thresholdMode]
        such that,
        thresholdUpper, thresholdUpperHysteresis, thresholdLower, thresholdLowerHysteresis:
            -> ADC Counts
        channel:
            A -> 0
            B -> 1
            C -> 2
            D -> 4
        thresholdMode:
            Level -> 0
            Window -> 1
    trig_adc_counts:
        -32512 <= trig_adc_counts <= +32512 (trigger threshold),
            -32512  -> corresponds to the Minimum Range Voltage
            0 -> corresponds to 0 Volts
            +32512 -> corresponds to the Maximum Range Voltage
    trig_directions:
        List of numbers indicating the trigger direction for each channel (trigger mode),
            Above (level)/ Inside (window) -> 0
            Below (level)/ Outside (window) -> 1
            Rising (level)/ Enter (window) -> 2
            Falling (level)/ Exit (window) -> 3
            Rising Or Falling (level) -> 4
            Above Lower (level) -> 5
            Below Lower (level) -> 6
            Rising Lower (level) -> 7
            Falling Lower (level) -> 8
            Positive Runt (level) -> 9
            Negative Runt (level) -> 10
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
    segments:
        Arbitrary number of segments that the internal memory should be divided in
    captures:
        Arbitrary number of waveforms to capture, captures <= segments
    downsampling_ratio_mode:
        None -> 0 (No downsampling)
        Aggregate -> 1 (Keep only block Max and Min)
        Average -> 2 (Keep block Average)
        Decimate -> 3 (Keep only first measured block value)
    downsampling_ratio:
        Samples per data block for downsampling
    '''
    if 'A' == channel:
        status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, coupling, crange, offset)
        assert_pico_ok(status["setChA"])
        if not complexTrig:
            status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, trig_adc_counts, trig_direction, trig_delay, trig_auto)
            assert_pico_ok(status["trigger"])
    elif 'B' == channel:
        status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, coupling, crange, offset)
        assert_pico_ok(status["setChB"])
        if not complexTrig:
            status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 1, trig_adc_counts, trig_direction, trig_delay, trig_auto)
            assert_pico_ok(status["trigger"])

    #Check for logical triggering conditions
    if complxTrig:
        trig_logic_config(chandle, status, trig_conditions, trig_directions, trig_properties, trig_auto)

    # Setting the number of sample to be collected
    maxsamples = preTriggerSamples + postTriggerSamples

    # Gets timebase innfomation
    timeIntervalns = ctypes.c_float()
    returnedMaxSamples = ctypes.c_int16()
    status["GetTimebase"] = ps.ps2000aGetTimebase2(chandle, timebase, maxsamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
    assert_pico_ok(status["GetTimebase"])

    # Creates a overlow location for data
    overflow = ctypes.c_int16()
    # Creates converted types maxsamples
    cmaxSamples = ctypes.c_int32(maxsamples)

    status["MemorySegments"] = ps.ps2000aMemorySegments(chandle, segments, ctypes.byref(cmaxSamples))
    assert_pico_ok(status["MemorySegments"])

    # sets number of captures
    status["SetNoOfCaptures"] = ps.ps2000aSetNoOfCaptures(chandle, captures)
    assert_pico_ok(status["SetNoOfCaptures"])

    # Starts the block capture
    status["runblock"] = ps.ps2000aRunBlock(chandle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
    assert_pico_ok(status["runblock"])

    # Setting the data buffer location for data collection from channel
    # Create buffers ready for assigning pointers for data collection
    bufferMax = []
    bufferMin = []
    if channel == 'A':
        for i in range(segments):
            bufferMax.append((ctypes.c_int16 * maxsamples)())
            bufferMin.append((ctypes.c_int16 * maxsamples)())
            status["SetDataBuffers"] = ps.ps2000aSetDataBuffers(chandle, 0, ctypes.byref(bufferMax[i]), ctypes.byref(bufferMin[i]), maxsamples, i, downsampling_ratio_mode)
            assert_pico_ok(status["SetDataBuffers"])
    elif channel == 'B':
        for i in range(segments):
            status["SetDataBuffers"] = ps.ps2000aSetDataBuffers(chandle, 1, ctypes.byref(bufferMax[i]), ctypes.byref(bufferMin[i]), maxsamples, i, downsampling_ratio_mode)
            assert_pico_ok(status["SetDataBuffers"])
            bufferMax.append((ctypes.c_int16 * maxsamples)())
            bufferMin.append((ctypes.c_int16 * maxsamples)())

    # Creates a overlow location for data
    overflow = (ctypes.c_int16 * 10)()
    # Creates converted types maxsamples
    cmaxSamples = ctypes.c_int32(maxsamples)

    # Checks data collection to finish the capture
    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["isReady"] = ps.ps2000aIsReady(chandle, ctypes.byref(ready))

    status["GetValuesBulk"] = ps.ps2000aGetValuesBulk(chandle, ctypes.byref(cmaxSamples), 0, segments-1, downsampling_ratio, downsampling_ratio_mode, ctypes.byref(overflow))
    assert_pico_ok(status["GetValuesBulk"])

    Times = (ctypes.c_int16*10)()
    TimeUnits = ctypes.c_char()
    status["GetValuesTriggerTimeOffsetBulk"] = ps.ps2000aGetValuesTriggerTimeOffsetBulk64(chandle, ctypes.byref(Times), ctypes.byref(TimeUnits), 0, segments-1)
    assert_pico_ok(status["GetValuesTriggerTimeOffsetBulk"])

    # Finds the max ADC count
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # Creates the time data
    time_ = np.linspace(0, (cmaxSamples.value) * timeIntervalns.value, cmaxSamples.value)

    # Converts ADC from channel A to mV
    results = []
    for i in range(segments):
        results.append([time_, adc2mV(bufferMax[i], crange, maxADC)])

    return results
