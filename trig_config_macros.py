import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.ps2000a import PS2000A_TRIGGER_CONDITIONS
from picosdk.ps2000a import PS2000A_TRIGGER_PROPERTIES
from picosdk.ps2000a import PS2000A_PWQ_CONDITIONS

def trig_pwq_config(chandle, status, trig_pwq_conditions, trig_direction, trig_lower, trig_upper, trig_type):
    pwq_list = []
    #Set channel conditions
    for condition in trig_pwq_conditions:
        condition = list(map(ctypes.c_int32, condition)) #Convert arguments to ctypes.c_int32
        pwq_list.append(PS2000A_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5]))
    #Set pulse width qualifier conditions
    status["setPulseWidthQualifier"] = ps.ps2000aSetPulseWidthQualifier(chandle, id(pwq_list), len(pwq_list), trig_direction, trig_lower, trig_upper, trig_type)

def trig_logic_config(chandle, status, trig_conditions, trig_directions, trig_properties, trig_auto):
    cond_list = []
    #Set channel conditions
    for condition in trig_conditions:
        condition = list(map(ctypes.c_int32, condition)) #Convert arguments to ctypes.c_int32
        cond_list.append(PS2000A_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6], condition[7]))
    status["setTriggerChannelConditions"] = ps.ps2000aSetTriggerChannelConditions(chandle, id(cond_list), len(cond_list))
    #Set channel directions
    ps.ps2000aSetTriggerChannelDirections(chandle, trig_directions[0], trig_directions[1], trig_directions[2], trig_directions[3], trig_directions[4], trig_directions[5])
    #Set channel properties
    prop_list = []
    for property in trig_properties:
        prop_list.append(PS2000A_TRIGGER_PROPERTIES(property[0], property[1], property[2], property[3], property[4], property[5]))
    status["setTriggerChannelProperties"] = ps.ps2000aSetTriggerChannelProperties(chandle, id(prop_list), len(prop_list), False, trig_auto)
