# 核心概念

本文档解释 SpecForge 的五大核心概念。

---

## SDD 循环

**规范驱动开发（Specification-Driven Development）** 是 SpecForge 的核心工作方法论。它将项目产出物的创作过程分解为九个有序阶段。

九个阶段依次为：

```text
制宪(constitution) → 规格(specify) → 澄清(clarify) → 计划(plan)
→ 任务(tasks) → 检查(checklist) → 分析(analyze)
→ 实施(implement) → 评审(review)
```

每个阶段通过 Slash Command（如 `/specforge.specify`）触发，由 AI Agent 执行该阶段的特定任务，生成对应的制品文件。制品依次存储在 `specs/<NNN>-<name>/` 目录中。

---

## 内容类型（Content Type）

内容类型定义了生成项目的模板结构和输出格式。

内置内容类型：

| 类型 Key | 中文名 | 适用场景 |
|----------|--------|---------|
| `novel` | 小说 | 长篇小说、系列故事创作 |
| `article` | 文章 | 技术文章、博客、论文 |
| `comic` | 漫画 | 漫画脚本、分镜设计 |
| `video` | 视频 | 视频脚本、分集规划 |

> **无需编写代码**：新增内容类型不需要修改 SpecForge 的 Python 源码。只需创建一个遵循规范目录结构的插件目录，通过 `--plugins-dir` 参数引用即可。

---

## 插件与扩展（Plugin）

插件是扩展 SpecForge 内容类型体系的主要方式。**无需编写任何 Python 代码**，只需创建标准目录结构即可。

```text
plugins/my-type/
├── plugin.yaml       # 元数据（key、name_cn、description）
├── templates/        # 阶段模板文件（Markdown）
└── commands/         # Slash Command 文件（含 YAML 前置元数据）
```

### 使用外部插件

```bash
# --plugins-dir 指向外部插件目录，无需安装或注册
specforge init --type my-type --plugins-dir /path/to/plugins --backend opencode
```

系统自动扫描该目录下所有合法插件。当内建和外部插件同名时，外部版本优先。**整个过程不需要编写代码、修改配置文件或运行注册命令。**

---

## AI 后端（Backend）

AI 后端定义了 SpecForge 命令文件的输出格式和安装位置。

| 后端 | 目录 | 输出类型 |
|------|------|---------|
| **OpenCode** | `.opencode/commands/` | Slash Commands（`.` 分隔）+ Skills（`-` 分隔） |
| **Cursor** | `.cursor/rules/` | Rules（`-` 分隔）+ Skills（`-` 分隔） |
| **Claude Code** | `.claude/commands/` | Slash Commands（`.` 分隔）+ Skills（`-` 分隔） |

**相关内容**：[支持的工具与后端](supported-tools.md)

---

## 阶段文件（Stage）

阶段文件是 SDD 循环中每个阶段的命令定义文件，存储在内容类型的 `commands/` 目录中：

```text
plugins/novel/commands/
├── constitution.md
├── specify.md
├── clarify.md
├── plan.md
├── tasks.md
├── checklist.md
├── analyze.md
├── implement.md
└── review.md
```

每个阶段文件包含 YAML 前置元数据和执行指令。AI Agent 读取这些文件以了解如何在当前阶段执行任务。

---

## 概念关系图

```text
SDD 循环 ──→ 定义九阶段工作流
  │
  ├── 每个阶段由 阶段文件(Stage) 定义
  │
  ├── 阶段文件按 内容类型(Content Type) 分组
  │
  ├── 内容类型由 插件(Plugin) 提供（无需编码）
  │
  └── 命令文件安装到 AI 后端(Backend) 的指定目录
```

**工作流** 章节详细说明如何将这些概念应用于实际开发：[工作流 →](workflow.md)
