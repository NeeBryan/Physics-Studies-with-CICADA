void Plot() {
    TFile* file = TFile::Open("CICADA_HIG-RunIISummer20UL17HLT_2025v11-13144.root");
    TTree* tree = (TTree*)file->Get("Events");

    // Pileup branch
    Int_t nPU = 0;
    Float_t nTruePU = 0;
    tree->SetBranchAddress("Pileup_nPU", &nPU);
    tree->SetBranchAddress("Pileup_nTrueInt", &nTruePU);

    // CICADA score branches
    Float_t cicada2024 = 0;
    Float_t cicada2025 = 0;
    tree->SetBranchAddress("CICADA2024_CICADAScore", &cicada2024);
    tree->SetBranchAddress("CICADA2025_CICADAScore", &cicada2025);

    // CICADA scouting loose Trigger bits
    Bool_t cicada_scouting_loose;
    tree->SetBranchAddress("DST_PFScouting_CICADALoose", &cicada_scouting_loose);

    // Histograms
    TH1F* h_nPU       = new TH1F("h_nPU", "Number of Pileup Interactions (Wto3Pi_HLT2025v11)", 100, 0, 100);
    TH1F* h_nTruePU       = new TH1F("h_nTruePU", "Number of True Pileup Interactions (Wto3Pi_HLT2025v11)",  100, 0, 100);
    TH1F* h_cicada2024 = new TH1F("h_cicada2024", "CICADA2024 Score (Wto3Pi_HLT2025v11)", 256, 0, 256);
    TH1F* h_cicada2025 = new TH1F("h_cicada2025", "CICADA2025 Score (Wto3Pi_HLT2025v11)", 256, 0, 256);
    TH1F* h_cicada_scouting_loose = new TH1F("h_cicada_scouting_loose", "CICADA Scouting Loose Trigger Bits (Wto3Pi_HLT2025v11)", 10, -5, 5);

    // Fill histos
    Long64_t nentries = tree->GetEntries();
    for (Long64_t i = 0; i < nentries; ++i) {
        tree->GetEntry(i);
        h_nPU->Fill(nPU);
        h_nTruePU->Fill(nTruePU);
        h_cicada2024->Fill(cicada2024);
        h_cicada2025->Fill(cicada2025);
        h_cicada_scouting_loose->Fill(cicada_scouting_loose);
    }

    // Plot
    TCanvas* c1 = new TCanvas("c1", "Pileup", 800, 600);
    h_nPU->Draw();
    c1->SaveAs("Wto3Pi_HLT2025v11_Pileup_nPU.png");

    TCanvas* c2 = new TCanvas("c2", "CICADA 2024 Score", 800, 600);
    h_cicada2024->Draw();
    c2->SaveAs("Wto3Pi_HLT2025v11_CICADA2024_Score.png");

    TCanvas* c3 = new TCanvas("c3", "CICADA 2025 Score", 800, 600);
    h_cicada2025->Draw();
    c3->SaveAs("Wto3Pi_HLT2025v11_CICADA2025_Score.png");

    TCanvas* c4 = new TCanvas("c4", "True Pileup", 800, 600);
    h_nTruePU->Draw();
    c4->SaveAs("Wto3Pi_HLT2025v11_Pileup_nTrueInt.png");

    TCanvas* c5 = new TCanvas("c4", "CICADA Scouting Loose", 800, 600);
    h_cicada_scouting_loose->Draw();
    c5->SaveAs("Wto3Pi_HLT2025v11_DST_PFScouting_CICADALoose.png");

    TFile* outfile = new TFile("Wto3Pi_HLT2025v11_Plot_Histos.root", "RECREATE");
    h_nPU->Write();
    h_nTruePU->Write();
    h_cicada2024->Write();
    h_cicada2025->Write();
    h_cicada_scouting_loose->Write();
    outfile->Close();

    std::cout << "Histograms saved to Wto3Pi_HLT2025v11_Plot_Histos.root" << std::endl;
}



