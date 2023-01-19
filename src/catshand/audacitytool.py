import os, sys, re, json
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from catshand.utility import configgen
from catshand.pipefunc import do_command, send_command, get_response, get_response_json

def getinfo2json():
    send_command('GetInfo: Format="JSON" Type="Tracks"')
    response = get_response_json()
    result = json.loads(response)
    return(result)

def importfiles(filepath):
    do_command(f'Import2: Filename={filepath}')
    do_command(f'Compressor: Threshold={str(-40)} NoiseFloor={str(-35)} Ratio={str(2)}')
    # do_command(f'Compressor: Threshold={str(-56)} NoiseFloor={str(-35)} Ratio={str(5.3)}')
    return

class audacitytool:
    def __init__(self, prj_path, mat_path):
        self.prjpath = Path(prj_path)
        self.matpath = Path(mat_path)
        self.audtconfigpath = self.prjpath.joinpath('config', 'audt_config.json')
        self.configpath = self.prjpath.joinpath('config', 'config.json')
        
        self.OPMUSIC_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_op.wav'))
        self.ENDMUSIC_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_end.wav'))
        self.ENDCREDIT_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_endcredit.wav'))
        
        # load config
        if self.configpath.is_file():
            with open(self.configpath, 'r') as f: 
                self.config = json.load(f)
            
            self.PROJECTNAME = self.config['project_name']
            self.HOSTS = self.config['hosts']
            self.GUESTS = self.config['guests']
        else: 
            configgen(self.prjpath)
            
        self.namesall = self.HOSTS + self.GUESTS
        
        # load audtconfig
        if self.audtconfigpath.is_file():
            with open(self.audtconfigpath, 'r') as f:
                self.audtconfig = json.load(f)
            self.TRACK_HEIGHT = self.audtconfig.get('track_height')
            self.TRACK_OFFSET = self.audtconfig.get('track_offset')
            self.HIGHLIGHT_OFFSET = self.audtconfig.get('highlight_offset')
            self.ENDCREDIT_OFFSET = self.audtconfig.get('endcredt_offset')
            self.ENDMUSIC_OFFSET = self.audtconfig.get('endmusic_offset')
                    
        else: 
            self.TRACK_HEIGHT = 80
            self.TRACK_OFFSET = 29.6
            self.HIGHLIGHT_OFFSET = 10
            self.ENDCREDIT_OFFSET = 9.2
            self.ENDMUSIC_OFFSET = -4
            
            self.audtconfig = {
                'track_height': self.TRACK_HEIGHT, 
                'track_offset': self.TRACK_OFFSET,
                'highlight_offset': self.HIGHLIGHT_OFFSET,
                'endcredt_offset': self.ENDCREDIT_OFFSET, 
                'endmusic_offset':self.ENDMUSIC_OFFSET,
                'opmusic_path': self.OPMUSIC_PATH, 
                'endmusic_path': self.ENDMUSIC_PATH, 
                'endcredit_path': self.ENDCREDIT_PATH, 
            }
            
            with open(self.audtconfigpath, 'w') as f:
                json.dump(self.audtconfig, f, indent=2, sort_keys=False)
        
        
        
        return
        
    def importrecording(self):
        print(self.config)
        prj_name = self.PROJECTNAME
        self.ipwavlist = {}
        
        trackinfos = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in trackinfos]
        
        for idx, name in enumerate(self.namesall):
            track_name = f'{prj_name}_{name}'
            if track_name not in tracknamelist:
                print(f'import track: {track_name}')
                importfiles(self.prjpath.joinpath('postedit_merged', f'{track_name}.wav'))
            do_command('SelectAll:')        
            do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
            do_command('ZoomSel')
            do_command(f'SetTrack: Height={self.TRACK_HEIGHT}')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET}"')
        
        return
    
    def importhighlight(self):
        hl_name = 'highlight'
        highlight_path = Path('highlight_export', f'{hl_name}.wav')
        
        trackinfos = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in trackinfos]
        
        if hl_name not in tracknamelist:
            print(f'import highlight: {highlight_path}')
            importfiles(self.prjpath.joinpath(highlight_path))
            
            do_command('SelectAll:')
            do_command(f'SelectTracks: Mode="Set" Track="{len(self.namesall)+3}" TrackCount="1"')
            do_command(f'SetTrack: Height={self.TRACK_HEIGHT}')
            do_command(f'SetClip: At="0" Start="{self.HIGHLIGHT_OFFSET}"')
            

        return
    
    def importmaterial(self):
        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]
        tracklengthlist = [trackinfo['end'] - trackinfo['start'] for trackinfo in trackinfo]
        self.TRACK_LENGTH_MAX = np.amax(tracklengthlist)

        if 'opmusic' not in tracknamelist:
            do_command(f'Import2: Filename="{self.OPMUSIC_PATH}"')
            do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="opmusic" Height={int(self.TRACK_HEIGHT*0.6)}')

        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

        if 'endmusic' not in tracknamelist:
            do_command(f'Import2: Filename="{self.ENDMUSIC_PATH}"')
            do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="endmusic" Height={int(self.TRACK_HEIGHT*0.6)}')
            do_command(f'SelectTime: Start="{0}" End="{2}"')
            do_command(f'AdjustableFade: preset="SCurveIn"')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.TRACK_LENGTH_MAX + self.ENDMUSIC_OFFSET}"')

        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

        if 'endcredit' not in tracknamelist:
            do_command(f'Import2: Filename="{self.ENDCREDIT_PATH}"')
            do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="endcredit" Height={int(self.TRACK_HEIGHT*0.6)}')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.TRACK_LENGTH_MAX + self.ENDCREDIT_OFFSET + self.ENDMUSIC_OFFSET}"')
        
        return
    
    # ===================================================================
    
    def _metadata2sectionlength(self, default_music = 'Middle_01.wav'):
        with open(self.metadatapath, 'r') as f:
            medatadict = json.load(f)
        
        self.posteditrawpath = self.prjpath.joinpath('postedit_raw')
        folderlist = sorted(self.posteditrawpath.iterdir())
        self.foldernamelist = [x.name for x in folderlist]        
        
        fs = medatadict['op_fs']
        
        section_length = []
        for idx in range(len(self.foldernamelist)):
            maxlength = float(medatadict['maxlength'][str(idx+1).zfill(2)])  
            section_length.append(int(maxlength * fs))
            
        breakmusic_time = [0]
        for idx in range(len(section_length)-1):
            breakmusic_time.append(breakmusic_time[-1] + section_length[idx])
        breakmusic_time = breakmusic_time[1:]
        
        breakmusic_time_hhmmss = []
        for timestamp in breakmusic_time:
            timestamp = timestamp / fs
            print(timestamp)
            hr = int(timestamp // (60*60))
            hr_rm = timestamp % (60*60)
            min = int(hr_rm // 60)
            sec = round(hr_rm % 60, 2)
            # breakmusic_time_hhmmss.append(f'{str(hr).zfill(1)}:{str(min).zfill(2)}:{str(sec).zfill(2)}')
            breakmusic_time_hhmmss.append(f'{hr}:{min}:{sec}')

        print(breakmusic_time_hhmmss)
        
        self.dfaddmusic = pd.DataFrame({
                'timestamp': breakmusic_time_hhmmss,
                'music': default_music,
                })
        self.dfaddmusic.to_csv(self.musiccsvpath, index = False)

        return
    
    def _importmusic(self):
        silence = 10
        music_offset = -3.5
        cumulative = 0
        for index, row in self.dfaddmusic.iterrows():
            hhmmss = row['timestamp']
            filename = row['music']
            
            [hours, minutes, seconds] = [x for x in hhmmss.split(':')]
            print(f'{hours}; {minutes}; {seconds}')
            self.MIDDLE_TIMESTAMP = int(hours)*60*60 + int(minutes)*60 + float(seconds)
            print(self.MIDDLE_TIMESTAMP)

            trackamount = len(getinfo2json())
            for idx in range(trackamount):
                trackinfo = getinfo2json()[idx]
                trackend = trackinfo['end']
                do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
                do_command(f'SelectTime: Start="{self.TRACK_OFFSET + self.MIDDLE_TIMESTAMP + cumulative}" End="{self.TRACK_OFFSET + trackend}"')
                do_command(f'SplitCut:')
                paste_time = self.TRACK_OFFSET + self.MIDDLE_TIMESTAMP + cumulative + silence + music_offset
                do_command(f'SelectTime: Start="{paste_time}" End="{paste_time}"')
                do_command(f'Paste:')
                
            cumulative += (silence + music_offset)
            
        cumulative = 0
        for index, row in self.dfaddmusic.iterrows():
            hhmmss = row['timestamp']
            filename = row['music']
            self.MIDDLEPATH = self.matpath.joinpath('02_transition', filename)

            [hours, minutes, seconds] = [x for x in hhmmss.split(':')]
            print(f'{hours}; {minutes}; {seconds}')
            self.MIDDLE_TIMESTAMP = int(hours)*60*60 + int(minutes)*60 + float(seconds)
            print(self.MIDDLE_TIMESTAMP)

            tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

            clipname = f'middle_{index + 1}'
            if clipname not in tracknamelist:
                do_command(f'Import2: Filename="{self.MIDDLEPATH}"')
                do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
                do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
                do_command(f'SetTrack: Name="{clipname}" Height={int(self.TRACK_HEIGHT*0.6)}')
                do_command(f'SelectTime: Start="{0}" End="{5}"')
                do_command(f'AdjustableFade: preset="SCurveIn"')
                do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.MIDDLE_TIMESTAMP + cumulative + music_offset}"')
            
            do_command('Enter:')
            cumulative += (silence + music_offset)

        return
    
    def addmusic(self, default_music):
        self.metadatapath = self.prjpath.joinpath('config', 'metadata.json')
        self.musiccsvpath = self.prjpath.joinpath('config', 'addmusic.csv')
        
        if self.musiccsvpath.is_file():
            self.dfaddmusic = pd.read_csv(self.musiccsvpath)
        else:
            self._metadata2sectionlength(default_music)
        
        self._importmusic()
        return
    
    def midedit(self):
        #trackinfos = getinfo2json()
        #tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]
        #tracklengthlist = [trackinfo['end'] - trackinfo['start'] for trackinfo in trackinfos]
        
        for idx in range(3):
            trackinfo = getinfo2json()[idx]
            trackend = trackinfo['end']
            do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
            do_command(f'SelectTime: Start="{self.TRACK_OFFSET + 50}" End="{self.TRACK_OFFSET + trackend}"')
            do_command(f'SplitCut:')
            do_command(f'SelectTime: Start="{self.TRACK_OFFSET + 50 + 10}" End="{self.TRACK_OFFSET + 50 + 10}"')
            do_command(f'Paste:')
        return
    
    def compressor(self):
        #tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

        for idx, name in enumerate(self.namesall):
            # track_name = f'{self.PROJECTNAME}_{name}'
            #do_command('SelectAll:')        
            do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
            #do_command('ZoomSel')
            do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
            #do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET}"')

        return