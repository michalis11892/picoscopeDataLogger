#Autodetect driver version for single connected picoscope
from picosdk.discover import find_unit
import fileinput
from os import listdir
import os

def driver_replacement(driver = None):
    dir = os.path.join('.', 'driver.log')
    if not os.path.exists(dir):
        f = open('driver.log', 'w')
        f.write('ps2000a')
        f.close()

    f = open('driver.log', 'r')
    to_replace = f.readline().replace('\n', '') #Current default present for this is ps2000a
    f.close()

    if driver == None:
        scope = find_unit() #Will contain infomration on all connected picoscopes
        driver = str(scope.info.driver).split(' ')[1]
        scope.close()
    if driver == to_replace:
        return 0

    ls = listdir()
    for file in ls:
        if file in ['setup.py', 'gui_startup.py', 'gui.py', 'driver_config_macros.py']:
            continue
        if file[-3:] == '.py':
            if driver != 'ps2000a':
                with fileinput.FileInput(file, inplace=True, backup='.bak') as file:
                    for line in file:
                        trigCond_toReplace = '_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6], condition[7])'
                        trigCond_new = '_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6])'
                        trigPWQ_toReplace = '_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5])'
                        trigPWQ_new = '_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4])'
                        print(line.replace(trigCond_toReplace, trigCond_new).replace(trigPWQ_toReplace, trigPWQ_new).replace(to_replace, driver).replace(to_replace.upper(), driver.upper()), end='')
            else:
                with fileinput.FileInput(file, inplace=True, backup='.bak') as file:
                    for line in file:
                        trigCond_new = '_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6], condition[7])'
                        trigCond_toReplace = '_TRIGGER_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5], condition[6])'
                        trigPWQ_new = '_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4], condition[5])'
                        trigPWQ_toReplace = '_PWQ_CONDITIONS(condition[0], condition[1], condition[2], condition[3], condition[4])'
                        print(line.replace(trigCond_toReplace, trigCond_new).replace(trigPWQ_toReplace, trigPWQ_new).replace(to_replace, driver).replace(to_replace.upper(), driver.upper()), end='')

    f = open('driver.log', 'w')
    f.write(driver)
    f.close()

def driver_autodetect():
    dir = os.path.join('.', 'driver.log')
    if not os.path.exists(dir):
        f = open('driver.log', 'w')
        f.write('ps2000a')
        f.close()

    f = open('driver.log', 'r')
    to_replace = f.readline().replace('\n', '') #Current default present for this is ps2000a
    f.close()

    scope = find_unit() #Will contain infomration on all connected picoscopes
    driver = str(scope.info.driver).split(' ')[1]
    scope.close()

    return driver
