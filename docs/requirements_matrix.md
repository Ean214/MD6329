# 课程要求全景对照表（Requirements Matrix）

> 依据：课程 Final Course Project 原文 + 封面页 13 题。核对日期 2026-10-25。
> 判定：✅ 已满足 ｜ ⏳ 待你操作 ｜ ⚪ 非要求（可选）

## A. 项目要求（Project）

| # | 原文要求 | 现状 | 证据 |
|---|---|---|---|
| A1 | must involve training **at least one deep learning model** on biomedical/healthcare data | ✅ 4 个神经网络 + XGBoost，全部在 HEMOBP 真实临床数据上训练 | `src/d1_nn.py`、E1 表 |
| A2 | simply re-running an existing implementation is not sufficient；须体现 **problem formulation / model design / training and hyperparameter selection / empirical analysis** | ✅ 问题自己定义（去传感器闭环可行性）；⑤ 模型自建；E7 超参研究（按验证集选参）；E1–E9 实证 | §1、§4、§5 E1–E9 |
| A3 | groups of **1–2 students** | ✅ 单人（评分按组规模校准） | 封面 A 区 |
| A4 | 鼓励 Software 3.0，但须 **critically evaluate** 并解释设计决策 | ✅ 三处讨论，且写明"AI 曾同意我的错误解读" | §1 末、§4 Software 3.0、§5 实验流程段 |
| A5 | 须有 **appropriate baselines** 与可复现细节（preprocessing / architecture / **training procedure** / **loss function** / **optimization** / **hyperparameters**） | ✅ XGBoost + MLP 作基线；Training procedure 段列全 BCE、pos_weight、Adam、lr、batch、epochs、早停、seed、dropout | §4 Training procedure、`src/` |
| A6 | 实验须 **为假设提供证据**（baselines / ablation / hyperparameter / robustness / error analysis / interpretation / representations） | ✅ 基线对照、模态消融、视野与容差敏感性、超参扫描、干预式解释 | E1–E9 |
| A7 | 使用 **appropriate healthcare metrics**，配图表 | ✅ AUPRC / AUROC / sens@80%spec / Brier / PPV / 假报警负担；8 图 7 表 | 全文 |
| A8 | 讨论 **Software 3.0 对编码与实验流程的贡献** | ✅ 两个实验源于 AI 提出的检查；同时写明 AI 首版会话构建失败 | §5 末 |

## B. 报告要求（Report）

| # | 原文要求 | 现状 | 证据 |
|---|---|---|---|
| B1 | 截止 **Oct 25** | ⏳ 今天截止，未上传 | — |
| B2 | **NeurIPS 模板**，排版接近已发表论文 | ✅ 官方 `neurips_2025.sty`，`[main, final]` 编译 | `report/main.tex` |
| B3 | Title / Authors / **Student ID** | ✅ 标题 + LE YI + G2605168D | 第 1 页 |
| B4 | Abstract | ✅ 问题/方法/贡献/关键结果 | p3 |
| B5 | **Problem Formulation (15%)** | ✅ 临床问题、三代方案、三个子问题、GenAI 的作用 | §1 |
| B6 | **Related Work (15%)**：联系 Lecture Recordings 并 **highlight relevant Slides/Time**；**≥10 引用** | ✅ 10 个讲次、18 处时间戳（五节分布）；**20 条参考文献** | §1/§2/§4/§5/§6 |
| B7 | **Data (15%)**：来源、特征、统计、预处理、定性例子 | ✅ 队列与来源、描述统计、IDH 三定义、清洗链与分视野排除表、一个真实会话示例 | §3、Table 1 |
| B8 | **Approach (25%)**：可复现细节、设计取舍、GenAI 角色 | ✅ 架构、训练程序、控制策略、因果诊断、Software 3.0 | §4 |
| B9 | **Experiments (25%)**：证据、指标、图表、GenAI 贡献 | ✅ E1–E9，含校准审计与置信区间 | §5 |
| B10 | **Conclusion (5%)**：发现、学到什么、局限、未来工作 | ✅ 含证据分层表与完整研发路线 | §6 |

## C. 提交要求（Submission）

| # | 原文要求 | 现状 | 文件 |
|---|---|---|---|
| C1 | (i) final report as **PDF** | ✅ 17 页（封面 2 + 正文 15） | `report/MD6329_Final_Project_Report.pdf` |
| C2 | (ii) presentation slides **in Python code using Lectrace** | ✅ 5 个 execution state，131 步 | `lectrace/md6329_idh_control.py`、`_site/` |
| C3 | (iii) all supplementary material in **a single ZIP** | ✅ 19.9 MB / 195 文件（含 `_site/`，解压可离线看讲义） | `zip/MD6329_FinalProject_LE_YI.zip` |
| C4 | **Any code used as a basis must be cited in the body** | ✅ 课程作业代码 + pyvene 均在正文引用 | §4 |

## D. LecTrace 演示要求

| # | 原文要求 | 现状 |
|---|---|---|
| D1 | **10 分钟**：2–3 min 问题/动机/方法 → **3–5 个精选 execution state** → 关键结果 + 医疗解读 | ✅ 恰好 5 个 state（会话重建 / 泄漏边界 / 患者切分 / 控制决策点 / 干预消融），前后各有开场与收尾 |

## E. Honor Code

| # | 原文要求 | 现状 |
|---|---|---|
| E1 | 引用外部来源 | ✅ 20 条参考文献 |
| E2 | **disclose substantial use of GenAI in your code and writeup** | ✅ 报告三处 + 封面 + **15 个脚本的 docstring** |
| E3 | 不得使用其他小组代码 | ✅ 仅本人作业 2 代码与公开库 |
| E4 | 必须能解释与辩护 | ✅ 主张台账 `docs/claims_register.md`、面试数字表 |
| E5 | 若与其他课程项目合并，须遵守该课程规定 | ✅ 未合并（取材于已完成的本科毕设，非并行课程作业） |

## F. 封面页

| # | 要求 | 现状 |
|---|---|---|
| F1 | 作为报告**第 1 页**附上 | ✅ 第 1–2 页 |
| F2 | 13 题全部作答 | ✅ 含 bug 题（sigmoid 饱和）、录像改进题（L6 门控缺数值实例） |

## G. 观看录像

| # | 要求 | 现状 |
|---|---|---|
| G1 | Watch the Lecture Video Recordings（NTU Learn 记录进度） | ⏳ 只能你本人点开；截图 11/11 齐全（自留凭证，非提交项） |

---

## 结论

**A–F 全部满足，只剩 G1 与 B1 两个"动作"**：点开录像、上传两件文件。

GitHub 仓库**不是要求**（封面注明"不适用可留空"），当前封面写"代码在补充 ZIP 中"，合规。
