void ListTreeBranches() {
    const char* filename = "HIG-RunIISummer20UL17HLT-13144_CICADA.root";
    TFile *file = TFile::Open(filename, "READ");
    if (!file || file->IsZombie()) {
        std::cerr << "Error: Cannot open ROOT file " << filename << std::endl;
        return;
    }

    std::ofstream out("tree_structure.txt");
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

