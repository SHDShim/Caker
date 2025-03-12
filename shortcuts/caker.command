#!/bin/bash
# you can move this script to /Applications folder
# chmod +x caker.command
# now double click will work
eval "$(conda shell.bash hook)"
conda activate pkpo2022fbs # replace the environment name
cd ~/your-folders/caker-0.0.1/caker # replace the path for PeakPo installation
python main-tk.py
# if your mac is Apple silicon, then make sure to run with rosetta.
# to setup, right click, get info, then rosetta.
