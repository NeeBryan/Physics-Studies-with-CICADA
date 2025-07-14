import uproot
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# --------------------------------------
# CONFIGURATION
# --------------------------------------
signal_files = {
    "Wto3Pi": "/afs/hep.wisc.edu/home/cnee/Wto3Pi/MC_Production/CMSSW_15_0_7/src/ADPaper_CICADA/CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root"
}

data_file = "./ADPaperCICADA/CICADA_ZeroBiasRun2024I.root"

# The single TTree name for BOTH signal and data
events_tree = "Events"

# Branches for HT sum extraction
branches_needed = [
    "nL1EtSum", "L1EtSum_bx", "L1EtSum_etSumType", "L1EtSum_pt"
]

# List of L1 trigger bits to check (these are all stored as leaves in "Events")
trigger_bits_to_check = [
    "DST_PFScouting_CICADAVLoose",
    "L1_ETMHF90_HTT60er",
    "L1_ETMHF90_SingleJet60er2p5_dPhi_Min2p1",
    "L1_SingleEG60",
    "L1_ETMHF100_HTT60er",
    "L1_Mu6_HTT240er",
    "L1_SingleIsoEG30er2p5",
    "L1_ETMHF110_HTT60er",
    "L1_DoubleMu0_Upt6_IP_Min1_Upt4",
    "L1_SingleIsoEG30er2p1",
    "L1_DoubleEG11_er1p2_dR_Max0p6",
    "L1_LooseIsoEG22er2p1_IsoTau26er2p1_dR_Min0p3",
    "L1_SingleIsoEG32er2p5",
    "L1_DoubleIsoTau34er2p1",
    "L1_LooseIsoEG24er2p1_IsoTau27er2p1_dR_Min0p3",
    "L1_SingleIsoEG32er2p1",
    "L1_DoubleEG_25_12_er2p5",
    "L1_DoubleEG_LooseIso18_LooseIso12_er1p5",
    "L1_DoubleMu0_Upt15_Upt7",
    "L1_DoubleEG_LooseIso20_LooseIso12_er1p5",
    "L1_DoubleEG_LooseIso22_LooseIso12_er1p5"
]

# --------------------------------------
# LOAD HT SUMS PER EVENT
# --------------------------------------
def extract_ht_per_event(filename):
    """
    From the Events TTree, extract the HT sum per event using:
      - BX == 0
      - etSumType == 1 (which is HT)
    """
    with uproot.open(filename)[events_tree] as tree:
        nL1EtSum = tree["nL1EtSum"].array(library="np")
        bx = tree["L1EtSum_bx"].array(library="np")
        etSumType = tree["L1EtSum_etSumType"].array(library="np")
        pt = tree["L1EtSum_pt"].array(library="np")

    per_event_ht = []
    for i in range(len(nL1EtSum)):
        count = nL1EtSum[i]
        if count == 0:
            per_event_ht.append(0.0)
            continue
        bx_vals = bx[i][:count]
        type_vals = etSumType[i][:count]
        pt_vals = pt[i][:count]
        mask = (bx_vals == 0) & (type_vals == 1)
        if np.any(mask):
            ht_max = np.max(pt_vals[mask])
            per_event_ht.append(ht_max)
        else:
            per_event_ht.append(0.0)
    return np.array(per_event_ht)

# --------------------------------------
# LOAD TRIGGER BITS FROM EVENTS TREE
# --------------------------------------
def load_trigger_bits(filename, trigger_bits):
    """
    From the Events TTree, load the specified trigger bits (all stored as leaves).
    """
    with uproot.open(filename)[events_tree] as tree:
        data = {bit: tree[bit].array(library="np") for bit in trigger_bits}
    return data

# --------------------------------------
# ROC PLOTTING
# --------------------------------------
def plot_trigger_roc(y_true, y_scores, trigger_name):
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    auc_val = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"AUC = {auc_val:.3f}", color="blue", lw=2)
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC for Trigger: {trigger_name}")
    plt.legend(loc="lower right")
    plt.grid()
    outname = f"ROC_{trigger_name}.png"
    plt.tight_layout()
    plt.savefig(outname)
    plt.close()
    print(f"Saved ROC curve for {trigger_name} to {outname}")

# --------------------------------------
# MAIN EXECUTION
# --------------------------------------
for signal_label, signal_path in signal_files.items():

    # Load HT sums
    signal_ht = extract_ht_per_event(signal_path)
    data_ht = extract_ht_per_event(data_file)

    # Load Trigger Bits (now both come from "Events" tree)
    signal_triggers = load_trigger_bits(signal_path, trigger_bits_to_check)
    data_triggers = load_trigger_bits(data_file, trigger_bits_to_check)

    print(f"\n[INFO] Signal events: {len(signal_ht)} | Data events: {len(data_ht)}")

    # For each trigger bit:
    for bit in trigger_bits_to_check:
        print(f"\n[INFO] Processing trigger: {bit}")

        # Mask HT only for events where trigger fired
        sig_mask = (signal_triggers[bit] > 0.001)
        data_mask = (data_triggers[bit] > 0.001)

        if not np.any(sig_mask) or not np.any(data_mask):
            print(f"  [WARNING] No events fired for {bit} in either signal or data!")
            continue

        signal_scores = signal_ht[sig_mask]
        data_scores = data_ht[data_mask]

        # Combine
        scores = np.concatenate([signal_scores, data_scores])
        labels = np.concatenate([np.ones_like(signal_scores), np.zeros_like(data_scores)])

        # Plot ROC
        plot_trigger_roc(labels, scores, bit)

    # --------------------------------------------------------
    # NEW SECTION: Global HT ROC curve (not trigger dependent)
    # --------------------------------------------------------
    print("\n[INFO] Making overall HT ROC curve using *all* events (no triggers).")

    # Combine all HT values
    all_scores = np.concatenate([signal_ht, data_ht])
    all_labels = np.concatenate([np.ones_like(signal_ht), np.zeros_like(data_ht)])

    # Compute ROC
    fpr, tpr, _ = roc_curve(all_labels, all_scores)
    auc_val = auc(fpr, tpr)

    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"AUC = {auc_val:.3f}", color="darkred", lw=2)
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"Global HT ROC Curve\n{signal_label} vs Data")
    plt.legend(loc="lower right")
    plt.grid()
    outname = f"ROC_HT_Global_{signal_label}.png"
    plt.tight_layout()
    plt.savefig(outname)
    plt.close()
    print(f"Saved global HT ROC curve to {outname}")


