void Plot_CICADA_Overlay_All() {
    gStyle->SetOptStat(0); // Disable stat box

    std::vector<std::string> dirs = {
        "EXO_2_MS-7_ctaus-10",
        "EXO_2_MS-7_ctaus-1000",
        "EXO_2_MS-7_ctaus-100000",
        "EXO_2_MS-55_ctaus-10",
        "EXO_2_MS-55_ctaus-1000",
        "EXO_2_MS-55_ctaus-100000",
        "ZeroBiasRun2024I"
    };

    std::vector<int> colors = {kGreen+1, kOrange+1, kOrange, kRed, kViolet, kPink+1, kBlue};

    TCanvas* c = new TCanvas("c", "CICADA Overlay Comparison", 1000, 1200);
    c->Divide(1, 2);

    // Updated legend position (top right)
    TLegend* leg2024 = new TLegend(0.68, 0.55, 0.95, 0.89);
    TLegend* leg2025 = new TLegend(0.68, 0.55, 0.95, 0.89);
    leg2024->SetBorderSize(0);
    leg2025->SetBorderSize(0);
    leg2024->SetTextSize(0.042);
    leg2025->SetTextSize(0.042);

    c->cd(1); gPad->SetLogy(); gPad->SetMargin(0.12, 0.05, 0.1, 0.1);
    TH1* first2024 = nullptr;

    c->cd(2); gPad->SetLogy(); gPad->SetMargin(0.12, 0.05, 0.12, 0.1);
    TH1* first2025 = nullptr;

    for (size_t i = 0; i < dirs.size(); ++i) {

        std::string dir = dirs[i];
        std::string filePath;
        std::string label;
        std::string prefix = "EXO_2_";
        if (dir != "ZeroBiasRun2024I") {
            label = dir.substr(prefix.length());
            filePath = dir + "/" + label + "_Plot_Histos.root";
        } else {
            label = "ZeroBiasRun2024I";
            filePath = "/afs/hep.wisc.edu/home/cnee/Wto3Pi/CMSSW_15_1_0_pre1/src/check_ROOT_file/ZeroBiasRun2024I/ZeroBiasRun2024I_Plot_Histos.root";
        }

        TFile* f = TFile::Open(filePath.c_str());
        if (!f || f->IsZombie()) {
            std::cerr << "Warning: could not open file " << filePath << std::endl;
            continue;
        }

        TH1F* h2024 = (TH1F*)f->Get("h_cicada2024");
        TH1F* h2025 = (TH1F*)f->Get("h_cicada2025");
        if (!h2024 || !h2025) {
            std::cerr << "Warning: histograms not found in " << filePath << std::endl;
            continue;
        }

        // Rebin histograms by factor of 4
        h2024->Rebin(4);
        h2025->Rebin(4);

        // Normalize
        h2024->Scale(1.0 / h2024->Integral());
        h2025->Scale(1.0 / h2025->Integral());

        int color = colors[i % colors.size()];
        h2024->SetLineColor(color); h2024->SetLineWidth(2);
        h2025->SetLineColor(color); h2025->SetLineWidth(2);

        h2024->SetLineStyle(10); 
        h2025->SetLineStyle(10); 

        c->cd(1);
        if (!first2024) {
            h2024->SetTitle("CICADA Anomaly Score (v2024);CICADA Score;a.u.");
            h2024->Draw("HIST");
            first2024 = h2024;
        } else {
            h2024->Draw("HIST SAME");
        }

        c->cd(2);
        if (!first2025) {
            h2025->SetTitle("CICADA Anomaly Score (v2025a);CICADA Score;a.u.");
            h2025->Draw("HIST");
            first2025 = h2025;
        } else {
            h2025->Draw("HIST SAME");
        }

        leg2024->AddEntry(h2024, label.c_str(), "l");
        leg2025->AddEntry(h2025, label.c_str(), "l");
    }

    c->cd(1); leg2024->Draw();
    c->cd(2); leg2025->Draw();
    c->SaveAs("CICADA_AnomalyScore_Overlay_All_LogY.png");
}



