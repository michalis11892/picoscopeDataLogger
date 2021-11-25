import os
import fileinput

ascii_art = '''
.--------------------------------=VZMMc:---------.
:                              ^8Z^` `r9$!       :
!                            `9E-       ,QG`     !
!                           ~#x           V#:    !
!                          v#!             =@*   !
:                         u#.               ,@v  :
@v                       3B`                 -#c !
v#x                     Mg`                   .Bz!
:'#u                   96                      `Q9
! `B3                `$Z                        `L
!  `R6              .#U                          !
!    UB.           !#v                           !
:     )#x        `V#:                            :
!      .G8*    `iBk`                             !
,--------:aEdZd0V---------------------------------

- By Michalis Panayiotou'''

name_art = '''______ _           _____                       ______      _          _
| ___ (_)         /  ___|                      |  _  \    | |        | |
| |_/ /_  ___ ___ \ `--.  ___ ___  _ __   ___  | | | |__ _| |_ __ _  | |     ___   __ _  __ _  ___ _ __
|  __/| |/ __/ _ \ `--. \/ __/ _ \| '_ \ / _ \ | | | / _` | __/ _` | | |    / _ \ / _` |/ _` |/ _ \ '__|
| |   | | (_| (_) /\__/ / (_| (_) | |_) |  __/ | |/ / (_| | || (_| | | |___| (_) | (_| | (_| |  __/ |
\_|   |_|\___\___/\____/ \___\___/| .__/ \___| |___/ \__,_|\__\__,_| \_____/\___/ \__, |\__, |\___|_|
                                  | |                                              __/ | __/ |
                                  |_|                                             |___/ |___/          '''

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

print('\n'+name_art)
print(ascii_art)
print('\n'+color.BOLD+'To select a default setting, simply press '+color.UNDERLINE+'enter'+color.END+color.BOLD+' for convenience'+color.END+'\n')
out_folder_name = 'runs_output'
ls = os.listdir(os.getcwd())
if out_folder_name not in ls:
    os.mkdir(os.path.join(os.getcwd(), out_folder_name))
pcmd = input('Terminal '+color.BOLD+'command'+color.END+' for the '+color.GREEN+'python'+color.END+' version to be used (default=python): ').replace(' ', '')
if pcmd == '':
    pcmd = 'python'
print(color.YELLOW+'Configuring...'+color.END)
with fileinput.FileInput('gui_startup.py', inplace=True, backup='.bak') as file:
    for line in file:
        if 'os.system' in line:
            print(line.replace(line.split('\'')[1].split(' ')[0], pcmd, 1), end='')
        else:
            print(line, end='')
while True:
    preinst = input(''+color.BOLD+'Install'+color.END+' all software '+color.DARKCYAN+'pre-requisites'+color.END+'? (Yes/ No): ')
    if preinst == 'Yes':
        print(color.YELLOW+'Installing...'+color.END)
        os.system(pcmd + ' -m pip install numpy picosdk matplotlib PyQt5')
        break
    elif preinst == 'No':
        break
    else:
        print(color.RED+'Invalid Response!'+color.END)
print(color.BOLD+color.GREEN+'Done!'+color.END)
