# HEMOBP 数据集卡片（Dataset Card）

**来源**：Lin et al., "Dataset supporting blood pressure prediction for the management of chronic hemodialysis", *Scientific Data* 6:313 (2019)。figshare article 6260654，**CC BY 4.0**（可再发布，须署名）。
**本地路径**：`project/hemobp/{d1,idp,vip}.csv`（2026-10-13 下载，274 MB）。

## 采集方式
台湾某中心 Nikkiso DBB 透析机经 Vital Info Portal 网关自动采集 + 医院信息系统人口学数据。三班制，末班跨午夜。

## 会话重建规则（P0 已执行）
- session = 同一患者读数连续段，**间隔 > 6 h 开新 session**
- 透析日 = (session 开始时刻 − 8 h).date（对齐 `d1.keyindate` 的 08:00 戳）
- 产出：`results/sessions.csv`（197,269 行，每行一次透析）

## 队列特征（实测）
| 项 | 值 |
|---|---|
| 患者 | 1,072（idp 匹配率 100%） |
| 会话 | 197,269（d1 字段匹配率 82.7%，可算 UFR/IDWG 的子集 163,054） |
| 年龄 | 64.4 ± 13.5（16–96） |
| 糖尿病比例 | 43.1% |
| 单次时长 | 236 ± 24.5 min（中位 239） |
| IDWG（透前体重−干体重） | 中位 2.32 kg（均值 2.67） |
| 平均 UFR | 8.26 ± 3.38 mL/kg/h（中位 7.8；KDOQI 红线 13 以上占少数） |
| BP 测量间隔（session 内中位） | **50.7 min** |

## IDH 定义与发生率（实测）
| 定义 | 发生率 | 处置 |
|---|---|---|
| nadir SBP < 90 mmHg | **11.24%**（22,165 例） | **主定义** |
| nadir SBP < 100 mmHg | 20.73% | 敏感性分析 |
| max−nadir 降幅 ≥ 20 mmHg | 84.42% | 弃用（正常波动即触发） |

主定义依据：发生率落在文献 10–30% 区间内；阳性样本量充足；单变量稳健。

## 字段清单
- session 级（sessions.csv）：pid, start/end, duration_min, nadir_sbp, max_sbp, first_sbp, mean_sbp/dbp, mean_uf, max_uf, mean_blood_flow, bp_interval_med, weightstart, weightend, dryweight, temperature, gender, birthday→age, DM, idwg, ufr_ml_kg_h, 三个 IDH 标志位
- 时序级（后续 D0 构建样本时用 vip.csv 原始读数）：sbp, dbp, uf, blood_flow, dia_temp_value, conductivity, time

## 数据清洗规则（D0 执行）
1. 时长 ∈ [60, 480] min（剔除 0 min 碎片与 14 h 异常）
2. weightstart ∈ [20, 200] kg
3. idwg ∈ [−2, 10] kg（剔除 ±20–38 kg 录入错误）
4. ufr_ml_kg_h ∈ [0, 20]（剔除 36.5 极端值）
5. sbp 缺失的读数不计入 nadir 计算

## 已知局限（报告必须写明）
1. **中心透析场景**：4 h、卧床、血压约 50 min 一测；≠ WAK 的 6–8 h 可走动连续传感
2. **无 PPG / ECG / IMU / 血容量监测**——WAK 核心模态不在其中
3. BP 稀疏 → "提前 5–15 min 预警"不可验证，视野实验下限 ≈60 min
4. 无症状/用药/护士干预记录 → 无法用"症状性 IDH"定义；混杂诊断只能靠 UF 扰动间接暴露
5. uf 为泵设定值的读数记录，非实际脱水量闭环测量
