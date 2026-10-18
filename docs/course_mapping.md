# 课程内容映射审计（Course Content Mapping）

> 日期：2026-10-19。目的：核对课程 12 讲内容与项目各环节的实际对应关系，确认不是"挂名引用"，而是每一讲对应一个真实的设计决策。
> 依据：`results/transcripts/L*.txt`（14 讲英文字幕，含时间戳）+ 报告正文引用位置。

## 一、总览

| 讲次 | 主题 | 在本项目中对应什么 | 报告位置 | 强度 |
|---|---|---|---|---|
| L1 | DL for Healthcare AI 导论 | 把 IDH 预测定位为"临床预测任务"，而非纯 ML 练习 | §1 末（~00:40） | 定位 |
| L2 | Medical Image Classification | 1D-CNN 的卷积/滤波器直觉（迁移到一维生理序列） | §4 Models(3)（~00:45） | 方法来源 |
| L3 | Classification and Segmentation | 分类任务的评估范式（分类 vs 分割的取舍） | §4 Models(3)（~00:39） | 任务范式 |
| L4 | Advanced Vision Models | **未使用**——本项目无影像数据，不强行挂靠 | — | 不适用 |
| L5 | EHR Introduction | 不规则、异质临床时序 → 会话重建与稀疏采样设计 | §1（~00:38）、§3 | 核心 |
| L6 | EHR Part 2: RNN/LSTM | LSTM 对照臂；梯度消失与门控的动机 | §4 Models(4)（~01:21/02:14） | 基线设计 |
| L7 | Transformer & BERT | 从零 Transformer encoder（位置编码、padding mask、多头注意力） | §4 Models(5)（~00:27/27:16） | 核心 |
| L8 | Multimodal & Contrastive | 模态消融的设计逻辑（多源信息是否互补） | §1、§5 E4（~00:11） | 实验设计 |
| L9 | More on Transformer: GPT & CLIP | 注意力变体；注意力图≠解释的预警 | §5 E6（~00:53） | 解释性 |
| L10 | Unsupervised & RL | 序贯决策视角：动作、奖励、策略 → 控制模拟的框架 | §1、§5 E5（~00:27） | 框架 |
| L11 | Interpretability & AI Ethics | 干预式消融 vs 观察式解释；模型边界与伦理表述 | §5 E6（~05:11） | 核心 |
| L12 | Federated Learning & Privacy | 居家部署的数据治理（端侧推理、联邦/隐私保护训练） | §6 Future work（~00:39） | 前瞻 |
| GL1/GL2 | 客座讲座（MSRA / Git Kim Ann） | **未使用**——主题与本题无直接接口 | — | 不适用 |

**覆盖**：12 讲中 10 讲被实质使用（L1、L2、L3、L5–L12），2 讲不适用（L4 影像、客座讲座）。全部以 `\citep{md6329lectures}` 进入参考文献，正文标注"讲次 + 时间戳"。

## 二、逐讲：不是引用，而是决策

**L5 → 数据设计。** "EHR data is heterogeneous, irregular"（~00:38）直接对应本项目最棘手的技术决定：血压中位 50.7 分钟一测、机器设置密集但生理信号稀疏。因此放弃"等间隔时间序列"的常规做法，改用"读数连续段 + padding mask"，并把预测时点 $T$ 作为显式变量扫 30/60/90/120。

**L6 → 为什么保留 LSTM。** 讲义用 LSTM 对比 logistic regression 处理 EHR 预测（~01:21），并讲门控如何缓解梯度消失（~02:14）。本项目据此把 LSTM 作为"序列建模的最低合理基线"，而不是拿它当主角——结果也证实它与 CNN+MLP 差距在噪声内（E9）。

**L7 → 从零实现。** 位置编码（~27:16）、QKV（~00:54）、masked LM 预训练（~34:41）。项目的 Transformer 不用预训练，只借用 encoder 结构与 mask 机制，这一点在 §4 明确写出——避免把 BERT 的预训练收益误算进本项目。

**L8 → 模态消融。** 讲义讲"如何组合多源数据"（~00:11）。本项目的 E4 正是把"组合"拆开验证：结果反而说明在当前特征集里机器设置没有独立增量。**这是对讲义框架的一次反向检验**，也是报告里最有产品含义的一条。

**L10 → 控制框架。** 强化学习讲"动作—奖励—策略"（~00:27）。本项目的 E5 借用了这个语言（动作=UF 候选、代价=残余液体/时间），但明确不做 RL：因为观测数据不支持反事实，只能做动作条件风险评分。

**L11 → 解释性的核心方法论。** 讲义区分可解释性与事后解释（~00:56、05:11）。本项目用"置零 attention vs 置零 FFN"的干预实验，得出注意力贡献≈0 的结论——这正是"观察≠干预"的直接应用，也是报告撤回"注意力图可作临床解释"的依据。

**L12 → 产品边界。** 居家透析数据敏感，端侧推理/联邦训练是部署前提。这条写进 Future work，而不是硬塞进实验。

## 三、映射上的两个诚实缺口

1. **L4 与客座讲座未使用**：不强行建立联系。报告没有为凑数而引用影像分割内容。
2. **L2/L3 的迁移是"类比"而非"直接方法"**：卷积在图像上是二维局部感受野，在一维生理序列上是一维局部模式；报告写的是"convolutional feature extraction as developed for medical images"，措辞上标明来源而不夸大等价性。

## 四、与 brief 要求的对照

brief 要求："connect your discussions with one of the Lecture Recordings whenever possible, and highlight relevant Slides/Time in Video Recordings."

- 正文出现 **10 个讲次、18 处时间戳**，覆盖 Problem Formulation、Related Work、Approach、Experiments、Future Work 五节；
- 参考文献含课程录像条目（`md6329lectures`）；
- 未使用的两讲在本文档中说明理由，不在报告中假装引用。

## 五、结论

课程内容不是"背景装饰"，而是进入了四个关键决策：**数据表示（L5）、模型选择（L6/L7）、实验设计（L8）、解释方法（L11）**；L10 提供控制框架语言，L12 界定部署边界，L1–L3 提供任务与方法定位。映射成立。
