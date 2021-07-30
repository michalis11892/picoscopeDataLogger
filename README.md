# Picoscope Data Logger
Simple python code that provides an interface (set of macros & GUI [WIP]) for picoscopes to be used for extended data logging beyond the current functionality of proprietary software

## Pre-requisites:
In order to effectively use this code, you should install the following python packages through pip:
- numpy
- picosdk

And, optionally, for the examples in main.py
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
4. [*Optional*] Setup trigger(s) using, depending on the use-case, trig_simple_config() OR trig_logic_config()
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
>***status***, a dictionary that stores all output codes of all run operations to the scope. *Useful for debugging*

These wil not be referenced again for the sake of simplicity
### Driver Configuration Macros:
***
**driver_replacement**(driver = None)
>***driver***, [*Optional*] driver version with compatible methods i.e.,
> - ps2000a
> - ps3000a
> - etc...
>
>Automatically replaces the correct detected driver version in the code to make it compatible with alternative drivers and picoscopes beyond the default ps2000a. If *driver* parameter is not specified, it will be auto-detected

### Capture Configuration Macros:
***
**channel_config**(chandle, status, enable, channels_, couplings_, cranges_, offsets_)
>***enable***, takes a value of either 0 or 1 and determines whether the macro will enable or disable these channeles respectively \
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***couplings_***, list of integers with values 0 or 1, representing AC or DC respectively,
>  - AC -> 0
>  - DC -> 1
>
>One element per channel, corresponding to the same order as *channels_* \
>***cranges_***, list of integers from 0 - 11, representing voltage ranges such that,
>  - 10 mV -> 0
>  - 20 mV -> 1
>  - 50 mV -> 2
>  - 100 mV -> 3
>  - 200 mV -> 4
>  - 500 mV -> 5
>  - 1 V -> 6
>  - 2 V -> 7
>  - 5 V -> 8
>  - 10 V -> 9
>  - 20 V -> 10
>  - 50 V -> 11
>
>One element per channel, corresponding to the same order as *channels_* \
>***offsets_***, list of arbitrary integers corresponding to the offset (in mV). One element per channel, corresponidng to the same order as *channels_*

**timebase_block_config**(chandle, status, timebase, totalSamples)
>***timebase***, arbitrary integer *n* representing the sample interval suhc that,
>  - If 2 >= n >= 0, then, sample interval = (2^n)/maximum sampling rate
>  - If n > 2, then, sample interval = 8(n - 2)/maximum sampling rate
>
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken

**timebase_stream_config**(totalSamples, sampleInterval, sampleUnits)
>***totalSamples***, arbitrary integer representing the total number of samples to be taken \
>***sampleInterval***, arbitrary integer representing the time difference between samples, in *sampleUnits* \
>***sampleUnits***, integer representing the time units of *sampleInterval*, with values, from 0 - 5, representing fs, ps, ns, μs, ms, s respectively

**buffer_block_config**(chandle, status, channels_, totalSamples, segments, downsampling_ratio_mode)
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken \
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***downsampling_ratio_mode***, integer representing the downsapling ratio mode such that,
>  - None -> 0
>  - Aggregate -> 1
>  - Decimate -> 2
>  - Average -> 4

**buffer_stream_config**(chandle, status, channels_, totalSamples, sizeOfOneBuffer, segments, downsampling_ratio_mode)
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken \
>***sizeOfOneBuffer***, arbitrary integer representing the number of samples per buffer \
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***downsampling_ratio_mode***, integer representing the downsapling ratio mode such that,
>  - None -> 0
>  - Aggregate -> 1
>  - Decimate -> 2
>  - Average -> 4
>

**segment_capture_config**(chandle, status, segments, captures, totalSamples)
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***captures***, arbitrary integer, equal or smaller to *segments* representing the number of captures to take \
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken

### Data Capture Macros:
***
**data_block**(chandle, status, preTriggerSamples, postTriggerSamples, timebase, downsampling_ratio_mode, downsampling_ratio)
>***preTriggerSamples***, arbitrary integer representing the number of samples to take before the trigger event time \
>***postTriggerSamples***, arbitrary integer representing the number of samples to take after the trigger event time \
>***timebase***, arbitrary integer *n* representing the sample interval suhc that,
>  - If 2 >= n >= 0, then, sample interval = (2^n)/maximum sampling rate
>  - If n > 2, then, sample interval = 8(n - 2)/maximum sampling rate
>
>***downsampling_ratio_mode***, integer representing the downsapling ratio mode such that,
>  - None -> 0
>  - Aggregate -> 1
>  - Decimate -> 2
>  - Average -> 4
>
>***downsampling_ratio***, arbitrary integer *n* fed to the selected *downsampling_ratio_mode* from above

**data_rapid_block**(chandle, status, preTriggerSamples, postTriggerSamples, timebase, segments, captures, downsampling_ratio_mode, downsampling_ratio)
>***preTriggerSamples***, arbitrary integer representing the number of samples to take before the trigger event time \
>***postTriggerSamples***, arbitrary integer representing the number of samples to take after the trigger event time \
>***timebase***, arbitrary integer *n* representing the sample interval suhc that,
>  - If 2 >= n >= 0, then, sample interval = (2^n)/maximum sampling rate
>  - If n > 2, then, sample interval = 8(n - 2)/maximum sampling rate
>
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***captures***, arbitrary integer, equal or smaller to *segments* representing the number of captures to take \
>***downsampling_ratio_mode***, integer representing the downsapling ratio mode such that,
>  - None -> 0
>  - Aggregate -> 1
>  - Decimate -> 2
>  - Average -> 4
>
>***downsampling_ratio***, arbitrary integer *n* fed to the selected *downsampling_ratio_mode* from above

**data_streaming**(chandle, status, sampleInterval, autoStopOn, buffersComplete, buffersMax, sizeOfOneBuffer, sampleUnits, preTriggerSamples, postTriggerSamples, downsampling_ratio_mode, downsampling_ratio)
>***sampleInterval***, arbitrary integer representing the time interval between samples in *sampleUnits* units \
>***autoStopOn***, integer 0 OR 1, representing True OR False respectively \
>***buffersComplete***, list of lists, returned by *buffer_stream_config()*. It contains the complete captuyre buffer after every run of *data_streaming()* \
>***buffersMax***, list of lists, returned by *buffer_stream_config()*. Acts as a temporary storage space used by *data_streaming()* to transfer data to *buffersComplete* \
>***buffersMin***, list of lists, returned by *buffer_stream_config()*. Acts as a temporary storage space used by *data_streaming()* to transfer data to *buffersComplete* \
>***sizeOfOneBuffer***, arbitrary integer representing the number of samples per buffer \
>***sampleUnits***, integer representing the time units of *sampleInterval*, with values, from 0 - 5, representing fs, ps, ns, μs, ms, s respectively \
>***preTriggerSamples***, arbitrary integer representing the number of samples to take before the trigger event time \
>***postTriggerSamples***, arbitrary integer representing the number of samples to take after the trigger event time \
>***downsampling_ratio_mode***, integer representing the downsapling ratio mode such that,
>  - None -> 0
>  - Aggregate -> 1
>  - Decimate -> 2
>  - Average -> 4
>
>***downsampling_ratio***, arbitrary integer *n* fed to the selected *downsampling_ratio_mode* from above

### Data Processing Macros:
***
**adc_to_mV**(chandle, status, buffer, crange)
>***buffer***, list representing an element of a buffer from a *Data Capture Macro* \
>***crange***, integer from 0 - 11, representing 10 mV, 20 mV, 50 mV, 100 mV, 200 mV, 500 mV, 1 V, 2 V, 5 V, 10 V, 20 V, 50 V, respectively

**run_to_mV**(chandle, status, run, channels_, cranges_, totalSamples, segments)
>***run***, list of lists, repsenting a buffer from a *Data Capture Macro* \
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***cranges_***, list of integers from 0 - 11, representing voltage ranges such that,
>  - 10 mV -> 0
>  - 20 mV -> 1
>  - 50 mV -> 2
>  - 100 mV -> 3
>  - 200 mV -> 4
>  - 500 mV -> 5
>  - 1 V -> 6
>  - 2 V -> 7
>  - 5 V -> 8
>  - 10 V -> 9
>  - 20 V -> 10
>  - 50 V -> 11
>
>One element per channel, corresponding to the same order as *channels_* \
>***totalSamples***, arbitrary integer representing the toal number of samples to be taken \
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment)

**run_to_file**(time_, run, channels_, segments, runIndx, fileName)
>***time_***, list of floats that represent the timestamp of each sample taken sequentially. It is returned by *timebase_block_config()* & *timebase_stream_config()* \
>***run***, list of lists, repsenting a buffer from a *Data Capture Macro* \
>***channels_***, list of integers from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***segments***, arbitrary integer representing the number of segments that the picoscopes memory will be split into aka the number of waveform captures that can be stored at once before data transfer to a PC is required (one waveform per segment) \
>***runIndx***, arbitrary integer representing the current count of the run that is being processed \
>***fileName***, name of the file to save the run in (including the extension)

**clear_file**(fileName)
>***fileName***, name of the file to save the run in (including the extension)

### Power Operation Macros:
***
**start_scope**(handles, serial = None)
>***handles***, c_int16 type variable that acts as a handle for the opened scope. It is aquired from the start_scope() macro \
>***serial***, optional argument representing the serial number of a specific scope that the macro should open

**stop_scope**(handles)
>***handles***, c_int16 type variable that acts as a handle for the opened scope. It is aquired from the start_scope() macro

**restart_scope**(handles, serial = None)
>***handles***, c_int16 type variable that acts as a handle for the opened scope. It is aquired from the start_scope() macro \
>***serial***, optional argument representing the serial number of a specific scope that the macro should open

### Signal Generator Macros:
***
**sigGen_stndrd**(chandle, status, offsetVoltage, pkToPk, waveType, startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggerType, triggerSource, extInThreshold)
>***offsetVoltage***, arbitrary integer representing the voltage offset of the signal generated (in μV) \
>***pkToPk***, arbitrary integer representing the peak-to-peak voltage of the signal generated (in μV) \
>***waveType***, integer between 0 - 8 representing the waveform of the signal such that,
>  - Sine -> 0
>  - Square -> 1
>  - Triangle -> 2
>  - DC Voltage -> 3
>  - Rising Sawtooth (Ramp Up) -> 4
>  - Falling Sawtooth (Ramp Down) -> 5
>  - Sin(x)/x -> 6
>  - Gaussian -> 7
>  - Half Sine -> 8
>
>***startFrequency***, integer representing the starting frequency of the generator's signal cycle (in Hz) \
>***stopFrequency***, integer representing the end frequency of the generator's signal cycle (in Hz) \
>***increment***, integer representing the frequency increment step per *dwellTime* (in Hz) \
>***dwellTime***, float representing the time between frequency increment steps (in seconds) \
>***sweepType***, integer representing the signal generators frequency change behavior within the cycle, from *startFrequency* to *stopFrequency*,
>  - Up -> 0
>  - Down -> 1
>  - Up-Down -> 2
>  - Down-Up -> 3
>
>***operation***, integer representing the signal generators operation function,
>  - Normal signal generator operation specified by waveType -> 0
>  - White noise and ignores all settings except pkToPk and offsetVoltage -> 1
>  - Pseudorandom binary sequence at the specified frequency or frequency range -> 2
>
>***shots***, integer such that,
>  - Sweep the frequency as specified by sweeps -> 0 \
>-*OR*-
>  - The number of cycles of the waveform to be produced after a trigger event [sweeps must be zero] (not PicoScope 2205 MSO)
>
>***sweeps***, integer such that,
>  - Produce number of cycles specified by shots -> 0 \
>-*OR*-
>  - The number of times to sweep the frequency after a trigger event, according to sweepType [shots must be zero] (not PicoScope 2205 MSO)
>
> *+NOTE: Both __shots__ & __sweeps__ can be zero at the same time* \
>***triggerType***, integer that specifies trigger type such that,
>  - Rising -> 0
>  - Falling -> 1
>  - Gate High -> 2
>  - Gate Low -> 3
>
>***triggerSource***, integer that specifies trigger source such that,
>  - None -> 0
>  - Scope Trigger -> 1
>  - Ext Input -> 2
>  - Software Trigger [*ps2000aSigGenSoftwareControl()*] -> 3
>  - Reserved -> 4
>
>***extInThreshold***, arbitrary integer that represents trigger level, in ADC counts, for external trigger

### Trigger Configuration Macros:
***
**trig_pwq_config**(chandle, status, trig_pwq_conditions, trig_direction, trig_lower, trig_upper, trig_type)
>***trig_pwq_conditions***, list of lists, where each list contains the conditions for a PS2000A_PWQ_CONDITIONS structure, which are effectively ANDed together to return one logical result per structure, and then all structure results are ORed together to return the final state of the qualifier. Each structure takes 7 conditions which have a specific position in a sublist,
>  - Channel A -> Position 0
>  - Channel B -> Position 1
>  - Channel C -> Position 2
>  - Channel D -> Position 3
>  - External -> Position 4
>  - Aux -> Position 5
>  - Digital -> Position 6 \
>-*AKA*-
>
>*[channelA; channelB; channelC; channelD; external; aux; pulseWidthQualifier; digital]*
>
> and each can have one of the following values,
>  - Don't Care -> 0
>  - True -> 1
>  - False -> 2
>
>***trig_direction***, integer representing the direction of the trigger such that,
>  - Above -> 0
>  - Below -> 1
>  - Rising -> 2
>  - Falling -> 3
>  - Rising Or Falling -> 4
>  - Above Lower -> 5
>  - Below Lower -> 6
>  - Rising Lower -> 7
>  - Falling Lower -> 8
>  - Positive Runt -> 9
>  - Negative Runt -> 10
>
>***trig_lower***, integer representing the lower limit of the pulse-width counter, measured in sample periods \
>***trig_upper***, integer representing the upper limit of the pulse-width counter, measured in sample periods \
>***trig_type***, integer representing the trigger type such that,
>  - Do not use the pulse width qualifier -> 0
>  - Pulse width less than lower -> 1
>  - Pulse width greater than lower -> 2
>  - Pulse width between lower and upper -> 3
>  - Pulse width not between lower and upper -> 4

**trig_logic_config**(chandle, status, trig_conditions, trig_directions, trig_properties, trig_auto)
>***trig_conditions***, list of lists, where each list contains the conditions for a PS2000A_TRIGGER_CONDITIONS structure, which are effectively ANDed together to return one logical result per structure, and then all structure results are ORed together to return the final state of the complex trigger. Each structure takes 7 conditions which have a specific position in a sublist,
>  - Channel A -> Position 0
>  - Channel B -> Position 1
>  - Channel C -> Position 2
>  - Channel D -> Position 3
>  - External -> Position 4
>  - Aux -> Position 5
>  - Digital -> Position 6 \
>-*AKA*-
>
>*[channelA; channelB; channelC; channelD; external; aux; pulseWidthQualifier; digital]*
>
> and each can have one of the following values,
>  - Don't Care -> 0
>  - True -> 1
>  - False -> 2
>
>***trig_directions***, list of integers representing the direction of the trigger per channel depending on position such that,
>  - Channel A -> Position 0
>  - Channel B -> Position 1
>  - Channel C -> Position 2
>  - Channel D -> Position 3
>  - External -> Position 4
>  - Aux -> Position 5
>  - Digital -> Position 6 \
>-*AKA*-
>
>*[channelA; channelB; channelC; channelD; external; aux; pulseWidthQualifier; digital]*
>
> with each position taking a value such as,
>  - Above (*level*)/ Inside (*window*) -> 0
>  - Below (*level*)/ Outside (*window*) -> 1
>  - Rising (*level*)/ Enter (*window*)/ None -> 2
>  - Falling (*level*)/ Exit (*window*) -> 3
>  - Rising Or Falling (*level*) -> 4
>  - Above Lower (*level*) -> 5
>  - Below Lower (*level*) -> 6
>  - Rising Lower (*level*) -> 7
>  - Falling Lower (*level*) -> 8
>  - Positive Runt (*level*) -> 9
>  - Negative Runt (*level*) -> 10
>
>***trig_properties***, list of lists, where each list contains the conditions for a PS2000A_TRIGGER_CHANNEL_PROPERTIES structure, where each structure represents the properties of one triggered channel. Each structure takes 6 conditions which have a specific position in a sublist,
>  - Upper Threshold -> Position 0
>  - Upper Threshold Hysteresis -> Position 1
>  - Lower Threshold -> Position 2
>  - Lower Threshold Hysteresis -> Position 3
>  - Channel -> Position 4
>  - Threshold Mode -> Position 5
>-*AKA*-
>
>*[thresholdUpper, thresholdUpperHysteresis, thresholdLower, thresholdLowerHysteresis, channel, thresholdMode]*
>
> where thresholds take arbitrary integer values representing adc counts, channel takes values such that,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
> and threshold mode takes values such that,
>  - Level -> 0
>  - Window -> 1

**trig_simple_config**(chandle, status, enable, channel, trig_adc_counts, trig_direction, trig_delay, trig_auto)
>***enable***, takes a value of either 0 or 1 and determines whether the macro will enable or disable these channeles respectively \
>***channel***, integer from 0 - 3, representing channels A - D, respectively,
>  - A -> 0
>  - B -> 1
>  - C -> 2
>  - D -> 3
>
>***trig_adc_counts***, arbitrary integer between +32512 and -32512, where each is scaled to the crange maximum and minimum respectively, representing the position of the trigger within the measurable range \
>***trig_direction***, integer representing the direction of the trigger such that,
>  - Above -> 0
>  - Below -> 1
>  - Rising -> 2
>  - Falling -> 3
>  - Rising Or Falling -> 4
>  - Above Lower -> 5
>  - Below Lower -> 6
>  - Rising Lower -> 7
>  - Falling Lower -> 8
>  - Positive Runt -> 9
>  - Negative Runt -> 10
>
>***trig_delay***, arbitrary integer representing a specified delay between the time the trigger event happens and the time the trigger starts sampling (in units of sample periods) \
>***trig_auto***, arbitrary integer representing the maximum amount of time the trigger will wait; and if it doesn't fire until then it'll automatically fire (in ms). When this is set to 0, auto-trigger is disabled
