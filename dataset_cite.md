# 数据集来源与引用情况

**Date**: 2026-03-17
**Purpose**: 整理项目中使用的 4 个数据集/环境的 origin paper 及代表性引用论文

---

## 1. HotpotQA

### Origin Paper

**Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W. W., Salakhutdinov, R., & Manning, C. D. (2018).**
*HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering.*
**EMNLP 2018**, pages 2369-2380.
arXiv: [1809.09600](https://arxiv.org/abs/1809.09600)

- **机构**: CMU, Stanford, MILA
- **规模**: 113K Wikipedia-based QA pairs，需多跳推理
- **特点**: 提供 sentence-level supporting facts 用于可解释性
- **引用数**: 4,550+

### 使用 HotpotQA 的代表性论文

| Paper | Venue | ArXiv | Citations | 与本项目关联 |
|-------|-------|-------|:---------:|------------|
| **ReAct**: Synergizing Reasoning and Acting in Language Models (Yao et al.) | ICLR 2023 | [2210.03629](https://arxiv.org/abs/2210.03629) | 1,800+ | 我们的 base agent 框架；HotpotQA 是 ReAct 四个评估环境之一 |
| **Reflexion**: Language Agents with Verbal Reinforcement Learning (Shinn et al.) | NeurIPS 2023 | [2303.11366](https://arxiv.org/abs/2303.11366) | 300+ | 我们的 rollout optimizer 参考；HotpotQA 是三类 benchmark 之一 |
| **LATS**: Language Agent Tree Search (Zhou et al.) | ICML 2024 | [2310.04406](https://arxiv.org/abs/2310.04406) | 50+ | MCTS-based search，HotpotQA 上 EM=0.63，超 ReAct/Reflexion |
| **FireAct**: Toward Language Agent Fine-Tuning (Chen et al.) | arXiv 2023 | [2310.05915](https://arxiv.org/abs/2310.05915) | ~50 | 在 HotpotQA trajectories 上 fine-tune LLM agent，Llama2-7B EM 提升 77% |
| **Scaling LLM Test-Time Compute Optimally** (Snell et al.) | ICLR 2025 | [2408.03314](https://arxiv.org/abs/2408.03314) | 1,326 | 建立 compute-optimal test-time scaling 范式 |

---

## 2. APPS (Automated Programming Progress Standard)

### Origin Paper

**Hendrycks, D., Basart, S., Kadavath, S., Mazeika, M., Arora, A., Guo, E., Burns, C., Puranik, S., He, H., Song, D., & Steinhardt, J. (2021).**
*Measuring Coding Challenge Competence With APPS.*
**NeurIPS 2021 Datasets and Benchmarks Track**.
arXiv: [2105.09938](https://arxiv.org/abs/2105.09938)

- **机构**: UC Berkeley
- **规模**: 10,000 Python 编程题，来自 Codewars, AtCoder, Kattis, Codeforces
- **难度分级**: Introductory, Interview, Competition（我们使用 Introductory 子集）
- **评估方式**: 测试用例执行 (pass@k)

### 使用 APPS 的代表性论文

| Paper | Venue | ArXiv | Citations | 与本项目关联 |
|-------|-------|-------|:---------:|------------|
| **CodeRL**: Mastering Code Generation through Pretrained Models and Deep RL (Le et al.) | NeurIPS 2022 | [2207.01780](https://arxiv.org/abs/2207.01780) | 642+ | Actor-critic RL 框架，在 APPS 上直接评估 |
| **AlphaCode**: Competition-level code generation (Li et al.) | Science 2022 | DOI: 10.1126/science.abq1158 | 2,161+ | 大规模采样 + 聚类范式；在 competitive programming 上评估 |
| **Self-Refine**: Iterative Refinement with Self-Feedback (Madaan et al.) | NeurIPS 2023 | [2303.17651](https://arxiv.org/abs/2303.17651) | — | 迭代自我修正，与 test-time compute allocation 相关 |
| **Let's Verify Step by Step** (Lightman et al.) | NeurIPS 2023 | [2305.20050](https://arxiv.org/abs/2305.20050) | 200+ | Process Reward Model (PRM) 逐步验证推理 |
| **Reflexion** (Shinn et al.) | NeurIPS 2023 | [2303.11366](https://arxiv.org/abs/2303.11366) | 300+ | 在 coding tasks (含 APPS 风格题目) 上评估自我反思 |

---

## 3. WebShop

### Origin Paper

**Yao, S., Chen, H., Yang, J., & Narasimhan, K. (2022).**
*WebShop: Towards Scalable Real-World Web Interaction with Grounded Language Agents.*
**NeurIPS 2022**, Vol. 35, pp. 34650-34667.
arXiv: [2207.01206](https://arxiv.org/abs/2207.01206)

- **机构**: Princeton NLP
- **规模**: 1.18M 真实商品，12,087 crowd-sourced 购物指令
- **特点**: 最佳 agent 成功率 29% vs 人类专家 59%；支持 sim-to-real 迁移到 Amazon/eBay
- **注**: WebShop 是 ReAct 原文四个评估环境之一，与对标方法直接可比

### 使用 WebShop 的代表性论文

| Paper | Venue | ArXiv | Citations | 与本项目关联 |
|-------|-------|-------|:---------:|------------|
| **ReAct** (Yao et al.) | ICLR 2023 | [2210.03629](https://arxiv.org/abs/2210.03629) | 1,800+ | 在 WebShop 上比 baseline 成功率 +10% |
| **Reflexion** (Shinn et al.) | NeurIPS 2023 | [2303.11366](https://arxiv.org/abs/2303.11366) | 300+ | WebShop 是三类核心 benchmark 之一 |
| **LATS** (Zhou et al.) | ICML 2024 | [2310.04406](https://arxiv.org/abs/2310.04406) | 50+ | GPT-3.5 gradient-free 达到 75.9% avg score |
| **AgentBench**: Evaluating LLMs as Agents (Liu et al.) | ICLR 2024 | [2308.03688](https://arxiv.org/abs/2308.03688) | 451+ | WebShop 是 8 个交互环境之一；评估 27 个模型 |
| **WebMall**: A Multi-Shop Benchmark (2025) | arXiv 2025 | [2508.13024](https://arxiv.org/abs/2508.13024) | — | 扩展 WebShop 到 multi-shop，最佳 agent <55% completion |

---

## 4. TextWorld Express (TWExpress)

### Origin Paper

**Jansen, P. A., & Côté, M.-A. (2023).**
*TextWorldExpress: Simulating Text Games at One Million Steps Per Second.*
**EACL 2023 (System Demonstrations)**, pages 169-177.
arXiv: [2208.01174](https://arxiv.org/abs/2208.01174)

- **机构**: University of Arizona, Microsoft Research
- **特点**: 高性能文本游戏模拟器（~1M steps/sec，比传统框架快 3 个数量级）
- **包含的 benchmark**: CoinCollector, TextWorld Commonsense (TWC), CookingWorld

**相关 origin（ScienceWorld，常与 TWExpress 一起使用）**:

**Wang, R., Jansen, P., Côté, M.-A., & Ammanabrolu, P. (2022).**
*ScienceWorld: Is your Agent Smarter than a 5th Grader?*
**EMNLP 2022**, pp. 11347-11368.
arXiv: [2203.07540](https://arxiv.org/abs/2203.07540)

- 30 个小学科学任务的交互式文本环境

### 使用 TextWorld/ScienceWorld 的代表性论文

| Paper | Venue | ArXiv | Citations | 与本项目关联 |
|-------|-------|-------|:---------:|------------|
| **SwiftSage**: A Generative Agent with Fast and Slow Thinking (Lin et al.) | NeurIPS 2023 | [2305.17390](https://arxiv.org/abs/2305.17390) | 119+ | Dual-process agent (fast T5 + slow GPT-4)，ScienceWorld 上 84.7 avg score |
| **DEPS**: Describe, Explain, Plan and Select (Wang et al.) | NeurIPS 2023 | [2302.01560](https://arxiv.org/abs/2302.01560) | ~50 | LLM planning 框架，ScienceWorld 上比 baseline +50% |
| **AgentBench** (Liu et al.) | ICLR 2024 | [2308.03688](https://arxiv.org/abs/2308.03688) | 451+ | 文本游戏是 8 个交互环境之一 |
| **ReAct** (Yao et al.) | ICLR 2023 | [2210.03629](https://arxiv.org/abs/2210.03629) | 1,800+ | ALFWorld 文本游戏上比 RL baseline +34% |
| **TALES** (2025) | arXiv 2025 | — | — | 122 个 text games 评估 34 个 LLM，top 模型 <15% 成功率 |

---

## 跨数据集观察

多篇论文横跨多个数据集，反映其作为基础 agent 框架的角色：

| Paper | HotpotQA | APPS/Code | WebShop | TextWorld |
|-------|:--------:|:---------:|:-------:|:---------:|
| **ReAct** (2210.03629) | ✅ | — | ✅ | ✅ (ALFWorld) |
| **Reflexion** (2303.11366) | ✅ | ✅ | ✅ | ✅ (ALFWorld) |
| **LATS** (2310.04406) | ✅ | ✅ (HumanEval) | ✅ | — |
| **AgentBench** (2308.03688) | — | ✅ | ✅ | ✅ |

这说明我们选择的 4 个环境（HotpotQA, APPS, WebShop, TWExpress）覆盖了 LLM agent 评估的主要类别（QA, Code, Web, Text Game），与领域主流 benchmark 高度对齐。

---

## BibTeX 参考

```bibtex
% === Dataset Origin Papers ===

@inproceedings{yang2018hotpotqa,
  author    = {Yang, Zhilin and Qi, Peng and Zhang, Saizheng and Bengio, Yoshua and Cohen, William W. and Salakhutdinov, Ruslan and Manning, Christopher D.},
  title     = {{HotpotQA}: A Dataset for Diverse, Explainable Multi-hop Question Answering},
  booktitle = {Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2018},
  pages     = {2369--2380},
  note      = {arXiv:1809.09600}
}

@inproceedings{hendrycks2021apps,
  author    = {Hendrycks, Dan and Basart, Steven and Kadavath, Saurav and Mazeika, Mantas and Arora, Akul and Guo, Ethan and Burns, Collin and Puranik, Samir and He, Horace and Song, Dawn and Steinhardt, Jacob},
  title     = {Measuring Coding Challenge Competence With {APPS}},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS) Datasets and Benchmarks Track},
  year      = {2021},
  note      = {arXiv:2105.09938}
}

@inproceedings{yao2022webshop,
  author    = {Yao, Shunyu and Chen, Howard and Yang, John and Narasimhan, Karthik},
  title     = {{WebShop}: Towards Scalable Real-World Web Interaction with Grounded Language Agents},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2022},
  volume    = {35},
  pages     = {34650--34667},
  note      = {arXiv:2207.01206}
}

@inproceedings{jansen2023textworldexpress,
  author    = {Jansen, Peter A. and C\^{o}t\'{e}, Marc-Alexandre},
  title     = {{TextWorldExpress}: Simulating Text Games at One Million Steps Per Second},
  booktitle = {Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL): System Demonstrations},
  year      = {2023},
  pages     = {169--177},
  note      = {arXiv:2208.01174}
}

% === Key Papers Using These Datasets ===

@inproceedings{yao2023react,
  author    = {Yao, Shunyu and Zhao, Jeffrey and Yu, Dian and Du, Nan and Shafran, Izhak and Narasimhan, Karthik and Cao, Yuan},
  title     = {{ReAct}: Synergizing Reasoning and Acting in Language Models},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2023},
  note      = {arXiv:2210.03629}
}

@inproceedings{shinn2023reflexion,
  author    = {Shinn, Noah and Cassano, Federico and Berman, Edward and Gopinath, Ashwin and Narasimhan, Karthik and Yao, Shunyu},
  title     = {Reflexion: Language Agents with Verbal Reinforcement Learning},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2023},
  note      = {arXiv:2303.11366}
}

@inproceedings{zhou2024lats,
  author    = {Zhou, Andy and Yan, Kai and Liu, Zhoujun and Wang, Yu-Xiong},
  title     = {Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2024},
  note      = {arXiv:2310.04406}
}

@inproceedings{liu2024agentbench,
  author    = {Liu, Xiao and Yu, Hao and Zhang, Hanchen and others},
  title     = {{AgentBench}: Evaluating {LLMs} as Agents},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2024},
  note      = {arXiv:2308.03688}
}
```

---

**⚠️ 注意**: 以上引用信息通过 research-lookup 搜索获得，建议在正式论文中引用前通过 Google Scholar / Semantic Scholar / DOI 二次验证。
