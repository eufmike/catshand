import sys, re
import json
import click
from pathlib import Path
import logging
from datetime import datetime

def loggergen(logfld):
    logtime = datetime.now().strftime('%m%d%Y_%H%M')
    logformat = "%(levelname)s:%(name)s:%(asctime)s:%(message)s"
    file_handler = logging.FileHandler(filename=logfld.joinpath(f'log_{logtime}.log'))
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    logging.basicConfig(
        format = logformat,
        handlers = handlers,
        encoding ='utf-8', 
        level = logging.INFO)
    logger = logging.getLogger()
    return logger

def timestamp2arrayidx(timestamp, fs):
    timestamp_list = timestamp.split(':')
    hr = int(timestamp_list[0])
    min = int(timestamp_list[1])
    sec = int(timestamp_list[2])
    # print(f'hr: {hr}, min:{min}, sec:{sec}')
    sec_total = hr*60*60 + min*60 + sec
    return sec_total * fs

def wavcut(arrayidx_list_ip, wav_data):
    # print(wav_data.shape)
    arrayidx_list = [0]
    arrayidx_list.extend(arrayidx_list_ip)
    
    arrayidx_list = sorted(arrayidx_list)
    if arrayidx_list[-1] > wav_data.shape[1]:
        raise Exception("The largest time stamp cannot be larger than the maximum length of input audio file.") 
    
    # print(arrayidx_list)
    arrayidx_list.append(wav_data.shape[1])
    # print(arrayidx_list)
    
    wav_data_list = []
    
    for idx in range(len(arrayidx_list) - 1):
        start_idx = arrayidx_list[idx]
        end_idx = arrayidx_list[idx + 1]
        wav_data_list.append(wav_data[:, start_idx:end_idx])
    return wav_data_list


def asknames(amount, type):
    names = []
    for i in range(amount):
        name = click.prompt(f'{type} number {i+1}', type = str)
        names.append(name)
    return names

def configgen(prjpath):
    prjpath = Path(prjpath)
    result = re.search(r'^.*EP([0-9]*).*$', prjpath.name)
    print(result.group)
    json_pars = {}
    if result: 
        EPnum = int(result.group(1))
        if click.confirm(f'Is {EPnum} the episode number?', default=True):
            json_pars['project_name'] = f'EP{str(EPnum).zfill(3)}'
        else:
            EPnum = click.prompt('The episode number for this project', type = int)
            json_pars['project_name'] = f'EP{str(int(EPnum)).zfill(3)}'
    else:
        EPnum = click.prompt('The episode number for this project', type = int)
        json_pars['project_name'] = f'EP{str(int(EPnum)).zfill(3)}'
    
    count_host = click.prompt('The amount of host(s)', type = int)
    json_pars['hosts'] = asknames(count_host, 'Host')
    count_guest = click.prompt('The amount of guest(s)', type = int)
    json_pars['guests'] = asknames(count_guest, 'Guest')
    
    opconfigdir = prjpath.joinpath('config')
    opconfigdir.mkdir(exist_ok = True)
    
    with open(opconfigdir.joinpath('config.json'), 'w') as f:
        json.dump(json_pars, f, indent=2, sort_keys=False)
    
    return   
