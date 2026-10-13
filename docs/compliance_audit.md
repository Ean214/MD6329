# 合规核对表（Compliance Audit）— MD6329 Final Course Project

> 对账日期：2026-10-13。依据：封面页 docx 原文 + 用户提供的 "Last Reminder" mandatory 段落 + 我方的 brief 解析记录。
> 2026-10-13 晚：用户提供了 brief 完整原文，已按全文复核并补充 F 段。
> 早期版本的这句提示已作废：。若课程系统中有额外条款（页数上限、命名规则、是否需答辩），本表未覆盖。**

## A. Mandatory（原文明确要求）

| # | 要求 | 现状 | 判定 |
|---|---|---|---|
| A1 | Cover Sheet 附在报告前 | `report/MD6329_Final_Project_Report.pdf` 第 1–2 页为官方封面，13 题全部填写 | ✅ |
| A2 | 提交 LecTrace Explanation-Presentation Python 脚本 | `lectrace/md6329_idh_control.py`；`lectrace run` 131 步，`lectrace build` 出 `_site/` | ✅ |
| A3 | 看 Lecture Video Recordings（NTU Learn 记进度→考勤） | 14 讲英文字幕已抓取并建索引；**NTU Learn 点开只能用户本人做** | ⚠️ 待用户 |
| A4 | Related Work 与课程录像相联系（whenever possible） | 正文挂 L5/L6/L7/L8/L10/L11/L12 共 7 处时间戳，并在 Problem Formulation 与 Related Work 两处 `\citep{md6329lectures}` | ✅ |
| A5 | 至少训练一个深度学习模型于生物医学数据 | 5 个模型全部在 HEMOBP（真实临床数据，CC BY 4.0）上训练 | ✅ |
| A6 | 报告 PDF（NeurIPS 模板） | 官方 `neurips_2025.sty`（`[main, final]`），tectonic 本地编译，9 页正文 | ✅ |
| A7 | 全部补充材料打包为单个 ZIP | `zip/MD6329_FinalProject_LE_YI.zip`，114 文件 / 19.1 MB | ✅ |
| A8 | 引用 ≥10 篇 | 参考文献 **16 条**，全文 34 处数字引用（`[4, 11, 12]` 已排序） | ✅ |
| A9 | 所有作为基础的代码须在正文引用 | Approach 中显式引用课程作业基础代码 `\citep{md6329assignment}` 与 pyvene 工具库 | ✅ |
| A10 | 讨论 Software 3.0 对编码/实验流程的贡献 | Approach 末尾独立一段，含具体三例（会话构建重构、sigmoid 饱和误读、设备放置 bug） | ✅ |
| A11 | Honor Code：GenAI 允许但须披露 + 能解释辩护 | 报告 Software 3.0 段披露；封面 bug 题与 LecTrace 题均如实说明 AI 参与范围 | ✅ |

## B. 报告六节与评分权重覆盖

| 节 | 权重 | 现状 | 判定 |
|---|---|---|---|
| Problem Formulation | 15% | 三代解决方案谱系 + 三个可检验子问题 + 课程录像映射 | ✅ |
| Related Work | 15% | 闭环超滤（Santoro/Ronco/Dong 2024）、IDH 定义与流行病学、ML 预测三线；明确指出两个空白 | ✅ |
| Data | 15% | HEMOBP 队列、重建规则、描述统计表、IDH 三定义表、采样设计、**独立局限段** | ✅ |
| Approach | 25% | 任务形式、三组模态、五模型、group split、评估协议、三控制策略、因果诊断、Software 3.0 | ✅ |
| Experiments | 25% | E1–E6 六个实验，6 张表 + 7 张图，全部 in-silico 标注 | ✅ |
| Conclusion | 5% | 三问三答 + 边界声明 + 产品含义 + 未来工作 | ✅ |

## C. 本轮发现并已修复的缺陷

| 缺陷 | 严重度 | 修复 |
|---|---|---|
| 参考文献 `note` 字段被 `plainnat` 印出，暴露内部标记 `[OK]`(11 处) / `[CHK: journal/issue]`(2 处) | **高**（正式文书出现工作流标记） | 将全部 note 改为 `%` 注释；重编译后残留 0 处 |
| 全文 0 处数字引用（natbib 默认作者-年份格式） | **高** | `\PassOptionsToPackage{numbers,square,sort,compress}{natbib}` → 34 处数字引用且编号升序 |
| 课程录像仅在正文提及、从未 `\cite`，故 A4 在形式上不成立 | **中** | 新增两处 `\citep{md6329lectures}`（Problem Formulation + Related Work） |
| 基础代码（课程作业）未在正文引用，A9 不成立 | **中** | 新增 `@misc{md6329assignment}` 并在 Approach 引用 |
| pyvene 工具库提及但未引用 | 低 | 补 `\citealp{wu2024pyvene}` |
| 含未核实的 TFT 占位文献 | 低 | 从 bib 移除（未在正文引用，不会印出；保留 TODO 注释） |

## D. 仍待用户处理 / 我无法核实

| 项 | 说明 |
|---|---|
| NTU Learn 点开录像 | 考勤由 NTU Learn 进度记录，只能用户本人操作 |
| GitHub push | 仓库已初始化、远端已配（`github.com/Ean214/md6329-idh-uf-control`），push 需用户凭据 |
| 封面 "Demo or presentation video" 栏 | 当前留空。若课程期望交演示视频，需补录；否则留空即可（封面注明"不适用可留空"） |
| 封面 "Overleaf / report link" 栏 | 当前留空；可填 GitHub 仓库地址 |
| brief 完整原文 | 未留档，无法核对是否存在页数上限、命名规则、答辩环节等未覆盖条款 |
| 小组规模 | 单人（brief 称按组规模校准评分，solo 属合规但工作量预期相应较低） |

## E. 结论

**Mandatory 项全部满足**（A3 考勤与 push 属用户手工动作）。报告六节与权重全覆盖，16 条引用中已含课程录像与课程作业代码。交付三件套齐备。


---

## F. 按 brief 完整原文的复核（2026-10-13 第二轮）

### F1. 主题判定 ✅ 合规

brief 允许三类选题，我们的项目落在前两类：

| brief 的选题类型 | 我们对应的地方 |
|---|---|
| **Novel problem**：新问题/新任务 | 提出"去掉光学血容量传感器后，仅用常规机器数据能否支撑超滤闭环"——这是新任务形式，不是复现 |
| **Novel analysis**：重新实现并批判分析、比较算法变体、考察不同输入表示、解释已有模型、预测不同结局 | 五模型对照（算法变体）+ 模态消融（输入表示）+ pyvene 干预（模型解释）+ 视野与容差敏感性 |

关键反证："Simply re-running an existing implementation is not sufficient" —— 我们不是复跑：
问题是我们自己重新定义的（并且**推翻了毕设原有的"预测优于 PID"框架**），控制权衡表是本项目首次量化，混杂诊断是本项目首次提出。

**必须满足的四项能力，逐项对照**：

| brief 要求 | 现状 |
|---|---|
| thoughtful problem formulation | ✅ 三代方案谱系 + 三个可检验子问题 |
| model design | ✅ 四种神经网络（含从零 Transformer）+ 一组树模型基线 |
| **training and hyperparameter selection** | ✅ **本轮补齐**：Approach 新增 Training procedure 段（loss/优化器/lr/batch/epoch/早停/种子）；Experiments 新增 **E7 超参数研究**（XGBoost 深度×树数网格 + CNN+MLP 学习率/类别权重扫描，见 Fig. 6） |
| empirical analysis | ✅ E1–E7 共 7 个实验、7 表 9 图 |

### F2. 本轮补齐的 5 处（原文逐字点名，此前未覆盖）

| # | 原文要求 | 此前 | 处理 |
|---|---|---|---|
| F2-1 | Approach 须含 "loss function, optimization, and relevant hyperparameters" | 报告 0 处 loss/Adam/lr/epoch | 新增 Training procedure 段（binary cross-entropy + `pos_weight` 17.1:1、Adam lr 1e-3、batch 256、≤10 epochs、patience 2、seed 42、dropout、Transformer d=64/4 heads/2 layers、XGBoost 全参数） |
| F2-2 | Goal 段要求 "training and hyperparameter selection" | "hyperparameter" 出现 0 次 | 新增 **E7**：XGBoost 深度 3/6/9 × 树数 200/600/1200 网格 + CNN+MLP lr 3 档 × 类别权重 2 档；发现树深主导（0.1904 vs 0.1520），调参后 E1 排序边际收窄 |
| F2-3 | Problem Formulation 须 "Discuss how Software 3.0 ... may have helped with problem formulation" | Software 3.0 仅在 Approach | Problem Formulation 末补：GenAI 用于文献普查 + 检验"预测优于 PID"框架是否成立（结论：不成立，且改变了研究问题本身） |
| F2-4 | Experiments 须 "Discuss how Software 3.0 or Gen-AI contributed to coding and experimental evaluation" | 无 | Experiments 末补 "Software 3.0 in the experimental workflow" 段（两个实验源于 AI 提出的检查；同时说明 AI 首版会话构建失败、验证仍需人工） |
| F2-5 | Data 须含 "qualitative examples where appropriate" | 无 | 补一个真实样本：IDWG 1.88 L / 已脱 0.46 L / 余 2.42 h / 临床 UFR 0.48 L/h → 残余 266 mL 且未发生 IDH，说明边界样本的标签噪声 |

### F3. Honor Code 细化项

| 原文 | 处理 |
|---|---|
| "disclose substantial use of Generative AI **in your code and writeup**" | ✅ 本轮为 `src/*.py` 与 `lectrace/*.py` **全部 14 个脚本**加了 disclosure docstring |
| "Any code used as a basis ... must be referenced and cited in the body" | ✅ 已引课程作业代码与 pyvene |
| "may not provide another group's code to an AI system" | ✅ 无外部小组代码；仅用本人作业 2 代码与公开库 |
| "If you combine this course project with a project from another class" | ⚠️ 说明：本项目**取材于**用户 2026 年 5 月已完成答辩的本科毕设（郑州大学，非并行课程），数据、模型、实验全部重做，非同一份作业的复用；毕设本身在报告中未作为课程作业提交 |

### F4. Lectrace 呈现要求 ✅

原文：2–3 min 问题/动机/方法 → **3–5 个精选 execution state**（每个说明发生了什么、什么变了、为什么重要）→ 不要整条 trace → 结尾给关键结果与医疗解读。
现状：`lectrace/md6329_idh_control.py` 恰好 5 个 state（会话重建 / 泄漏边界 / 患者切分 / 控制决策点 / 干预消融），前后各有一段开场与收尾（含临床解读）。✅

### F5. 提交三件套 ✅

(i) 报告 PDF `report/MD6329_Final_Project_Report.pdf`（12 页）✅
(ii) Lectrace Python 脚本 ✅
(iii) 单 ZIP `zip/MD6329_FinalProject_LE_YI.zip`（121 文件 / 19.4 MB）✅

### F6. 仍未覆盖 / 待用户

- NTU Learn 点开录像（考勤，只能本人操作）
- GitHub push（远端已配，需用户凭据）
- 封面 "Demo or presentation video" 与 "Overleaf / report link" 两栏留空；若课程期望演示视频需补录

## G. 结论（第二轮）

按 brief **完整原文**逐字复核：主题判定合规（Novel problem + Novel analysis），"四项能力"全部满足（超参数选择为本轮补齐），7 处原文点名要求中 5 处此前未覆盖、现已补齐，Honor Code 的代码侧披露已加。交付三件套齐备，报告 12 页、16 条引用、34 处数字引用、0 处内部标记。
