# MM-EPC Experiment Code

This repository contains the code for reproducing the experiments in the paper **"Multimodal Evaluator Preference Collapse: Cross-Modal Contagion in Self-Evolving Agents"**.

## Core Experiment Files

### `mm_epc_phase1.py`
- **Purpose**: Phase 1 - Baseline preference collapse measurement (PCI calculation)
- **Input**: Text-only and multimodal evaluation tasks
- **Output**: Preference Collapse Index (PCI) values for GPT-4o vs text-only models

### `mm_epc_contagion.py`
- **Purpose**: Phase 2 - Cross-modal contagion experiment
- **Input**: Text and visual evaluator pairs in iterative rounds
- **Output**: Contagion matrix Γ and asymmetry metrics

### `mm_epc_phase3_significance.py`
- **Purpose**: Phase 3 - Real-world significance validation
- **Input**: 2000 real API calls to GPT-4o
- **Output**: Statistical significance of observed effects

### `statistical_bootstrap.py`
- **Purpose**: Bootstrap analysis for statistical validation
- **Input**: Simulated independent experiments (N=10, 50 rounds each)
- **Output**: Confidence intervals, p-values, effect sizes

## Data Files

### `experiments/mm_epc_phase3_bootstrap.json`
Contains the bootstrap analysis results:
- p-value: 0.0002
- Cohen's d: 1.30
- Achieved power: 0.9727
- 95% confidence intervals for γ values

### `experiments/statistical_table.tex`
LaTeX table for the statistical validation section in the paper.

## Requirements

- Python 3.9+
- OpenAI API key (for GPT-4o experiments)
- Required packages: `openai`, `numpy`, `scipy`, `pandas`, `matplotlib`

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Experiments

1. **Baseline PCI measurement**:
   ```bash
   python mm_epc_phase1.py
   ```

2. **Cross-modal contagion**:
   ```bash
   python mm_epc_contagion.py
   ```

3. **Statistical validation**:
   ```bash
   python statistical_bootstrap.py
   ```

## Reproducibility

All random seeds are fixed in the code. The bootstrap analysis uses 10,000 resamples for robust confidence intervals. The real API experiment uses actual GPT-4o calls (requires API key).

## Citation

If you use this code, please cite our paper:

```bibtex
@article{liu2026mmepc,
  title={Multimodal Evaluator Preference Collapse: Cross-Modal Contagion in Self-Evolving Agents},
  author={Liu, Zewen},
  journal={arXiv preprint},
  year={2026}
}
```

## License

MIT License