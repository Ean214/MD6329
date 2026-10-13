# 合规核对表（Compliance Audit）— MD6329 Final Course Project

> 对账日期：2026-10-13。依据：封面页 docx 原文 + 用户提供的 "Last Reminder" mandatory 段落 + 我方的 brief 解析记录。
> **注意：brief 完整原文未留档（当时贴入对话）。若课程系统中有额外条款（页数上限、命名规则、是否需答辩），本表未覆盖。**

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
