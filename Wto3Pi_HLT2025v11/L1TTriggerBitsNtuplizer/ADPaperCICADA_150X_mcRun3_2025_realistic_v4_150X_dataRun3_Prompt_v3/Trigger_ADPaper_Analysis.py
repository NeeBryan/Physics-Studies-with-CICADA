"""
=====================================================================
This script analyzes Level-1 (L1) trigger efficiencies for a Monte Carlo (MC) signal sample.
It does the following:

1. Reads a *data* ROOT file (e.g. ZeroBias or JetMET) containing *prescale=1* L1 trigger bits.
   - The data L1 emulator output is assumed to be generated using the **simpleCICADAConfiguration**
     (https://github.com/aloeliger/simpleCICADAConfiguration).

2. Identifies all L1 trigger bits in data with prescale = 1 across all events.

3. Reads the *MC signal* ROOT file, which should contain the same L1 trigger bits.
   - The MC signal emulator output is assumed to be generated using the **ADPaper** repository
     (https://github.com/aloeliger/ADPaper/tree/main).

4. Computes the mean (efficiency) of each prescale=1 trigger in the MC sample.

5. Adds the efficiency of the CICADA trigger ("L1_CICADA_VLoose") from the MC sample.

6. Sorts all triggers by their efficiencies (including CICADA) in descending order.

7. Computes a comparison for each trigger alone vs. (trigger OR CICADA) efficiency.

8. Saves two ROOT histograms and PNG plots:
   - One showing the original trigger efficiencies.
   - One showing the "Trigger OR CICADA" efficiencies.

This allows you to see whether adding the CICADA trigger improves the coverage of
the top triggers selected from the data-driven prescale=1 list.
=====================================================================
"""

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
                break
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
    mc_tree = mc_root.Get("Events")
    if not mc_tree:
        print("Error: Cannot find TTree in MC file.")
        return

    # 3. Compute CICADA trigger efficiency on MC
    cicada_trigger = "DST_PFScouting_CICADAVLoose"
    cicada_vals = []
    for entry in mc_tree:
        try:
            cicada_vals.append(float(getattr(entry, cicada_trigger)))
        except Exception:
            continue
    cicada_mean = np.mean(cicada_vals) if cicada_vals else 0.0
    print(f"\nCICADA Trigger Efficiency on MC: {cicada_mean:.4f}")

    trigger_means = compute_trigger_means(mc_tree, prescale_1_triggers)
    trigger_means[cicada_trigger] = cicada_mean

    # 4. Pick top 20 triggers
    top20 = sorted(trigger_means.items(), key=lambda x: x[1], reverse=True)[5:26]
    top20_names = [name for name, val in top20]
    top20_vals = [val for name, val in top20]
    print("\nSelected top 20 triggers:")
    for name, val in top20:
        print(f"  {name}: {val:.4f}")

    # 5. Compute "trigger OR CICADA" efficiencies for top 20 triggers
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

    # 6. Print comparison table
    print("\nComparison of Trigger Efficiencies with/without CICADA OR:")
    print(f"{'Trigger':<40} {'Orig':>8} {'OR_CICADA':>10} {'Delta':>8}")
    for name in top20_names:
        orig = trigger_means.get(name, 0.0)
        or_cic = trigger_or_cicada_means.get(name, 0.0)
        delta = or_cic - orig
        print(f"{name:<40} {orig:8.4f} {or_cic:10.4f} {delta:8.4f}")

    # 7. Plotting
    ROOT.gStyle.SetOptStat(0)

    n_bins = len(top20_names)
    hist_orig = ROOT.TH1F("hist_orig", "Trigger Alone", n_bins, 0, n_bins)
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
    hist_or.GetYaxis().SetTitle("Efficiency")

    # Adjust labels
    hist_orig.GetXaxis().LabelsOption("v")
    hist_orig.GetXaxis().SetLabelSize(0.025)
    hist_or.GetXaxis().LabelsOption("v")
    hist_or.GetXaxis().SetLabelSize(0.025)

    # Base name for file naming
    mc_basename = os.path.basename(mc_file).replace("CICADA_", "").replace(".root", "")

    # Canvas 1: Trigger Alone
    canvas1 = ROOT.TCanvas("canvas1", "Trigger Alone", 1000, 600)
    canvas1.SetBottomMargin(0.35)
    hist_orig.SetTitle(f"Trigger Efficiencies Alone (MC: {mc_basename})")
    hist_orig.Draw("HIST")

    legend1 = ROOT.TLegend(0.65, 0.7, 0.88, 0.88)
    legend1.SetTextSize(0.025)
    legend1.AddEntry(hist_orig, "Trigger Alone", "l")
    legend1.Draw()

    # Save Canvas 1
    output1_png = f"top20_trigger_means_{mc_basename}.png"
    canvas1.SaveAs(output1_png)

    # Canvas 2: Trigger OR CICADA
    canvas2 = ROOT.TCanvas("canvas2", "Trigger OR CICADA", 1000, 600)
    canvas2.SetBottomMargin(0.35)
    hist_or.SetTitle(f"Trigger Efficiencies with CICADA OR (MC: {mc_basename})")
    hist_or.Draw("HIST")

    legend2 = ROOT.TLegend(0.65, 0.7, 0.88, 0.88)
    legend2.SetTextSize(0.025)
    legend2.AddEntry(hist_or, "Trigger + CICADA", "l")
    legend2.Draw()

    # Save Canvas 2
    output2_png = f"compare_OR_CICADA_{mc_basename}.png"
    canvas2.SaveAs(output2_png)

    # Write both histograms to ROOT output
    output_root = ROOT.TFile(output_file, "RECREATE")
    hist_orig.Write()
    hist_or.Write()
    output_root.Close()

    print(f"\nSaved 'Trigger Alone' plot as {output1_png}")
    print(f"Saved 'Trigger + CICADA OR' plot as {output2_png}")

# === MAIN SCRIPT ===

mc_files = [
    "/afs/hep.wisc.edu/user/cnee/Wto3Pi/MC_Production/CMSSW_15_0_7/src/ADPaper_CICADA/CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root"
]

data_file = "/afs/hep.wisc.edu/user/cnee/Wto3Pi/CMSSW_15_0_7/src/PU_Run3Winter24GS/L1TTriggerBitsNtuplizer/ADPaperCICADA_150X_mcRun3_2025_realistic_v4_150X_dataRun3_Prompt_v3/CICADA_ZeroBiasRun2024I.root"

for mc_file in mc_files:
    mc_base = os.path.basename(mc_file).replace(".root", "")
    output_file = f"L1T_{mc_base}.root"

    print(f"\n>>> Processing {mc_base}")
    analyze_triggers(mc_file=mc_file, data_file=data_file, output_file=output_file)



