# 提交前清单（Submission Checklist）

> 更新时间：2026-10-21。对应 MD6329 Final Course Project，deadline **Oct 25**。
> 状态标记：✅ 已完成 / ⬜ 待你操作 / ⚪ 可选

## 一、必交三件套

| # | 要求 | 现状 | 说明 |
|---|---|---|---|
| 1 | Final report PDF | ✅ | `report/MD6329_Final_Project_Report.pdf`，17 页（封面 2 + 正文 15），20 条参考文献，8 图 7 表 |
| 2 | LecTrace 演示（Python 代码） | ✅ | `lectrace/md6329_idh_control.py`；`lectrace build` 已生成 `_site/`（4.7 MB，131 步） |
| 3 | 全部补充材料打包成单个 ZIP | ✅ | `zip/MD6329_FinalProject_LE_YI.zip`，含 `src/`、`lectrace/`、`_site/`、`results/`、`docs/`、报告 |

## 二、待你本人操作的四件事

### ✅ 1. 课程录像（已完成 11/11）

**课程要求的是"看"和"在报告里标注讲次/时间"，不是交截图。** 原文两处：

- 必做清单：`Watch the Lecture Video Recordings`（进度由 NTU Learn 记录）
- Related Work：`connect your discussions with one of the Lecture Recordings ... and highlight relevant Slides/Time in Video Recordings`

报告已完成后者：**10 个讲次、18 处时间戳**，覆盖 Problem Formulation / Related Work / Approach / Experiments / Future Work 五节。

截图属**自留凭证**，不进 ZIP、不计分。已存 `docs/lecture_watch/`：L1、L2、L3、L5、L6、L7、L8、L9、L10、L11、L12（11/11 被引用讲次）。L4 与两场客座未在报告引用，不要求。

### ⚪ 2. GitHub 上传（**不是课程要求**，时间紧可跳过）

已排查到确切阻塞点，不是命令写错：

| 检查项 | 结果 |
|---|---|
| 本地分支 | 原为 `master`，**已改名为 `main`** |
| 远端地址 | `https://github.com/Ean214/md6329-idh-uf-control.git` |
| 凭据 | 未存（`cmdkey` 无 GitHub 条目，无 SSH key） |
| `git push` | `remote: Repository not found` → **GitHub 上还没有这个仓库** |

要 push，按这三步：

```bash
# 1) 浏览器打开 github.com/new，仓库名 md6329-idh-uf-control，不要勾 README
# 2) 回到终端
cd "E:/WorkBuddy Data/2026-09-04-10-40-13/project"
git push -u origin main        # 会弹登录窗口，登录后自动完成
```

封面已写"代码在补充 ZIP 中"，**不 push 完全合规**。

### ⬜ 3. 封面链接栏：二选一

封面 B 区现在写的是「代码在补充 ZIP 中，无公开仓库链接」。如果你 push 成功，可以改回真实链接：

| 栏位 | 现在 | push 后建议填 |
|---|---|---|
| Online repository | Code in supplementary ZIP | `https://github.com/Ean214/md6329-idh-uf-control` |
| LecTrace script or trace link | `lectrace/...py` in ZIP | 仓库内路径，或 Pages 地址 |

改完需要我重新导出封面 → 合并 PDF → 重建 ZIP（约 2 分钟），你说一声即可。

### ⚪ 4. 演示视频（封面有栏位，但不是硬性要求）

封面「Demo or presentation video」目前留空。若想补：屏幕录制 `lectrace serve` 的 10 分钟讲解即可，结构照脚本里的 5 个 execution state。不做也不影响合规——封面已注明不适用可留空。

## 三、提交动作

1. NTU Learn 对应作业入口上传 **PDF**（不要上传 ZIP 里的 `main.pdf`，那是未合并封面的正文）；
2. 同一入口上传 **ZIP**；
3. 上传后**下载回来抽查**：封面第 1 页是否为 Cover Sheet、参考文献 [16][17] 是否为 Chee Wei Tan、页码是否连续。

## 四、常见踩坑

- **别交未合并封面的 PDF**：`report/main.pdf` 是正文（15 页），没封面；要交 `report/MD6329_Final_Project_Report.pdf`（17 页）。
- **ZIP 里不要有临时文件**：已自动排除 `check_*.png`、`*_v8.pdf`、`.pkl/.npz` 等。
- **文件名**：课程未规定命名格式，现用 `MD6329_FinalProject_LE_YI.zip`；如需改学号格式，改完重新上传即可。
- **截止时间**：Oct 25（周六）。建议 10-24 前完成上传，留一天缓冲。
