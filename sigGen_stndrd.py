import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import assert_pico_ok

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
