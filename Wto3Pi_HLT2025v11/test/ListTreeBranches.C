/**
 * @file ListTreeBranches.cpp
 * @brief Utility function to inspect the structure of TTrees in a ROOT file.
 *
 * This function opens a specified ROOT file, searches for all TTrees inside it,
 * and lists each tree's branches and leaves (including their types). The output
 * is written to a text file named `tree_structure.txt`.
 *
 * This is particularly useful when working with unfamiliar ROOT files, e.g., to
 * explore what data is stored in CMS NanoAOD, HLT output, or custom ntuples.
 *
 * Example usage (in a compiled ROOT macro or C++ script):
 *
 *   root -b -q ListTreeBranches.C
 *
 * Make sure the ROOT file name is correctly set inside the function.
 */

void ListTreeBranches() {
    const char* filename = "CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root";
    TFile *file = TFile::Open(filename, "READ");
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Cannot open ROOT file " << filename << std::endl;
        return;
    }

    std::ofstream out("CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144_tree_structure.txt");
    if (!out.is_open()) {
        std::cerr << "Error: Cannot open output file!" << std::endl;
        return;
    }

    out << "ROOT File: " << filename << "\n\n";

    TIter next(file->GetListOfKeys());
    TKey *key;

    while ((key = (TKey*)next())) {
        TObject *obj = key->ReadObj();
        if (obj->InheritsFrom("TTree")) {
            TTree *tree = (TTree*)obj;
            out << "Tree: " << tree->GetName() << "\n";

            TObjArray *branches = tree->GetListOfBranches();
            for (int i = 0; i < branches->GetEntries(); ++i) {
                TBranch *branch = (TBranch*)branches->At(i);
                out << "  Branch: " << branch->GetName() << "\n";

                TObjArray *leaves = branch->GetListOfLeaves();
                for (int j = 0; j < leaves->GetEntries(); ++j) {
                    TLeaf *leaf = (TLeaf*)leaves->At(j);
                    out << "    Leaf: " << leaf->GetName()
                        << " (Type: " << leaf->GetTypeName() << ")\n";
                }
            }
            out << "\n";
        }
    }

    out.close();
    file->Close();

    std::cout << "Tree structure written to tree_structure.txt\n";
}

