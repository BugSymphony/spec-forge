# Article 创作宪法

<!-- 文章创作项目的核心原则与开发准则 -->

## 核心创作原则 (Core Creative Principles)

### I. Spec 驱动 (Spec-First, NON-NEGOTIABLE)

**所有创作必须始于完整的 Spec 文档**：

- 主题定位必须清晰且有价值
- 目标读者必须明确（年龄段、知识水平、兴趣领域）
- 内容结构必须有逻辑性和层次感
- 风格设定必须匹配发布平台和读者群体
- **禁止**在没有 Spec 的情况下直接开始写作

### II. Plan 指导 (Plan-Guided)

**每个项目必须有创作策略计划**：

- 从 Spec 中提取核心内容和表达策略
- 明确文章类型（教程、评论、故事、科普等）
- 进行合规性检查（Constitution Check）
- 定义清晰的内容结构和交付格式
- **只关注"做什么"和"为什么做"**，不涉及具体段落写作

### III. Tasks 分解 (Task-Breakdown)

**Plan 必须拆解为可执行的内容创作任务**：

- 每个部分有明确的主题、字数要求、关键信息点
- 任务之间有清晰的逻辑顺序和依赖关系
- 每个任务包含内容要点、素材需求、质量标准
- **这是 tasks 命令的职责**，不应在 Plan 阶段涉及

### IV. 一致性维护 (Consistency Maintenance)

**所有产出必须严格遵循 Spec 和 Plan 的约束**：

- 观点论述必须前后一致，不得自相矛盾
- 专业术语使用必须准确且统一
- 风格基调必须保持一致（避免语调漂移）
- 引用和数据必须有可靠来源
- **每次生成后必须进行 Schema 校验**

### V. 质量优先 (Quality-First)

**每个阶段的产出必须符合质量标准**：

**Spec 阶段标准**：

- 主题明确、有价值、可执行
- 目标读者清晰
- 内容结构合理
- 约束条件可行

**Plan 阶段标准**：

- 内容策略明确且可执行
- 结构设计完整
- 合规性检查通过
- 交付格式清晰

**Tasks 阶段标准**：

- 每个部分任务目标明确
- 任务之间逻辑连贯
- 可执行性强

**Dist 阶段标准**：

- 内容符合 Spec/Plan/Tasks 的所有约束
- 表达流畅、逻辑清晰
- 信息准确、有据可查
- 无错别字或语法错误

## 创作流程规范 (Development Workflow)

### 阶段顺序（严格执行）

```
1. Specify → 2. Plan → 3. Tasks → 4. Implement (内容草稿)
```

**禁止跳过任何阶段**，每个阶段的输出是下一阶段的前提。

### 各阶段职责边界

| 阶段          | 职责        | 输出文件             | 核心问题                |
|-------------|-----------|------------------|---------------------|
| **Specify** | 定义内容大纲和定位 | `specs/spec.md`  | What & Why          |
| **Plan**    | 制定内容策略和结构 | `specs/plan.md`  | Strategy & Approach |
| **Tasks**   | 拆解为段落/章节任务 | `specs/tasks.md` | How to Execute      |
| **Dist**    | 产出最终内容草稿  | `dist/articles/` | Final Content       |

### 跨阶段反馈机制

- **Dist → Spec**: 内容写作中发现定位问题时，需反向更新 Spec
- **Tasks → Plan**: 任务分解发现结构问题时，需反向更新 Plan
- **Plan → Spec**: 策略规划发现大纲缺陷时，需反向更新 Spec
- **所有变更必须记录版本历史**

## 文档组织标准 (Documentation Standards)

SpecForge 采用三层架构模型：

```
specs/   → 规范层（Declarative Layer）
build/   → 中间结构层（Structural Artifact Layer）
dist/    → 最终产物层（Output Layer）
```

### Specs/ 目录结构

```
specs/
├── spec.md              # 原始内容大纲与定位（输入文件）
├── plan.md              # 内容策略总纲
└── tasks.md             # 内容创作任务分解
```

### Build/ 中间结构层

```
build/
├── xxx.md
```

### Dist/ 目录结构

```
dist/
└── articles/
    ├── article_01.md    # 第 1 篇：[文章标题]
    ├── article_02.md    # 第 2 篇：[文章标题]
    └── ...
```

## Schema 校验要求 (Schema Validation Requirements)

### 强制校验点

1. **Spec 生成后** - 必须通过 `schema.yaml` 校验
2. **Plan 生成后** - 必须通过 `plan-schema.yaml` 校验（如有）
3. **每篇文章完成后** - 必须检查是否符合 Spec/Plan 约束

### 校验维度

- **完整性检查**: 必填字段是否齐全
- **一致性检查**: 是否与已有设定冲突
- **可行性检查**: 规模、复杂度是否在可控范围内
- **质量检查**: 是否符合各阶段的质量标准

## 工具使用规范 (Tool Usage Guidelines)

### Forge 命令使用

| 命令                              | 用途       | 输入               | 输出                           |
|---------------------------------|----------|------------------|------------------------------|
| `forge specify --idea="..."`    | 生成 Spec  | 创意想法             | `specs/spec.md`              |
| `forge plan`                    | 生成 Plan  | `specs/spec.md`  | `specs/plan.md`              |
| `forge tasks`                   | 生成 Tasks | `specs/plan.md`  | `specs/tasks.md`             |
| `forge implement --article=N`   | 生成文章     | `specs/tasks.md` | `dist/articles/article_N.md` |

### LLM 使用原则

- **AI 辅助，人类决策**: AI 生成内容，人类审核把关
- **迭代优化**: 接受初稿不完美，通过多轮对话改进
- **保持上下文**: 每轮对话提供足够的背景信息（Spec/Plan/Tasks）
- **明确边界**: 清楚说明当前处于哪个阶段，需要何种输出

## 版本控制 (Version Control)

### 文档版本管理

- **Spec**: 重大定位变更时升级版本号（v1.0 → v2.0）
- **Plan**: 策略调整时更新日期和版本
- **Tasks**: 任务调整时保留历史记录
- **Articles**: 每篇文章保留修改历史

### 变更记录格式

```markdown
## Changelog

### v2.0 (2026-03-19)

- 修改：[具体内容]
- 原因：[变更理由]
- 影响：[影响范围]
```

## 治理与修正 (Governance & Amendments)

### 宪法权威

本宪法是该文章创作项目的最高准则，所有其他实践和约定都必须遵循本宪法。

### 修正流程

1. **提出修正**: 任何参与者都可以提出宪法修正建议
2. **讨论评估**: 团队讨论修正的必要性和影响
3. **记录变更**: 在 Changelog 中记录修正内容和理由
4. **更新版本**: 升级宪法版本号

### 违规处理

- **轻微违规**: 在代码审查或内容审核中指出并修正
- **严重违规**: 暂停相关阶段，重新审视 Spec/Plan 的合理性
- **系统性问题**: 触发宪法修订流程

---

**版本**: v1.0  
**生效日期**: 2026-03-19  
**最后修订**: 2026-03-19

---

## 附录：快速参考卡片 (Quick Reference Card)

### 创作流程速查

```
创意 → [Specify] → Spec → [Plan] → Plan → [Tasks] → Tasks → [Implement] → Articles
         ↓            ↓           ↓          ↓           ↓             ↓
      想法整理    内容定位   策略规划   任务分解   文章草稿     最终内容
```

### 各阶段核心问题

- **Specify**: 我要写什么内容？主题、读者、结构是什么？
- **Plan**: 如何组织内容？策略、方向、质量标准是什么？
- **Tasks**: 如何分段执行？每部分写什么？顺序和依赖是什么？
- **Dist**: 如何落地？文章内容是否符合所有约束？

### 禁止事项清单

❌ 没有 Spec 就开始 Plan  
❌ 没有 Plan 就开始 Tasks  
❌ 没有 Tasks 就开始写文章  
❌ 在 Plan 阶段涉及具体段落写作  
❌ 在文章草稿中违反 Spec 定位  
❌ 跳过 Schema 校验

✅ 严格遵守阶段顺序  
✅ 每个阶段都进行质量检查  
✅ 保持文档的一致性和可追溯性  
✅ 及时反向更新上游文档  
✅ 所有变更都有记录和理由
