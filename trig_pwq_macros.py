import ctypes
from ctypes import *

'''Pulse Width Qualifiers change structures between driver versions and their respective condition structures are not always available trhough the sdk,
   [Use at your own discression][Untested]'''
from picosdk.ps2000a import ps2000a as ps2
from picosdk.functions import assert_pico_ok
from picosdk.ps2000a import PS2000A_PWQ_CONDITIONS

'''ps2000a variant'''
def trig_pwq_config(chandle, status, trig_pwq_conditions, trig_direction, trig_lower, trig_upper, trig_type):
    #Set channel conditions
    pwq_list = []
    for condition in trig_pwq_conditions:
        condition = list(map(ctypes.c_int32, condition)) #Convert arguments to ctypes.c_int32
        pwq_list.append(PS2000A_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5]))
    pwq_list_c = (PS2000A_PWQ_CONDITIONS * len(pwq_list))(*pwq_list)

    #Set pulse width qualifier conditions
    status["setPulseWidthQualifier"] = ps2.ps2000aSetPulseWidthQualifier(chandle, ctypes.byref(pwq_list_c), len(pwq_list), trig_direction, trig_lower, trig_upper, trig_type)
    assert_pico_ok(status["setPulseWidthQualifier"])


'''ps3000a variant, also compatible with other drivers such as ps5000a'''
from picosdk.ps3000a import ps3000a as ps3
class P3000A_PWQ_CONDITIONS(Structure): #Class is unavailabe in the sdk for ps3000a
    _pack_ = 1
    _fields_ = [("channelA", c_int32),
                ("channelB", c_int32),
                ("channelC", c_int32),
                ("channelD", c_int32),
                ("external", c_int32),
                ("aux", c_int32)]

def trig_pwq_config_ps3000a(chandle, status, trig_pwq_conditions, trig_direction, trig_lower, trig_upper, trig_type):
    #Set channel conditions
    pwq_list = []
    for condition in trig_pwq_conditions:
        condition = list(map(ctypes.c_int32, condition)) #Convert arguments to ctypes.c_int32
        pwq_list.append(PS3000A_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4]))
    pwq_list_c = (PS3000A_PWQ_CONDITIONS * len(pwq_list))(*pwq_list)

    #Set pulse width qualifier conditions
    status["setPulseWidthQualifier"] = ps3.ps3000aSetPulseWidthQualifier(chandle, ctypes.byref(pwq_list_c), len(pwq_list), trig_direction, trig_lower, trig_upper, trig_type)
    assert_pico_ok(status["setPulseWidthQualifier"])
