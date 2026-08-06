# CLI 命令参考

SpecForge 提供两类终端命令：**用户直接调用**的命令和 **AI Agent 通过 Slash Command 调用**的命令。

---

## 用户直接调用

以下命令由用户在终端中直接执行，用于项目初始化、环境验证和后端管理。

### 基础命令

| 命令 | 说明 |
|------|------|
| `specforge version` | 查看版本和构建信息 |
| `specforge init` | 初始化 SpecForge 项目 |
| `specforge check` | 校验开发环境 |

### 后端管理

| 命令 | 说明 |
|------|------|
| `specforge backend list` | 列出可用后端 |
| `specforge backend install` | 安装后端 |
| `specforge backend uninstall` | 卸载后端 |
| `specforge backend switch` | 切换后端 |

### 参数详情

#### `specforge init`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--type` | string | 否 | 内容类型 `novel` `article` `comic` `video` |
| `--backend` | string | 否 | AI Agent `opencode` `cursor` `claude_code` |
| `--plugins-dir` | path | 否 | 外部插件目录 |
| `--ai-skills` | boolean | 否 | 安装 AI Skills |
| `--force` | boolean | 否 | 强制重新初始化 |

#### `specforge backend install / switch`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--name` | string | 是 | `opencode` `cursor` `claude_code` |

---

## AI Agent 调用

以下命令由 AI Agent 在 Slash Command 工作流执行过程中自动调用，用户通常无需手动执行。

| 命令 | 说明 |
|------|------|
| `specforge list` | 列出所有 feature |
| `specforge show` | 显示 feature 信息 |
| `specforge use` | 切换活动 feature |
| `specforge new` | 创建新 feature |
| `specforge validate` | 校验 artifact 完整性 |
| `specforge setup plan` | 初始化 plan 环境 |
| `specforge setup tasks` | 初始化 tasks 环境 |
| `specforge templates` | 查看模板路径 |

### 参数详情

#### `specforge validate`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--stage` | string | 是 | 校验阶段 |

#### `specforge setup plan / setup tasks`

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--force` | boolean | 否 | 强制覆盖 |
| `--json` | boolean | 否 | JSON 输出 |
