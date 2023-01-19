# Post-edit Processing order

- Download finalized edited audio from Google Drive
- Rename all session to 01, 02, 03...
- Rename all fileanmes by hosts' and guests' name. Ensure the naming fashion is the same as config.json

- run wavconverter.py on postedit wavs
    
    ```shell
    \tools\wavfconverter.py -i C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_raw
    ```

- run wav files merger postfilemerger.py
    ```
    python .\tools\postfilemerger.py -i 'C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_raw_export\' -o 'C:\Users\michaelshih\Documents\Podcast_tmp\EP024\postedit_merged\' -cfg C:\Users\michaelshih\Documents\Podcast_tmp\EP024\config\config.json
    ```

- Download hightlight from Google Drive, current only support wav
- Rename the filename to `highlight.wav`
- run wavconverter.py on pthe hightlight
    
    ```shell
    python .\tools\wavfconverter.py -i C:\Users\michaelshih\Documents\Podcast_tmp\EP024\highlight -o C:\Users\michaelshih\Documents\Podcast_tmp\EP024\highlight_export --ext 'wav'
    ```


- run Audacity macro tool 
python .\tools\audacity_tool.py -i C:\Users\michaelshih\Documents\Podcast_tmp\EP025 -m Z:\sc2.shih\Drive\Podcast\Edit\material
