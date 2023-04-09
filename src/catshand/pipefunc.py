import os
import sys
import json
import click
import subprocess as sp
from pathlib import Path
from time import sleep

def getpipename():
    if sys.platform == 'win32':
        print("pipe-test.py, running on windows")
        TONAME = '\\\\.\\pipe\\ToSrvPipe'
        FROMNAME = '\\\\.\\pipe\\FromSrvPipe'
        EOL = '\r\n\0'
    else:
        print("pipe-test.py, running on linux or mac")
        TONAME = '/tmp/audacity_script_pipe.to.' + str(os.getuid())
        FROMNAME = '/tmp/audacity_script_pipe.from.' + str(os.getuid())
        EOL = '\n'
    return TONAME, FROMNAME, EOL

def notify(title, text):
    os.system("""
    osascript -e 'display notification "{}" with title "{}"'
    """.format(text, title))

def LaunchAudacity_win(sleeptime = 0.5):
    if click.confirm('Do you want to launch Audacity?', default=True):
        sp.Popen(["C:\Program Files\Audacity\Audacity.exe"])
    else:
        sys.exit()
    sleep(sleeptime)
    return

def LaunchAudacity_mac(sleeptime = 3):
    if click.confirm('Do you want to launch Audacity?', default=True):
        process_name= "Audacity" # change this to the name of your process
        tmp = os.popen("ps -Af").read()
        if process_name not in tmp[:]:
            print (f"The {process_name} is not running. Let's restart.")
            """"Use nohup to make sure it runs like a daemon"""
            
            notify(f"{process_name} is Down", f"Restarting {process_name} now.")
            
            sp.call(
            ["/usr/bin/open", "-a", f"/Applications/{process_name}.app"]
            )
        else:
            print(f"The {process_name} is running.")
    else:
        sys.exit()
    sleep(sleeptime)
    return

def checkpipe(TONAME, FROMNAME, launchstate = False):
    print("Write to  \"" + TONAME +"\"")
    if os.path.exists(TONAME) and os.path.exists(FROMNAME):
        print(f"-- Both {TONAME} and {FROMNAME} exist. Good.")
        if sys.platform == 'win32':
            return
        tmp = os.popen("ps -Af").read()
        if "Audacity" in tmp[:]:
            return
    elif (not os.path.exists(TONAME)) and (not os.path.exists(FROMNAME)):
        print(f"-- {TONAME} and {FROMNAME} do not exist")
    elif not os.path.exists(TONAME):
        print(f"-- {TONAME} do not exist")
    else:
        print(f"--{FROMNAME} do not exist") 
    
    if sys.platform == 'win32':
        if not launchstate:
            LaunchAudacity()
            sleep(5)
            launchstate = True
        checkpipe(TONAME, FROMNAME, launchstate = launchstate)
    elif sys.platform == 'darwin':
        if not launchstate:
            LaunchAudacity_mac()
            sleep(5)
            launchstate = True
        checkpipe(TONAME, FROMNAME, launchstate = launchstate)
    return

#-------------------------------------------
TONAME, FROMNAME, EOL = getpipename()
checkpipe(TONAME, FROMNAME)
sleep(0.01)
TOFILE = open(TONAME, 'w')
print("-- File to write to has been opened")
FROMFILE = open(FROMNAME, 'rt')
print("-- File to read from has now been opened too\r\n")

def send_command(command):
    """Send a single command."""
    print("Send: >>> \n"+command)
    TOFILE.write(command + EOL)
    TOFILE.flush()

def get_response():
    """Return the command response."""
    result = ''
    line = ''
    while True:
        result += line
        line = FROMFILE.readline()
        if line == '\n' and len(result) > 0:
            break
    return result

def remove_last_line_from_string(s):
    s_tmp = s.split("\n")
    s_new = "\n".join(s_tmp[:-2])
    return s_new

def get_response_json():
    """Return the command response."""
    result = ''
    line = ''
    while True:
        result += line
        line = FROMFILE.readline()
        if line == '\n' and len(result) > 0:
            break
    result = remove_last_line_from_string(result)
    return result

def do_command(command):
    """Send one command, and return the response."""
    send_command(command)
    response = get_response()
    print("Rcvd: <<< \n" + response)
    return response

def quick_test():
    """Example list of commands."""
    do_command('Help: Command=Help')
    do_command('Help: Command="GetInfo"')
    #do_command('SetPreference: Name=GUI/Theme Value=classic Reload=1')

def main():
    quick_test()

if __name__ == '__main__':
    main()