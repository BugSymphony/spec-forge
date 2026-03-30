"""
LLM 工厂
统一初始化 LLM 客户端
"""
from forge.utils.logging import logger


def init_llm(provider: str = None, verbose: bool = True):
    """
    初始化 LLM 客户端（通用）

    Args:
        provider: LLM 提供商（deepseek/openai），从配置读取
        verbose: 是否输出日志

    Returns:
        LLM 客户端实例或 None
    """

    from .deepseek import DeepSeekClient
    from .openai import OpenAIClient

    # 1. 从配置读取提供商
    if not provider:
        try:
            from forge.config.project_config import ProjectConfig
            config = ProjectConfig()
            provider = config.get_llm_provider()
        except Exception:
            provider = 'deepseek'  # 默认值

    # 2. 根据提供商初始化
    if provider == 'openai':
        try:
            client = OpenAIClient()
            if verbose:
                logger.debug(f"使用 OpenAI: {client.model}")
            return client
        except Exception as e:
            if verbose:
                logger.error(f"OpenAI 初始化失败：{e}")
    elif provider == 'deepseek':
        try:
            client = DeepSeekClient()
            if verbose:
                logger.debug(f"使用 DeepSeek: {client.model}")
            return client
        except Exception as e:
            if verbose:
                logger.error(f"DeepSeek 初始化失败：{e}")
    else:
        if verbose:
            logger.warning(f"未知的 LLM 提供商：{provider}，尝试使用 DeepSeek")
        try:
            client = DeepSeekClient()
            if verbose:
                logger.debug(f"使用 DeepSeek: {client.model}")
            return client
        except Exception:
            pass

    # 3. fallback
    if verbose:
        logger.warning("LLM 未配置，将使用模板生成占位符 Spec")

    return None
