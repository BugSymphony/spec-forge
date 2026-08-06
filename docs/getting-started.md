# 快速开始

## 前提条件

- Python 3.10+ 已安装
- git 已安装

## 第一步：安装

```bash
git clone https://github.com/your-org/specforge.git
cd specforge
pip install -e .
specforge --version
```

## 第二步：初始化项目

```bash
specforge init --type novel --backend opencode --force
```

输出示例：

```text
✨ SpecForge 项目初始化完成！
📁 内容类型: novel
🔧 后端: opencode
```

## 第三步：查看生成的文件

```text
.opencode/
├── commands/
│   ├── specforge.specify.md
│   ├── specforge.clarify.md
│   ├── specforge.plan.md
│   └── ...
.specforge/
└── config.yml
```

这些命令文件定义了 SDD 循环中各阶段的斜杠命令，AI Agent 会自动加载它们。

## 下一步

- [核心概念](core-concepts.md) — 了解 SDD 循环、内容类型、插件等核心概念
- [工作流](workflow.md) — 深入了解 SDD 九阶段工作流
- [CLI 命令参考](cli-reference.md) — 查看全部命令和参数
