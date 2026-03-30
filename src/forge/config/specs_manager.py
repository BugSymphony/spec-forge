"""
Specs 文档管理器
获取用户项目 specs 目录下的各种文档
"""
from pathlib import Path
from typing import Optional, Dict, List


class SpecsManager:
    """Specs 文档管理器 - 统一获取 specs 目录下的文档"""

    def __init__(self, base_dir: Path = Path('.')):
        """
        初始化 Specs 文档管理器
        
        Args:
            base_dir: 项目根目录
        """
        self.base_dir = base_dir
        self.specs_dir = base_dir / "specs"

    def get_spec_path(self, must_exist: bool = True) -> Optional[Path]:
        """
        获取 Spec 文件路径

        Args:
            must_exist: 是否要求文件必须存在（默认 True）

        Returns:
            spec.md 路径 或 None
        """
        spec_path = self.specs_dir / "spec.md"

        if must_exist and not spec_path.exists():
            return None

        return spec_path

    def get_plan_path(self, must_exist: bool = True) -> Optional[Path]:
        """
            获取 Plan 文件路径

            Args:
                must_exist: 是否要求文件必须存在（默认 False）

            Returns:
                plan.md 路径 或 None
            """
        plan_path = self.specs_dir / "plan.md"

        if must_exist and not plan_path.exists():
            return None

        return plan_path

    def get_tasks_path(self, must_exist: bool = True) -> Optional[Path]:
        """
        获取 Tasks 文件路径

        Args:
            must_exist: 是否要求文件必须存在（默认 False）
        
        Returns:
            tasks.md 文件路径 或 None
        """
        tasks_path = self.specs_dir / "tasks.md"

        if must_exist and not tasks_path.exists():
            return None

        return tasks_path

    def get_constitution_path(self, must_exist: bool = True) -> Optional[Path]:
        """
        获取 Constitution 文件路径

        Args:
            must_exist: 是否要求文件必须存在（默认 False）
        
        Returns:
            constitution.md 文件路径 或 None
        """
        constitution_path = self.specs_dir / "constitution.md"

        if must_exist and not constitution_path.exists():
            return None

        return constitution_path

    def get_tasks_data_path(self, must_exist: bool = True) -> Optional[Path]:
        """
        获取 Tasks 数据文件路径

        Args:
            must_exist: 是否要求文件必须存在（默认 False）

        Returns:
            tasks_data.yaml 文件路径 或 None
        """
        tasks_data_path = self.specs_dir / "tasks_data.yaml"

        if must_exist and not tasks_data_path.exists():
            return None

        return tasks_data_path

    def get_stage_document(self, stage: str, must_exist: bool = True) -> Optional[Path]:
        """
        根据阶段名称获取对应的文档路径

        Args:
            stage: 阶段名称（specify/plan/tasks/constitution）
            must_exist: 是否要求文件必须存在（默认 True）

        Returns:
            对应阶段的文档路径，如果不存在则返回 None
        """
        stage_to_file = {
            'specify': self.specs_dir / "spec.md",
            'plan': self.specs_dir / "plan.md",
            'tasks': self.specs_dir / "tasks.md",
            'constitution': self.specs_dir / "constitution.md"
        }

        path = stage_to_file.get(stage)
        if not path:
            return None

        if must_exist and not path.exists():
            return None

        return path

    def get_document_content(self, doc_name: str) -> Optional[str]:
        """
        获取文档内容

        Args:
            doc_name: 文档名称（spec/plan/tasks/constitution）

        Returns:
            文档内容字符串
        """
        doc_path = self.get_stage_document(doc_name)
        if doc_path and doc_path.exists():
            return doc_path.read_text(encoding='utf-8')
        return None

    def get_spec_content(self) -> Optional[str]:
        """获取 Spec 文件内容"""
        return self.get_document_content('spec')

    def get_plan_content(self) -> Optional[str]:
        """获取 Plan 文件内容"""
        return self.get_document_content('plan')

    def get_tasks_content(self) -> Optional[str]:
        """获取 Tasks 文件内容"""
        return self.get_document_content('tasks')

    def get_constitution_content(self) -> Optional[str]:
        """获取 Constitution 文件内容"""
        return self.get_document_content('constitution')

    def list_all_documents(self) -> Dict[str, Optional[Path]]:
        """
        列出所有文档路径

        Returns:
            包含所有文档路径的字典
        """
        return {
            'spec': self.get_spec_path(),
            'plan': self.get_plan_path(),
            'tasks': self.get_tasks_path(),
            'constitution': self.get_constitution_path()
        }

    def check_completeness(self) -> Dict[str, bool]:
        """
        检查文档完整性

        Returns:
            文档存在性检查结果
        """
        docs = self.list_all_documents()
        return {name: (path is not None) for name, path in docs.items()}
