# MM-EPC: Multimodal Evaluator Preference Collapse

**Cross-Modal Contagion in Self-Evolving Agents**

[![arXiv](https://img.shields.io/badge/arXiv-2506.xxxxx-b31b1b)](https://arxiv.org/abs/2506.xxxxx)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

When LLMs serve as evaluators in closed-loop agent training, systematic biases emerge. This project investigates **cross-modal contagion**: evaluator preferences learned on one modality (text/vision) transfer to and corrupt strategy selection on another.

**Key finding**: Cross-model evaluators (GPT-4o, Qwen) induce strong contagion (JSD 50-100x above baseline), while self-evaluation provides near-complete immunity (97% zero contagion). Contagion is not a structural artifact -- it persists under 3 methodological ablations and generalizes across executors.

## Reproduction

### Requirements
```bash
# No external packages required (Python stdlib only)
python --version  # Python 3.8+
```

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

## Paper

- **arXiv**: [2506.xxxxx](https://arxiv.org/abs/2506.xxxxx) (full paper, 19 pages)
- **AAAI Student Abstract**: `aaai_student_abstract/aaai_abstract.tex`
- **LaTeX source**: `paper/mm_epc_paper.tex`

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
