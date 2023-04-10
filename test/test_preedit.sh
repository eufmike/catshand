#!/bin/sh

PRJPATH="/Users/mikeshih/Documents/Podcast/EP099"
THREADS=9
IPFLD="00_Raw"

catshand prjinit -d /Users/mikeshih/Documents/Podcast/ -n EP099 -m /Users/mikeshih/Documents/Podcast/material
catshand audio2wav -p $PRJPATH -m
catshand audacitypipe_prjpre -p $PRJPATH -t $THREADS
catshand audio2wav -p $PRJPATH -i $PRJPATH/${IPFLD}_wav_prjpre -lr -t $THREADS
catshand silrm -p $PRJPATH -pz -t $THREADS
catshand audiosplit -p $PRJPATH -ts 00:02:00 00:04:00 
catshand trackmerger -p $PRJPATH -s -sp
catshand audiosplit -p $PRJPATH  -i $PRJPATH/merged -ts 00:02:00 00:04:00