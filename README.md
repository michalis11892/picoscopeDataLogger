# Picoscope Data Logger
Simple python code that provides an interface (set of macros) for picoscopes to be used for extended data logging beyond the current functionality of proprietary software

## Pre-requisites:
In order to effectively use this code, you should install the following python packages through pip:
- numpy
- picosdk

And. optionally, for the examples in main.py
- matplotlib

Users should also make sure that they have the correct drivers and SDK installed for their respective PicoScope.
These can be found in the official PicoTech website, [*here*](https://www.picotech.com/downloads)


**IMPORTANT:** Please make sure that your python architecture and your installed PicoScope driver architecture are the same, if this is not the case then the software will fail to identify any connected units.

## Basics:
There are 3 available data capture modes,
- **Block Mode**, In this mode, the scope stores data in internal buffer memory and then transfers it to the PC. When the data has been collected it is possible to examine the data, with an optional downsampling factor
- **Rapid Block Mode**, This is a variant of block mode that allows you to capture more than one waveform at a time with a minimum of delay between captures. You can use downsampling in this mode if you wish.
- **Streaming Mode**, In this mode, data is passed directly to the PC without being stored in the scope's internal buffer memory. This enables long periods of data collection for chart recorder and data-logging applications. Streaming mode supports downsampling and triggering, while providing fast streaming at typical rates of 1 to 10 MS/s, as specified in the data sheet for the device

## Data Capture Mode Usage Instructions
Since each of these modes works slightly differently from each other, they require different setup and configuration before they can be properly used.\
*Full descriptions and documentation on all available macros can be found in the Appendix*

### Block Mode
1. Open the scope using start_scope()
2. Configure the channels that will be used for the data capture using channel_config()
3. Configure a timebase to be used for the capture using timebase_block_config()
4. Setup trigger(s) using, depending on the use-case, trig_simple_config() OR trig_logic_config()
5. Configure buffer(s) using buffer_block_config()
6. Capture data using data_block()
7. Deepcopy the data from the buffer
8. Repeat 6 & 7 as many times as needed
9. Convert the data to mV using run_to_mV() once on each data_block()'s buffer deepcopy
10. Export, Plot, etc.. the data
11. Close the scope using stop_scope()

### Rapid Block Mode
1. Open the scope using start_scope()
2. Configure the channels that will be used for the data capture using channel_config()
3. Configure a timebase to be used for the capture using timebase_block_config()
4. Setup trigger(s) using, depending on the use-case, trig_simple_config() OR trig_logic_config()
5. Configure buffer(s) & segment(s) using buffer_block_config()
6. Capture data using data_rapid_block()
7. Deepcopy the data from the buffer
8. Repeat 6 & 7 as many times as needed
9. Convert the data to mV using run_to_mV() once on each data_rapid_block()'s buffer deepcopy
10. Export, Plot, etc.. the data
11. Close the scope using stop_scope()

### Streaming Mode
1. Open the scope using start_scope()
2. Configure the channels that will be used for the data capture using channel_config()
3. Configure a timebase to be used for the capture using timebase_stream_config()
4. [*Optionally*] Setup trigger(s) using, depending on the use-case, trig_simple_config() OR trig_logic_config()
5. Configure buffer(s) & segment(s) using buffer_stream_config()
6. Capture data using data_streaming()
7. Deepcopy the data from the buffer
8. Repeat 6 & 7 as many times as needed
9. Convert the data to mV using run_to_mV() once on each data_streaming()'s buffer deepcopy
10. Export, Plot, etc.. the data
11. Close the scope using stop_scope()

## Apendix:
Some universal parameters that appear in almost every macro are,
>***chandle***, c_int16 type variable that acts as a handle for the opened scope. It is aquired from the start_scope() macro\
>***status***, a dictionary that stores all output codes of all run opreations to the scope. Useful for debugging

These wil not be referenced again for the sake of simplicity

### Capture Configuration Macros:
- **channel_config**(chandle, status, enable, channels_, couplings_, cranges_, offsets_)
>***enable***, takes a value of either 0 or 1 and determines whether the macro will enable or disable these channeles respectively \
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively \
>***couplings_***, list of integers with values 0 or 1, representing AC or DC respectively. One element per channel, corresponidng to the same order as *channels_* \
>***cranges_***, list of integers from 0 - 11, representing 10 mV, 20 mV, 50 mV, 100 mV, 200 mV, 500 mV, 1 V, 2 V, 5 V, 10 V, 20 V, 50 V, respectively. One element per channel, corresponidng to the same order as *channels_* \
>***offsets_***, list of integers corresponding to the offset (in mV). One element per channel, corresponidng to the same order as *channels_*

- **timebase_block_config**(chandle, status, timebase, totalSamples)
>***timebase***, arbitrary integer *n* representing the sample interval. This can be calculated as such:\
 If 2 >= n >= 0, then, sample interval = (2^n)/maximum sampling rate\
 If n > 2, then, sample interval = 8(n - 2)/maximum sampling rate \
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken

- **timebase_stream_config**(totalSamples, sampleInterval, sampleUnits)
>***totalSamples***, arbitrary integer representing the total number of samples to be taken \
>***sampleInterval***, arbitrary integer representing the time difference between samples, in *sampleUnits* \
>***sampleUnits***, integer representing the time units of *sampleInterval*, with values, from 0 - 5, representing fs, ps, ns, μs, ms, s respectively \

- **buffer_block_config**(chandle, status, channels_, totalSamples, segments, downsampling_ratio_mode)
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively \
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken \
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***downsampling_ratio_mode***, integer of a value [0, 1 ,2 ,4] which represents [None, Aggregate, Decimal, Average]

- **buffer_stream_config**(chandle, status, channels_, totalSamples, sizeOfOneBuffer, segments, downsampling_ratio_mode)
>
- **segment_capture_config**(chandle, status, segments, captures, totalSamples)
>

### Data Capture Macros:
- **data_block**(chandle, status, preTriggerSamples, postTriggerSamples, timebase, downsampling_ratio_mode, downsampling_ratio)
>
- **data_rapid_block**(chandle, status, preTriggerSamples, postTriggerSamples, timebase, segments, captures, downsampling_ratio_mode, downsampling_ratio)
>
- **data_streaming**(chandle, status, sampleInterval, autoStopOn, buffersComplete, buffersMax, sizeOfOneBuffer, sampleUnits, preTriggerSamples, postTriggerSamples, downsampling_ratio_mode, downsampling_ratio)
>

### Data Processing Macros:
- **adc_to_mV**(chandle, status, buffer, crange)
>
- **run_to_mV**(chandle, status, run, channels_, cranges_, totalSamples, segments)
>
- **run_to_file**(time_, run, channels_, segments, runIndx, fileName)
>
- **clear_file**(fileName)
>

### Power Operation Macros:
- **start_scope**(handles, serial = None)
>
- **stop_scope**(handles)
>
- **restart_scope**(handles, serial = None)
>

### Signal Generator Macros:
- **sigGen_stndrd**(chandle, status, offsetVoltage, pkToPk, waveType,  startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggerType, triggerSource, extInThreshold)
>

### Trigger Configuration Macros:
- **trig_pwq_config**(chandle, status, trig_pwq_conditions, trig_direction, trig_lower, trig_upper, trig_type)
>
- **trig_logic_config**(chandle, status, trig_conditions, trig_directions, trig_properties, trig_auto)
>
- **trig_simple_config**(chandle, status, enable, channel, trig_adc_counts, trig_direction, trig_delay, trig_auto)
>
