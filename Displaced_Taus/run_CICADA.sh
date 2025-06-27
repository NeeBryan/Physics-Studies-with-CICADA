#!/bin/bash

# -----------------------------------------------------------------------------
# Script: run_CICADA.sh
# Description:
#   This script runs CMS software using a CICADA CMSSW configuration on
#   a list of input MC signal ROOT files. It produces CICADA-processed output files.
#
# Requirements:
#   - CMSSW environment must be set up (cmsenv)
#   - The CMSSW config must be valid and point to the correct CICADA setup
#
# Example usage:
#   ./run_CMSSW_CICADA_conversion.sh
# -----------------------------------------------------------------------------

# List of input MC root files (unprocessed)
root_files_dir="/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_13_0_14/src/PU_MinBias_TuneCP5_13p6TeV-pythia8_Run3Winter24GS-133X_mcRun3_2024_realistic_v7-v1/CMSSW_13_3_0/src"
root_files=(
    "${root_files_dir}/EXO_2_MS-7_ctaus-10.root"
    "${root_files_dir}/EXO_2_MS-7_ctaus-1000.root"
    "${root_files_dir}/EXO_2_MS-7_ctaus-100000.root"
    "${root_files_dir}/EXO_2_MS-55_ctaus-10.root"
    "${root_files_dir}/EXO_2_MS-55_ctaus-1000.root"
    "${root_files_dir}/EXO_2_MS-55_ctaus-100000.root"
)

# Path to CMSSW config
cmssw_config="ADPaper/Ntuples/python/l1nano_AD.py"

# Loop through each input ROOT file
for input_file in "${root_files[@]}"; do
    # Extract base name (no extension)
    file_base=$(basename "$input_file" .root)
    
    # Define output file name
    output_file="/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_15_1_0_pre1/src/${file_base}_CICADA.root"

    echo "Running cmsRun on: $file_base"
    echo "Output will be:    $output_file"

    # Run the cmsRun command
    cmsRun "$cmssw_config" \
        inputFiles="file:${input_file}" \
        outputFile="file:${output_file}"

    if [[ $? -ne 0 ]]; then
        echo "❌ Failed: $input_file"
    else
        echo "✅ Done: $output_file"
    fi

    echo "-------------------------------------------"
done

echo "All files processed."

