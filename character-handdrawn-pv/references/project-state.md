# 项目状态与可选检查工具

优先沿用已有有效工程；不为了使用此 skill 搬动大项目。新长项目可选用 `assets/project-template.json`。文件名可换，但指定一个权威入口，其他审核页和程序配置从它派生。

新项目默认把歌词、分镜、方案、检查建议与复盘放入 `docs/`，提示词、生成任务和生成审核 JSON 放入 `generation/`。`project.json`、工程配置、交付索引和 `AGENTS.md` 留在工程根目录。其他素材、音频、源码和成片按项目需要分开保存；已有工程可继续使用现有目录名。

manifest 中的文档与素材路径均以 manifest 所在目录为基准。`brief.lyrics_file` 可填 `docs/lyrics.md`，`brief.storyboard_file` 可填 `docs/storyboard-v1.md`；未完成时保持 `null`。不要因为文件位于 docs 内就再拼接一次 docs。文档文件指针支持绝对路径，但分享前应改为可移植路径。

## 模板字段

| 字段 | 约定 |
| --- | --- |
| `schema_version` | 当前模板为 1 |
| `revision` | 当前工程版本；改变选图、时间轴、音频或字幕时更新 |
| `route` | `original` / `adaptation` / `replacement` |
| `directories` | 可选的目录配置；新模板含 `docs` 与 `generation`。目录值为项目内相对路径，不含 `..`；可使用已有命名，例如 `notes` |
| `brief.lyrics_file` / `brief.storyboard_file` | 可选文档路径或 null，以 manifest 所在目录为基准；`--files` 检查已填写的文件是否存在 |
| `output` | `width`、`height`、`fps`、`total_frames`；草案可为 null，fps 可为数值或 `"30000/1001"` |
| `timeline_policy` | `contiguous`：镜头连续且不重叠；`composited`：明确允许叠镜，工具仍检查覆盖 |
| `audio` | 每条包含 `id`、`role`、`path`、`offset_frames`，可加来源与时间原点说明 |
| `assets` | 每条包含唯一 `id`、`path`、`state`，可选 `sha256`；记录候选或已选素材，不强制逐张用户批准 |
| `scenes` | 唯一 `id` 和整数 `order`，`asset_id` 引用已选素材，半开区间 `[start_frame, end_frame)` |
| `review` | 已检查/已确认的 revision、范围、问题；不要由脚本自动声称人类批准 |
| `export_authorization` | `allowed`、用户指令原意 `evidence`、可选限定 `revision`；不替代真实授权 |

将人物、画风和未定事项记录在 `brief` 自由字段。字幕、音效或转场需要时间数据时可扩展字段，但保持同一时间基准，注明暂定/自动对齐/人工核对。检查工具只验证已定义的结构和时间不变量，不代替内容审核。

## 使用

在本机 Python 3.10+ 中运行，路径按当前 skill 的真实位置替换：

```text
python <skill>/scripts/project.py init <项目目录> --name <项目名>
python <skill>/scripts/project.py check <项目目录>/project.json
python <skill>/scripts/project.py check <项目目录>/project.json --files
python <skill>/scripts/project.py check <项目目录>/project.json --for-export --files
```

`init` 创建不存在的 `project.json`、`docs/`、`generation/` 和 `docs/README.md` 文档索引。已有 manifest 时拒绝初始化；已有文档索引保留原文，不创建虚构的歌词或分镜，不下载依赖，也不自动移动旧文件。

`check` 只读，输出 JSON；错误退出 1，成功退出 0。草案缺少参数、定时或素材时给警告；`--for-export` 将这些必要项提升为错误，并检查导出授权记录。`--files` 检查已填写的歌词/分镜文档以及已引用素材与音频是否存在、可选摘要是否匹配。未填写的文档指针不会阻止导出。它不渲染、不联网、不改变审核状态。

这些字段是 schema_version 1 的可选扩展，旧 manifest 不必增加 `directories` 或迁移原文档。用户要求整理已有项目时，先核对目标路径和同名冲突，移动后同步活动脚本、配置与 Markdown 链接；提示词 JSON 内的素材路径仍按 manifest 或项目记录约定解析，不能默认改成相对于 generation/。冻结导出包、输入基线和历史备份保持原样。

`--for-export` 不要求“每张图都由用户确认”。用户已经明确允许整片导出时，把该指令记录进授权即可；用户要求先预览时保持 `allowed: false`。限定旧 revision 的授权会被提示不匹配；未限定版本的授权仍需遵守后来收紧的用户指令。

字幕内容、艺术质量、听感和真实授权不能通过 JSON 验证。脚本通过只说明结构性检查通过；未使用此模板的工程应完成等价核对，不能要求用户重建工程才能继续。
