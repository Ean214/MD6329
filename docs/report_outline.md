# 报告论证结构（Report Outline）— 红色任务：先定论证，再填内容

> NeurIPS 模板六节。每节写清：论点 → 证据 → 边界。全部 in-silico 表述。
> 标题（暂定）：*Feasibility of Sensor-Light Closed-Loop Ultrafiltration Control in Hemodialysis: An In-Silico Study on Routine Machine Data*

## 1. Problem Formulation (15%)
- 临床问题：IDH 发生率高（本数据 11.2%）、危害大（心肌顿抑、死亡率）
- 现有解法及其缺口：PID 式事后反应 → 生物反馈闭环（Hemocontrol/BVM，28 项研究 23 项有效）但依赖**光学血容量传感器**，可穿戴/居家场景装不了
- 我们的问题：**仅用常规机器数据（无专用传感器）能否支撑"预测→调 UFR"的闭环？代价是什么？**——把产品可行性问题转化为三个可检验子问题（预测多早/多准；调控的 trade-off；因果可信度）
- 与课程连接：序列建模（L6/L7）、多模态（L8）、可解释性（L11）

## 2. Related Work (15%)
- 三代技术线：事后反应（PID/阈值）→ 血容量生物反馈闭环（Santoro 1998; Ronco 2000; Dong 2024 综述）→ ML 预测（RF/Bi-LSTM/XGBoost/TFT）
- 空白：现有 ML 预测几乎只做"报警"，不与控制闭环耦合评估；也不量化"降 UFR 的代价"
- 我们的位置：把预测模型放进控制回路做 in-silico 评估 + 正面处理混杂
- ≥10 引用 + 挂课程录像（L6/L7/L8/L11 时间戳，建索引后填）

## 3. Data (15%)
- HEMOBP（CC BY 4.0）：1,072 患者 / 197,269 透析次；字段、重建规则、清洗
- EDA：时长 236 min、UFR 中位 7.8 mL/kg/h、IDH(nadir<90) 11.24%、BP 中位间隔 50.7 min
- 采样设计：预测点 T∈{30,60,90,120}，只用 ≤T 信息，标签=余程 nadir<90（防泄漏）
- **局限节必须写**：中心透析 ≠ WAK；无 PPG/ECG/IMU/血容量；BP 稀疏；无症状记录

## 4. Approach (25%)
- 任务形式：分类为主（"余程是否 IDH"），轨迹模型仅用于控制模拟内部
- 四模型：XGBoost（临床基线）/ 1D-CNN+MLP 融合（本科架构迁移）/ LSTM / 从零 Transformer encoder（承作业 2：正弦位置编码、padding mask、多头注意力）
- 评估协议：按患者 group split 70/15/15、AUPRC 主指标、固定种子
- 控制策略：恒定 / 反应式（模拟生物反馈）/ 预测式（模型在候选 UF 网格中选最小风险解，受残余液体容差约束）
- E6 因果诊断：UF 扰动梯度 + pyvene 层消融

## 5. Experiments (25%)
- E1 四模型对照（表+图）→ C1/C2
- E2 算力账：参数/FLOPs/延迟 vs AUPRC（Pareto 图）→ C2
- E3 视野曲线 30/60/90/120 → C1（"5–15 min 需连续传感"的证据）
- E4 模态消融（生理/机器设置/静态）→ C3
- **E5 三策略权衡表：IDH 率 vs 残余液体 mL vs 需延长 min（核心表）**→ C4/C5
- E6 因果诊断：扰动梯度 + 粗关联图 → 暴露混杂 → Discussion
- 每个实验：数字进表、图进 results/、结论进 claims_register

## 6. Conclusion (5%)
- 回答三个子问题：能预测多早多准（E1/E3 数字）；trade-off 存在且可量化（E5 表）；因果可信度有限（E6）
- **明确边界**：in-silico 非临床验证；回顾性数据无法验证调控策略本身（混杂）；WAK 场景需高频传感+前瞻试验
- 落地路线一句话：医生预设安全包络 + 物理层 fail-safe（呼应本科设计）+ 本研究证明的"预测价值上限"

## Software 3.0 节（放 Approach 或 Experiments 末尾）
- AI 编码助手在数据处理（会话重建 3 次重构优化）、pyvene 坑位定位（sigmoid 饱和）中的实际贡献
- 与封面页"最耗时的 bug"题呼应；如实披露（Honor Code 要求）
