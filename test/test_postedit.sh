#!/bin/sh

PRJPATH="/Users/mikeshih/Documents/Podcast/EP099"
IPFLD="00_Raw_wav_prjpre_wav_silrm_splitted"
HLFLD="05_Highlight"
THREADS=9
echo $PRJPATH/${IPFLD}_wav

catshand audio2wav -p $PRJPATH -i $PRJPATH/$IPFLD -l -t 4
catshand audmerger -p $PRJPATH -i $PRJPATH/${IPFLD}_wav -t 4
catshand audio2wav -p $PRJPATH -i $PRJPATH/$HLFLD -l
catshand audacitypipe -p $PRJPATH -i $PRJPATH/${IPFLD}_wav_merged