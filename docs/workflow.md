# 工作流

本文档详述 SDD 九阶段工作流的每个阶段。

---

## 概览

```text
制宪 → 规格 → 澄清 → 计划 → 任务 → 检查清单 → 分析 → 实施 → 评审
```

每阶段通过 Slash Command 触发，由 AI Agent 自动执行。制品文件保存在 `specs/<NNN>-<name>/` 目录。

---

## 阶段

### 0. 制宪（Constitution）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.constitution` |
| **输出** | `.specforge/constitution.md` |
| **频率** | 每个项目一次 |

定义 AI Agent 的行为规则、输出格式和质量标准。可选的上游步骤。

### 1. 规格（Specify）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.specify` |
| **输入** | 用户自然语言需求 |
| **输出** | `specs/<NNN>-<name>/spec.md` |

### 2. 澄清（Clarify）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.clarify` |
| **输入** | `spec.md` |
| **输出** | 嵌入 spec.md 的问答 |

### 3. 计划（Plan）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.plan` |
| **输入** | `spec.md` |
| **输出** | `plan.md`, `build/`|
| **前置** | `specforge setup plan` |

### 4. 任务（Tasks）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.tasks` |
| **输入** | `plan.md`, `spec.md` |
| **输出** | `tasks.md` |
| **前置** | `specforge setup tasks` |

### 5. 检查清单（Checklist）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.checklist` |
| **输入** | `spec.md`, `plan.md`, `tasks.md` |
| **输出** | `checklist.md` |

### 6. 分析（Analyze）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.analyze` |
| **输入** | `spec.md`, `plan.md`, `tasks.md` |
| **输出** | 一致性分析报告 |
| **模式** | 只读 |

### 7. 实施（Implement）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.implement` |
| **输入** | `tasks.md`, `checklist.md` |
| **输出** | 代码和文件变更 |

### 8. 评审（Review）

| 属性 | 说明 |
|------|------|
| **命令** | `/specforge.review` |
| **输入** | `spec.md`, `tasks.md`, 产物变更 |

---

## 速查

| 阶段 | Slash Command | 环境准备 |
|------|-------------|---------|
| 规格 | `/specforge.specify` | - |
| 澄清 | `/specforge.clarify` | - |
| 计划 | `/specforge.plan` | `specforge setup plan` |
| 任务 | `/specforge.tasks` | `specforge setup tasks` |
| 检查清单 | `/specforge.checklist` | - |
| 分析 | `/specforge.analyze` | - |
| 实施 | `/specforge.implement` | - |
| 评审 | `/specforge.review` | - |

## 相关文档

- [核心概念](core-concepts.md) — SDD 循环、内容类型、插件等基础概念
- [CLI 命令参考](cli-reference.md) — 全部命令和参数说明
