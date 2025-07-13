import ROOT
import numpy as np
import os

# ========================
# Define the triggers to check
# ========================
TRIGGER_LIST = [
    "DST_PFScouting_DoubleMuonNoVtx",
    "DST_PFScouting_DoubleMuonVtx",
    "DST_PFScouting_DoubleMuonVtxMonitorJPsi",
    "DST_PFScouting_DoubleMuonVtxMonitorZ",
    "DST_PFScouting_DoubleEG",
    "DST_PFScouting_JetHT",
    "DST_PFScouting_CICADAVLoose",
    "DST_PFScouting_CICADALoose",
    "DST_PFScouting_CICADAMedium",
    "DST_PFScouting_CICADATight",
    "DST_PFScouting_CICADAVTight",
    "DST_PFScouting_SingleMuon",
    "DST_PFScouting_SinglePhotonEB",
    "DST_PFScouting_ZeroBias"
]

# ========================
# Function to compute efficiencies
# ========================
def compute_trigger_efficiencies(mc_file, triggers, txt_output=None, root_output=None):
    print(f"Opening MC ROOT file: {mc_file}")
    mc_root = ROOT.TFile.Open(mc_file, "READ")
    if not mc_root or mc_root.IsZombie():
        print("Error: Cannot open MC file.")
        return

    mc_tree = mc_root.Get("Events")
    if not mc_tree:
        print("Error: Cannot find 'Events' tree in MC file.")
        return

    efficiencies = {}
    total_events = mc_tree.GetEntries()
    print(f"Total MC events = {total_events}")

    for trig in triggers:
        count = 0
        for entry in mc_tree:
            try:
                if getattr(entry, trig):
                    count += 1
            except Exception:
                continue
        eff = count / total_events if total_events > 0 else 0.0
        efficiencies[trig] = eff

    mc_root.Close()

    # Sort triggers by efficiency
    sorted_triggers = sorted(efficiencies.items(), key=lambda x: x[1], reverse=True)

    # Print results
    print("\n=== Trigger Efficiencies ===")
    for trig, eff in sorted_triggers:
        print(f"{trig:<40}: {eff:.4f}")

    # Optionally save to text file
    if txt_output:
        with open(txt_output, "w") as f:
            for trig, eff in sorted_triggers:
                f.write(f"{trig}: {eff:.4f}\n")
        print(f"\nEfficiencies saved to: {txt_output}")

    # ========================
    # Make and save ROOT histogram
    # ========================
    if root_output:
        print(f"Saving ROOT histogram to: {root_output}")
        n_bins = len(sorted_triggers)
        hist = ROOT.TH1F("trigger_efficiencies", "Trigger Efficiencies", n_bins, 0, n_bins)
        for i, (trig, eff) in enumerate(sorted_triggers):
            hist.SetBinContent(i+1, eff)
            hist.GetXaxis().SetBinLabel(i+1, trig)

        hist.GetYaxis().SetTitle("Efficiency")
        hist.GetXaxis().LabelsOption("v")
        hist.GetXaxis().SetLabelSize(0.025)
        hist.SetLineColor(ROOT.kBlue + 2)
        hist.SetLineWidth(2)

        # Draw and save to canvas as PNG
        canvas = ROOT.TCanvas("canvas", "Trigger Efficiencies", 1000, 600)
        canvas.SetBottomMargin(0.35)
        hist.SetTitle(f"Trigger Efficiencies (MC: {os.path.basename(mc_file)})")
        hist.Draw("HIST")
        png_name = root_output.replace(".root", ".png")
        canvas.SaveAs(png_name)
        print(f"Also saved histogram plot as: {png_name}")

        # Write histogram to ROOT file
        out_root = ROOT.TFile.Open(root_output, "RECREATE")
        hist.Write()
        out_root.Close()

# ========================
# MAIN
# ========================

mc_input_file = "/afs/hep.wisc.edu/user/cnee/Wto3Pi/MC_Production/CMSSW_15_0_7/src/ADPaper_CICADA/CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root"       
output_txt_file = "DSTTriggers_Means.txt"
output_root_file = "DST_HIG-RunIISummer20UL17HLT_2025v11-13144.root"

compute_trigger_efficiencies(
    mc_input_file,
    TRIGGER_LIST,
    txt_output=output_txt_file,
    root_output=output_root_file
)
