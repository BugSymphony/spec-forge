# SpecForge

<div align="center">

**规则驱动的 AI 内容生成引擎**

</div>

---

## 📖 简介

**SpecForge** 是一个**规范驱动（Specification-Driven, SDD）**的 AI 内容生成引擎，灵感来源于 [Spec Kit](https://github.com/spec-kit) 的规范驱动开发理念。

我们的目标是：**让 AI 生成可控、可预测、高质量的内容**。

### 🎯 核心理念

传统 AI 内容生成的痛点：
- ❌ 输出不可控，随机性强
- ❌ 质量不稳定，依赖运气
- ❌ 缺乏流程，难以协作
- ❌ 无法追溯，难以优化

SpecForge 的解决方案：
- ✅ **规范驱动** - 用明确的 Spec 约束 AI 输出
- ✅ **流程可控** - 标准化的生成流程（Specify → Plan → Tasks → Implement）
- ✅ **质量保证** - Schema 校验 + 多阶段审查
- ✅ **可追溯性** - 每个输出都有明确的来源和依据

### 💡 与 Spec Kit 的关系

SpecForge 借鉴了 [Spec Kit](https://github.com/spec-kit/spec-kit) 的核心思想：

| Spec Kit | SpecForge |
|----------|-----------|
| 规则驱动的代码生成 | 规则驱动的内容生成 |
| TypeScript/JavaScript | 小说/文章/漫画/视频脚本 |
| AST + Schema 校验 | YAML Schema + Markdown 模板 |
| 代码结构规范 | 内容结构规范 |

我们不是简单的模仿，而是将**规范驱动开发（SDD, Specification-Driven Development）**的理念扩展到了**AI 内容生成领域**。

---

## ✨ 特性

### 🔥 核心特性

- **📋 规范驱动生成**
  - 基于 Spec（规格说明）驱动整个生成流程
  - 每个阶段都有明确的输入输出标准
  - Schema 校验确保输出格式正确

- **🤖 多 LLM 支持**
  - 内置 DeepSeek、OpenAI 等主流模型支持
  - 统一的 LLM 接口，轻松切换
  - 支持自定义 LLM 后端

- **📝 多内容类型**
  - 📚 **Novel** - 小说创作（奇幻/科幻/悬疑等）
  - 📄 **Article** - 文章写作（技术文/观点文/教程等）
  - 🎨 **Comic** - 漫画脚本（剧情/角色/分镜）
  - 🎬 **Video** - 视频脚本（分镜表/拍摄脚本）

- **🔄 四阶段流程**
  ```
  Specify → Plan → Tasks → Implement
  ↓          ↓       ↓        ↓
  定义规格   制定计划 拆解任务  生成内容
  ```

- **⚙️ 配置化架构**
  - Prompt 模板可配置
  - Schema 规则可配置
  - 澄清规则可配置
  - 输出格式可配置

- **🛡️ 质量保障**
  - Schema 自动校验
  - 多阶段审查机制
  - 错误自动修复（YAML Fix Agent）

### 🚀 高级特性

- **🔍 需求澄清（Clarify）**
  - 智能检测 Spec 中的模糊点
  - 自动生成澄清问题
  - 支持交互式问答完善需求

- **🎯 任务拆解（Tasks）**
  - 将复杂计划拆解为可执行的小任务
  - 任务间依赖管理（DAG）
  - 支持增量生成

- **🔧 插件化设计**
  - 易于添加新的内容类型
  - 支持自定义 Stage
  - 可扩展的 Agent 系统

---

## 🚀 快速开始

### 1. 安装

```bash
#从源码安装
git clone https://github.com/BugSymphony/spec-forge.git
cd spec-forge
pip install -e .
```

### 2. 初始化项目

```bash
# 创建新项目（以小说为例）
forge init --type=novel

# 查看可用的内容类型
forge types --list
```

### 3. 生成 Spec（规格说明）

```bash
# 方式一：提供创意想法
forge specify --idea="我想写一部关于时间旅行的科幻小说"

# 方式二：交互模式（推荐）
forge specify
```

示例输出：
```markdown
# 小说大纲：时空旅人

## 主题定位
- 核心主题：一个物理学家意外发现时间旅行方法...
- 目标观众：科幻爱好者，年龄 18-35 岁
- 价值主张：探索时间与命运的哲学思考

## 内容结构
1. 序幕：实验室的意外发现
2. 第一次穿越：回到 1969 年
3. 蝴蝶效应：改变历史的代价
...
```

### 4. 生成 Plan（创作计划）

```bash
forge plan
```

Plan 会定义：
- 叙事策略（线性/倒叙/多线）
- 章节结构（起承转合）
- 人物关系图
- 世界观设定

### 5. 生成 Tasks（任务清单）

```bash
forge tasks
```

Tasks 会将计划拆解为可执行的小任务：
```yaml
stories:
  - story_id: Story-1
    goal: "完成序幕章节"
    tasks:
      - id: TASK-1
        description: "撰写序幕开头 500 字"
        output: "chapters/prologue.md"
```

### 6. 执行任务，生成内容

```bash
# 单步执行（适合调试）
forge implement --mode=single --task=TASK-1

# 循环执行（自动完成所有任务）
forge implement --mode=loop --auto
```

### 7. 查看成果

```bash
# 生成的内容在 dist/ 目录
ls dist/
# novels/
#   chapters/
#     prologue.md
#     chapter-1.md
#     ...
```

---

## 📚 核心概念

### 1. SDD（规范驱动）

**什么是 Spec？**
- Spec = Specification（规格说明）
- 是对内容的**结构化定义**，而非简单描述

**为什么需要 Spec？**
```
❌ 坏的输入："写一部科幻小说"
→ AI 不知道写什么，输出随机

✅ 好的输入：
   主题：时间旅行的道德困境
   主角：35 岁物理学家，性格内向
   冲突：拯救爱人 vs 保护历史
   结构：三幕剧
→ AI 知道怎么写，输出可控
```

### 2. 四阶段流程

#### Stage 1: Specify（定义规格）
**输入**: 创意想法  
**输出**: `specs/spec.md`  
**作用**: 将模糊的想法转化为结构化的规格说明

#### Stage 2: Plan（制定计划）
**输入**: `specs/spec.md`  
**输出**: `specs/plan.md`  
**作用**: 从策略层面定义如何呈现内容

#### Stage 3: Tasks（拆解任务）
**输入**: `specs/plan.md`  
**输出**: `specs/tasks.md`  
**作用**: 将计划拆解为可执行的小任务

#### Stage 4: Implement（执行实现）
**输入**: `specs/tasks.md`  
**输出**: `dist/` (最终内容)  
**作用**: 逐任务执行，生成实际内容

### 3. Schema 校验

每个阶段都有对应的 Schema 进行校验：

```yaml
# schema.yaml 示例
type: object
required:
  - title
  - topic_positioning
  - content_structure

properties:
  title:
    type: string
    description: 作品标题
  
  topic_positioning:
    type: object
    required: [main_topic, target_audience]
```

**好处**:
- ✅ 防止遗漏关键信息
- ✅ 保证格式一致性
- ✅ 便于自动化处理

### 4. Agent 系统

SpecForge 包含多个专用 Agent：

| Agent | 职责 |
|-------|------|
| **SpecAgent** | 生成 Spec 文档 |
| **PlanAgent** | 生成创作计划 |
| **TasksAgent** | 拆解任务清单 |
| **ImplAgent** | 执行任务，生成内容 |
| **YamlFixAgent** | 自动修复 YAML 错误 |
| **ClarifyAgent** | 需求澄清（可选） |

每个 Agent 都是独立的，可以单独使用和测试。

---

## 📖 使用指南

### 完整工作流示例

#### 场景：创作一部奇幻小说

```bash
# 1. 初始化
forge init --type=novel

# 2. 生成 Spec
forge specify --idea="少年魔法师寻找失落的神器，途中结识伙伴，对抗黑暗势力"

# 3. 生成计划
forge plan

# 4. 拆解任务
forge tasks

# 5. 执行任务
forge implement --mode=loop --auto

# 6. 查看成果
cat dist/novels/chapters/chapter-1.md
```

### 命令行参考

#### 全局命令

```bash
forge --help           # 查看帮助
forge --version        # 查看版本
forge types --list     # 列出内容类型
```

#### 各阶段命令

```bash
# Specify 阶段
forge specify --idea="..." --no-prompt

# Plan 阶段
forge plan --output=custom-plan.md

# Tasks 阶段
forge tasks --llm=deepseek

# Implement 阶段
forge implement --mode=single --task=TASK-1
forge implement --mode=loop --auto
```

### 配置说明

#### 项目配置

`.forge/config.yaml`:
```yaml
# 内容类型
content_type: novel

# LLM 提供商（deepseek/openai）
llm_provider: deepseek

# Schema 校验开关
schema_validation: true

# 阶段配置（可选，自定义路径时使用）
stages:
  specify:
    prompt: templates/prompt/specify.md
    output: specs/spec.md
    schema: schemas/specify_schema.yaml
```

#### Prompt 模板

可以为不同内容类型自定义 Prompt：

```
templates/agent-prompts/
├── specify/
│   ├── novel.md
│   ├── article.md
│   └── video.md
├── plan/
│   └── ...
└── tasks/
    └── ...
```

---

## 🔧 扩展开发

### 添加新的内容类型

1. 创建 Prompt 模板
```bash
templates/agent-prompts/specify/podcast.md
```

2. 定义 Schema
```yaml
# specs/podcast/schema.yaml
type: object
properties:
  episode_title: {type: string}
  duration: {type: string}
  guests: {type: array}
```

3. 注册内容类型
```python
# src/forge/config/constants.py
class ContentType(str, Enum):
    PODCAST = "podcast"
```

### 自定义 Agent

继承 `BaseAgent` 即可：

```python
from forge.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def generate(self, **kwargs):
        # 你的实现
        pass
```

### 添加新的 LLM 后端

实现 `BaseLLM` 接口：

```python
from forge.llm.base import BaseLLM
from forge.llm.types import Message

class MyLLM(BaseLLM):
    def chat(self, messages: list[Message]) -> Message:
        # 调用你的 LLM API
        pass
```

---

## 🤝 贡献指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/BugSymphony/spec-forge.git
cd spec-forge

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -e ".[dev]"

```


### 提交流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- **[Spec Kit](https://github.com/spec-kit/spec-kit)** - 规则驱动开发的灵感来源
- **[Click](https://click.palletsprojects.com/)** - 优秀的 CLI 框架

---

## 📬 联系方式

- **Issues**: [GitHub Issues](https://github.com/BugSymphony/spec-forge/issues)
- **讨论**: [Discussions](https://github.com/BugSymphony/spec-forge/discussions)
- **邮件**: 17278327036@163.com

---

<div align="center">

**Made with ❤️ by SpecForge Team**

⭐ 如果这个项目对你有帮助，请给我们一个 Star！

</div>
