import json
from pathlib import Path 
import numpy as np
import logging
import librosa
from tqdm import tqdm
import multiprocessing as mp
mp.set_start_method('fork', force=True)
from scipy.io.wavfile import read, write
from scipy.signal import resample
from pydub import AudioSegment
from pydub.effects import normalize
from pydub.silence import split_on_silence
from pydub.effects import compress_dynamic_range
    
class postproc:
    def __init__(self, prjconfig_path):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f'prjconfig: {prjconfig_path}')
        
        with open(prjconfig_path) as f:
            self.prjconfig = json.load(f)       
        
        with open(Path(__file__).parent.joinpath('config', 'hosts_dict.json')) as f:
            self.hostsnameidx = json.load(f)
        
        config_fld = prjconfig_path.parent
        self.metadata_path = config_fld.joinpath('metadata.json')
        return
    
    def filedict_gen(self, ip_path, op_path, single_track = None):
        self.ip_path = ip_path
        self.op_path = op_path
        self.prj_name = self.prjconfig['project_name']

        if not single_track:
            self.namelistorder = self.prjconfig['hosts'] + self.prjconfig['guests']
            self.folderlist = [x.name for x in sorted(ip_path.iterdir()) if x.name != '.DS_Store']
            self.logger.info(f'folderlist_new: {self.folderlist}')
        else:
            self.namelistorder = [self.prj_name]
            self.folderlist = ['xxxx']

        self.ipfilelist_dict = {}
        self.opfilelist = {}
        
        if not single_track:
            for name in self.namelistorder:
                self.ipfilelist_dict[name] = {}
                for fldname in self.folderlist:
                    self.ipfilelist_dict[name][fldname] = sorted(ip_path.joinpath(fldname).glob(f'*{name}*.wav'))
                self.opfilelist[name] = op_path.joinpath(f'{name}.wav')
            self.logger.info(f'ipfilelist_dict: {self.ipfilelist_dict}')
            self.logger.info(f'opfilelist: {self.opfilelist}')
            self.logger.info(f'folderlist: {self.folderlist}')
        
        else: 
            self.ipfilelist_dict[self.prj_name] = {}
            self.ipfilelist_dict[self.prj_name] = sorted(ip_path.glob(f'*.wav'))
            self.opfilelist[self.prj_name] = op_path.joinpath(f'{self.prj_name}.wav')

            self.logger.info(f'ipfilelist_dict: {self.ipfilelist_dict}')
            self.logger.info(f'opfilelist: {self.opfilelist}')
        
        return

    def createmetadata(self, check_file_exist=True, single_track = None):
        if self.metadata_path.is_file() and check_file_exist:
            with open(self.metadata_path, 'r') as f:
                mainmetadata_dict = json.load(f)
        else: 
            self.metadata_dict = {}

            if not single_track:
                for section in self.folderlist:
                    self.metadata_dict[section] = {}
                    print(section)
                    print(self.ipfilelist_dict)
                    print(self.namelistorder)
                    wavfilelist = []
                    # wavfilelist = [self.ipfilelist_dict[x][section][0] for x in self.namelistorder]
                    for name in self.namelistorder:
                        print(name)
                        wavfilelist_tmp = self.ipfilelist_dict[name][section][0]
                        print(wavfilelist_tmp)
                        wavfilelist.append(wavfilelist_tmp)
                    print(wavfilelist)
                    for wavfile in wavfilelist:
                        fs, data = read(wavfile)
                        self.metadata_dict[section][wavfile.name] = {
                                                        'fs': fs, 
                                                        'shape': data.shape,
                                                        }
            else:
                self.metadata_dict[self.prj_name] = {}
                wavfilelist = self.ipfilelist_dict[self.prj_name]
                print(wavfilelist)
                for wavfile in wavfilelist:
                    print(wavfile)
                    fs, data = read(wavfile)
                    print(data.shape)
                    self.metadata_dict[self.prj_name][wavfile.name] = {
                                                    'fs': fs, 
                                                    'shape': data.shape,
                                                    }
            mainmetadata_dict = {}
            mainmetadata_dict['postedit'] = self.metadata_dict
            with open(self.metadata_path, 'w') as f:
                json.dump(mainmetadata_dict, f, indent=2, sort_keys=True)
        
        self.mainmetadata_dict = mainmetadata_dict
        
        return 

    def remove_silence(self, sound):
        
        chunks = split_on_silence(
            sound, 
            min_silence_len = 1000,
            silence_thresh = -40
        )
        self.logger.info(len(chunks))
        sound_result = sum(chunks)
        return sound_result

    def match_target_amplitude(self, sound, sound_nosilence, target_dBFS):
        change_in_dBFS = target_dBFS - sound_nosilence.dBFS
        return sound.apply_gain(change_in_dBFS)

    def _wav2mergemono(self, name, target_fs, loudness, single_track):
        self.logger.info(name)
        if not self.opfilelist[name].is_file():
            print('ssss')
            print(self.opfilelist[name])
            # print('folderlist:'+ self.folderlist)
            sound_combined = AudioSegment.empty()

            if not single_track:
                for section in self.folderlist:
                    wavfile = self.ipfilelist_dict[name][section][0]
                    self.logger.info(str(wavfile))
                    
                    # fs, data = read(str(wavfile))
                    sound = AudioSegment.from_file(str(wavfile))
                    sound = sound.set_channels(1)
                    sound = sound.set_frame_rate(target_fs)           
                    max_length_second = float(self.mainmetadata_dict['maxlength'][section])
                    
                    max_length_ms = max_length_second * 1000
                    if max_length_ms >= len(sound):
                        silence = AudioSegment.silent(duration=max_length_ms-len(sound))
                        sound = sound + silence
                    else:
                        sound = sound[:max_length_ms]

                    sound_combined = sound_combined + sound
            else:
                for wavfile in self.ipfilelist_dict[name]:
                    self.logger.info(str(wavfile))
                    
                    # fs, data = read(str(wavfile))
                    sound = AudioSegment.from_file(str(wavfile))
                    sound = sound.set_channels(1)
                    sound = sound.set_frame_rate(target_fs)           
                    sound_combined = sound_combined + sound

            if loudness: 
                sound_combined_downsample = sound_combined.set_frame_rate(600)
                sound_combined_downsample_nosilence = self.remove_silence(sound_combined_downsample)
                sound_combined = self.match_target_amplitude(sound_combined, sound_combined_downsample_nosilence, -20)
            
            self.logger.info(len(sound_combined))
            sound_combined.export(self.opfilelist[name], format="wav", bitrate=target_fs)
        
        self.logger.info(f'mainmetadata_dict: {self.mainmetadata_dict}')
        return

    def _mp_wav2mergemono(self, target_fs, loudness, threads, single_track):

        if threads > 1:
            pbar = tqdm(total=len(self.namelistorder))
            results = []
            def pbar_update(result):
                results.append(result)
                pbar.update(1)
            
            pool = mp.Pool(threads)
            # sections = []
            for name in self.namelistorder:
                pool.apply_async(self._wav2mergemono, args=(name, target_fs, loudness, single_track), callback=pbar_update)
            pool.close()
            pool.join()

        else:
            for name in tqdm(self.namelistorder):
                self._wav2mergemono(name, target_fs, loudness, single_track)
            
        return

    def wav2mergemono(self, target_fs = 32000, loudness = False, threads = 1, single_track = None):
        with open(self.metadata_path, 'r') as f:
            self.mainmetadata_dict = json.load(f)

        maxlength_dict = {}

        if not single_track:
            for section in self.folderlist:    
                audiolength = []
                for wavfile in sorted(self.mainmetadata_dict['postedit'][section].keys()):
                    value = self.mainmetadata_dict['postedit'][section][wavfile]
                    audiolength.append(value['shape'][0] / value['fs'])

                max_audiolength = np.amax(audiolength)
                maxlength_dict[section] = str(max_audiolength)
        else:
            for wavfile in sorted(self.mainmetadata_dict['postedit'][self.prj_name].keys()):
                value = self.mainmetadata_dict['postedit'][self.prj_name][wavfile]
                maxlength_dict[wavfile] = str(value['shape'][0] / value['fs'])
        
        self.logger.info(maxlength_dict)
        
        with open(self.metadata_path, 'r+') as f:
            self.mainmetadata_dict = json.load(f)
            f.seek(0)
            self.mainmetadata_dict['maxlength'] = maxlength_dict
            self.mainmetadata_dict['op_fs'] = target_fs
            json.dump(self.mainmetadata_dict, f, indent=2, sort_keys=True)
            f.truncate()      
        
        self._mp_wav2mergemono(target_fs, loudness = loudness, threads=threads, single_track = single_track)
        
        return

# =========================================================

def highlightproc(ippath, oppath, target_fs = 32000):
    fs, wavtmp = read(str(ippath))
    
    wavtmp_as = AudioSegment(
                        wavtmp.tobytes(), 
                        frame_rate = target_fs,
                        sample_width = wavtmp.dtype.itemsize, 
                        channels = 1)

    wavtmp_as_short_nosilence = remove_silence(wavtmp_as)
    wavtmp_as_result = match_target_amplitude(wavtmp_as, wavtmp_as_short_nosilence, -20)
    wavtmp_as_result = np.array(wavtmp_as_result.get_array_of_samples())
    write(oppath, target_fs, wavtmp_as_result)
    return

def match_target_amplitude(sound, sound_nosilence, target_dBFS):
    change_in_dBFS = target_dBFS - sound_nosilence.dBFS
    return sound.apply_gain(change_in_dBFS)

def remove_silence(sound, min_silence_len = 1000, silence_thresh = -40, logger = None):
    if logger is not None:
        logger.info('start remove_silence')
    chunks = split_on_silence(
        sound, 
        min_silence_len = min_silence_len,
        silence_thresh = silence_thresh
    )
    if logger is not None:
        logger.info('end remove_silence')

    sound_result = sum(chunks)
    return sound_result
