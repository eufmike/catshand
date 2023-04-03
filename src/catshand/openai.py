import os, sys, re
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import opencc

def merge_tran_csv(csvdir, docdir, tag = ''):
    csvdir = Path(csvdir)
    docdir = Path(docdir)

    df = []
    for file in tqdm(csvdir.glob('*.csv')):
        name = re.findall(r'(.+?)\.csv', str(file.name))[0]
        tmp = pd.read_csv(file)
        tmp.dropna(inplace=True)
        tmp.insert(0, 'name', name)
        df.append(tmp)
    
    df = pd.concat(df, axis=0, ignore_index=False)
    df.reset_index(drop = False, inplace = True)

    # Define a function to format the timedelta as "HH:MM:SS"
    def format_timedelta(t):
        return '{:02d}:{:02d}:{:02d}'.format(t.components.hours, t.components.minutes, t.components.seconds)

    timeconvertcols = ['start_time', 'end_time']
    x = 1
    for timeconvertcol in timeconvertcols:
        df[f'{timeconvertcol}_tmp'] = pd.to_timedelta(df[timeconvertcol], unit='ms')
        
        # Apply the formatting function to the timedelta column
        df.insert(x, f'{timeconvertcol}_format', df[f'{timeconvertcol}_tmp'].apply(format_timedelta))
        df.drop(columns=[f'{timeconvertcol}_tmp'], inplace=True)
        x += 1

    df['duration'] = df['end_time'] - df['start_time']
    df = df[df['duration'] > 500]

    # convert simplified chinese to traditional chinese
    converter = opencc.OpenCC('s2tw.json')
    df['transcript'] = df['transcript'].apply(converter.convert)

    # export a csv file with all the details
    df.sort_values(by=['start_time'], inplace=True, ignore_index=True)
    df.to_csv(docdir.joinpath(f'merge_detail{tag}.csv'), index=False, encoding='utf-16')

    # export a csv file for csv display
    df.drop(columns=['index', 'duration', 'start_time', 'end_time'], inplace=True)
    df.to_csv(docdir.joinpath(f'merge{tag}.csv'), index=False, encoding='utf-16')

    return