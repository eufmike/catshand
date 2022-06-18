import json
import numpy as np
import logging
import librosa
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
            prjconfig = json.load(f)
        
        self.prjconfig = prjconfig
        
        
        config_fld = prjconfig_path.parent
        self.metadata_path = config_fld.joinpath('metadata.json')
        return
    
    def filedict_gen(self, ip_path, op_path):
        self.ip_path = ip_path
        self.op_path = op_path
        self.prj_name = self.prjconfig['project_name']
        self.namelistorder = self.prjconfig['hosts'] + self.prjconfig['guests']
    
        self.folderlist = [x.name for x in sorted(ip_path.iterdir())]
        self.ipfilelist_dict = {}
        self.opfilelist = {}
        for name in self.namelistorder:
            self.ipfilelist_dict[name] = {}
            for fldname in self.folderlist:
                self.ipfilelist_dict[name][fldname] = sorted(ip_path.joinpath(fldname).glob(f'*{name}*.wav'))
            self.opfilelist[name] = op_path.joinpath(f'{self.prj_name}_{name}.wav')
        
        self.logger.info(f'ipfilelist_dict: {self.ipfilelist_dict}')
        self.logger.info(f'opfilelist: {self.opfilelist}')
        self.logger.info(f'folderlist: {self.folderlist}')
        return

    def createmetadata(self):
        if self.metadata_path.is_file():
                with open(self.metadata_path, 'r') as f:
                    mainmetadata_dict = json.load(f)
        else: 
            self.metadata_dict = {}
            for section in self.folderlist:
                self.metadata_dict[section] = {}
                wavfilelist = [self.ipfilelist_dict[x][section][0] for x in self.namelistorder]
                
                for wavfile in wavfilelist:
                    fs, data = read(wavfile)
                    self.metadata_dict[section][wavfile.name] = {'fs': fs, 
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

    def wav2mergemono(self):
        
        with open(self.metadata_path, 'r') as f:
            self.mainmetadata_dict = json.load(f)

        maxlength_dict = {}
        for section in self.folderlist:    
            audiolength = []
            for wavfile, value in self.mainmetadata_dict['postedit'][section].items():
                audiolength.append(value['shape'][0])

            max_audiolength = np.amax(audiolength)
            maxlength_dict[section] = str(max_audiolength)
        
        self.logger.info(maxlength_dict)
        
        with open(self.metadata_path, 'r+') as f:
            self.mainmetadata_dict = json.load(f)
            f.seek(0)
            self.mainmetadata_dict['maxlength'] = maxlength_dict
            json.dump(self.mainmetadata_dict, f, indent=2, sort_keys=True)
            f.truncate()
        
        for name in self.namelistorder:
            self.logger.info(name)
            if not self.opfilelist[name].is_file():
                target_fs = 44100
                
                wavtmp = []
                for section in self.folderlist:
                    wavfile = self.ipfilelist_dict[name][section][0]
                    self.logger.info(str(wavfile))
                    
                    fs, data = read(str(wavfile))
                    # print(fs)
                    # print(data.dtype)
                    if data.ndim == 2:
                        data = data[:, 0]
                        
                    if data.dtype == 'int32':
                        #data = data.astype(np.float32, order='C') / 2147483647
                        data = data / 2147483647 * 32768
                        data = data.astype(np.int16, order='C') 
                        
                    if fs != target_fs:
                        fs_factor = target_fs / fs
                        target_length = int(len(data)*fs_factor)
                        # data = resample(data, target_length).astype(np.int16, order='C')
                        data = data.astype('float')
                        data = librosa.resample(data, 32000, 44100)
                        data = data.astype(np.int16, order='C') 
                    else:
                        fs_factor = 1
                    
                    max_length = int(int(self.mainmetadata_dict['maxlength'][section]) * fs_factor)
                    new_length = data.shape[0]
                    self.logger.info(max_length)
                    self.logger.info(new_length)
                    if (max_length - new_length) > 0:
                        data_tmp = np.pad(data, (0, int(int(self.mainmetadata_dict['maxlength'][section]) * fs_factor) - data.shape[0]), 'constant')
                    else:
                        data_tmp = data
                        
                    # print(np.max(data_tmp), np.min(data_tmp))
                    self.logger.info(data_tmp.dtype)
                    
                    wavtmp.append(data_tmp)
                
                wavtmp = np.concatenate(wavtmp, axis = 0)
                self.logger.info(wavtmp.shape)
                
                wavtmp_as = AudioSegment(
                        wavtmp.tobytes(), 
                        frame_rate = target_fs,
                        sample_width = wavtmp.dtype.itemsize, 
                        channels = 1)
                
                wavtmp_short = wavtmp[:10000000]
                wavtmp_as_short = AudioSegment(
                        wavtmp_short.tobytes(), 
                        frame_rate = target_fs,
                        sample_width = wavtmp_short.dtype.itemsize, 
                        channels = 1)
                
                wavtmp_as_short_nosilence = self.remove_silence(wavtmp_as_short)
                wavtmp_as_result = self.match_target_amplitude(wavtmp_as, wavtmp_as_short_nosilence, -20)
                # wavtmp_as_result = compress_dynamic_range(wavtmp_as_result)
                wavtmp_as_result = np.array(wavtmp_as_result.get_array_of_samples())
                
                self.logger.info(wavtmp_as_result.shape)
                write(self.opfilelist[name], target_fs, wavtmp_as_result)
        
        self.logger.info(f'mainmetadata_dict: {self.mainmetadata_dict}')
        
        return 