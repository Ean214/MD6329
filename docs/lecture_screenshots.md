# 录像要截哪一张 slide（逐条对照）

> 用途：报告里每一处 `Lecture N, ~mm:ss` 引用，都能对应到一张具体 slide。
>
> L1–L5 的页码来自本机 `C:/Users/LEYI/Downloads/MD6329_Lecture 0X.pdf`（已核对页内文字）；L6–L12 无 PDF，按字幕内容给出"找什么标题"。
>
> 截图存 `docs/lecture_watch/`，命名见最后一列。

> **时间戳来源**：全部取自课程 YouTube 播放列表（`PLORG7zBQosxw`）的英文字幕，用 yt-dlp 抓取，逐行带时间码。
>
> 如果 NTU Learn 播放器的时间轴与 YouTube 一致（同一份录像），按上表拖即可；若 NTU Learn 重新编码或分段，可能整体偏移几秒到几十秒。
>
> **可靠的定位方式不是时间码，是"听到这句话"**——见下表最后一列。听到就暂停，再往前/往后微调找那一页。

## 一、直接截课件：第几页、哪一页

> 下面页码已在本地课件 PDF 上逐页核对（`MD6329_Lecture 1/02/03/05.pdf`）。L6–L12 本机没有 PDF，只能给"页内标题 + Ctrl+F 关键词"。
> **注意区分两种页**：视频到那个时间点时，屏幕上往往是**议程页**；真正讲这个内容的**概念页**在后面。截图优先截概念页。

### L1 — 引用 ~00:40

| | 页码 | 页面标题 | 说明 |
|---|---|---|---|
| 引用时刻画面 | p4 | Today's Agenda | 议程页 |
| **建议截图** | **p3** | **Welcome — Course Learning Outcomes** | 三条能力：Broad Knowledge / Deep Learning Fluency / **Real-World Deployment**（对应报告里"临床数据 + 真实医学问题"） |

### L2 — 引用 ~00:45

| | 页码 | 页面标题 |
|---|---|---|
| 引用时刻画面 | p2 | Today's Agenda（"convolutional layer in detail" 是议程第二条） |
| **建议截图** | **p19** | **The Convolutional Layer — Key Concepts**（Spatial Preservation 等要点） |

### L3 — 引用 ~00:39

| | 页码 | 页面标题 |
|---|---|---|
| 引用时刻画面 | p2 / p21 | 议程或章节过渡页 |
| **建议截图** | **p23**（图在 **p24**） | **SEMANTIC SEGMENTATION — U-NET ARCHITECTURE**；p24 是 U-Net 的 572×572 输入、逐级下采样示意图 |

### L5 — 引用 ~00:38

| | 页码 | 页面标题 |
|---|---|---|
| 引用时刻画面 | p2 | Today's Agenda |
| **建议截图** | **p38** | **Recurrent Neural Networks - Architecture / Why RNNs for EHR?** —— 页内原文：*"Lab results drawn at irregular intervals"、"FC networks require fixed-length input"*，正是报告 E5 前那句"不规则、部分缺失"的依据 |

### L6–L12：按标题找页（本机无 PDF）

| 讲次 | 在课件里 Ctrl+F 搜 | 要截的画面 |
|---|---|---|
| L6 | `LSTM cell` 或 `three gates` | 三个门：forget / input / output 的结构图 |
| L7 | `Positional Encoding` | 正弦余弦公式 + "attention has no notion of position" |
| L7（备选） | `Query` 或 `scaled dot` | QKV 注意力计算式 |
| L8 | `Contrastive` | 正/负样本对 + 对比损失示意 |
| L9 | `CLIP` | 图文双塔架构图 |
| L10 | `Reinforcement` 或 `reward` | agent–action–reward 循环 |
| L11 | `Saliency` | 显著性图示例（原图 / 热力图并排） |
| L12 | `Federated` | 数据留在医院、模型下发的示意图 |

> 把 L6–L12 的 PDF 放到 `docs/lecture_slides/`，我可以像 L1–L5 一样把页码逐页核出来补进这张表。

## 二、如果只为"看过了"留证（每讲一张，够用）

| 讲次        | 推荐截这一张                                              | 时间点        |
| --------- | --------------------------------------------------- | ---------- |
| L1        | Course Learning Outcomes                            | ~00:40     |
| L2        | The Convolutional Layer — Key Concepts（p19）         | ~00:45     |
| L3        | SEMANTIC SEGMENTATION — U-NET（p23）                  | ~00:39     |
| L4        | 任意一页 Advanced Vision 模型对比图                          | 中段         |
| L5        | MIMIC III 数据集页（p17）                                 | ~00:38     |
| L6        | **The LSTM cell: three gates**（forget/input/output） | **~08:08** |
| L7        | **Query–Key–Value self-attention** 公式页              | **~43:04** |
| L8        | 对比学习（positive/negative pairs）示意                     | 中段         |
| L9        | CLIP 架构图                                            | ~00:53     |
| L10       | RL 的 agent–action–reward 循环                         | ~00:27     |
| L11       | Saliency maps                                       | ~05:11     |
| L12       | Federated learning 示意图                              | ~02:15     |
| GL1 / GL2 | 讲者标题页                                               | 开头         |

## 三、截图要求（一张合格证据的四个要素）

1. 浏览器地址栏可见 `learn.ntu.edu.sg`
2. 课程页头有 **MD6329**
3. 视频标题（Lecture N: ...）
4. 播放进度条 + 播放器时间码（与上表时间点对得上）

不要只截播放器区域，也不要从 YouTube 截。

## 四、命名与存放

```
E:\WorkBuddy Data\2026-09-04-10-40-13\project\docs\lecture_watch\
L1.png  L2.png  ...  L12.png  GL1.png  GL2.png
（报告引用的额外页可用后缀：L7_pos.png、L11_saliency.png）
```

检查进度：

```bash
cd "E:/WorkBuddy Data/2026-09-04-10-40-13/project"
C:/Users/LEYI/.workbuddy/binaries/python/envs/default/Scripts/python.exe src/check_watch.py
```
