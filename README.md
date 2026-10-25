# MM-EPC: Multimodal Evaluator Preference Collapse
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  [![Data](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](LICENSE)

**Cross-Modal Contagion in Self-Evolving Agents**

[![arXiv](https://img.shields.io/badge/arXiv-2606.16682-b31b1b)](https://arxiv.org/abs/2606.16682)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

When LLMs serve as evaluators in closed-loop agent training, systematic biases emerge. This project investigates **cross-modal contagion**: evaluator preferences learned on one modality (text/vision) transfer to and corrupt strategy selection on another.

**Key finding**: Cross-model evaluators (GPT-4o, Qwen) induce strong contagion (JSD 50-100x above baseline), while self-evaluation provides near-complete immunity (97% zero contagion). Contagion is not a structural artifact -- it persists under 3 methodological ablations and generalizes across executors.

## Reproduction

### Requirements
```bash
python --version  # Python 3.8+ (CI runs on 3.12, see .github/workflows/ci.yml)
```
- All `mm_epc_*.py` experiment scripts use the Python standard library only
  (`json`, `os`, `re`, `random`, `time`, `urllib.request`), except
  `mm_epc_phase3_significance.py`, which additionally needs `numpy` and `scipy`.
- The `compute_*.py` analysis scripts are stdlib-only as committed;
  `statistical_bootstrap.py` and `postprocess_phase3.py` need `numpy`/`scipy`.
- Full dependency list for statistics/visualization tooling: `pip install -r requirements.txt`

### Seeds and determinism
- `mm_epc_multi_seed.py` seeds the PRNG per repetition (`random.seed(seed)`) and
  fixes the bootstrap resampling seed (`random.seed(42)`).
- Results depend on live LLM API responses (temperature>0 endpoints), so repeated
  runs are not bit-identical; per-repetition seeds make the task/round ordering reproducible.

### API Keys
Set environment variables or edit scripts directly:
- `DEEPSEEK_API_KEY` -- for executor (DeepSeek-chat)
- `API2D_KEY` / Alibaba Cloud key -- for evaluator (GPT-4o / Qwen)

### Run Experiments

```bash
# Phase 1: Baseline PCI measurement
python mm_epc_phase1.py

# Phase 2: Cross-modal contagion (single run)
python mm_epc_contagion.py

# Phase 3: Statistical validations
python mm_epc_gpt4o_replication.py        # GPT-4o N=8
python mm_epc_qwen37_replication.py       # Qwen3.7 N=8 (free Alibaba credits)
python mm_epc_real_image.py               # Real-image N=10
python mm_epc_multi_seed.py               # DeepSeek self-eval N=30

# Ablations
python mm_epc_ablation_no_s0.py           # Remove baseline from candidates
python mm_epc_ablation_symmetric.py       # Symmetric learning rates
python mm_epc_multiexecutor.py            # GPT-4o-mini executor
python mm_epc_same_modality_control.py    # T->T, V->V inertia baselines

# Analysis
python compute_bounded_metrics.py         # JSD/Hellinger from weights
python compute_random_baseline.py         # Random evaluator baseline
```

## Results

All JSON outputs in `experiments/`:

| Experiment | N | gTV | gVT | JSD_TV | Zero% |
|-----------|----|-----|-----|--------|-------|
| GPT-4o-mini real-image | 10 | 1.145 | 0.937 | 0.342 | 0% |
| GPT-4o text-proxy | 8 | 1.176 | 1.089 | 0.316 | 0% |
| Qwen3.7-plus | 8 | 1.059 | 1.008 | 0.230 | 0% |
| DashScope | 10 | 0.273 | 0.341 | 0.05 | 70% |
| DeepSeek self-eval | 30 | 0.033 | 0.023 | 0.003 | 97% |
| T→T inertia control | 3 | 0.390 | -- | 0.049 | -- |
| V→V inertia control | 3 | -- | 0.829 | 0.119 | -- |

**Total: N=80 independent repetitions, ~35,000 API calls.**

### Result file map

Each table row maps to raw JSON committed under `experiments/`:

| Table row | Raw JSON |
|-----------|----------|
| GPT-4o-mini real-image | `experiments/mm_epc_real_image.json` |
| GPT-4o text-proxy | `experiments/mm_epc_gpt4o_replication.json` |
| Qwen3.7-plus | `experiments/mm_epc_qwen37_final.json` (+ `mm_epc_qwen_partial.json` checkpoint) |
| DeepSeek self-eval | `experiments/mm_epc_multi_seed_ds_final.json` (N=30; mean γ 0.033/0.023; 29/30 repetitions with zero contagion) |
| T→T / V→V inertia controls | `experiments/same_modality_checkpoint.json` |
| Random evaluator baseline | `experiments/random_baseline.json` |
| Phase 1 baseline PCI | `experiments/mm_epc_phase1.json` |
| Bootstrap significance | `experiments/mm_epc_phase3_bootstrap.json` |

The JSD/Hellinger columns are recomputed from the stored per-repetition weight
vectors by `python compute_bounded_metrics.py` (it prints bounded metrics and
writes a summary note to `experiments/bounded_metrics.json`). The DashScope
gui-plus initial validation (N=10, R=50) is reported aggregate-only in
`experiments/statistical_table.tex`; its per-repetition raw JSON is not committed.
The paper-side aggregate table is `experiments/statistical_table.tex`, shared by
`paper/mm_epc_paper.tex` and `aaai_student_abstract/aaai_abstract.tex`.

## Paper

- **arXiv**: [2506.xxxxx](https://arxiv.org/abs/2506.xxxxx) — full paper (19 pages), `paper/mm_epc_paper.tex`
- **AAAI 2027 Student Abstract**: `aaai_student_abstract/aaai_abstract.tex` — 2-page standalone submission
- `paper/statistical_table.tex` — shared between both documents

## Repository Structure

```
mm-epc/
├── README.md                       ← this file
├── paper/
│   ├── mm_epc_paper.tex           ← arXiv full paper
│   └── statistical_table.tex      ← shared data table
├── aaai_student_abstract/
│   └── aaai_abstract.tex          ← AAAI 2-page submission
├── mm_epc_*.py                     ← experiment scripts
├── compute_*.py                    ← analysis scripts
└── experiments/                    ← all result JSON files
```

## Citation

```bibtex
@article{liu2026mmepc,
  title={Multimodal Evaluator Preference Collapse: Cross-Modal Contagion in Self-Evolving Agents},
  author={Liu, Zewen},
  journal={arXiv preprint arXiv:2506.xxxxx},
  year={2026}
}
```

## License

CC BY 4.0

---

*Liu Zewen (刘泽文) -- Qilu Institute of Technology, 2026*


> **Dual license.** MM-EPC releases the experiments, raw results, and the evidence manifest under