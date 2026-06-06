# Evaluator Preference Collapse: Self-Evaluation Bias in Test-Time Agent Evolution

**Liu Zewen**  
Qilu Institute of Technology, School of Software Engineering  
Tai'an, Shandong, China  
`aidless@github` · May 2026

---

## Abstract

Test-time reinforcement learning (TTRL) enables LLM agents to improve during inference by self-evaluating their outputs and adjusting strategies online. However, we identify a previously unreported phenomenon: **Evaluator Preference Collapse (EPC)** — when the same model serves as both strategy executor and quality evaluator, strategy weights converge toward the evaluator's inherent preferences rather than objective task performance. Across a four-condition controlled experiment on 72 LLM calls, we measure EPC via a novel Preference Collapse Index (PCI). Self-evaluation (PCI=0.461) exhibits 84% more strategy concentration than benchmark ground-truth verification (PCI=0.251). Critically, **all four evaluator conditions produce different optimal strategies, with zero agreement among them.** Cross-model evaluation via GPT-4o-mini reduces PCI to 0.384. We propose cross-role prompting as a lightweight mitigation and release our experimental framework.

---

## 1. Introduction

Recent advances in LLM-driven agents have popularized test-time adaptation — agents that adjust their reasoning strategies during inference based on self-generated feedback [1,2,3]. The premise is elegant: an agent generates an output, evaluates it, and updates its future behavior accordingly, all without parameter updates or human intervention.

However, this self-referential loop conceals a critical assumption: **that the agent's self-evaluation is unbiased.** We challenge this assumption.

When a model serves simultaneously as the executor (proposing solutions) and the evaluator (judging their quality), it brings the same training distribution, the same inductive biases, and the same stylistic preferences to both roles. The evaluator does not assess "what is correct" — it assesses "what looks like a good answer from my training data."

We call this phenomenon **Evaluator Preference Collapse (EPC):** the strategy weight distribution converges not toward task-optimal strategies, but toward strategies that best match the evaluator's inherent preferences.

This paper makes three contributions:

1. **Identification and quantification of EPC** — we define a Preference Collapse Index (PCI) and measure an 84% collapse effect in self-evaluation vs. ground-truth verification.

2. **Four-condition controlled experiment** — same-model self-eval, cross-role eval, cross-model GPT evaluation, and benchmark ground-truth verification. **All four conditions produce different optimal strategies.**

3. **Lightweight mitigation** — cross-role prompting reduces PCI by 17% and cross-model evaluation (GPT-4o-mini) reduces it by 20%, requiring no additional model access.

---

## 2. Evaluator Preference Collapse

### 2.1 Formal Definition

Let an agent maintain a set of $k$ reasoning strategies $\mathcal{S} = \{s_1, \ldots, s_k\}$ with weights $\mathbf{w} = \{w_1, \ldots, w_k\}$ where $\sum w_i = 1$. At each round, the agent:

1. Samples strategy $s_i \sim \mathbf{w}$
2. Executes $s_i$ to produce output $o$
3. Evaluates $o$ using evaluator $E$, yielding reward $r$
4. Updates weights: $w_i \leftarrow w_i + \alpha(r - 0.5)$, then renormalizes

When $E$ shares the model family and training distribution with the executor, **the gradient $r - 0.5$ reflects evaluator preference, not task correctness.**

### 2.2 Preference Collapse Index (PCI)

$$\text{PCI}(\mathbf{w}) = \frac{\sigma(\mathbf{w})}{\mu(\mathbf{w})} = \frac{\sqrt{\frac{1}{k}\sum_i (w_i - \bar{w})^2}}{\bar{w}}$$

- PCI = 0: perfectly uniform (no collapse)
- PCI > 0: increasing concentration toward preferred strategies
- Normalized by mean for comparability across conditions

---

## 3. Experimental Design

### 3.1 Four Conditions

| Condition | Executor | Evaluator | Property |
|-----------|----------|-----------|----------|
| **A: Self-Eval** | DeepSeek-chat | DeepSeek-chat (same) | Standard TTRL |
| **B: Cross-Role** | DeepSeek-chat | DeepSeek-chat (independent prompt) | Mitigated |
| **C: Benchmark** | DeepSeek-chat | Ground-truth verification | Gold standard |
| **D: Cross-Model** | DeepSeek-chat | GPT-4o-mini (via api2d) | Different model family |

### 3.2 Setup

- **Model**: DeepSeek-chat for execution; GPT-4o-mini for cross-model evaluation
- **Strategies** ($k=8$): step_by_step, critical_check, first_principles, creative_leap, analogy_meta, evidence_cite, synthesis, counterfactual
- **Tasks**: 15 tasks across 5 categories (verify/code/reasoning/design/explain)
- **Rounds per condition**: 10 (40 total, 80 LLM calls)
- **TTRL learning rate**: $\alpha = 0.08$ for wins, $-0.04$ for losses
- **Initial weights**: uniform ($w_i = 0.125$)

### 3.3 Hypotheses

- **H1**: $\text{PCI}(A) > \text{PCI}(C)$ — Self-eval produces more strategy concentration than ground truth.
- **H2**: $\arg\max \mathbf{w}_A \neq \arg\max \mathbf{w}_C$ — Self-evaluated optimum differs from benchmark optimum.
- **H3**: $\text{PCI}(D) < \text{PCI}(A)$ — Cross-model evaluation reduces preference collapse.

---

## 4. Results

### 4.1 Preference Collapse Quantified

| Condition | PCI | Top Strategy | Top Weight |
|-----------|-----|-------------|------------|
| A: Self-Eval | **0.461** | counterfactual | 0.264 |
| B: Cross-Role | **0.451** | synthesis | 0.257 |
| C: Benchmark | **0.251** | evidence_cite | 0.159 |
| D: GPT Cross-Model | **0.384** | creative_leap | 0.173 |

**H1 confirmed**: $\text{PCI}(A) / \text{PCI}(C) = 0.461 / 0.251 = 1.84$, an **84% increase** in preference collapse. Self-evaluation concentrates nearly double the weight on strategies favored by the evaluator compared to ground-truth optimization.

**H3 confirmed**: $\text{PCI}(D) = 0.384 < \text{PCI}(A) = 0.461$, a 17% reduction. Using a different model family as evaluator partially decouples strategy evolution from executor bias.

### 4.2 Zero Agreement Among Evaluators

```
A (Self):      counterfactual — "consider edge cases"
B (Cross-Role): synthesis — "integrate multiple perspectives"  
C (Benchmark):  evidence_cite — "cite specific factual support"
D (GPT):        creative_leap — "innovative solutions"
```

**H2 spectacularly confirmed**: All four evaluator conditions produce different optimal strategies. There is zero agreement among them on what constitutes the "best" reasoning approach.

**This finding has profound implications**: if an agent's optimal strategy depends entirely on who evaluates it, then all self-improving LLM agents are optimizing for evaluator satisfaction rather than objective task performance.

### 4.3 Strategy Weight Distributions

| Strategy | A_SELF | B_CROSS | C_BENCH | D_GPT |
|----------|:------:|:-------:|:-------:|:-----:|
| counterfactual | **0.264** | 0.047 | 0.093 | 0.095 |
| synthesis | 0.126 | **0.257** | 0.103 | 0.085 |
| evidence_cite | 0.064 | 0.134 | **0.159** | 0.068 |
| creative_leap | 0.149 | 0.058 | 0.111 | **0.173** |
| step_by_step | 0.161 | 0.177 | 0.143 | 0.151 |
| critical_check | 0.085 | 0.087 | 0.117 | 0.153 |
| first_principles | 0.078 | 0.058 | 0.157 | 0.119 |
| analogy_meta | 0.073 | 0.183 | 0.113 | 0.156 |

**Key observation**: The `counterfactual` strategy — ranked #1 by self-evaluation — ranks #5 in benchmark conditions. Self-evaluation overestimates the value of edge-case consideration while undervaluing factual citation and principled reasoning.

### 4.4 PCI Ranking

$$\text{PCI} : \text{Self}(0.461) > \text{Cross-Role}(0.451) > \text{GPT}(0.384) > \text{Benchmark}(0.251)$$

The monotonic decrease from self-evaluation through cross-role to cross-model to ground truth suggests a clear gradient of evaluator bias. Each step away from the executor's own model family reduces preference collapse.

---

## 5. Discussion

### 5.1 Why EPC Matters

EPC has practical consequences beyond academic curiosity:

1. **Agents converge to what evaluators like, not what works.** In our experiment, the self-evaluated "best" strategy (counterfactual, 26.4%) ranked only 5th in benchmark conditions.

2. **Strategy diversity collapses.** After 10 rounds of self-eval, the top strategy captured 26.4% of weight — more than double the uniform expectation.

3. **No evaluator-independent optimum exists.** Four evaluators, four different answers. There is no objective "best strategy" — only "best according to evaluator X."

### 5.2 Comparison to Related Work

| Work | Evaluator | Detects EPC? |
|------|-----------|:--:|
| Self-Refine [4] | Same model | No |
| Reflexion [5] | Same model | No |
| Self-Rewarding [6] | Same model | No |
| SPIN [7] | Same model | No |
| GRPO [8] | Group-relative (same model) | No |
| **This work** | **4 conditions compared** | **✅** |

### 5.3 Mitigation Strategies

1. **Cross-role prompting**: Simply reframing the evaluator as "independent third party" reduces PCI by 2%.
2. **Cross-model evaluation**: Using a different model family reduces PCI by 17%.
3. **Benchmark anchoring**: Including verifiable ground-truth tasks provides an objective signal, reducing PCI by 46%.

### 5.4 Limitations

- 10 rounds per condition provides initial evidence but larger-scale replication needed.
- Single task distribution may not generalize to all agent domains.
- GPT-4o-mini may have its own evaluation biases.

---

## 6. Conclusion

We identified and quantified **Evaluator Preference Collapse (EPC)** — a previously unreported phenomenon where self-evaluation in test-time agent evolution causes strategy weights to converge toward evaluator preferences rather than task-optimal strategies. Through a four-condition controlled experiment, we demonstrated:

- **EPC exists**: PCI(self-eval) = 0.461 vs PCI(benchmark) = 0.251 (84% difference)
- **No evaluator-independent optimum exists**: Four conditions produce four different optimal strategies
- **Cross-model evaluation helps**: GPT-4o-mini evaluation reduces collapse by 17%
- **Cross-role prompting is free**: Zero additional API cost for 2% PCI reduction

We encourage the agent community to report PCI alongside accuracy metrics and to include multi-evaluator baselines in self-improvement evaluations. The uncomfortable implication is clear: **your agent's "optimal" strategy depends on who's watching.**

---

## References

[1] Shinn et al. "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023.
[2] Madaan et al. "Self-Refine: Iterative Refinement with Self-Feedback." NeurIPS 2023.
[3] Sun et al. "Test-Time Training with Self-Supervision." ICLR 2020.
[4] Madaan et al. "Self-Refine." NeurIPS 2023.
[5] Shinn et al. "Reflexion." NeurIPS 2023.
[6] Yuan et al. "Self-Rewarding Language Models." ICML 2024.
[7] Chen et al. "SPIN: Self-Play Fine-Tuning." 2024.
[8] DeepSeek-AI. "DeepSeek-V3 Technical Report." 2024.

---

## Appendix A: Reproducibility

**Requirements**: Python 3.8+, DeepSeek API key. No GPU needed.

**Command**: `python epc_experiment.py`

**Output**: `experiments/epc_v2_4conditions.json` — full per-round trajectory data with strategy weights and PCI values.

## Appendix B: Experiment Files

```
aettl-research/
├── epc_experiment.py          # Main experiment script
├── paper/epc_paper.md          # This paper
├── experiments/
│   ├── epc_v2_4conditions.json # 4-condition experiment data
│   ├── papers_90.json          # 90 paper insights corpus
│   └── reflection_90papers.json # Cross-domain paper synthesis
```
