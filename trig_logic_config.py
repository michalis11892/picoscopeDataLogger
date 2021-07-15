import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.ps2000a import PS2000A_TRIGGER_CONDITIONS

def trig_logic_config(chandle, status, trig_conditions):
    cond_list = []
    for condition in trig_conditions:
        condition = list(map(ctypes.c_int32, condition)) #Convert arguments to ctypes.c_int32
        cond_list.append(PS2000A_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6], condition[7]))
    status["setTriggerChannelConditions"] = ps.ps2000aSetTriggerChannelConditions(chandle, id(cond_list), len(cond_list))
