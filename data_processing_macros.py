import os
from os import listdir
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

def run_to_mV(chandle, status, run, channels_, cranges_, totalSamples, segments):
    data_mV_segmented = []
    for i in range(len(channels_)):
        run_channel = adc_to_mV(chandle, status, run[i], cranges_[i])
        channel_temp = []
        for j in range(segments):
            channel_temp.append(run_channel[j*totalSamples:(j+1)*totalSamples])
        data_mV_segmented.append(channel_temp)
    return data_mV_segmented

def run_to_file(time_, timeUnits, run, channels_, segments, runIndx, fileName):
    out_folder_name = 'runs_output'
    f = open(os.path.join(os.getcwd(), out_folder_name, fileName.split('.')[0]+'_Run-'+str(runIndx)+'.'+fileName.split('.')[1]), 'w')
    titleRow = 'Time ('+timeUnits+')'
    for i in channels_:
        #titleRow += ' '+channels[i]+'('+runUnits[i].replace(' ', '')+')'
        titleRow += ' '+channels[i]+'(mV)'
    f.write(titleRow+'\n')
    for segment in range(segments):
        f.write('\n'+str(segments)+'\n')
        for element in range(len(run[-1][segment])):
            outLine = ''
            for channel in range(len(run)):
                outLine += ' '+str(run[channel][segment][element])
            f.write(str(time_[element])+outLine+'\n')
    f.close()

def clear_file(fileName):
    ls = listdir()
    for file in ls:
        if file.split('_') == fileName.split('.')[0] and file.split('.')[1] == filename.split('.')[1]:
            '''f = open(file, 'w')
            f.close()'''
            os.remove(file)
