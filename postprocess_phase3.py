"""
Post-processing: read phase3 results, update statistical_table.tex, recompile paper.
"""
import json, os, sys, re, shutil, subprocess
import numpy as np

RESULT_FILE = r"C:\Users\Administrator\Desktop\aettl-research\experiments\mm_epc_phase3_final.json"
TABLE_FILE = r"C:\Users\Administrator\Desktop\aettl-research\experiments\statistical_table.tex"
PAPER_DIR = r"C:\Users\Administrator\Desktop\aettl-research\paper"
PDFLATEX = r"C:\Users\Administrator\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"

def main():
    print("=" * 60)
    print("Phase 3 Post-Processing")
    print("=" * 60)

    # 1. Load results
    with open(RESULT_FILE, encoding='utf-8-sig') as f:
        data = json.load(f)
    stats = data["statistical_analysis"]
    summary = data["summary"]

    print(f"\nResults loaded: {len(data['raw_results'])} repetitions")
    print(f"  γ_T→V: {summary['gamma_TV_mean']:.4f} ± {summary['gamma_TV_std']:.4f}")
    print(f"  γ_V→T: {summary['gamma_VT_mean']:.4f} ± {summary['gamma_VT_std']:.4f}")
    print(f"  Δγ: {summary['mean_difference']:.4f}")
    print(f"  p-value: {summary['p_value']:.4f}")
    print(f"  Significant: {summary['significant']}")

    # 2. Generate updated statistical table
    ci_str = f"[{stats['ci_95'][0]:.4f}, {stats['ci_95'][1]:.4f}]"
    p_str = f"{stats['p_value']:.4f}"
    sig_mark = "***" if stats['p_value'] < 0.001 else ("**" if stats['p_value'] < 0.01 else ("*" if stats['p_value'] < 0.05 else ""))

    new_table = f"""\\begin{{table}}[ht]
\\centering
\\caption{{Statistical Validation of Cross-Modal Asymmetric Contagion}}
\\label{{tab:statistical}}
\\begin{{tabular}}{{lccc}}
\\toprule
\\textbf{{Metric}} & \\textbf{{Value}} & \\textbf{{95\\% CI}} & \\textbf{{Significance}} \\\\
\\midrule
$\\gamma_{{T\\to V}}$ (Text $\\to$ Visual) & {summary['gamma_TV_mean']:.4f} $\\pm$ {summary['gamma_TV_std']:.4f} & [{stats['mean_gamma_TV'] - 1.96*stats['std_gamma_TV']:.4f}, {stats['mean_gamma_TV'] + 1.96*stats['std_gamma_TV']:.4f}] & --- \\\\
$\\gamma_{{V\\to T}}$ (Visual $\\to$ Text) & {summary['gamma_VT_mean']:.4f} $\\pm$ {summary['gamma_VT_std']:.4f} & [{stats['mean_gamma_VT'] - 1.96*stats['std_gamma_VT']:.4f}, {stats['mean_gamma_VT'] + 1.96*stats['std_gamma_VT']:.4f}] & --- \\\\
\\midrule
Asymmetry ($\\Delta\\gamma$) & {summary['mean_difference']:.4f} $\\pm$ {stats['std_gamma_VT'] + stats['std_gamma_TV']:.4f} & {ci_str} & p = {p_str} {sig_mark} \\\\
\\bottomrule
\\end{{tabular}}

\\vspace{{4pt}}
\\begin{{minipage}}{{\\textwidth}}
\\footnotesize
\\textit{{Note.}} Real API experiment with $N={len(data['raw_results'])}$ independent repetitions ({data['rounds_per_phase']} rounds each, {data['total_llm_calls']} total GPT-4o evaluation calls). Bootstrap analysis with 10,000 resamples. One-sided test: $H_0: \\gamma_{{V\\to T}} \\leq \\gamma_{{T\\to V}}$. $^{{*}}p<0.05$, $^{{**}}p<0.01$, $^{{***}}p<0.001$.
\\end{{minipage}}
\\end{{table}}"""

    # Backup old table
    backup = TABLE_FILE.replace('.tex', '_backup.tex')
    if os.path.exists(TABLE_FILE):
        shutil.copy2(TABLE_FILE, backup)
        print(f"\nBacked up old table to: {backup}")

    with open(TABLE_FILE, 'w', encoding='utf-8') as f:
        f.write(new_table)
    print(f"Updated: {TABLE_FILE}")

    # 3. Recompile paper (original)
    print("\nRecompiling paper...")
    os.chdir(PAPER_DIR)
    for i in range(3):
        subprocess.run([PDFLATEX, "-interaction=nonstopmode", "mm_epc_paper.tex"],
                       capture_output=True)
    pdf_path = os.path.join(PAPER_DIR, "mm_epc_paper.pdf")
    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"Paper compiled: {pdf_path} ({size_kb:.0f} KB)")
    else:
        print("ERROR: PDF not created")

    # 4. Update blind version too
    print("\nRecompiling blind version...")
    for i in range(3):
        subprocess.run([PDFLATEX, "-interaction=nonstopmode", "mm_epc_paper_blind.tex"],
                       capture_output=True)
    blind_pdf = os.path.join(PAPER_DIR, "mm_epc_paper_blind.pdf")
    if os.path.exists(blind_pdf):
        size_kb = os.path.getsize(blind_pdf) / 1024
        print(f"Blind version compiled: {blind_pdf} ({size_kb:.0f} KB)")

    # 5. Create completion marker
    marker = r"C:\Users\Administrator\Desktop\aettl-research\experiments\postprocess_done.txt"
    with open(marker, 'w') as f:
        f.write("Post-processing complete\n")
        f.write(f"γ_T→V: {summary['gamma_TV_mean']:.4f}\n")
        f.write(f"γ_V→T: {summary['gamma_VT_mean']:.4f}\n")
        f.write(f"p-value: {p_str}\n")

    print(f"\n{'='*60}")
    print("Post-processing complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()