# Picoscope Data Logger
Simple python code that provides an interface (set of macros) for picoscopes to be used for extended data logging beyond the current functionality of proprietary software

## Pre-requisites:
In order to effectively use this code, you should install the following python packages through pip:
- numpy
- picosdk

And. optionally, for the examples in main.py
- matplotlib

Users should also make sure that they have the correct drivers and SDK installed for their respective PicoScope.
These can be found in the official PicoTech website, [here](https://www.picotech.com/downloads)


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
### Capture Configuration Macros
### Data Capture Macros
### Data Processing Macros
### Power Operation Macros
### Signal Generator Macros
### Trigger Configuration Macros
