import ctypes
import numpy as np
from matplotlib import pyplot as plt
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
import time

'''Autodetect driver version for single connected picoscope
from picosdk.discover import find_all_units
scopes = find_all_units() #Will contain infomration on all connected picoscopes
str(scopes[0].info.driver).split(' ')[1]
'''
#-----------------------------------------[Functions]-----------------------------------------
def data_block(chandle, status, channel, coupling, crange, offset,
                trig_channel, trig_adc_counts, trig_direction, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples,
                timebase, downsampling_ratio_mode, downsampling_ratio):
    '''
    chandle -> Picoscope handle
    status, coupling, crange, offset -> Lists,
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
        status["setChA"] = ps.ps2000aSetChannel(chandle, 0, 1, coupling[0], crange[0], offset[0])
        assert_pico_ok(status["setChA"])
    if 'B' in channel:
        status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, coupling[1], crange[1], offset[1])
        assert_pico_ok(status["setChB"])

    #Set triggers
    if trig_channel == 'A':
        status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, trig_adc_counts, trig_direction, trig_delay, trig_auto)
        assert_pico_ok(status["trigger"])
    elif trig_channel == 'B':
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
    time_ = np.linspace(0, (cTotalSamples.value) * timeIntervalns.value, cTotalSamples.value) #In nanoseconds
    results = [[], []] #In mV

    # convert ADC counts data to mV
    if 'A' in channel:
        adc2mVChAMax =  adc2mV(bufferAMax, crange[0], maxADC)
        results[0] = [time_, adc2mVChAMax]
    if 'B' in channel:
        adc2mVChBMax =  adc2mV(bufferBMax, crange[1], maxADC)
        results[1] = [time_, adc2mVChBMax]

    return results

def data_rapid_block(chandle, status, channel, coupling, crange, offset,
                complxTrig, trig_conditions, trig_adc_counts, trig_direction, trig_delay, trig_auto, preTriggerSamples, postTriggerSamples,
                timebase, segments, captures, downsampling_ratio_mode, downsampling_ratio): #Measured deadtime between calls ~30 ms (in data)
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
        status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 0, trig_adc_counts, trig_direction, trig_delay, trig_auto)
        assert_pico_ok(status["trigger"])
    elif 'B' == channel:
        status["setChB"] = ps.ps2000aSetChannel(chandle, 1, 1, coupling, crange, offset)
        assert_pico_ok(status["setChB"])
        status["trigger"] = ps.ps2000aSetSimpleTrigger(chandle, 1, 1, trig_adc_counts, trig_direction, trig_delay, trig_auto)
        assert_pico_ok(status["trigger"])

    #Check for logical triggering conditions
    if complxTrig:
        cond_list = []
        try:
            for condition in trig_conditions:
                cond_list.append(PS2000A_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6], condition[7]))

            command = 'ps2000a.ps2000aSetTriggerChannelConditions(chandle'
            for i in range(len(cond_list)):
                command += ', cond_list['+str(i)+']'
            command += ', '+str(len(cond_list))+')'
            exec(comand) #BE VARY CAREFUL!!! VERY HARMFUL IF EXPLOITED
        except:
            print('ERROR')
            exit()

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
    '''nextSample = 0
    autoStopOuter = False
    wasCalledBack = False'''

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

def sigGen_stndrd(chandle, status, offsetVoltage, pkToPk, waveType,  startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggerType, triggerSource, extInThreshold):
    '''
    chandle -> Picoscope handle
    status:
        Empty list
    offsetVoltage:
        Signal offset voltage from 0, in μV
    pkToPk:
        Signal peak-to-peak voltage, in μV
    waveType:
        Sine -> 0
        Square -> 1
        Triangle -> 2
        DC Voltage -> 3
        Rising Sawtooth (Ramp Up) -> 4
        Falling Sawtooth (Ramp Down) -> 5
        Sin(x)/x -> 6
        Gaussian -> 7
        Half Sine -> 8
    startFrequency:
        Start frequency, in Hz (careful wiht specific signal frequency bounds)
    stopFrequency:
        End frequency, in Hz (careful wiht specific signal frequency bounds)
    increment:
        Amount of frequency increase or decrease in sweep mode
    dwellTime:
        Time for which the sweep stays at each frequency, in seconds
    sweepType:
        Up -> 0
        Down -> 1
        Up-Down -> 2
        Down-Up -> 3
    operation:
        Normal signal generator operation specified by waveType -> 0
        White noise and ignores all settings except pkToPk and offsetVoltage -> 1
        Pseudorandom binary sequence at the specified frequency or frequency range -> 2
    shots:
        Sweep the frequency as specified by sweeps -> 0
            OR
        The number of cycles of the waveform to be produced after a trigger event [sweeps must be zero]
        (not PicoScope 2205 MSO)
    sweeps:
        Produce number of cycles specified by shots -> 0
            OR
        The number of times to sweep the frequency after a trigger event, according to sweepType [shots must be zero]
    triggerType:
        Rising -> 0
        Falling -> 1
        Gate High -> 2
        Gate Low -> 3
    triggerSource:
        None -> 0
        Scope Trigger -> 1
        Ext Input -> 2
        Software Trigger [ps2000aSigGenSoftwareControl()] -> 3
        Reserved -> 4
    extInThreshold:
        Trigger level, in ADC counts, for external trigger
    '''
    waveType = ctypes.c_int16(waveType)
    sweepType = ctypes.c_int32(sweepType)
    triggertype = ctypes.c_int32(triggerType)
    triggerSource = ctypes.c_int32(triggerSource)

    status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle, offsetVoltage, pkToPk, waveType, startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggertype, triggerSource, extInThreshold)
    assert_pico_ok(status["SetSigGenBuiltIn"])

def restart_scope():
    global chandle, status
    # Stop the scope
    status["stop"] = ps.ps2000aStop(chandle)
    assert_pico_ok(status["stop"])

    # Close unitDisconnect the scope
    status["close"] = ps.ps2000aCloseUnit(chandle)
    assert_pico_ok(status["close"])

    # display status returns
    print(status)

    chandle = ctypes.c_int16()
    status = {}

    # Open the scope
    status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
    assert_pico_ok(status["openunit"])

#-----------------------------------------[Main Code]-----------------------------------------
chandle = ctypes.c_int16()
status = {}

# Open the scope
status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(chandle), None)
assert_pico_ok(status["openunit"])

#TEST sigGen_stndrd()
sigGen_stndrd(chandle, status, 0, 1000000, 0, 100, 10000, 100, 0.1, 0, 0, 0, 0, 0, 0, 1)
#time.sleep(60)

'''#TEST data_block()
f = open('test.txt', 'w')
for axis in data_block(chandle, status, 'A', [0,0], [6,0], [0,0], 'A', 1024, 2, 0, 1000, 2500, 2500, 8, 0, 1)[0]:
    f.write('--------------------------------------------------------------------\n')
    for element in axis:
        f.write(str(element)+'\n')
f.close()'''

'''#TEST data_rapid_block() #Measured deadtime between calls ~30 ms (in data)
buff = []
for i in range(10):
    buff.append(data_rapid_block(chandle, status, 'A', 0, 6, 0, False, [], 1024, 2, 0, 800, 800, 1000, 32, 6, 6, 0, 1))
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
    elif False: #True for file writing
        for list in run:
            f.write('--------------------------------------------------------------------=[List]=--------------------------------------------------------------------\n')
            for axis in list:
                f.write('--------------------------------------------------------------------=[Axis]=--------------------------------------------------------------------\n')
                for element in axis:
                    f.write(str(element)+'\n')
f.close()'''


'''#TEST data_streaming()
nextSample = 0 #global variable
autoStopOuter = False #global variable
wasCalledBack = False #global variable

f = open('test.txt', 'w')
for axis in data_streaming(chandle, status, 'A', [0,0], [6,0], [0,0], 500, 10, 2, 0, 1)[0]:
    f.write('--------------------------------------------------------------------\n')
    for element in axis:
        f.write(str(element)+'\n')
f.close()'''

# Stop the scope
status["stop"] = ps.ps2000aStop(chandle)
assert_pico_ok(status["stop"])

# Close unitDisconnect the scope
status["close"] = ps.ps2000aCloseUnit(chandle)
assert_pico_ok(status["close"])

# display status returns
print(status)
