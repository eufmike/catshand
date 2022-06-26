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
    do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
    return

class audacitytool:
    def __init__(self, prj_path, mat_path):
        self.prjpath = Path(prj_path)
        self.matpath = Path(mat_path)
        self.audtconfigpath = self.prjpath.joinpath('config', 'audt_config.json')
        self.configpath = self.prjpath.joinpath('config', 'config.json')
        
        # load config
        if self.configpath.is_file():
            with open(self.configpath, 'r') as f: 
                self.config = json.load(f)
            
            self.PROJECTNAME = self.config['project_name']
            self.HOSTS = self.config['hosts']
            self.GUESTS = self.config['guests']
        else: 
            configgen(self.prjpath)
        
        # load audtconfig
        if self.audtconfigpath.is_file():
            with open(self.audtconfigpath, 'r') as f:
                self.audtconfig = json.load(f)
            self.TRACK_HEIGHT = self.audtconfig.get('track_height')
            self.TRACK_OFFSET = self.audtconfig.get('track_offset')
            self.ENDCREDIT_OFFSET = self.audtconfig.get('endcredt_offset')
                    
        else: 
            self.TRACK_HEIGHT = 80
            self.TRACK_OFFSET = 29.6
            self.ENDCREDIT_OFFSET = 9.2
             
            self.audtconfig = {
                'track_height': self.TRACK_HEIGHT, 
                'track_offset': self.TRACK_OFFSET, 
                'endcredt_offset': self.ENDCREDIT_OFFSET, 
                'opmusic_path': self.OPMUSIC_PATH, 
                'endmusic_path': self.ENDMUSIC_PATH, 
                'endcredit_path': self.ENDCREDIT_PATH, 
            }
            
            with open(self.audtconfigpath, 'w') as f:
                json.dump(self.audtconfig, f, indent=2, sort_keys=False)
        
        self.OPMUSIC_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_op.wav'))
        self.ENDMUSIC_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_end.wav'))
        self.ENDCREDIT_PATH = str(self.matpath.joinpath('direct_import', 'direct_import_endcredit.wav'))
        
        return
        
    def importrecording(self):
        # get wav file name 
        # get trackinfo
        self.namesall = self.HOSTS + self.GUESTS
        
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
    
    def importmaterial(self):
        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]
        tracklengthlist = [trackinfo['end'] - trackinfo['start'] for trackinfo in trackinfo]
        self.TRACK_LENGTH_MAX = np.amax(tracklengthlist)

        if 'opmusic' not in tracknamelist:
            do_command(f'Import2: Filename="{self.OPMUSIC_PATH}"')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="opmusic" Height={int(self.TRACK_HEIGHT*0.6)}')

        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

        if 'endmusic' not in tracknamelist:
            do_command(f'Import2: Filename="{self.ENDMUSIC_PATH}"')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="endmusic" Height={int(self.TRACK_HEIGHT*0.6)}')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.TRACK_LENGTH_MAX}"')

        trackinfo = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

        if 'endcredit' not in tracknamelist:
            do_command(f'Import2: Filename="{self.ENDCREDIT_PATH}"')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="endcredit" Height={int(self.TRACK_HEIGHT*0.6)}')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.TRACK_LENGTH_MAX + self.ENDCREDIT_OFFSET}"')
        
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
            timestamp = timestamp//fs
            
            hr = timestamp // (60*60)
            hr_rm = timestamp % (60*60)
            min = hr_rm // (60)
            sec = hr_rm // (60)
            breakmusic_time_hhmmss.append(f'{str(hr).zfill(1)}:{str(min).zfill(2)}:{str(sec).zfill(2)}')

        print(breakmusic_time_hhmmss)
        
        self.dfaddmusic = pd.DataFrame({
                'timestamp': breakmusic_time_hhmmss,
                'music': default_music,
                })
        self.dfaddmusic.to_csv(self.musiccsvpath, index = False)

        return
    
    def _importmusic(self):
        for index, row in self.dfaddmusic.iterrows():
            hhmmss = row['timestamp']
            filename = row['music']
            self.MIDDLEPATH = self.matpath.joinpath('02_transition', filename)

            [hours, minutes, seconds] = [int(x) for x in hhmmss.split(':')]
            self.MIDDLE_TIMESTAMP = timedelta(hours=hours, minutes=minutes, seconds=seconds).seconds
            print(self.MIDDLE_TIMESTAMP)

            tracknamelist = [trackinfo['name'] for trackinfo in getinfo2json()]

            clipname = f'middle_{index + 1}'
            if clipname not in tracknamelist:
                do_command(f'Import2: Filename="{self.MIDDLEPATH}"')
                do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
                do_command(f'SetTrack: Name="{clipname}" Height={int(self.TRACK_HEIGHT*0.6)}')
                do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.MIDDLE_TIMESTAMP}"')
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