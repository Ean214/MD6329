# 录像要截哪一张 slide（逐条对照）

> 用途：报告里每一处 `Lecture N, ~mm:ss` 引用，都能对应到一张具体 slide。
> L1–L5 的页码来自本机 `C:/Users/LEYI/Downloads/MD6329_Lecture 0X.pdf`（已核对页内文字）；L6–L12 无 PDF，按字幕内容给出"找什么标题"。
> 截图存 `docs/lecture_watch/`，命名见最后一列。


> **时间戳来源**：全部取自课程 YouTube 播放列表（`PLORG7zBQosxw`）的英文字幕，用 yt-dlp 抓取，逐行带时间码。
> 如果 NTU Learn 播放器的时间轴与 YouTube 一致（同一份录像），按上表拖即可；若 NTU Learn 重新编码或分段，可能整体偏移几秒到几十秒。
> **可靠的定位方式不是时间码，是"听到这句话"**——见下表最后一列。听到就暂停，再往前/往后微调找那一页。

## 一、报告实际引用的时间戳（必须截这几张）

| 讲次 | 报告引用 | 那一刻在讲什么 | 要截的 slide（找这个标题/画面） | 页码 | 存成 | 听到这句就暂停 |
|---|---|---|---|---|---|
| L1 | ~00:40 | "你们在医院会遇到的临床数据类型"，课程定位 | **Welcome — Course Learning Outcomes**（三项能力）或紧接的 **Today's Agenda** | p3–p4 | `L1.png` | *…on the kind of clinical data you will encounter in our hospitals* |
| L2 | ~00:45 | 卷积层细节、三种损失、数据划分 | **The Convolutional Layer — Key Concepts**（Spatial Preservation 等要点） | **p19** | `L2.png` | *…convolutional layer in detail* |
| L3 | ~00:39 | 从分类转向分割，U-Net 是主力架构 | **SEMANTIC SEGMENTATION — U-NET ARCHITECTURE** | **p23**（架构图在 p24） | `L3.png` | *We leave classification behind and step up to segmentation* |
| L5 | ~00:38 | EHR 数据异质、不规则、部分缺失、按时间序列组织 | **MIMIC III – A Real Open-Access EHR Dataset**（38,597 患者 / 49,785 次住院） | **p17** | `L5.png` | *E H R data is heterogeneous, irregular, partially missing* |
| L6 | ~02:14 | RNN 的梯度消失，长序列受限，引出 LSTM | **Vanishing gradient / RNN 局限** 那一页（下一页即 LSTM 介绍） | — | `L6.png` | *…dependencies because of the vanishing gradient problem* |
| L7 | ~00:27 | 三大主线：word embedding → Transformer → BERT | **Today's Agenda / 三条链** 总览页 | — | `L7.png` | *Second, the transformer, the architecture that has eaten machine learning* |
| L7 | ~27:16 | 位置编码加到词向量上，注意力本身没有位置概念 | **Positional Encoding**（正弦/余弦那条公式 + "attention has no notion of position"） | — | `L7_pos.png` | *…vectors and added to positional encodings* |
| L8 | ~00:11 | 多模态：把不同医疗数据合成一个模型；自监督；对比学习 | **Multimodal learning 总览**（三个关键词并列那页） | — | `L8.png` | *Multimodal learning, how to combine different kinds of medical data* |
| L9 | ~00:53 | CLIP 架构细节回顾，然后讲生物医学里的 Transformer 变体 | **CLIP 架构图**（图文双塔 + 对比损失） | — | `L9.png` | *…revisit clip with the architectural details filled in* |
| L10 | ~00:27 | 第二部分强化学习：为奖励而行动，动作依赖历史 | **Reinforcement Learning 开篇**（agent–action–reward 示意） | — | `L10.png` | *Part two is reinforcement learning* |
| L11 | ~00:56 | 可解释/可解释性/透明/不确定性/公平/伦理 词汇表 | **Responsible AI 词汇表**（一串术语并列） | — | `L11.png` | *interpretability, explainability, transparency, uncertainty* |
| L11 | ~05:11 | 可视化、显著性图、代理模型；都只是"一瞥" | **Saliency maps / surrogate models** 那页 | — | `L11_saliency.png` | *visualization, saliency maps, and surrogate models* |
| L12 | ~00:39 | 联邦学习与去中心化数据；数据不能出院 | **Federated Learning 动机页**（数据留在医院，模型去找数据） | — | `L12.png` | *First, we explain federated learning and why decentralized data matters* |

> 注：L1–L5 的 slide 页脚带 "Adapted for NTU LKC School of Medicine — Chee Wei Tan"，可一并证明课程归属。

## 二、如果只为"看过了"留证（每讲一张，够用）

| 讲次 | 推荐截这一张 | 时间点 |
|---|---|---|
| L1 | Course Learning Outcomes | ~00:40 |
| L2 | The Convolutional Layer — Key Concepts（p19） | ~00:45 |
| L3 | SEMANTIC SEGMENTATION — U-NET（p23） | ~00:39 |
| L4 | 任意一页 Advanced Vision 模型对比图 | 中段 |
| L5 | MIMIC III 数据集页（p17） | ~00:38 |
| L6 | **The LSTM cell: three gates**（forget/input/output） | **~08:08** |
| L7 | **Query–Key–Value self-attention** 公式页 | **~43:04** |
| L8 | 对比学习（positive/negative pairs）示意 | 中段 |
| L9 | CLIP 架构图 | ~00:53 |
| L10 | RL 的 agent–action–reward 循环 | ~00:27 |
| L11 | Saliency maps | ~05:11 |
| L12 | Federated learning 示意图 | ~02:15 |
| GL1 / GL2 | 讲者标题页 | 开头 |

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
