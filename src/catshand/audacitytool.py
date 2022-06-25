import os, sys, re, json
from pathlib import Path
from catshand.pipefunc import do_command, send_command, get_response, get_response_json

class audacitytool():
    def __init__(self, prj_path):
        self.prj_path = Path(prj_path)
        self.config = self.prj_path.joinpath('config', 'audt_config.json')
        if self.config.exists():
            
        
        
        return
        
    '''
    def getinfo2json():
        send_command('GetInfo: Format="JSON" Type="Tracks"')
        response = get_response_json()
        result = json.loads(response)
        return(result)

    trackinfo = getinfo2json()
    print(trackinfo)

    filename_noext = [re.sub('.wav', '', value.name) for idx, value in opmonofilelist.items()]

    tracknamelist = [trackinfo['name'] for trackinfo in trackinfo]
    name_tag = 'EP20'

    def importfiles(filepath):
        do_command(f'Import2: Filename={filepath}')

    TRACK_HEIGHT = 80
    TRACK_OFFSET = 29.6
    MATERIAL_DIR = Path('Z:\sc2.shih\Drive\Podcast\Edit\material')
    OPMUSIC_PATH = MATERIAL_DIR.joinpath('direct_import', 'direct_import_op.wav')
    ENDMUSIC_PATH = MATERIAL_DIR.joinpath('direct_import', 'direct_import_end.wav')
    ENDCREDIT_PATH = MATERIAL_DIR.joinpath('direct_import', 'direct_import_endcredit.wav')
    ENDCREDIT_OFFSET = 9.2
    '''