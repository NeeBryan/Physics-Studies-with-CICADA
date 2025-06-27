import uproot
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# -----------------------------
# Configuration
# -----------------------------
signal_files = {
    "GluGluHToGG":      "./GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8/CICADA_GluGluHToGG_M-125_TuneCP5_13p6TeV_powheg-pythia8.root",
    "GluGluHToTauTau":  "./GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8/CICADA_GluGluHToTauTau_M-125_TuneCP5_13p6TeV_powheg-pythia8.root",
    "HTo2LL4b":         "./HTo2LongLivedTo4b_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV_pythia8/CICADA_HTo2LongLivedTo4b_MH-125_MFF-12_CTau-900mm_TuneCP5_13p6TeV_pythia8.root",
    "TTbar":            "./TT_TuneCP5_13p6TeV_powheg-pythia8/CICADA_TT_TuneCP5_13p6TeV_powheg-pythia8.root",
    "VBFHToTauTau":     "./VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8/CICADA_VBFHto2B_M-125_TuneCP5_13p6TeV_powheg-pythia8.root",
    "VBFHto2B":         "./VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8/CICADA_VBFHToTauTau_M125_TuneCP5_13p6TeV_powheg-pythia8.root",
    "ZprimeToTauTau":   "./ZprimeToTauTau_M-4000_TuneCP5_tauola_13p6TeV-pythia8/CICADA_ZprimeToTauTau_M-4000_TuneCP5_tauola_13p6TeV-pythia8.root",
    "ZZ":               "./ZZ_TuneCP5_13p6TeV_pythia8/CICADA_ZZ_TuneCP5_13p6TeV_pythia8.root",
    "Wto3Pi":           "../PU_Run3Winter24GS/HIG-RunIISummer20UL17HLT-13144_CICADA.root"
}

zerobias_file = "./ZeroBiasRun2024I/CICADA_ZeroBiasRun2024I.root"
tree_name = "Events"
branch_2024 = "CICADA2024_CICADAScore"
branch_2025 = "CICADA2025_CICADAScore"

# -----------------------------
# Helper Functions
# -----------------------------
def load_branch(file_path, branch):
    try:
        with uproot.open(file_path)[tree_name] as tree:
            return tree[branch].array(library="np")
    except Exception as e:
        print(f"[ERROR] Failed to load {branch} from {file_path}:\n  {e}")
        return np.array([])

def collect_scores(branch):
    signal_scores = []
    for name, path in signal_files.items():
        score = load_branch(path, branch)
        signal_scores.append(score)
    signal_scores = np.concatenate(signal_scores)

    # Label: 1 for signal
    y_signal = np.ones_like(signal_scores)

    # Load background (ZeroBias)
    background_scores = load_branch(zerobias_file, branch)
    y_bkg = np.zeros_like(background_scores)

    # Combine
    scores = np.concatenate([signal_scores, background_scores])
    labels = np.concatenate([y_signal, y_bkg])
    return scores, labels

def plot_roc(y_true, y_scores, label, color, outname):
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    auc_val = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"AUC = {auc_val:.3f}", color=color, lw=2)
    plt.plot([0, 1], [0, 1], linestyle="--", color="gray")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(f"ROC Curve: {label}")
    plt.legend(loc="lower right")
    plt.grid()
    plt.savefig(outname)
    plt.close()
    print(f"Saved ROC to {outname}")

def collect_roc_for_all_signals(branch):
    roc_data = {}
    background = load_branch(zerobias_file, branch)
    for name, path in signal_files.items():
        signal = load_branch(path, branch)
        if len(signal) == 0 or len(background) == 0:
            continue
        y_true = np.concatenate([np.ones_like(signal), np.zeros_like(background)])
        y_score = np.concatenate([signal, background])
        fpr, tpr, _ = roc_curve(y_true, y_score)
        roc_auc = auc(fpr, tpr)
        roc_data[name] = (fpr, tpr, roc_auc)
    return roc_data

import matplotlib.pyplot as plt

def plot_all_rocs(roc_data, title, outname):
    # Fixed color map in desired legend order
    color_map = {
        "GluGluHToGG":        "limegreen",
        "GluGluHToTauTau":    "orange",
        "HTo2LL4b":           "gold",
        "TTbar":              "red",
        "VBFHto2B":           "purple",
        "VBFHToTauTau":       "pink",
        "ZprimeToTauTau":     "yellowgreen",
        "ZZ":                 "brown",
        "ZeroBiasRun2024I":   "blue",
        "Wto3Pi":             "deepskyblue",
    }

    plt.figure(figsize=(8, 6))
    
    for label in color_map:
        if label not in roc_data:
            continue  # Skip missing data
        fpr, tpr, auc_val = roc_data[label]
        plt.plot(fpr, tpr, label=f"{label} (AUC={auc_val:.2f})", color=color_map[label], lw=2)

    plt.plot([0, 1], [0, 1], "k--", lw=1)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.grid()
    plt.legend(loc="lower right", fontsize="small")
    plt.tight_layout()
    plt.savefig(outname)
    plt.close()
    print(f"Saved ROC plot to {outname}")


# -----------------------------
# Main Execution
# -----------------------------

# 2024 ROC
y_scores_2024, y_true_2024 = collect_scores(branch_2024)
plot_roc(y_true_2024, y_scores_2024, "CICADA 2024 Score vs ZeroBias", "blue", "roc_2024_vs_zerobias.png")

# 2025 ROC
y_scores_2025, y_true_2025 = collect_scores(branch_2025)
plot_roc(y_true_2025, y_scores_2025, "CICADA 2025 Score vs ZeroBias", "red", "roc_2025_vs_zerobias.png")

roc_2024 = collect_roc_for_all_signals(branch_2024)
plot_all_rocs(roc_2024, "CICADA 2024: Signal vs ZeroBias", "roc_signals_vs_zerobias_2024.png")

roc_2025 = collect_roc_for_all_signals(branch_2025)
plot_all_rocs(roc_2025, "CICADA 2025: Signal vs ZeroBias", "roc_signals_vs_zerobias_2025.png")
