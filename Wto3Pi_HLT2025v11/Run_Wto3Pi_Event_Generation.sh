#!/bin/bash

# Usage: ./Run_Wto3Pi_Event_Generation.sh [NUM_EVENTS]
# Default is 500 if not specified

NUM_EVENTS=${1:-500}

echo ">>> Running full chain with ${NUM_EVENTS} events"


# Check if CMSSW already exists
if [ ! -d "CMSSW_13_0_14/src" ]; then
  echo ">>> Creating CMSSW_13_0_14 area"
  # Enter singularity container
  cmssw-el8 || { echo "Failed to enter cmssw-el8"; exit 1; }
  cmsrel CMSSW_13_0_14 || { echo "cmsrel failed"; exit 1; }
fi

cd CMSSW_13_0_14/src || exit 1
cmsenv

# Add Configuration package
git cms-addpkg Configuration

# Check if the fragment is already downloaded
FRAG_PATH="Configuration/GenProduction/python/HIG-RunIISummer20UL17wmLHEGEN-13119-fragment.py"
if [ ! -f "${FRAG_PATH}" ]; then
  echo ">>> Downloading fragment"
  curl -s -k https://cms-pdmv-prod.web.cern.ch/mcm/public/restapi/requests/get_fragment/HIG-RunIISummer20UL17wmLHEGEN-13119 \
    --retry 3 --create-dirs -o "${FRAG_PATH}"
fi

# Step 1: LHE + GEN
cmsDriver.py "${FRAG_PATH}" \
  --eventcontent RAWSIM,LHE \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN,LHE \
  --conditions 130X_mcRun3_2023_realistic_postBPix_v2 \
  --beamspot Realistic25ns13p6TeVEarly2023Collision \
  --step LHE,GEN \
  --geometry DB:Extended \
  --era Run3_2023 \
  --python_filename HIG-RunIISummer20UL17wmLHEGEN-13119_1_cfg.py \
  --fileout file:HIG-RunIISummer20UL17wmLHEGEN-13119.root \
  --no_exec --mc -n ${NUM_EVENTS} \
  --customise_commands "process.source.numberEventsInLuminosityBlock = cms.untracked.uint32(25)"

cmsRun HIG-RunIISummer20UL17wmLHEGEN-13119_1_cfg.py

# Step 2: SIM
cmsDriver.py \
  --eventcontent RAWSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN-SIM \
  --conditions 130X_mcRun3_2023_realistic_postBPix_v2 \
  --beamspot Realistic25ns13p6TeVEarly2023Collision \
  --step SIM \
  --geometry DB:Extended \
  --era Run3_2023 \
  --python_filename HIG-RunIISummer20UL17SIM-13144_1_cfg.py \
  --fileout file:HIG-RunIISummer20UL17SIM-13144.root \
  --filein file:HIG-RunIISummer20UL17wmLHEGEN-13119.root \
  --runUnscheduled --no_exec --mc -n ${NUM_EVENTS}

cmsRun HIG-RunIISummer20UL17SIM-13144_1_cfg.py

# Step 3: DIGIPremix
if [ ! -f "pileup_input.txt" ]; then
  echo ">>> Copying pileup_input.txt"
  cp /hdfs/store/user/chnee/pileup_input.txt .
fi

cmsDriver.py \
  --eventcontent PREMIXRAW \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN-SIM-DIGI \
  --conditions 130X_mcRun3_2023_realistic_postBPix_v2 \
  --step DIGI,DATAMIX,L1,DIGI2RAW \
  --procModifiers premix_stage2 \
  --geometry DB:Extended \
  --datamix PreMix \
  --era Run3_2023 \
  --python_filename HIG-RunIISummer20UL17DIGIPremix-13144_1_cfg.py \
  --fileout file:HIG-RunIISummer20UL17DIGIPremix-13144.root \
  --filein file:HIG-RunIISummer20UL17SIM-13144.root \
  --pileup_input filelist:pileup_input.txt \
  --runUnscheduled --no_exec --mc -n ${NUM_EVENTS}

cmsRun HIG-RunIISummer20UL17DIGIPremix-13144_1_cfg.py

# Step 4: HLT
cmsDriver.py \
  --eventcontent RAWSIM \
  --customise Configuration/DataProcessing/Utils.addMonitoring \
  --datatier GEN-SIM-RAW \
  --conditions 130X_mcRun3_2023_realistic_postBPix_v2 \
  --customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
  --step HLT:2023v12 \
  --geometry DB:Extended \
  --era Run3_2023 \
  --python_filename HIG-RunIISummer20UL17HLT-13144_1_cfg.py \
  --fileout file:HIG-RunIISummer20UL17HLT-13144.root \
  --filein file:HIG-RunIISummer20UL17DIGIPremix-13144.root \
  --no_exec --mc -n ${NUM_EVENTS}

cmsRun HIG-RunIISummer20UL17HLT-13144_1_cfg.py

echo ">>> Finished full chain with ${NUM_EVENTS} events!"

