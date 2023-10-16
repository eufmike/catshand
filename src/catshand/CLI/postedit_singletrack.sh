while getopts 'p:n:' OPTION; do
    case "$OPTION" in
        p) prj_path=${OPTARG};;
        n) prj_name=${OPTARG};;
    esac
done

# prj_path="/Users/mikeshih/Documents/Podcast"
# prj_name="EP033"

echo "prj_path: $prj_path";
echo "prj_name: $prj_name";

EPISODE_PATH=$prj_path/$prj_name

catshand audio2wav -p $EPISODE_PATH -i $EPISODE_PATH/03_Editing_02 -l -t 4
catshand audmerger -p $EPISODE_PATH -i $EPISODE_PATH/03_Editing_02_wav -t 4
catshand audio2wav -p $EPISODE_PATH -i $EPISODE_PATH/05_Highlight -l
catshand audacitypipe -p $EPISODE_PATH -i $EPISODE_PATH/03_Editing_02_wav_merged