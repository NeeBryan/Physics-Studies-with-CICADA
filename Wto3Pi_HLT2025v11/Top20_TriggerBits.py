import ROOT
import numpy as np

def analyze_root_file(input_file, output_file):
    # Open the ROOT file
    root_file = ROOT.TFile.Open(input_file, "READ")
    if not root_file or root_file.IsZombie():
        print("Error: Cannot open file.")
        return
    
    # Get the TDirectory
    directory = root_file.Get("L1TTriggerBitsNtuplizer")
    if not directory:
        print("Error: No such directory found in file.")
        return
    
    # Get the TTree
    tree = directory.Get("L1TTriggerBits")
    if not tree:
        print("Error: No TTree named 'L1TTriggerBits' found in directory.")
        return
    
    # Get the list of branches
    branch_means = {}

    for branch in tree.GetListOfBranches():
        branch_name = branch.GetName()
        
        # Exclude specific branches
        # if branch_name in ["run", "evt", "lumi"] or "prescale" in branch_name:
        #     continue

        # Exclude specific branches
        if "prescale" not in branch_name:
            continue
        
        values = []
        
        for entry in tree:
            try:
                value = float(getattr(entry, branch_name))  # Ensure numeric conversion
                values.append(value)
            except (ValueError, TypeError):
                print(f"Skipping non-numeric branch: {branch_name}")
                break  # If we find non-numeric values, we skip this branch
        
        if values:  # Only process branches with numeric data
            prescale_value = np.mean(values)
            branch_means[branch_name] = prescale_value
    
    # # Sort branches by mean value and select the top 20
    # top_branches = sorted(branch_means.items(), key=lambda x: x[1], reverse=True)[:20]
    prescale_1_branches = 
    
    # Create a histogram with 20 bins
    hist = ROOT.TH1F("top20_means", "Top 20 Branch Means", 20, 0, 20)
    
    # Fill histogram
    for i, (branch_name, mean_value) in enumerate(top_branches):
        hist.SetBinContent(i + 1, mean_value)
        hist.GetXaxis().SetBinLabel(i + 1, branch_name)
    
    # Save histogram to output file
    output_root = ROOT.TFile(output_file, "RECREATE")
    hist.Write()
    output_root.Close()
    root_file.Close()
    
    print(f"Histogram saved to {output_file}")

# Example usage
analyze_root_file("HIG_2_CICADA_ntuple_Updated.root", "output.root")
