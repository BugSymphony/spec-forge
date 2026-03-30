from abc import ABC, abstractmethod
from typing import Optional

from rich.console import Console


class Logger(ABC):
    """日志接口 - 定义统一的输出规范"""

    @abstractmethod
    def debug(self, msg: str):
        pass

    @abstractmethod
    def info(self, msg: str):
        pass

    @abstractmethod
    def success(self, msg: str):
        pass

    @abstractmethod
    def warning(self, msg: str):
        pass

    @abstractmethod
    def error(self, msg: str):
        pass

    @abstractmethod
    def step(self, msg: str):
        pass


class RichLogger(Logger):
    """基于 Rich 的实现"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def debug(self, msg: str):
        self.console.print(f"[dim]{msg}[/dim]")

    def info(self, msg: str):
        self.console.print(f"{msg}")

    def success(self, msg: str):
        self.console.print(f"[green]✓ {msg}[/green]")

    def warning(self, msg: str):
        self.console.print(f"[yellow]⚠️ {msg}[/yellow]")

    def error(self, msg: str):
        self.console.print(f"[red]✗ {msg}[/red]")

    def step(self, msg: str):
        self.console.print(f"\n[cyan]▶ {msg}[/cyan]")


# 全局实例
logger: Logger = RichLogger()


# 快捷函数
def debug(msg: str): logger.debug(msg)


def info(msg: str): logger.info(msg)


def success(msg: str): logger.success(msg)


def warning(msg: str): logger.warning(msg)


def error(msg: str): logger.error(msg)


def step(msg: str): logger.step(msg)
