# MM-EPC: Multimodal Evaluator Preference Collapse

[![CI](https://github.com/aidless/mm-epc/actions/workflows/ci.yml/badge.svg)](https://github.com/aidless/mm-epc/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)  [![Data](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](LICENSE)

**Cross-Modal Coupling in Self-Evolving Agents**

[![arXiv](https://img.shields.io/badge/arXiv-2606.16682-b31b1b)](https://arxiv.org/abs/2606.16682)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey)](https://creativecommons.org/licenses/by/4.0/)

When LLMs serve as evaluators in closed-loop agent training, systematic biases emerge. This project investigates **cross-modal contagion**: evaluator preferences learned on one modality (text/vision) transfer to and corrupt strategy selection on another.

**Status (2026-10-28):** The canonical paper is arXiv:2606.16682v3, which is a
preprint and has not been peer-reviewed. The AAAI 2027 student abstract is a
submission, not an acceptance.

**Key finding**: Cross-model evaluators (GPT-4o, Qwen) produce strong coupling
(JSD approximately 0.19-0.34 across the reported configurations), while
self-evaluation provides near-complete immunity (97% of N=30 repetitions show
zero coupling, JSD=0.003). The repository records three methodological
ablations and a multi-executor check.

## 面试叙事：这个仓解决什么 / 为什么重要 / 结果 / 边界

**解决什么问题。** 当 LLM 充当闭环 agent 训练中的评估器时，系统性的偏好
偏差会累积。这个仓研究**跨模态传染（cross-modal contagion）**：在一个模态
（文本/视觉）上学到的评估器偏好，会迁移并污染在另一个模态上的策略选择。
多数「自我进化 agent」研究只看单模态内的自我修正；本仓证明**跨模态的偏好
传染是真实存在且方向不对称的**，并把「自我评估近乎免疫」量化出来。

**为什么重要。** 任何用 LLM 评估器做反馈环的 AI 系统——自我进化 agent、
RLAIF、AI-as-judge——都可能**悄悄收敛到「评估器喜欢的策略」而不是「任务
最优策略」**。如果偏好会跨模态传染，那么单模态内验证过的系统，在扩到多模态
时会带上隐藏的偏差。这个仓给出一个可度量的框架（contagion matrix + γ 系数）
来检测它，并识别出「自我评估」是有效的缓解手段。

**我用了什么方法。** 四阶段隔离训练范式（T 文本 → V 视觉 → TV 跨模态 →
VT 跨模态），测每个阶段的策略权重分布，用 γ 系数（权重向量的一致性）
量化传染强度，用 JSD/Hellinger/TV 距离量化分布差异。三种评估器架构（GPT-4o
text-proxy、GPT-4o-mini real-image、Qwen3.7）各 N=8–10；DeepSeek 自我评估
N=30 多 seed；外加三组消融（去基线/对称学习率/多执行器）与同模态惯性对照。

**结果如何。** 跨模态评估器产生强耦合（JSD 0.19–0.34），且方向不对称
（GPT-4o text-proxy: γ_TV=1.176 > γ_VT=1.089，即 T→V 主导）；real-image
的 GPT-4o-mini 给出最一致的方向（70% T→V, d=0.56）；自我评估近乎免疫
（N=30 中 97% 零传染，JSD=0.003，γ_TV=0.033/γ_VT=0.023, Cohen's d=0.07）。
DashScope 高轮数（R=50）收敛到单策略主导（70% 零传染）。总计 N=80 独立
重复、~35k API 调用。

**边界在哪。** 见下方「证明什么 / 不证明什么」——关键几条：这是**单作者**
探索性研究（arXiv 预印本，未同行评审，AAAI 2027 学生摘要为投稿非录用）；
样本量 N=8–30 对效应量估计够但非大样本；LLM API 响应温度>0 不可位级复现；
JSD/Hellinger 列中 GPT-4o / real-image 两行**缺权重向量，无法离线重算**
（见「结果文件映射」与复算说明）；不证明任何真实生产系统的鲁棒性。

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

> **⚠️ 复算诚实说明（2026-11-01 核对）.** `compute_bounded_metrics.py` 重算
> JSD/Hellinger 需要每个 repetition 的完整权重向量 `w_T/w_V/w_TV/w_VT`。
> 核对结果：
> - **可离线重算**：DeepSeek self-eval（`multi_seed_ds_checkpoint.json`,
>   JSD=0.0032 ✓ 匹配 README 0.003；γ 0.033/0.023 ✓；97% 零传染 ✓）、
>   Qwen3.7-plus（`qwen37_checkpoint.json`，JSD TV=0.226 / VT=0.2305，
>   README 0.230 ≈ VT 均值；γ 1.059/1.008 ✓）、Multi-seed old
>   （`multi_seed_checkpoint.json`，JSD=0.0308 ✓）、以及所有行的 γ 旧指标
>   （GPT-4o γ=1.176/1.089 ✓、real-image γ=1.145/0.937 ✓，均从各自
>   `mm_epc_*.json` 的 per-rep gTV/gVT 重算）。
> - **不可离线重算（缺权重向量）**：GPT-4o text-proxy 的 JSD=0.316、
>   GPT-4o-mini real-image 的 JSD=0.342。这两行的 `mm_epc_gpt4o_replication.json`
>   / `mm_epc_real_image.json` 的 `results` 只含 `gTV/gVT/top_*/time`，
>   **无 `w_T` 权重向量**（脚本当前版只在 GPT-4o 脚本写权重，且提交的 JSON
>   是旧版产物；real-image 脚本不写权重）。**因此这两行的 JSD 值只能作为
>   论文声称值引用，仓库内无重算来源**。`compute_bounded_metrics.py` 对
>   GPT-4o 行打印 `file not found`（它期望 `gpt4o_replication_checkpoint.json`，
>   该文件不在仓库）。
> - **DashScope**：仅 aggregate（`statistical_table.tex`），per-rep JSON 未提交，
>   不可重算 per-rep。
> 绝不为了凑齐 JSD 列而编造权重向量；缺数据的行已如实标注。

### 证明什么 / 不证明什么

**证明（evidence-backed，均可从仓库内文件重算）：**
1. **跨模态传染真实存在且方向不对称**。GPT-4o text-proxy γ_TV=1.176 >
   γ_VT=1.089（T→V 主导），Qwen3.7 γ_TV=1.059 > γ_VT=1.008。可从
   `mm_epc_gpt4o_replication.json` / `qwen37_checkpoint.json` 的 per-rep
   gTV/gVT 重算。
2. **真实视觉输入产生最一致的方向**。GPT-4o-mini real-image 70% T→V,
   d=0.56（`mm_epc_real_image.json`）。
3. **自我评估近乎免疫**。DeepSeek N=30 中 29/30 零传染（97%），
   JSD=0.003，γ 0.033/0.023，Cohen's d=0.07。可从
   `multi_seed_ds_checkpoint.json` 重算。
4. **高轮数跨模型收敛到单策略主导**。DashScope R=50 时 70% 零传染
   （aggregate，`statistical_table.tex`）。
5. **方法学消融**：去掉基线候选会改变传染方向、对称学习率抑制传染、
   多执行器改变耦合——各自 `ablation_*_checkpoint.json`。

**不证明（boundary）：**
1. **不证明普遍性**。这是**单作者**探索性研究（arXiv 2606.16682v3 预印本，
   未同行评审；AAAI 2027 学生摘要是投稿非录用）。N=8–30 对效应量估计够用
   但非大样本，且三种评估器架构不代表所有 LLM。
2. **不证明因果机制的完备性**。γ 系数与 JSD 度量「偏好传染的强度」，不
   解释**为什么**它发生（是提示/API/模型特性？）；四阶段范式隔离了模态，
   但未隔离提示语言、任务难度等混淆。
3. **不证明位级可复现**。LLM API 响应温度>0，重复运行非 bit-identical；
   per-repetition seeds 只保证任务/轮次顺序可复现，不保证输出值相同。
4. **不证明生产鲁棒性**。结果来自受控实验脚本（DeepSeek-chat 执行器 +
   固定提示模板），不涉及真实生产系统中的延迟、成本、并发、策略漂移。
5. **GPT-4o / real-image 两行的 JSD 不可离线重算**（缺权重向量，见上）。
   引用这两行 JSD 时必须注明「论文声称值，仓库内无重算来源」。

## Paper

- **arXiv**: [2606.16682](https://arxiv.org/abs/2606.16682) - v3 preprint, 17 pages
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
  title={Multimodal Evaluator Preference Collapse: Cross-Modal Coupling in Self-Evolving Agents},
  author={Anonymous},
  journal={arXiv preprint arXiv:2606.16682},
  year={2026}
}
```

## License

MIT for software. CC BY 4.0 for data, documentation, and pre-registration
artifacts.

---

*MM-EPC Contributors, 2026*

> **Dual license.** MM-EPC releases the experiments, raw results, and the evidence manifest under
> MIT; data, documentation, and pre-registration artifacts are released under
> CC BY 4.0.
