# 项目状态与可选检查工具

优先沿用已有有效工程；不为了使用此 skill 搬动大项目。新长项目可选用 `assets/project-template.json`。文件名可换，但指定一个权威入口，其他审核页和程序配置从它派生。

推荐把歌词、脚本、原始参考、候选画面、已选画面、音频、预览代码及导出分开保存。这里不规定目录名；manifest 中素材路径以 manifest 所在目录为基准，支持绝对路径但分享前应改为可移植路径。

## 模板字段

| 字段 | 约定 |
| --- | --- |
| `schema_version` | 当前模板为 1 |
| `revision` | 当前工程版本；改变选图、时间轴、音频或字幕时更新 |
| `route` | `original` / `adaptation` / `replacement` |
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

`init` 只创建不存在的 `project.json`，不覆盖项目，不下载依赖。`check` 只读，输出 JSON；错误退出 1，成功退出 0。草案缺少参数、定时或素材时给警告；`--for-export` 将这些必要项提升为错误，并检查导出授权记录。`--files` 检查已引用素材与音频是否存在、可选摘要是否匹配。它不渲染、不联网、不改变审核状态。

`--for-export` 不要求“每张图都由用户确认”。用户已经明确允许整片导出时，把该指令记录进授权即可；用户要求先预览时保持 `allowed: false`。限定旧 revision 的授权会被提示不匹配；未限定版本的授权仍需遵守后来收紧的用户指令。

字幕内容、艺术质量、听感和真实授权不能通过 JSON 验证。脚本通过只说明结构性检查通过；未使用此模板的工程应完成等价核对，不能要求用户重建工程才能继续。
