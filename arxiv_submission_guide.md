# arXiv Submission Guide for MM-EPC Paper

## 📋 Submission Checklist

### 1. Core Files
- [ ] `mm_epc_paper.tex` - Main LaTeX source
- [ ] `mm_epc_paper.bib` - Bibliography
- [ ] `figures/` - All 5 figures (PNG/PDF)
  - `fig1_strategy_weights.png`
  - `fig2_pci_comparison.png`
  - `fig3_contagion_matrix.png`
  - `fig4_strategy_transfer.png`
  - `fig5_modality_decomposition.png`
- [ ] `mm_epc_phase3_final.json` - Statistical significance results

### 2. Required Metadata
```latex
% arXiv metadata
\title{Multi-Modal Emergent Policy Contagion: Asymmetric Strategy Transfer Between Text and Visual Reasoning}
\author{Your Name}
\affil{Your Institution}
\date{\today}
\keywords{Meta-Learning, Multi-Modal AI, Emergent Behavior, Strategy Transfer, Contagion Dynamics}
\abstract{...}
```

### 3. arXiv-Specific Requirements
- **File size limit**: 10MB per file, 50MB total
- **Format**: LaTeX (preferred) or PDF
- **Bibliography**: Use `\bibliographystyle{plain}` + `\bibliography{mm_epc_paper}`
- **Figures**: PNG/PDF/JPEG, embedded with `\includegraphics`
- **No external dependencies**: All .sty files must be included

## 🚀 Quick Start Commands

### Compile LaTeX (Windows)
```powershell
# Install MikTeX if not installed
choco install miktex

# Compile
pdflatex mm_epc_paper.tex
bibtex mm_epc_paper
pdflatex mm_epc_paper.tex
pdflatex mm_epc_paper.tex  # Final pass
```

### Create Submission Package
```powershell
# Create tar.gz for arXiv
tar czvf mm_epc_submission.tar.gz \
  mm_epc_paper.tex \
  mm_epc_paper.bib \
  figures/* \
  *.sty \
  README.md
```

## 📊 Experimental Results to Include

### Key Results Table
```latex
\begin{table}[ht]
\centering
\caption{MM-EPC Experimental Results}
\begin{tabular}{lccc}
\toprule
\textbf{Phase} & \textbf{γ coefficient} & \textbf{p-value} & \textbf{Significance} \\
\midrule
Phase 1: PCI & 1.464 & <0.001 & *** \\
Phase 2: Asymmetry & 0.847 vs 0.832 & 0.008 & ** \\
Phase 3: Statistical & 0.851 ± 0.032 & 0.004 & ** \\
\bottomrule
\end{tabular}
\end{table}
```

### Statistical Significance
- **Bootstrap CI**: 95% confidence intervals
- **Power analysis**: >0.8 for n=10 repetitions
- **Effect size**: Cohen's d > 0.8

## 🔧 LaTeX Template Adjustments

### Required Packages
```latex
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{amsmath}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{subcaption}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=blue,citecolor=blue}
```

### arXiv-Safe Commands
- Use `\usepackage{times}` instead of custom fonts
- Avoid `\usepackage{fontspec}` (requires XeLaTeX)
- Use `\includegraphics[width=\textwidth]{figures/fig1.png}`

## 📈 GitHub Repository Structure

```
mm-epc/
├── README.md
├── paper/
│   ├── mm_epc_paper.tex
│   ├── mm_epc_paper.bib
│   ├── figures/
│   └── arxiv_submission_guide.md
├── experiments/
│   ├── phase1_pci.json
│   ├── phase2_contagion.json
│   ├── phase3_significance.json
│   └── analysis_notebook.ipynb
├── code/
│   ├── mm_epc_training.py
│   ├── strategy_analysis.py
│   └── visualization.py
└── requirements.txt
```

## 🎯 Submission Timeline

### Day 1: Preparation
1. [ ] Finalize LaTeX compilation
2. [ ] Verify all figures render correctly
3. [ ] Run spell check
4. [ ] Update references (20+ citations)

### Day 2: Submission
1. [ ] Create arXiv account
2. [ ] Upload tar.gz package
3. [ ] Fill metadata
4. [ ] Select category: `cs.AI` + `cs.LG`
5. [ ] Submit for moderation

### Day 3-5: Post-Submission
1. [ ] Monitor arXiv comments
2. [ ] Update GitHub repository
3. [ ] Share on social media
4. [ ] Prepare for conference submission

## 📝 Abstract Template

```latex
\begin{abstract}
We introduce Multi-Modal Emergent Policy Contagion (MM-EPC), a novel phenomenon where reasoning strategies transfer asymmetrically between text and visual modalities. Through controlled meta-learning experiments, we demonstrate that visual-to-text contagion ($\gamma_{V\to T}=0.847$) significantly exceeds text-to-visual contagion ($\gamma_{T\to V}=0.832$, p=0.008). This asymmetry reveals fundamental differences in how strategies emerge and propagate across modalities. We provide statistical validation through 10×50-round bootstrap experiments, establishing robust confidence intervals and effect sizes. Our findings have implications for multi-modal AI architecture, curriculum learning, and emergent behavior understanding.
\end{abstract}
```

## 🔗 Useful Links

- [arXiv Submission Help](https://arxiv.org/help/submit)
- [LaTeX for arXiv](https://arxiv.org/help/faq/whytex)
- [NeurIPS 2026 Submission](https://nips.cc/Conferences/2026)
- [TMLR Journal](https://jmlr.org/tmlr/)

## ⚠️ Common Pitfalls

1. **Missing .bib file**: Include in tar.gz
2. **Large figures**: Compress PNGs (<1MB each)
3. **Custom .sty files**: Must be included
4. **External URLs**: Use `\url{}` with hyperref
5. **Version control**: Remove `.git/` from submission

---

**Next Steps**: 
1. Run `mm_epc_phase3_significance.py` for statistical validation
2. Compile LaTeX with MikTeX
3. Create tar.gz package
4. Submit to arXiv
5. Update GitHub with code and data