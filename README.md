# SpecForge

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**SpecForge — 规范驱动开发（SDD）的内容生成引擎**

SpecForge 是一个**基于规范驱动开发（SDD）的 AI 内容生成引擎**。它以显式、可验证的规范为唯一事实源，驱动 AI Agent 在严格的九阶段循环中完成从创意到成品的结构化生成，确保产出全程可控、过程可追溯、结果可复现。

## 核心功能

- **SDD 工作流管理** — 从规范到实现的完整九阶段循环
- **多内容类型支持** — 内置小说、文章、漫画、短剧四种内容类型，支持插件扩展
- **多 AI 后端集成** — 支持 OpenCode、Cursor、Claude Code 三大 AI Agent 平台
- **插件系统** — 通过 `--plugins-dir` 引入自定义内容类型插件，无需编写代码
- **Slash Commands & Skills 支持** — 为 AI Agent 安装斜杠命令和技能文件

## 快速开始

```bash
git clone https://github.com/your-org/specforge.git
cd specforge
pip install -e .
specforge init --type novel --backend opencode --force
```

[📖 完整快速开始教程 →](docs/getting-started.md)

## 文档导航

| 文档 | 说明 |
|------|------|
| [📦 安装指引](docs/installation.md) | 源码安装、依赖说明 |
| [🚀 快速开始](docs/getting-started.md) | 端到端入门教程 |
| [🧠 核心概念](docs/core-concepts.md) | SDD、内容类型、插件、后端、阶段 |
| [🔄 工作流](docs/workflow.md) | SDD 九阶段循环详解 |
| [⌨️ CLI 命令参考](docs/cli-reference.md) | 终端命令 + AI 斜杠命令 |
| [🔧 支持的工具](docs/supported-tools.md) | AI 后端对比与功能矩阵 |
| [⚙️ 自定义配置](docs/customization.md) | 插件、后端、Skills 等配置选项 |

## 致谢

SpecForge 的设计和实现深受以下项目的启发：

- **[SpecKit](https://github.com/anomalyco/speckit)** — 规范驱动开发（SDD）方法论和循环框架。SpecForge 的九阶段工作流、斜杠命令体系、制品目录结构等核心架构均源自其设计理念。
- **[OpenSpec](https://github.com/anomalyco/openspec)** — 开源SDD框架。
- **[OpenCode](https://github.com/anomalyco/opencode)** — AI Agent 平台。SpecForge 的后端集成、Slash Commands 和 Skills 机制参考了其工具链接口规范。

## 许可证

MIT License — 详见项目 LICENSE 文件。
