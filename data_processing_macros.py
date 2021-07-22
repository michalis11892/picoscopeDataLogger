import ctypes
import numpy as np
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

channels = ['A', 'B', 'C', 'D']

def adc_to_mV(chandle, status, buffer, crange):
    # find maximum ADC count value
    maxADC = ctypes.c_int16()
    status["maximumValue"] = ps.ps2000aMaximumValue(chandle, ctypes.byref(maxADC))
    assert_pico_ok(status["maximumValue"])

    # convert ADC counts data to mV
    temp = []
    try:
        for segment in buffer:
            check = len(segment) #Will create an exception if segment isnt an array
            temp += adc2mV(segment, crange, maxADC)
    except:
        temp += adc2mV(buffer, crange, maxADC)

    return temp

def run_to_mV(chandle, status, run, channels_, crange, totalSamples, segments):
    data_mV_segmented = []
    for i in range(len(channels_)):
        run_channel = adc_to_mV(chandle, status, run[i], 7)
        channel_temp = []
        for j in range(segments):
            channel_temp.append(run_channel[j*totalSamples:(j+1)*totalSamples])
        data_mV_segmented.append(channel_temp)
    return data_mV_segmented

def run_to_file(time_, run, channels_, segments, runIndx, fileName):
    f = open(fileName, 'a')
    f.write('--------------------------------------------------------------------=[Run '+str(runIndx+1)+']=--------------------------------------------------------------------\n')
    for channel in range(len(run)):
        f.write('--------------------------------------------------------------------=[Channel '+str(channels[channels_[channel]])+']=--------------------------------------------------------------------\n')
        for segment in range(segments):
            f.write('--------------------------------------------------------------------=[Segment '+str(segment+1)+']=--------------------------------------------------------------------\n')
            for element in range(len(run[channel][segment])):
                f.write(str(time_[element])+', '+str(run[channel][segment][element])+'\n')
    f.close()
