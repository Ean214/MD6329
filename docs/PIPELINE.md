# MD6329 Final Project — 研究/开发/输出 流水线设计

> 本文档是 12 天执行的总规程。每步映射到具体产出文件；每阶段有质量门（gate），不过门不进入下一步。
> 更新时间：2026-10-13。项目目标：补足人工肾产品技术逻辑（求职），同时满足课程硬性要求 M1–M12。

---

## 目录结构（所有产出的落点）

```
project/
├── data/            # HEMOBP 原始 CSV（已在位）+ 构建后的数据集
├── src/             # 全部可执行脚本（编号对应流水线步骤）
├── results/         # 每次实验的 JSON 结果 + 图（进报告的唯一来源）
├── report/          # 报告骨架（第 1 天建立，每日填图）
├── lectrace/        # LecTrace 讲义脚本
├── zip/             # 最终打包
└── docs/
    ├── PIPELINE.md          # 本文件
    ├── claims_register.md   # C1–C6 主张登记表（假设+接受标准+结论）
    ├── dataset_card.md      # 数据集卡片（EDA 产出）
    ├── lecture_index.md     # 课程录像主题→时间戳索引
    ├── references.bib       # 文献库（≥10 条）
    └── interview_sheet.md   # 面试数字表（一页纸，活文档）
```

---

## Stage R — 研究（Day 1–2）：把问题钉死

| 步骤 | 动作 | 产出文件 | 对应 |
|---|---|---|---|
| R1 | 合规清单锁定（已确认 M1–M12） | 计划文件 §一 | 课程要求 |
| R2 | 抓 14 讲字幕 → 建主题索引；文献锚定（闭环超滤/Hemocontrol/IDH 定义/KDOQI） | `docs/lecture_index.md`、`docs/references.bib` | M3/M6、Related Work 15% |
| R3 | HEMOBP EDA：会话重建、IDH 多定义发生率、UFR 分布、BP 间隔、缺失率 | `docs/dataset_card.md` + `results/eda_*.png/json` | Data 15% |
| R4 | 冻结 C1–C6 检验清单：每条写清假设、指标、接受标准 | `docs/claims_register.md` | Approach/Exp 50% |

**质量门 R**：EDA 数字必须能支撑任务定义——IDH 主定义下发生率 ≥5%（否则换定义）、可建模样本量 ≥1 万 session、视野实验可行（BP 间隔中位 ≤60 min）。不满足 → 回退改定义/改抽样，**不许带着不合格的地基进开发**。

## Stage D — 开发（Day 2–9）：逐实验推进

| 步骤 | 动作 | 产出 | 对应主张 |
|---|---|---|---|
| D0 | 工程骨架：数据 pipeline（会话→样本）、**按患者 group split**、评估协议（AUPRC 主指标）、固定种子、结果统一落盘 JSON | `src/d0_*.py`、`results/protocol.json` | 全部（防泄漏是红线） |
| D1 | E1 四模型对照：XGBoost / 1D-CNN+MLP / LSTM / 从零 Transformer | `results/e1_*.json/png` | C1/C2 |
| D2 | E2 算力账：参数量/FLOPs/推理延迟 | `results/e2_compute.json` | C2（Edge AI 论据） |
| D3 | E3 视野曲线（30/60/90/120 min+余程）、E4 模态消融 | `results/e3_*.json`、`results/e4_*.json` | C1/C3 |
| D4 | **E5 离体控制：恒定 UF vs 反应式 vs 预测式 → IDH 率 vs 残余液体量 vs 需延长时长** | `results/e5_tradeoff.json/png` | **C4/C5（核心，不可裁剪）** |
| D5 | E6 因果诊断：pyvene ZeroIntervention + 输入 UF 扰动 → 暴露混杂 | `results/e6_*.json/png` | 结论边界 |
| D6 | E7 仿真敏感性（HEMOBP 分布标定 → 外推讨论，可降级） | `results/e7_*.png` + 报告讨论段 | 产品外推 |

**写→跑→验→图→进报告** 五拍循环，每实验：
1. 脚本可独立复现（`python src/dN_xxx.py` 一键出结果）
2. 数值 sanity check（AUC 在 [0.5,1]、样本数对得上、无 NaN 污染）
3. 图存 `results/`（报告只从 results 取图，保证可追溯）
4. 结论写进 `claims_register.md`（对应 C 编号 + 数字 + 一句话边界）

**质量门 D**：任何实验若 group split 后测试集 AUC < 0.55，先查泄漏/标签/特征工程，不解释为"模型不行"——直到排除工程问题。

## Stage O — 输出（Day 1 起持续，Day 9–12 收尾）

| 步骤 | 动作 | 产出 | 对应 |
|---|---|---|---|
| O1 | **报告骨架第 1 天建立**（NeurIPS 模板六节标题+引用管理），每日把 results 图填进去 | `report/` | M5 |
| O2 | 封面页 13 题填写 → docx 导出 PDF → 合并为报告第 1 页 | `report/cover.pdf` | M1 |
| O3 | LecTrace 讲义脚本（2–3 min 问题→3–5 execution state→结果+临床解读） | `lectrace/` | M4 |
| O4 | GitHub repo（Ean214）推代码 → GitHub Pages 部署 LecTrace | repo + Pages URL | M4、封面 B 区 |
| O5 | 单 ZIP：代码+数据说明+权重+图+讲义 | `zip/` | M7 |
| O6 | Software 3.0 节 + 封面两道论述题（bug=作业 2 sigmoid 饱和+cuda/cpu；录像改进=看完写） | 报告节 + 封面 | M10/M12 |
| O7 | 面试数字表定稿：C1–C6 各一行结论+数字+边界 | `docs/interview_sheet.md` | 求职交付 |

**降级顺序**（时间不足时）：E7→只剩讨论段 → Transformer 对照退 LSTM → E4 缩 2 组 → E3/E2 缩规模 → **E5 永不裁**。

**诚实红线**（任何产出不得违反）：in-silico 必标注；不夸大数字；混杂问题正面写；HEMOBP≠WAK 的错配明示。

---

## 产出 → 收益映射（为什么做这些）

| 产出 | 课程侧（保底） | 求职侧（主目标） |
|---|---|---|
| 数据集卡片+EDA | Data 15% | "你的数据从哪来、什么质量"答得上 |
| E1 四模型+算力账 | Approach/Exp | "为什么选 1D-CNN 不选 Transformer"有实测答案 |
| E3 视野曲线 | Experiments | "提前多久能预警"有数字；解释为何 WAK 需连续传感 |
| E4 模态消融 | Experiments | "传感器 BOM 能砍什么"有依据 |
| E5 权衡表 | Experiments | "降超滤防低血压的代价"——你论文没算的那笔账 |
| E6 混杂诊断 | Conclusion/Discussion | "我知道技术边界在哪" |
| 面试数字表 | — | 六条可背的技术结论，撑起「AI × 医疗器械」叙事 |

---

## 模型分工协议（强模型 vs 便宜模型）

> 目的：省成本。原则：**协议和判断用强模型，跑批和组装用便宜模型。**
> 便宜模型必读本文档 + `docs/dataset_card.md` + `docs/claims_register.md`，这三份是自包含上下文。

### 🔴 红色：必须强模型（判断错误会毁掉后续全部）
| 步骤 | 为什么 |
|---|---|
| D0 工程骨架 | 样本怎么从稀疏 BP+密集机器设置构建、group split、评估协议——此处错一步，全部数字作废 |
| D1 首个模型端到端跑通+数值验证 | 确立"基线长什么样"，便宜模型才知道什么叫正常、什么叫异常 |
| D4 / E5 离体控制设计与解读 | 核心交付 + 方法学最危险（模拟器、策略定义、trade-off 口径），表述不诚实=求职反噬 |
| 报告论证结构 + Discussion/局限 | 哪些话能说、哪些不能说，是判断力 |
| E6 因果诊断解读 | pyvene 有已知坑（见技能 pytorch-arch-ab-experiment），结论形态需把关 |

### 🟡 黄色：强模型起头，跑通后可放手
| 步骤 | 放手条件 |
|---|---|
| D1 其余三模型 | 参考实现已验证后，改配置跑批即可 |
| D3 视野/消融 | D1 协议冻结后，变参数执行 |
| R2 文献筛选 | 强模型圈定 ≥10 篇清单，便宜模型抓元数据/格式化 BibTeX |
| D5 pyvene 干预代码 | 强模型写好模板+坑位注释，便宜模型跑 |

### 🟢 绿色：纯执行，便宜模型可做（带验收清单）
- 抓 14 讲字幕建时间戳索引（R2 执行段）
- D2 算力账 profiling
- 所有"跑实验配置 → 出 JSON + 图"的批量循环
- 图表生成、封面页填写、LecTrace 组装、GitHub push、ZIP 打包
- 参考文献格式化、LecTrace 字幕转写文本整理

### 交接触发器（便宜模型见到以下任一情况，停止并请求强模型）
1. 任何 group split 后测试 AUC < 0.55（先怀疑工程，不许解释为"模型不行"）
2. 结果 JSON 出现 NaN / 样本数对不上 / 正负例比例异常
3. 需要改评估协议、换 IDH 定义、改样本构建方式
4. 需要写任何"结论性"文字（进报告/数字表的话）

### 切换时点建议
**不要现在切。** 当前进度 P0 完成，D0/D1 尚未存在——它们恰恰是红色步骤。
最优切换点 = **D1 首个模型（XGBoost 基线）端到端跑通、数字合理之后**：届时协议已冻结、参考实现已验证，剩余 80% 工作量是绿色跑批。
