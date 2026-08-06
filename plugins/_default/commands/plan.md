---
description: 执行创作计划工作流，使用计划模板生成设计制品，包括研究文档、数据模型、契约和快速入门。
handoffs:
  - label: 创建任务清单
    agent: tasks
    prompt: 将计划分解为可执行任务
    send: true
  - label: 创建检查清单
    agent: checklist
    prompt: 为以下领域创建检查清单...
---

## User Input

```text
$ARGUMENTS
```

**必须**在继续之前考虑用户输入（若不为空）。

## Pre-Execution Checks

1. 确认当前目录为 SpecForge 项目：检查 `.specforge/` 目录是否存在
2. 执行 `specforge show --paths-only` 获取当前活动 feature 的路径信息：
   - 提取 `FEATURE_DIR`、`SPEC_FILE`、`IMPL_PLAN`
   - 若解析失败，ERROR：无法确定当前 feature，请先执行 `/specforge.specify`
3. 确认 `SPEC_FILE` 存在，若不存在则 ERROR：规格文件缺失
4. 执行 `specforge setup plan --json` 初始化计划环境：
   - 若失败，ERROR：计划环境初始化失败，检查 `.specforge/templates/plan-template.md` 是否存在
   - 解析 JSON 输出，获取 `PLAN_FILE`、`BUILD_DIR` 等路径
   - 确认模板已复制到 `FEATURE_DIR/plan.md`
5. 执行 `specforge validate --stage clarify --json` 检查规格是否已完成澄清阶段
   - 若验证失败且规格含有 `[待澄清]` 标记，WARN：建议先完成 `/specforge.clarify`
   - 验证是可选的——用户可跳过澄清直接进入计划阶段
6. 读取 `.specforge/constitution.md` 加载宪法约束

## Outline

目标：将规格（what/why）转化为可执行的创作计划（how），生成全部设计制品。

### 第 1 步：加载上下文

1. 执行 `specforge show --artifact spec` 加载规格内容
2. 提取关键信息：
   - 创作目标和受众
   - 内容规模指标
   - 创作场景和验收标准
   - 核心要素清单
   - 成功标准
   - 假设和约束
3. 加载 `.specforge/constitution.md` 提取创作原则和质量标准
4. 加载 `.specforge/templates/plan-template.md` 了解所需结构

### 第 2 步：填写创作上下文

在计划模板的「创作上下文」章节填入：

#### 内容类型与技术方案

- **内容类型**：{content_type_cn}
- **创作工具**：列出使用的写作/设计/协作工具
- **存储方案**：内容文件的组织和命名规范
- **发布平台**：目标交付平台
- **内容规模**：从 spec 中提取的具体规模指标
- 对于未确定的技术选择，标记为 `[待确定: 具体问题]`

#### 创作上下文示例

- 小说：`Markdown → 本地文件 → 按章存储 → dist/novel/第N章-标题.md`
- 文章：`Markdown → 本地文件 → 按文存储 → dist/article/标题.md`
- 漫画：`Markdown 分镜脚本 → 本地文件 → dist/comic/第N话-脚本.md`
- 视频：`Markdown 分镜头脚本 → 本地文件 → dist/video/第N集-分镜头脚本.md`

### 第 3 步：宪法合规性检查

逐条检查宪法原则与计划的一致性：

```markdown
| 原则 | 状态 | 备注 |
|------|------|------|
| 一：[原则名称] | ✅ / ⚠️ / ❌ | [合规说明或违规说明] |
```

- ✅ 合规：计划完全遵守该原则
- ⚠️ 需要说明：计划偏离但理由充分
- ❌ 违规：计划违反宪法，必须修正

若出现未合理说明的违规项，ERROR 并停止执行——在修正前不能继续。

### 第 4 步：设计内容结构

定义内容的整体架构和分阶段创建计划：

1. **内容拆分方案**：
   - 小说的章节拆分和叙事弧线
   - 文章的论证链和段落展开
   - 漫画的分镜排列和页面分配
   - 视频的场次拆分和场景顺序

2. **创作阶段规划**：
   - Phase 1：设定与大纲（世界观/人物/论点/分镜框架）
   - Phase 2-N：按顺序逐章/逐段/逐话/逐集创作
   - Phase Final：修订与打磨

3. **组件/素材复用策略**：
   - 人物设定和性格的一致性维护方案
   - 世界观设定的参考维护
   - 跨章节的情节一致性检查点

### 第 5 步：生成设计制品

#### Phase 0：调研文档（research.md）

针对创作上下文中的每个 `[待确定]` 标记，生成调研任务并输出到 `research.md`：

```markdown
## 决策记录

### 决策：[主题]

- **选择**：[最终选择]
- **理由**：[选择原因]
- **备选方案**：[被排除的选项及排除原因]
```

- 所有 NEEDS CLARIFICATION 在此阶段解决
- 输出文件：`FEATURE_DIR/research.md`

#### Phase 1：数据模型（data-model.md）与契约（contracts/）

1. **提取核心要素并生成 `data-model.md`**：
   - 元素名称、属性、关系
   - 验证规则（来自需求的约束）
   - 状态转换（若有生命周期）
   - 内容类型特有字段：
     - 小说：人物属性表、世界观元素表、章节状态机
     - 漫画：角色设计属性、分镜元素定义
     - 文章：论点逻辑链、引用索引结构
     - 视频：场景属性、对话结构

2. **生成契约文档 `contracts/`**（若有外部接口）：
   - 命令行工具 → 命令 Schema
   - 通用创作 → 模板结构契约
   - 无外部接口则跳过

3. **生成 `quickstart.md`**：
   - 快速上手指南
   - 创作流程概述
   - 关键文件路径索引

### 第 6 步：补充资源约束

列出创作过程中的资源和限制：

- **时间预估**：每个阶段的预期耗时
- **参考资料**：需要的研究资料和参考文献
- **外部依赖**：合作的平台、工具或人员
- **质量检查点**：每个阶段的验收标准
- **里程碑节点**：关键交付日期和中间审核点

### 第 7 步：写回计划文件

1. 将填充好的内容写入 `IMPL_PLAN`（`FEATURE_DIR/plan.md`）
2. 确认所有章节完整，无占位符残留
3. 确保宪法合规性检查结果已记录

### 第 8 步：Plan 后宪法检查

完成所有设计制品后，重新运行宪法合规性检查：
- 逐条对比设计决策与宪法原则
- 标记任何在新设计中暴露的潜在冲突
- 若发现新的应标记违规项，回到相应设计步骤修正

### 第 9 步：报告完成

向用户输出：

- **计划文件路径**：`IMPL_PLAN`
- **已生成制品清单**：
  - `FEATURE_DIR/plan.md`
  - `FEATURE_DIR/research.md`
  - `FEATURE_DIR/data-model.md`
  - `FEATURE_DIR/contracts/`（如有）
  - `FEATURE_DIR/quickstart.md`
- **宪法合规性摘要**
- **下一步建议**：执行 `/specforge.tasks` 分解任务

## 内容类型专用设计文档

各内容类型在 Phase 1 应额外生成以下类型专用文档：

**小说 (novel)**：
- `FEATURE_DIR/design/character-map.md` — 人物关系图
- `FEATURE_DIR/design/timeline.md` — 情节时间线
- `FEATURE_DIR/design/chapter-outline.md` — 章节细纲
- `FEATURE_DIR/design/setting-reference.md` — 设定参考

**文章 (article)**：
- `FEATURE_DIR/design/argument-chain.md` — 论证逻辑链
- `FEATURE_DIR/design/reference-list.md` — 引用清单
- `FEATURE_DIR/design/paragraph-outline.md` — 段落大纲

**漫画 (comic)**：
- `FEATURE_DIR/design/character-sheet.md` — 人物设计稿
- `FEATURE_DIR/design/storyboard-plan.md` — 分镜草图规划
- `FEATURE_DIR/design/art-style-reference.md` — 画风参考板

**视频 (video)**：
- `FEATURE_DIR/design/storyboard-template.md` — 分镜头脚本模板
- `FEATURE_DIR/design/scene-layout.md` — 场景布置方案
- `FEATURE_DIR/design/prop-checklist.md` — 演员/道具清单

向用户输出：

- **计划文件路径**：`IMPL_PLAN`
- **已生成制品清单**：
  - `FEATURE_DIR/plan.md`
  - `FEATURE_DIR/research.md`
  - `FEATURE_DIR/data-model.md`
  - `FEATURE_DIR/contracts/`（如有）
  - `FEATURE_DIR/quickstart.md`
- **宪法合规性摘要**
- **下一步建议**：执行 `/specforge.tasks` 分解任务

## Output

- **主要制品**：`FEATURE_DIR/plan.md`
- **辅助制品**：
  - `FEATURE_DIR/research.md` — 技术决策记录
  - `FEATURE_DIR/data-model.md` — 核心要素模型
  - `FEATURE_DIR/contracts/` — 接口契约（如有）
  - `FEATURE_DIR/quickstart.md` — 快速上手指南
- **格式**：Markdown

## Stage Checkpoints

- [ ] 创作上下文已完整填写，无 `[待确定]` 残留
- [ ] 宪法合规性检查已逐条完成，违规项已处理
- [ ] 内容结构拆分方案合理且可迭代执行
- [ ] 每个创作阶段有明确的输入和输出
- [ ] research.md 中所有调研决策已记录
- [ ] data-model.md 涵盖所有核心要素及其关系
- [ ] quickstart.md 提供清晰的入门指引
- [ ] 资源约束和里程碑已明确

## 质量门禁

- 计划是否仅描述"怎么做"（how），不重复 spec 中的"什么/为什么"（what/why）？
- 内容结构拆分是否足够具体，可直接进入任务分解？
- 每个设计制品的格式是否遵循模板规范？
- 宪法合规性是否有任何未合理说明的违规项？
- 资源估算是否在合理范围内（不过度乐观也不过度悲观）？
- 所有 CLI 调用是否使用了 `--json` 参数（如适用）？
- 本文件中是否**不包含** git、branch、commit、hook 相关引用？

**下一步**：执行 `/specforge.tasks` 将计划分解为可执行的任务清单。
