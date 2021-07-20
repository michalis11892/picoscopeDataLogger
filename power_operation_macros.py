import ctypes
from picosdk.ps2000a import ps2000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

def start_scope(handles, serial = None):
    '''
    handles = [chandle, status]
    '''
    # Start/ Open the scope
    handles[1]["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(handles[0]), serial)
    assert_pico_ok(handles[1]["openunit"])

def stop_scope(handles):
    '''
    handles = [chandle, status]
    '''
    # Stop the scope
    handles[1]["stop"] = ps.ps2000aStop(handles[0])
    assert_pico_ok(handles[1]["stop"])

    # Close unitDisconnect the scope
    handles[1]["close"] = ps.ps2000aCloseUnit(handles[0])
    assert_pico_ok(handles[1]["close"])

    # display status returns
    print(handles[1])

def restart_scope(handles, serial = None):
    '''
    handles = [chandle, status]
    '''
    # Stop the scope
    handles[1]["stop"] = ps.ps2000aStop(handles[0])
    assert_pico_ok(handles[1]["stop"])

    # Close unitDisconnect the scope
    handles[1]["close"] = ps.ps2000aCloseUnit(handles[0])
    assert_pico_ok(handles[1]["close"])

    # display status returns
    print(handles[1])

    handles[0] = ctypes.c_int16()
    handles[1] = {}

    # Open the scope
    handles[1]["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(handles[0]), serial)
    assert_pico_ok(handles[1]["openunit"])
