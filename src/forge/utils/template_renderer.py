from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from pathlib import Path
from typing import Dict, Any, Union

from forge import RenderError


class TemplateRenderer:
    """
    Jinja2 模板渲染器
    """

    @staticmethod
    def render_string(template_str: str, context: Dict[str, Any]) -> str:
        """
        直接渲染模板字符串

        Args:
            template_str: 模板字符串
            context: 模板上下文变量

        Returns:
            渲染后的文本

        Raises:
            TemplateRenderFailedError: 渲染失败
        """
        try:
            env = Environment(
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )
            template = env.from_string(template_str)
            return template.render(**context)
        except Exception as e:
            raise RenderError(f"模板字符串渲染失败：{str(e)}")

    @staticmethod
    def render_from_path(
            template_path: Union[str, Path],
            context: Dict[str, Any]
    ) -> str:
        template_file = Path(template_path)

        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在：{template_path}")

        if not template_file.is_file():
            raise FileNotFoundError(f"模板路径不是文件：{template_path}")

        try:
            loader = FileSystemLoader(
                str(template_file.parent),
                encoding='utf-8'
            )

            env = Environment(
                loader=loader,
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True
            )

            template = env.get_template(template_file.name)
            return template.render(**context)

        except TemplateNotFound:
            raise FileNotFoundError(f"模板文件不存在：{template_path}")
        except Exception as e:
            raise RenderError(f"模板 '{template_path}' 渲染失败：{str(e)}")

    @staticmethod
    def render_to_file(
            template_path: Union[str, Path],
            context: Dict[str, Any],
            output_path: Union[str, Path],
            create_dirs: bool = True
    ) -> Path:

        content = TemplateRenderer.render_from_path(
            template_path,
            context
        )

        output_file = Path(output_path)

        if create_dirs:
            output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[green]✅ 模板已保存到文件：{output_file.absolute()}[/green]")
        return output_file
