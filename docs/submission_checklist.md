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

### ⬜ 1. NTU Learn 点开课程录像（考勤）

课程明确要求观看 14 讲录像，**进度由 NTU Learn 记录**。注意：

- 必须从 **NTU Learn 的链接**进入（YouTube 直接看不会计入进度）；
- 建议看完一讲就截一张图（含讲次标题 + 你的账号/进度条），存到 `docs/lecture_watch/`；
- 14 讲清单与时间戳索引见 `docs/lecture_index.md`（L1–L12 + 两场客座）。

如果你想留一份可核对的记录，可用下面的模板：

```
| 讲次 | 日期 | 时长 | 截图文件 |
|---|---|---|---|
| L1 | 2026-10-21 | 58 min | lecture_watch/L1.png |
```

### ⬜ 2. GitHub 上传（可选但建议）

仓库已初始化、已提交 6 次、远端已配好，**只差 push**（需要你的 GitHub 凭据，本机无 `gh` CLI）：

```bash
cd "E:/WorkBuddy Data/2026-09-04-10-40-13/project"
git push -u origin main
```

如果远端仓库还没建：先在 GitHub 建一个**空**仓库 `md6329-idh-uf-control`（不要勾 README），再执行上面的命令。

推送成功后，如果你想让 LecTrace 有可点开的在线版：

```bash
lectrace init      # 生成 GitHub Actions 工作流
git add .github && git commit -m "Add Pages workflow" && git push
```

然后在仓库 Settings → Pages 选择 GitHub Actions。**注意**：`lectrace init` 会改写配置，执行前先确认它不会覆盖现有文件（它会提示）。

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
