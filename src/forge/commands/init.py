"""
项目初始化命令
创建 .forge 配置目录，加载内容类型相关的 schema 和模板
"""
from pathlib import Path

import yaml
import shutil

from ..config.constants import ContentType
from ..config.resource_template_config import ResourceTemplateConfig
from ..utils.logging import logger


def handle_init(
        content_type: str,
        force: bool = False
):
    """
    处理 init 命令
    
    Args:
        content_type: 内容类型（novel|article|comic|video）
        force: 是否强制覆盖已存在的配置
    """
    logger.info(f"\n[bold blue]✨ SpecForge - 项目初始化[/bold blue]\n")

    # 1. 验证内容类型
    valid_types = ContentType.values()
    if content_type not in valid_types:
        logger.error(f"无效的内容类型：{content_type}")
        logger.info(f"💡 可选类型：{', '.join(valid_types)}")
        return

    # 2. 创建 .forge 目录结构
    forge_dir = Path(".forge")

    if forge_dir.exists():
        if not force:
            logger.warning("  .forge 目录已存在")
            logger.info("💡 使用 --force 参数强制重新初始化\n")

            # 显示现有配置
            config_file = forge_dir / "config.yaml"
            if config_file.exists():
                _show_current_config(config_file)
            return

        # 强制模式：清理旧配置
        logger.info("[dim]正在清理旧配置...[/dim]")
        shutil.rmtree(forge_dir)

    # 按阶段组织目录
    agent_prompts_specify = forge_dir / "agent-prompts" / "specify"
    agent_prompts_plan = forge_dir / "agent-prompts" / "plan"
    agent_prompts_tasks = forge_dir / "agent-prompts" / "tasks"
    agent_prompts_implement = forge_dir / "agent-prompts" / "implement"

    output_docs_constitution = forge_dir / "output-docs" / "constitution"
    output_docs_specify = forge_dir / "output-docs" / "specify"
    output_docs_plan = forge_dir / "output-docs" / "plan"
    output_docs_tasks = forge_dir / "output-docs" / "tasks"

    # 创建目录结构
    forge_dir.mkdir(exist_ok=True)
    agent_prompts_specify.mkdir(parents=True, exist_ok=True)
    agent_prompts_plan.mkdir(parents=True, exist_ok=True)
    agent_prompts_tasks.mkdir(parents=True, exist_ok=True)

    output_docs_constitution.mkdir(parents=True, exist_ok=True)
    output_docs_specify.mkdir(parents=True, exist_ok=True)
    output_docs_plan.mkdir(parents=True, exist_ok=True)
    output_docs_tasks.mkdir(parents=True, exist_ok=True)

    logger.info(f"✅ 创建配置目录：[dim]{forge_dir.absolute()}[/dim]")

    # 3. 复制模板文件

    # 定义各阶段的模板配置
    stage_configs = {
        'specify': [
            ('schema', output_docs_specify / "schema.yaml", "Specify Schema", f"{content_type}/schema.yaml"),
            ('output', output_docs_specify / "template.md", "Specify 输出模板", f"{content_type}/template.md"),
            ('prompt', agent_prompts_specify / "prompt.md", "Specify Prompt", f"{content_type}.md"),
        ],
        'plan': [
            ('prompt', agent_prompts_plan / "prompt.md", "Plan Prompt", f"{content_type}.md"),
            ('output', output_docs_plan / "template.md", "Plan 输出模板", f"{content_type}/template.md"),
            ('schema', output_docs_plan / "schema.yaml", "Plan Schema", f"{content_type}/schema.yaml"),
        ],
        'tasks': [
            ('prompt', agent_prompts_tasks / "prompt.md", "Tasks Prompt", f"{content_type}.md"),
            ('output', output_docs_tasks / "template.md", "Tasks 输出模板", f"{content_type}/template.md"),
            ('schema', output_docs_tasks / "schema.yaml", "Tasks Schema", f"{content_type}/schema.yaml"),
        ],
        'implement': [
            ('prompt', agent_prompts_implement / "prompt.md", "Implement Prompt", f"{content_type}.md"),
        ],
        'constitution': [
            (
                'output', output_docs_constitution / "template.md", "Constitution 输出模板",
                f"{content_type}/template.md"),
        ]
    }

    # 创建 ResourceTemplateConfig 实例
    resource_config = ResourceTemplateConfig()

    # 按阶段复制模板文件
    for stage_name, files in stage_configs.items():
        for file_type, target_path, description, success_msg in files:
            resource_path = resource_config.get_stage_template(stage_name, file_type, content_type);

            _copy_template_file(
                resource_path=resource_path,
                target_path=target_path,
                description=description
            )

            if success_msg:
                logger.info(f"✅ 加载{description}: {success_msg}")

    # 4. Specs 内置 Constitution 模板

    # 准备 specs 目录
    specs_content_dir = Path("specs")
    specs_content_dir.mkdir(parents=True, exist_ok=True)

    _copy_template_file(
        resource_path=resource_config.get_output_template('constitution', content_type),
        target_path=specs_content_dir / "constitution.md",
        description="Constitution"
    )
    logger.info(f"✅ 加载 Constitution 模板：{content_type}/constitution.md")

    # 5. 创建配置文件
    # 注意：config.yaml 中的路径是相对于config.yaml 的相对路径（不包含 .forge/）
    config_data = {
        'version': '1.0',
        'content_type': content_type,
        'llm_provider': 'deepseek',
        'stages': transform_stage_configs(stage_configs, forge_dir)
    }

    config_file = forge_dir / "config.yaml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True, default_flow_style=False)
    logger.info(f"✅ 创建配置文件：config.yaml")

    # 6. 创建 .gitignore
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(".forge/\n")
            f.write("specs/\n")
        logger.info(f"✅ 创建 .gitignore")

    # 7. 显示完成信息
    logger.info("\n[green]✨ 项目初始化完成！[/green]\n")
    logger.info("📁 项目结构:")
    _show_project_structure(stage_configs, forge_dir, content_type)
    logger.info("")
    logger.info("💡 下一步:")
    logger.info(f"  forge specify --idea=\"你的创意想法\"")
    logger.info(f"  forge plan")
    logger.info(f"  forge tasks")
    logger.info("")
    logger.info("[dim]提示：所有命令将自动使用当前初始化的内容类型 ({})[/dim]".format(content_type))


def _show_project_structure(stage_configs: dict, forge_dir: Path, content_type: str):
    """动态显示项目结构"""
    # .forge 目录
    logger.info("  .forge/")
    logger.info("  ├── config.yaml                    # 项目配置")

    # agent-prompts 目录
    logger.info("  ├── agent-prompts/")

    # 按阶段展示 agent-prompts 下的 prompt 文件
    stages_with_prompts = [stage for stage in ['specify', 'plan', 'tasks', 'implement'] if stage in stage_configs]
    for idx, stage in enumerate(stages_with_prompts):
        is_last_stage = (idx == len(stages_with_prompts) - 1)
        prefix = "      ├── " if not is_last_stage else "      └── "

        logger.info(f"{prefix}{stage}/")
        logger.info(
            f"{'      │   ' if not is_last_stage else '          '}└── prompt.md              # {stage.capitalize()} Prompt")

    # output-docs 目录
    logger.info("  ├── output-docs/")

    # 按阶段展示 output-docs 下的文件
    stages_with_outputs = [stage for stage in ['constitution', 'specify', 'plan', 'tasks'] if stage in stage_configs]
    for idx, stage in enumerate(stages_with_outputs):
        is_last_stage = (idx == len(stages_with_outputs) - 1)
        prefix = "      ├── " if not is_last_stage else "      └── "
        indent = "      │   " if not is_last_stage else "          "

        logger.info(f"{prefix}{stage}/")

        # 获取该阶段的文件
        stage_files = stage_configs[stage]
        output_files = [(ft, desc) for ft, _, desc, _ in stage_files if ft in ['schema', 'output']]

        for file_idx, (file_type, desc) in enumerate(output_files):
            is_last_file = file_idx == len(output_files) - 1
            file_prefix = indent + ("└── " if is_last_file else "├── ")

            if file_type == 'schema':
                logger.info(f"{file_prefix}schema.yaml            # {desc}")
            elif file_type == 'output':
                logger.info(f"{file_prefix}template.md            # {desc}")

    # specs 目录
    logger.info("  specs/")
    logger.info(f"  └── constitution.md                # {content_type} 创作宪法")


def normalize_path(path: Path) -> str:
    return path.as_posix()


def transform_stage_configs(stage_configs: dict, forge_dir: Path) -> dict:
    """
    将 stage_configs 转换为目标结构（用于 config.yaml）

    Args:
        stage_configs: 阶段配置字典
         forge_dir: .forge 目录路径

     Returns:
         转换后的配置字典，路径为相对于 forge_dir 的相对路径
     """
    result = {}

    for stage, configs in stage_configs.items():
        stage_dict = {}

        for item in configs:
            key, path_obj, *_ = item  # 只取前两个字段
            # 转换为相对于 forge_dir 的路径
            relative_path = path_obj.relative_to(forge_dir)
            stage_dict[key] = normalize_path(relative_path)

        result[stage] = stage_dict

    return result


def _copy_template_file(
        resource_path: Path,
        target_path: Path,
        description: str
) -> bool:
    """
    通用模板文件复制函数（从 forge templates 到用户项目 .forge）

    Args:
        resource_path: 资源模板路径（from forge templates）
        target_path: 目标文件路径（to user project .forge）
        description: 文件描述（用于输出）

    Returns:
        是否成功复制
    """
    if resource_path and resource_path.exists():
        content = resource_path.read_text(encoding='utf-8')
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding='utf-8')
        return True
    else:
        logger.warning(f" {description} 不存在：{resource_path}")
        return False


def _show_current_config(config_file: Path):
    """显示当前配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        logger.info("📋 当前配置:")
        logger.info(f"  内容类型：[bold]{config.get('content_type', 'unknown')}[/bold]")
        logger.info(f"  版本：{config.get('version', 'unknown')}")
    except Exception as e:
        logger.info(f"[yellow]无法读取配置：{e}[/yellow]")


def list_content_types():
    """列出所有内容类型"""
    logger.info("\n[bold]可用的内容类型:[/bold]\n")

    types = [
        ('novel', '小说', '长篇小说、短篇故事、网络文学'),
        ('article', '文章', '技术文章、博客、评论、教程'),
        ('comic', '漫画', '日式漫画、条漫、绘本'),
        ('video', '视频', '短视频、纪录片、教育视频'),
    ]

    for type_id, name, desc in types:
        logger.info(f"  [cyan]{type_id:12}[/cyan] - {name}")
        logger.info(f"  [dim]{' ' * 12}  {desc}[/dim]")
        logger.info("")
