# 角色手书制作

**character-handdrawn-pv** · 面向 Codex 的通用角色音乐手书制作 skill。

从角色设定、歌词和音乐出发，编写分镜、统一画风、制作整幅插画，再完成字幕、动效、音频与视频合成。适用于已有角色和 OC，不限定题材、画风、镜头数量、分辨率或帧率。

这是可复用的制作流程与检查工具。绘图、演唱和视频合成使用当前环境中可用的工具；仓库不附带图像模型、声库、音色模型或一键生成视频程序。

## 三种制作路线

| 路线 | 适合的需求 | 保留与调整 |
| --- | --- | --- |
| 原创分镜 | 根据歌词讲述角色经历 | 从音乐结构与人物情绪设计镜头 |
| 原片改编 | 参考已有手书的气质、构图或节奏 | 按新歌词和剧情选择性继承、重排画面 |
| 严格换角 | 让指定角色出演原 PV | 保留分镜、时长、动作与字幕时钟，逐镜匹配 |

可以从任意阶段接入已有项目，也可以只做分镜、单镜修图、音频、合成或封面。严格换角阶段可配合已安装的 `pv-character-replacement` skill；其他路线无需它。

## 安装

在 Codex 中发送：

```text
$skill-installer
从 https://github.com/CandyRGB/skill-character-handdrawn-pv
安装 character-handdrawn-pv 目录中的 skill。
```

也可以下载或克隆本仓库，将整个 `character-handdrawn-pv` 目录放入 Codex 的个人 skill 目录 `~/.agents/skills/`。Windows 对应 `%USERPROFILE%\.agents\skills\`；仅当前项目使用时，可放入该项目的 `.agents/skills/`。

安装后调用 `$character-handdrawn-pv`。若列表未更新，可重新启动 Codex。安装与发现机制见 [OpenAI 官方 skills 文档](https://developers.openai.com/codex/skills)。

## 开始使用

准备已有材料即可，缺少内容可以在制作过程中补齐：

- **角色**：设定图、造型版本、重要识别特征；正侧背面或局部参考按镜头需要提供。
- **内容**：歌词、角色经历、想表达的情绪；如有对白，提供真实录音或标记待补。
- **音乐**：成曲、伴奏、导唱或 MIDI/歌声工程，明确各文件类型。
- **视觉参考**：目标画风、原片，以及需要保留的构图、节奏或动作。
- **交付要求**：项目目录、画幅、工具与预算，以及本次做到哪一步。

### 先写分镜

```text
$character-handdrawn-pv
根据这些角色设定和歌词制作音乐手书。
采用暖色水彩线稿，人物以中近景为主。
已有最终演唱，不需要重新生成音频。
先完成全片分镜脚本，暂不绘图。
```

### 参考原片改编

```text
$character-handdrawn-pv
参考这支手书的线条、配色和节奏，根据我的新歌词重新组织剧情。
优先绘制人物与场景统一的整图，保留正确的水体和家具遮挡。
先做代表性样张，再按通过的风格制作整片。
```

### 接着合成预览

```text
$character-handdrawn-pv
沿用项目中已确认的分镜和画面，使用 Remotion 合成。
加入与歌词和声音事件对应的字幕与图形动效。
本次只提供可播放预览，等我明确说导出后再导出视频。
```

## 制作流程

1. **整理输入与版本**：确认路线、当前阶段、素材和已有决定，沿用有效工程。
2. **确定音乐与故事结构**：覆盖前奏、主副歌、间奏、独白和尾奏，区分音乐位置与故事时间。
3. **编写可绘制的分镜**：明确剧情作用、景别、人物占比、动作接触、遮挡和文字区域，检查重复与时间倒置。
4. **建立角色和视觉基准**：区分身份、画风和构图参考，用少量代表镜头验证难点。
5. **成组制作与局部修订**：以整幅场景统一人物和环境，核对眼睛左右、头发连接、手脚、服装及连续性。
6. **合成与播放预览**：共用时间轴，添加适量字幕、动效和混音，检查实际播放结果。
7. **按授权导出与交付**：验证编码后文件；需要时再制作风格一致的封面与简介。

已有可用成曲时直接使用。需要填词演唱时，先做短段导唱检查，再决定是否进行全曲合成与音色转换；不强制购买或安装某款软件。

用户要求先预览时不导出；已经明确授权本次导出时，完成检查后直接执行，不重复要求确认。画面、音频与整片的确认范围分别记录。

## 工具与依赖

| 阶段 | 所需能力 |
| --- | --- |
| 歌词、分镜、项目记录 | 可读取参考与本地文件的 Codex 环境 |
| 插画生成与修图 | 可用的图像生成/编辑工具，以及角色、画风和构图参考 |
| 演唱与对白处理（可选） | 可用的合成器、声库、音色转换或人声分离工具 |
| Remotion 合成（可选） | 可用的 Remotion / Node.js 环境，以及项目需要的字体与媒体工具 |
| 项目检查脚本（可选） | Python 3.10+，仅使用标准库，无需额外 Python 包 |

Remotion 是一种合成实现；用户指定其他剪辑器时可沿用其工程。skill 不自动安装上表工具，也不包含它们的付费服务或使用额度。

## 项目模板与时间轴检查

长项目可选用 [项目模板](character-handdrawn-pv/assets/project-template.json) 记录镜头、素材、时间轴、版本和导出范围。已有工程不必为此重新建目录。

新项目初始化后具有以下结构：

```text
my-pv/
├── project.json
├── docs/
│   └── README.md       # 文档索引；已有内容不会被覆盖
└── generation/         # 提示词、生成任务和审核 JSON
```

歌词、分镜、方案与复盘集中放在 `docs/`；工程配置、交付入口和 `AGENTS.md` 保留根目录。实际文档按需要创建，将 `brief.lyrics_file`、`brief.storyboard_file` 分别填为 `docs/lyrics.md`、`docs/storyboard-v1.md` 等路径；未完成时保留 `null`。这些路径统一相对于 `project.json`，已有项目仍可沿用原路径。

以下命令从仓库根目录执行，将路径换成自己的项目位置：

```bash
# 创建 project.json；已有文件时拒绝覆盖
python character-handdrawn-pv/scripts/project.py init ./my-pv --name "我的角色手书"

# 检查结构与时间轴
python character-handdrawn-pv/scripts/project.py check ./my-pv/project.json

# 同时检查引用文件与可选 SHA-256 摘要
python character-handdrawn-pv/scripts/project.py check ./my-pv/project.json --files

# 检查导出所需字段及已记录的授权
python character-handdrawn-pv/scripts/project.py check ./my-pv/project.json --for-export --files
```

脚本检查重复 ID、文档与素材引用、帧区间空缺与重叠、文件和摘要，以及限定版本的导出授权。草案可保留未定时间和参数；检查不会渲染、联网或改写审核状态。旧 manifest 无需补目录字段，不会被自动迁移。

> [!NOTE]
> 检查通过只表示数据结构符合约定，不代表插画、听感或音画同步已经合格。授权字段是对真实用户指令的记录，不能自行填写来代替授权。

详细字段与行为见 [项目状态说明](character-handdrawn-pv/references/project-state.md)。

## 文件结构

```text
.
├── README.md
└── character-handdrawn-pv/
    ├── SKILL.md                         # 主入口与阶段路由
    ├── agents/openai.yaml               # Codex 显示信息
    ├── assets/
    │   ├── project-template.json        # 可选项目模板
    │   └── docs-index.md                # 新建工程使用的文档索引
    ├── scripts/project.py               # 初始化与只读检查
    └── references/
        ├── storyboard-and-style.md      # 分镜、剧情与视觉设计
        ├── art-and-review.md            # 参考分工、绘图与局部修订
        ├── audio-and-timing.md          # 填词演唱、对白与时间基准
        ├── remotion-and-delivery.md     # 合成、预览、导出与发布素材
        └── project-state.md             # 版本、素材与检查工具
```

完整制作指令见 [SKILL.md](character-handdrawn-pv/SKILL.md)。

## 检查工具的回归验证

在仓库根目录运行，使用 Python 标准库即可：

```bash
python -m unittest discover -s tests -v
```
