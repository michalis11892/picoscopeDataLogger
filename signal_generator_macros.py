import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok

def sigGen_stndrd(chandle, status, offsetVoltage, pkToPk, waveType,  startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggerType, triggerSource, extInThreshold):
    waveType = ctypes.c_int16(waveType)
    sweepType = ctypes.c_int32(sweepType)
    triggertype = ctypes.c_int32(triggerType)
    triggerSource = ctypes.c_int32(triggerSource)

    status["SetSigGenBuiltIn"] = ps.ps2000aSetSigGenBuiltIn(chandle, offsetVoltage, pkToPk, waveType, startFrequency, stopFrequency, increment, dwellTime, sweepType, operation, shots, sweeps, triggertype, triggerSource, extInThreshold)
    assert_pico_ok(status["SetSigGenBuiltIn"])
