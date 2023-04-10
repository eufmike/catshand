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

def importfiles(filepath, compressor = True):
    do_command(f'Import2: Filename={filepath}')
    if compressor:
        do_command(f'Compressor: Threshold={str(-40)} NoiseFloor={str(-35)} Ratio={str(2)}')
        # do_command(f'Compressor: Threshold={str(-56)} NoiseFloor={str(-35)} Ratio={str(5.3)}')
    return

class audacitytool:
    def __init__(self, prj_path, ip_dir = None, hl_dir = None, premerge = None):
        self.prjpath = Path(prj_path)
        # self.matpath = Path(mat_path)
        self.audtconfigpath = self.prjpath.joinpath('config', 'audt_config.json')
        self.configpath = self.prjpath.joinpath('config', 'config.json')
        
        # load config
        if not self.configpath.is_file():
            raise Exception("config file not found. Please run 'prjgen' command first to create the config file.")
        else:
            with open(self.configpath, 'r') as f:
                config_dict = json.load(f)
        self.config = config_dict
        self.PROJECTNAME = config_dict.get('project_name')
        self.HOSTS = config_dict.get('hosts')
        self.GUESTS = config_dict.get('guests')
        self.namesall = self.HOSTS + self.GUESTS

        # load audtconfig if the file exists
        if self.audtconfigpath.is_file():
            with open(self.audtconfigpath, 'r') as f:
                self.audtconfig = json.load(f)

        self.TRACK_HEIGHT = self.audtconfig.get('track_height')
        self.TRACK_OFFSET = self.audtconfig.get('track_offset')
        self.HIGHLIGHT_OFFSET = self.audtconfig.get('highlight_offset')
        self.ENDCREDIT_OFFSET = self.audtconfig.get('endcredt_offset')
        self.ENDMUSIC_OFFSET = self.audtconfig.get('endmusic_offset')
        
        material_dict = self.audtconfig.get('material')
        material_root = Path(material_dict.get('root'))
        self.OPMUSIC_PATH = material_root.joinpath(material_dict.get('opmusic_path'))
        self.ENDMUSIC_PATH = material_root.joinpath(material_dict.get('endmusic_path'))
        self.ENDCREDIT_PATH = material_root.joinpath(material_dict.get('endcredit_path'))
        self.TRANSITIONFLD = material_root.joinpath(material_dict.get('transition_path'))

        # set path 
        if not ip_dir is None: 
            self.IPFOLDER = self.prjpath.joinpath(ip_dir)
        if premerge is None:
            premerge_fldname = '_'.join(self.IPFOLDER.name.split('_')[:-1])
            self.PREMERGEFLD = self.prjpath.joinpath(premerge_fldname)

        if not hl_dir is None: 
            self.HIGHLIGHTFLD = self.prjpath.joinpath(hl_dir)
            self.HIGHLIGHTPATH = sorted(self.HIGHLIGHTFLD.glob(f'*.wav'))[0]

        return
        
    def importrecording(self, importall = False, ipformat = '.wav', 
                        add_offset = True, compressor = True):
        print(self.config)
        prj_name = self.PROJECTNAME
        self.ipwavlist = {}
        
        trackinfos = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in trackinfos]
        
        if importall:
            track_names = sorted([name for name in self.IPFOLDER.glob(f'*{ipformat}')])
        else:
            track_names = [f'{name}{ipformat}' for name in self.namesall]

        for idx, track_name in enumerate(track_names):
            if track_name not in tracknamelist:
                print(f'import track: {track_name}')
                importfiles(self.IPFOLDER.joinpath(f'{track_name}'), compressor = compressor)
            do_command('SelectAll:')        
            do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
            do_command('ZoomSel')
            do_command(f'SetTrack: Height={self.TRACK_HEIGHT}')
            if add_offset:
                do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET}"')
        
        return
    
    def importhighlight(self):
        hl_name = 'highlight'
        highlight_path = str(self.HIGHLIGHTPATH)
        print(highlight_path)
        trackinfos = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in trackinfos]
        
        if hl_name not in tracknamelist:
            print(f'import highlight: {highlight_path}')
            importfiles(highlight_path)
            
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

        print(self.ENDCREDIT_PATH)
        if 'endcredit' not in tracknamelist:
            do_command(f'Import2: Filename="{self.ENDCREDIT_PATH}"')
            do_command(f'Compressor: Threshold={str(-12)} NoiseFloor={str(-35)} Ratio={str(2)}')
            do_command(f'SelectTracks: Mode="Set" Track="{len(tracknamelist)}" TrackCount="1"')
            do_command(f'SetTrack: Name="endcredit" Height={int(self.TRACK_HEIGHT*0.6)}')
            do_command(f'SetClip: At="0" Start="{self.TRACK_OFFSET + self.TRACK_LENGTH_MAX + self.ENDCREDIT_OFFSET + self.ENDMUSIC_OFFSET}"')
        
        return
    
    # ===================================================================
    
    def _metadata2sectionlength(self, default_music = 'Middle_01.wav'):
        print('add music')
        with open(self.metadatapath, 'r') as f:
            medatadict = json.load(f)
        
        folderlist = sorted(self.PREMERGEFLD.iterdir())
        self.foldernamelist = [x.name for x in folderlist]        
        
        fs = medatadict['op_fs']
        
        section_length = []
        for idx, foldername in enumerate(self.foldernamelist):
            maxlength = float(medatadict['maxlength'][foldername])  
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
            self.MIDDLEPATH = self.TRANSITIONFLD.joinpath(filename)

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
    
    def exportwav_seperate(self, tmp_dir, only_hostguest=False):
        
        print(self.config)
        prj_name = self.PROJECTNAME
        self.ipwavlist = {}
        
        trackinfos = getinfo2json()
        tracknamelist = [trackinfo['name'] for trackinfo in trackinfos]
        for idx, trackname in enumerate(tracknamelist):
            if only_hostguest:
                if not trackname in self.namesall:
                    continue
            do_command('SelectAll:')
            do_command(f'SelectTracks: Mode="Set" Track="{idx}" TrackCount="1"')
            exportpath = tmp_dir.joinpath(f'{trackname}.wav')
            do_command(f'Export2: Filename={str(exportpath)}')

        return
    
    def importlabel(self, label_path):
        # do_command(f'Import2: Filename={str(label_path)}')
        do_command('ImportLabels')
        return