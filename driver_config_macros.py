#Autodetect driver version for single connected picoscope
from picosdk.discover import find_unit
import fileinput
from os import listdir

def driver_replacement(driver = None):
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
        if file[-3:] == '.py':
            with fileinput.FileInput(file, inplace=True, backup='.bak') as file:
                for line in file:
                    print(line.replace(to_replace, driver), end='')

    f = open('driver.log', 'w')
    f.write(driver)
    f.close()
