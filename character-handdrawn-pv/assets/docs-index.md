# 项目文档

本目录用于歌词、分镜脚本、制作方案、检查建议和复盘。按项目需要命名，不必一次创建全部文档。

- 当前歌词：写入 `project.json` 的 `brief.lyrics_file`。
- 当前分镜：写入 `project.json` 的 `brief.storyboard_file`。
- 尚未完成的文档路径保持 `null`，不把占位文件当作已完成的内容。

所有文档路径以 `project.json` 所在目录为基准，例如 `{{docs_dir}}/lyrics.md`、`{{docs_dir}}/storyboard-v1.md`。本文档中的 `public/`、`production/`、`src/` 等工程路径也采用同一基准。

提示词、生成任务和生成审核 JSON 放入 `{{generation_dir}}/`。项目配置、交付入口与 `AGENTS.md` 保留工程根目录。已有工程沿用其原有组织方式；移动文件时同步更新脚本、配置和文档链接，不改冻结存档。
