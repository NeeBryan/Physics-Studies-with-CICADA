# Andrew Loeliger
# This configuration will take a GEN-SIM-RAW MC file, and emulate

import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run3_2024_cff import Run3_2024

import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing('analysis')
options.register(
    'isData',
    False,
    VarParsing.VarParsing.multiplicity.singleton,
    VarParsing.VarParsing.varType.bool,
    "Use data based configuration options or not. Defaults to False i.e. not Data",
)
options.register(
    'isScouting',
    False,
    VarParsing.VarParsing.multiplicity.singleton,
    VarParsing.VarParsing.varType.bool,
    "Use Scouting data configuration options. Defaults to False.",
)


options.parseArguments()

process = cms.Process("NTUPLIZE",Run3_2024)
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_Data_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

#Process input files from command line
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

#Don't report every event
process.MessageLogger.cerr.FwkReport.reportEvery = 10000

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(options.inputFiles),
)

process.options = cms.untracked.PSet(
    # FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    # SkipEvent = cms.untracked.vstring(),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    makeTriggerResults = cms.obsolete.untracked.bool,
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

from Configuration.AlCa.GlobalTag import GlobalTag
if options.isData:
    print("Treating config as data.")
    # process.GlobalTag = GlobalTag(process.GlobalTag, '130X_dataRun3_Prompt_v4', '')
    # process.GlobalTag = GlobalTag(process.GlobalTag, '140X_dataRun3_Prompt_v4_HcalPFCuts_2023_V1p0_HB_1p5x', '')
    process.GlobalTag = GlobalTag(process.GlobalTag, '150X_dataRun3_Prompt_v3', '')

else:
    print("Treating config as simulation.")
    # process.GlobalTag = GlobalTag(process.GlobalTag, '130X_mcRun3_2023_realistic_postBPix_v2', '')
    process.GlobalTag = GlobalTag(process.GlobalTag, '150X_mcRun3_2025_realistic_v4', '')

process.raw2digi_step = cms.Path(process.RawToDigi)
process.endjob_step = cms.EndPath(process.endOfProcess)

process.schedule = cms.Schedule(process.raw2digi_step, process.endjob_step)

from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# ------------------------------------------
# 1. Apply the correct L1 trigger re-emulation customisation
# ------------------------------------------
if options.isData:
    from L1Trigger.Configuration.customiseReEmul import L1TReEmulFromRAW
    process = L1TReEmulFromRAW(process)
else:
    from L1Trigger.Configuration.customiseReEmul import L1TReEmulMCFromRAW
    process = L1TReEmulMCFromRAW(process)

# ------------------------------------------
# 2. Add the L1Ntuple path
# ------------------------------------------
from L1Trigger.L1TNtuples.customiseL1Ntuple import L1NtupleRAWEMU
process = L1NtupleRAWEMU(process)

# ------------------------------------------
# 3. For Data: Patch InputTags pointing to rawDataCollector -> hltFEDSelectorL1
# ------------------------------------------
if options.isScouting:
    print("\n[INFO] Patching rawDataCollector -> hltFEDSelectorL1 in InputTags")

    def replace_rawDataCollector_inputtags(pset):
        for name in pset.parameterNames_():
            val = getattr(pset, name)

            if isinstance(val, cms.InputTag):
                if val.getModuleLabel() == "rawDataCollector":
                    print(f'Replacing: {val}')
                    setattr(pset, name, cms.InputTag("hltFEDSelectorL1"))

            elif isinstance(val, cms.VInputTag):
                new_list = []
                for tag in val:
                    if isinstance(tag, cms.InputTag) and tag.getModuleLabel() == "rawDataCollector":
                        new_list.append(cms.InputTag("hltFEDSelectorL1"))
                    else:
                        new_list.append(tag)
                print(f'Replacing: {val}')
                if not val.isTracked(): #make it untracked
                    setattr(pset, name, cms.untracked.VInputTag(*new_list))
                else: #other thing
                    setattr(pset, name, cms.VInputTag(*new_list))

            elif isinstance(val, cms.PSet):
                replace_rawDataCollector_inputtags(val)

            elif isinstance(val, cms.VPSet):
                for subpset in val:
                    replace_rawDataCollector_inputtags(subpset)

    # Concatenate producers and analyzers safely
    all_modules = list(process.producers_())
    all_modules.extend(list(process.analyzers_()))

    for modname in all_modules:
        mod = getattr(process, modname)
        replace_rawDataCollector_inputtags(mod)

    print("[INFO] Patching complete.\n")

simpleCICADANtuplizer = cms.EDAnalyzer(
    "simpleCICADANtuplizer",
    scoreSource = cms.InputTag("simCaloStage2Layer1Summary", "CICADAScore")
)

L1TTriggerBitsNtuplizer = cms.EDAnalyzer(
    'L1TTriggerBitsNtuplizer',
    gtResults    = cms.InputTag("gtStage2Digis"),
    verboseDebug = cms.bool(False),
)

process.simpleCICADANtuplizer = simpleCICADANtuplizer
process.L1TTriggerBitsNtuplizer = L1TTriggerBitsNtuplizer
process.NtuplePath = cms.Path(
    process.simpleCICADANtuplizer +
    process.L1TTriggerBitsNtuplizer
)
process.schedule.append(process.NtuplePath)

process.TFileService = cms.Service(
	"TFileService",
        fileName = cms.string(options.outputFile)
)

print("schedule:")
print(process.schedule)
print("schedule contents:")
print([x for x in process.schedule])
