"""
/implement 命令处理
执行 tasks.md 中定义的任务，生成最终产物
"""
from pathlib import Path
from typing import Optional

from ..config import ProjectConfig
from ..config.specs_manager import SpecsManager
from ..agents.impl_agent import ImplementationAgent
from ..exceptions import RenderError, YAMLParseError, LLMError
from ..llm.factory import init_llm
from ..utils.logging import logger


def handle_implement(
        mode: str = 'loop',
        task_id: Optional[str] = None,
        auto_confirm: bool = False,
        llm_provider: str = None
):
    """
    处理 implement 命令
    
    Args:
        mode: 执行模式 ('single' | 'loop')
        task_id: 指定任务 ID（single 模式使用）
        auto_confirm: 是否自动确认（loop 模式使用）
        llm_client: LLM 客户端名称（openai|deepseek）
    """
    logger.info(f"[bold blue]✨ SpecForge - Implementation 执行器[/bold blue]")

    # 1. 检查项目是否已初始化
    config = ProjectConfig()
    content_type = config.get_content_type()
    logger.debug(f"内容类型：{content_type}")

    # 2. 检查必要文件是否存在
    specs_mgr = SpecsManager()

    required_files = {
        'Spec': specs_mgr.get_spec_path(),
        'Plan': specs_mgr.get_plan_path(),
        'Tasks': specs_mgr.get_tasks_path()
    }

    for name, path in required_files.items():
        if not path or not path.exists():
            logger.error(f"错误：{name} 文件不存在：{path or 'N/A'}")
            return

    logger.debug(f"✓ Spec: {required_files['Spec']}")
    logger.debug(f"✓ Plan: {required_files['Plan']}")
    logger.debug(f"✓ Tasks: {required_files['Tasks']}")

    # 3. 初始化 LLM
    llm = init_llm(provider=llm_provider)

    # 4. 创建 Agent
    agent = ImplementationAgent(llm=llm)

    # 5. 执行模式说明
    if mode == 'single':
        logger.step(f"执行模式：单步执行")
        if task_id:
            logger.warning("  目标任务：{task_id}")
        else:
            logger.warning("  目标任务：下一个可执行任务")
    elif mode == 'loop':
        logger.step(f"执行模式：循环执行")
        if auto_confirm:
            logger.info("  交互：禁用（自动执行）")
        else:
            logger.info(" 交互：启用（每个任务前询问）")

    # 6. 执行
    logger.info("\n[bold]开始执行任务...[/bold]\n")

    try:
        success = agent.generate(
            mode=mode,
            task_id=task_id,
            auto_confirm=auto_confirm
        )

        if success:
            logger.success("执行完成！")

            # 显示输出位置
            dist_dir = Path('./dist')
            if dist_dir.exists():
                logger.warning(f"生成的产物:")
                for file in dist_dir.rglob('*'):
                    if file.is_file():
                        logger.info(f"  📄 {file.relative_to(dist_dir)}")
        else:
            logger.warning("执行过程中遇到错误")

    except LLMError as e:
        logger.error(f"LLM 错误：{e}")
    except YAMLParseError as e:
        logger.error(f"YAML 解析错误：{e}")
    except RenderError as e:
        logger.error(f"渲染错误：{e}")
    except KeyboardInterrupt:
        logger.warning("用户中断执行")
    except Exception as e:
        logger.error(f"错误：{e}")
        import traceback
        traceback.print_exc()
