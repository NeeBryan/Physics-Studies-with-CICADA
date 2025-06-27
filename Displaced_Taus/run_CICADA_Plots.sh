# -----------------------------------------------------------------------------
# Script: run_CICADA_Plots.sh
# Author: Bryan Nee
#
# Description:
#   This script processes a list of MC signal ROOT files with the CICADA macro.
#   For each file:
#     - It updates the Histograms.h file to point to unique histogram and image directories
#     - It executes the CICADA macro in ROOT
#     - It outputs histograms and PNG images into structured subfolders
#
# Requirements:
#   - ROOT environment must be set up
#   - CICADA.c and Histograms.h must exist at specified paths
#   - ROOT files must exist at specified input paths
#
# Output:
#   - Histograms saved in ./HistFile/<tag>/
#   - PNGs saved in ./Image/<tag>/
#
# Example usage:
#   ./run_CICADA.sh
# -----------------------------------------------------------------------------

#!/bin/bash

# Define the list of ROOT files to process
root_files=(
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-7_ctaus-10_CICADA.root"
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-7_ctaus-1000_CICADA.root"
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-7_ctaus-100000_CICADA.root"
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-55_ctaus-10_CICADA.root"
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-55_ctaus-1000_CICADA.root"
    "/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_0_3/src/EXO_2_MS-55_ctaus-100000_CICADA.root"
)

# Path to the CICADA macro and Histograms.h
macro_path="/afs/hep.wisc.edu/user/cnee/Displaced_Tau/CMSSW_15_0_3/src/CICADA.c"
histogram_header_path="/afs/hep.wisc.edu/user/cnee/Displaced_Tau/CMSSW_15_0_3/src/Histograms.h"

# Check if the macro and histogram header exist
if [[ ! -f "$macro_path" ]]; then
    echo "Error: CICADA macro not found at $macro_path"
    exit 1
fi

if [[ ! -f "$histogram_header_path" ]]; then
    echo "Error: Histograms.h file not found at $histogram_header_path"
    exit 1
fi

# Function to update the Histograms.h file
update_histogram_path() {
    local root_file="$1"

    # Extract the "MS_..." part from the ROOT file name
    local file_base=$(basename "$root_file" .root | sed 's/EXO_2_//')

    # Generate new directory name based on the extracted part
    local new_hist_dir="./HistFile/${file_base}"
    local new_image_dir="./Image/${file_base}"

    # Create the directories if they do not exist
    mkdir -p "$new_hist_dir"
    mkdir -p "$new_image_dir"

    # Update Histograms.h with the new paths
    sed -i "s|HistFile/.*|HistFile/${file_base}/\" + histFileName;|" "$histogram_header_path"
    sed -i "s|Image/.*|Image/${file_base}/\" + iter.first + \".png\";|" "$histogram_header_path"
}

# Loop through each ROOT file and process it
for root_file in "${root_files[@]}"; do
    echo "Processing file: $root_file"

    # Check if the ROOT file exists
    if [[ ! -f "$root_file" ]]; then
        echo "Error: ROOT file not found: $root_file"
        continue
    fi

    # Update the Histograms.h file for the current ROOT file
    update_histogram_path "$root_file"

    # Run the CICADA macro with the current ROOT file
    root -l -q "${macro_path}(\"${root_file}\")"

    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to process $root_file"
    else
        echo "Successfully processed $root_file"
    fi

    echo "---------------------------------------"
done

echo "All files processed."

