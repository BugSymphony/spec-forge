# Tasks 报告（SpecForge - Video 视频制作脚本）

## 总览（Summary）

- 任务总数：{{ total_tasks }}
- 阶段数量：{{ phase_count }}
- Story 数量：{{ story_count }}

⚠️ **说明**: 本任务清单用于指导视频制作脚本的撰写和视频制作流程。

---

## 阶段（Phases）

{% for phase in phases %}

### {{ phase.name }}

- 顺序：{{ phase.order }}
- 阶段目标：{{ phase.purpose }}
- 任务数量：{{ phase.task_count }}

{% endfor %}

---

# Phase 1: Setup（初始化）

> 建立制作基础约束

{% set setup = setup|default({}) %}

- 阶段目标：{{ setup.purpose }}
- 任务数量：{{ setup.task_count }}

#### 任务列表

{% for task in setup.tasks %}

- [{% if task.status == 'completed' %}x{% else %} {% endif %}] {{ task.id }} [{{ task.phase }}] [Setup] {{ task.description }}
    - 路径：{{ task.path }}
    - 依赖：{{ task.depends }}

    - 目标:
      {{ task.goal }}

    - 执行动作:
      {% for a in task.action %}
        - {{ a }}
          {% endfor %}

    - 输出:
      {% for o in task.output %}
        - {{ o }}
          {% endfor %}

    - 验收标准:
      {% for ac in task.acceptance %}
        - {{ ac }}
          {% endfor %}

{% endfor %}

---

## Phase 2: Foundation（基础任务）

> 所有镜头的共通前置条件

{% set foundation = foundation|default({}) %}

- 阶段目标：{{ foundation.purpose }}
- 任务数量：{{ foundation.task_count }}

#### 任务列表

{% for task in foundation.tasks %}

- [{% if task.status == 'completed' %}x{% else %} {% endif %}] {{ task.id }} [{{ task.phase }}] [Foundation] {{ task.description }}
    - 路径：{{ task.path }}
    - 依赖：{{ task.depends }}

    - 目标:
      {{ task.goal }}

    - 执行动作:
      {% for a in task.action %}
        - {{ a }}
          {% endfor %}

    - 输出:
      {% for o in task.output %}
        - {{ o }}
          {% endfor %}

    - 验收标准:
      {% for ac in task.acceptance %}
        - {{ ac }}
          {% endfor %}

{% endfor %}

---

## 故事任务（Stories）

{% for story in stories %}

### {{ story.story_id }}（优先级：{{ story.priority }}）

- 目标：{{ story.goal }}
- 独立验证：{{ story.independent_test }}
- 任务数量：{{ story.task_count }}

#### 任务列表

{% for task in story.tasks %}

- [{% if task.status == 'completed' %}x{% else %} {% endif %}] {{ task.id }} [{{ task.phase }}] [Story] {{ task.description }}
    - 路径：{{ task.path }}
    - 依赖：{{ task.depends }}

    - 目标:
      {{ task.goal }}

    - 执行动作:
      {% for a in task.action %}
        - {{ a }}
          {% endfor %}

    - 输出:
      {% for o in task.output %}
        - {{ o }}
          {% endfor %}

    - 验收标准:
      {% for ac in task.acceptance %}
        - {{ ac }}
          {% endfor %}

{% endfor %}
{% endfor %}

---

## 最终阶段（Polish）

{% set polish = polish|default({}) %}

- 阶段目标：{{ polish.purpose }}
- 任务数量：{{ polish.task_count }}

#### 任务列表

{% for task in polish.tasks %}

- [{% if task.status == 'completed' %}x{% else %} {% endif %}] {{ task.id }} [{{ task.phase }}]  [Global] {{ task.description }}
    - 路径：{{ task.path }}
    - 依赖：{{ task.depends }}

    - 目标:
      {{ task.goal }}

    - 执行动作:
      {% for a in task.action %}
        - {{ a }}
          {% endfor %}

    - 输出:
      {% for o in task.output %}
        - {{ o }}
          {% endfor %}

    - 验收标准:
      {% for ac in task.acceptance %}
        - {{ ac }}
          {% endfor %}

{% endfor %}
