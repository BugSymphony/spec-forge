# 支持的工具与后端

SpecForge 支持三种 AI 后端，负责将命令文件安装到 AI Agent 的配置目录中。

---

## 后端对比

| 后端 | 命令目录 | 输出类型 |
|------|---------|---------|
| **OpenCode** | `.opencode/commands/` | Slash Commands + Skills |
| **Cursor** | `.cursor/rules/` | Slash Commands  + Skills |
| **Claude Code** | `.claude/commands/` | Slash Commands + Skills |

## 后端管理

```bash
specforge backend list
specforge backend install --name cursor
specforge backend uninstall
specforge backend switch --name cursor
```

## 相关文档

- [CLI 命令参考](cli-reference.md) — `backend` 命令完整参数
- [定制指南](customization.md) — 后端和插件配置
