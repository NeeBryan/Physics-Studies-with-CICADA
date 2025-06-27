import ROOT
import numpy as np
import os 

def get_prescale_1_triggers(tree):
    """Find all trigger bits with prescale = 1 across *all entries* in the data tree."""
    prescale_1_triggers = []

    for branch in tree.GetListOfBranches():
        name = branch.GetName()
        if "prescale" not in name:
            continue

        trigger_bit_name = name.replace("_prescale", "")
        values = []

        for entry in tree:
            try:
                val = float(getattr(entry, name))
                values.append(val)
            except Exception:
                values = []
                break  # Skip this branch if we encounter error

        if values and all(v == 1 for v in values):
            prescale_1_triggers.append(trigger_bit_name)

    return prescale_1_triggers

def compute_trigger_means(tree, trigger_bits):
    """Compute mean values (efficiencies) for trigger bits in the MC tree."""
    mean_values = {}

    for bit in trigger_bits:
        values = []
        for entry in tree:
            try:
                val = float(getattr(entry, bit))
                values.append(val)
            except Exception:
                continue
        if values:
            mean_values[bit] = np.mean(values)
        else:
            mean_values[bit] = 0.0

    return mean_values

def analyze_triggers(mc_file, data_file, output_file):
    # 1. Get prescale=1 triggers from data
    data_root = ROOT.TFile.Open(data_file, "READ")
    if not data_root or data_root.IsZombie():
        print("Error: Cannot open data file.")
        return
    data_tree = data_root.Get("L1TTriggerBitsNtuplizer/L1TTriggerBits")
    if not data_tree:
        print("Error: Cannot find TTree in data file.")
        return
    prescale_1_triggers = get_prescale_1_triggers(data_tree)
    data_root.Close()
    print(f"Found {len(prescale_1_triggers)} prescale=1 triggers in data.")

    # 2. Compute MC efficiencies for these triggers
    mc_root = ROOT.TFile.Open(mc_file, "READ")
    if not mc_root or mc_root.IsZombie():
        print("Error: Cannot open MC file.")
        return
    mc_tree = mc_root.Get("L1TTriggerBitsNtuplizer/L1TTriggerBits")
    if not mc_tree:
        print("Error: Cannot find TTree in MC file.")
        return

    trigger_means = compute_trigger_means(mc_tree, prescale_1_triggers)

    # 3. Pick top 20 triggers
    top20 = sorted(trigger_means.items(), key=lambda x: x[1], reverse=True)[5:25]
    top20_names = [name for name, val in top20]
    top20_vals = [val for name, val in top20]

    print("Top 20 triggers selected:")
    for name, val in top20:
        print(f"  {name}: {val:.4f}")

    # 4. Compute CICADA trigger efficiency
    cicada_trigger = "DST_PFScouting_CICADAVLoose"
    cicada_vals = []
    for entry in mc_tree:
        try:
            cicada_vals.append(float(getattr(entry, cicada_trigger)))
        except Exception:
            continue
    cicada_mean = np.mean(cicada_vals) if cicada_vals else 0.0
    print(f"CICADA Trigger Efficiency: {cicada_mean:.4f}")

    # 5. Compute "trigger OR CICADA" efficiencies
    trigger_or_cicada_means = {}
    for bit in top20_names:
        vals = []
        for entry in mc_tree:
            try:
                trig_val = float(getattr(entry, bit))
                cic_val = float(getattr(entry, cicada_trigger))
                or_val = max(trig_val, cic_val)
                vals.append(or_val)
            except Exception:
                continue
        trigger_or_cicada_means[bit] = np.mean(vals) if vals else 0.0

    mc_root.Close()

    # 6. Plot comparison
    mc_basename = os.path.basename(mc_file).replace("CICADA_", "")
    ROOT.gStyle.SetOptStat(0)
    canvas = ROOT.TCanvas("canvas", "Trigger Efficiencies", 1000, 600)
    ROOT.gPad.SetBottomMargin(0.35)

    n_bins = len(top20_names)
    hist_orig = ROOT.TH1F("hist_orig", "Trigger Efficiencies", n_bins, 0, n_bins)
    hist_or = ROOT.TH1F("hist_or", "Trigger OR CICADA", n_bins, 0, n_bins)

    for i, name in enumerate(top20_names):
        hist_orig.SetBinContent(i+1, top20_vals[i])
        hist_orig.GetXaxis().SetBinLabel(i+1, name)
        hist_or.SetBinContent(i+1, trigger_or_cicada_means[name])
        hist_or.GetXaxis().SetBinLabel(i+1, name)

    hist_orig.SetLineColor(ROOT.kBlue)
    hist_orig.SetLineWidth(2)
    hist_or.SetLineColor(ROOT.kRed)
    hist_or.SetLineWidth(2)

    hist_orig.GetYaxis().SetTitle("Efficiency")
    hist_orig.GetXaxis().LabelsOption("v")
    hist_orig.GetXaxis().SetLabelSize(0.025)
    hist_orig.SetTitle(f"Top 20 Trigger Efficiencies vs OR with CICADA (MC: {mc_basename})")

    hist_orig.Draw("HIST")
    hist_or.Draw("HIST SAME")

    legend = ROOT.TLegend(0.65, 0.7, 0.88, 0.88)
    legend.SetTextSize(0.025)
    legend.AddEntry(hist_orig, "Trigger Alone", "l")
    legend.AddEntry(hist_or, "Trigger OR CICADA", "l")
    legend.Draw()

    # Save outputs
    output_png = f"compare_OR_CICADA_{mc_basename}.png"
    output_root = ROOT.TFile(output_file, "RECREATE")
    hist_orig.Write()
    hist_or.Write()
    output_root.Close()
    canvas.SaveAs(output_png)
    print(f"Saved comparison plot as {output_png}")



# # Example usage
# analyze_triggers(
#     mc_file="/afs/hep.wisc.edu/home/cnee/Displaced_Tau/CMSSW_13_0_14/src/EXO_2_MS-7_ctaus-10_CICADA.root",
#     data_file="CICADA-Run2024D_Tau_RAW_d471695c-0b25-4260-8607-4e30fad32346.root",
#     output_file="L1T_EXO_2_MS-7_ctaus-10.root"
# )

# List of MC ROOT files
mc_files = [
    "/afs/hep.wisc.edu/user/cnee/Wto3Pi/CMSSW_15_0_7/src/PU_Run3Winter24GS/L1TTriggerBitsNtuplizer/CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root"
]

# Shared data file
data_file = "/afs/hep.wisc.edu/user/cnee/Wto3Pi/CMSSW_15_0_7/src/PU_Run3Winter24GS/L1TTriggerBitsNtuplizer/CICADA_JetMET0Run2024G.root"

# Loop through MC files and run analysis
for mc_file in mc_files:
    mc_base = os.path.basename(mc_file).replace(".root", "")
    output_file = f"L1T_{mc_base}.root"

    print(f"\n>>> Processing {mc_base}")
    analyze_triggers(mc_file=mc_file, data_file=data_file, output_file=output_file)


