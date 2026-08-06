# 定制指南

本文档介绍 SpecForge 的全部可定制选项。**所有自定义都不需要编写 Python 代码**——通过参数和目录结构即可完成。

---

## 内容类型选择

```bash
specforge init --type novel       # 小说
specforge init --type article     # 文章
specforge init --type comic       # 漫画
specforge init --type video       # 视频
```

---

## 外部插件目录（无需编码）

```bash
specforge init --type wuxia --plugins-dir ~/my-plugins --backend opencode
```

插件目录结构：

```text
~/my-plugins/
├── wuxia/              # 插件目录名 → 内容类型 key
│   ├── plugin.yaml     # 元数据
│   ├── templates/      # 阶段模板
│   └── commands/       # Slash Command 定义
```

每个插件是一个普通目录，系统自动扫描发现。外部与内建插件同名时，外部版本优先。

---

## AI 后端选择

```bash
specforge init --type novel --backend opencode   # OpenCode（默认）
specforge init --type novel --backend cursor      # Cursor
specforge init --type novel --backend claude_code # Claude Code
```

| 值 | 安装目录 | 文件格式 |
|------|---------|---------|
| `opencode` | `.opencode/commands/` | `.md`（Slash Commands） |
| `cursor` | `.cursor/skills/` | `.md`（Skills） |
| `claude_code` | `.claude/commands/` | `.md`（Slash Commands） |

---

## AI Skills

```bash
specforge init --type article --backend opencode --ai-skills
```

Skills 文件安装到后端 skills 目录（如 `.opencode/skills/`），命名格式：`specforge-<stage>.md`。

---

## 完整组合示例

```bash
# 外部插件 + Cursor 后端 + Skills
specforge init --type wuxia \
  --plugins-dir ~/my-plugins \
  --backend cursor \
  --ai-skills \
  --force
```

---

## 相关文档

- [核心概念](core-concepts.md) — 内容类型、插件、后端的概念
- [支持的工具与后端](supported-tools.md) — 后端对比
- [CLI 命令参考](cli-reference.md) — `init` 命令完整参数
