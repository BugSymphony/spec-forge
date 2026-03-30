"""
文件操作工具类
提供安全的文件和目录操作功能
"""
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from enum import Enum

from forge.utils.logging import logger


class ResourceType(str, Enum):
    """资源类型枚举"""
    FILE = "file"
    DIRECTORY = "directory"


class FileAction(str, Enum):
    """文件操作枚举"""
    CREATE_DIR = "create_dir"  # 创建目录
    CREATE_EMPTY_FILE = "create_empty_file"  # 创建空文件
    WRITE_CONTENT = "write_content"  # 写入内容
    COPY = "copy"  # 复制
    MOVE = "move"  # 移动
    DELETE = "delete"  # 删除


class ResourceSpec:
    """
    资源规格说明
    
    用于描述一个资源 (文件、目录或其他) 的完整信息和操作意图
    
    Attributes:
        path: 资源路径
        resource_type: 类型 (file/directory)
        action: 操作类型
        content: 内容 (仅 write_content 时需要)
        metadata: 额外元数据
    """

    def __init__(self, path: str, resource_type: str = "file",
                 action: str = "create_empty_file",
                 content: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.path = path
        self.resource_type = ResourceType(resource_type)
        self.action = FileAction(action)
        self.content = content
        self.metadata = metadata or {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceSpec':
        """从字典创建 ResourceSpec"""
        return cls(
            path=data.get('path', ''),
            resource_type=data.get('type', 'file'),
            action=data.get('action', 'create_empty_file'),
            content=data.get('content'),
            metadata=data.get('metadata', {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'path': self.path,
            'type': self.resource_type.value,
            'action': self.action.value,
            'content': self.content,
            'metadata': self.metadata
        }


class FileSystemTools:
    """文件系统操作工具类"""

    @staticmethod
    def create_directory(path: str, base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        创建目录
        
        Args:
            path: 目录路径
            base_dir: 基础目录 (可选)
            
        Returns:
            (成功标志，消息)
        """
        try:
            dir_path = Path(path) if Path(path).is_absolute() else (base_dir or Path.cwd()) / path
            dir_path.mkdir(parents=True, exist_ok=True)
            return True, f"目录：{dir_path}"
        except Exception as e:
            return False, f"创建目录失败：{e}"

    @staticmethod
    def create_empty_file(path: str, base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        创建空文件
        
        Args:
            path: 文件路径
            base_dir: 基础目录 (可选)
            
        Returns:
            (成功标志，消息)
        """
        try:
            file_path = Path(path) if Path(path).is_absolute() else (base_dir or Path.cwd()) / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.touch()
            return True, f"文件：{file_path}"
        except Exception as e:
            return False, f"创建文件失败：{e}"

    @staticmethod
    def write_content(path: str, content: str, base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        写入内容到文件
        
        Args:
            path: 文件路径
            content: 要写入的内容
            base_dir: 基础目录 (可选)
            
        Returns:
            (成功标志，消息)
        """
        try:
            file_path = Path(path) if Path(path).is_absolute() else (base_dir or Path.cwd()) / path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, str(file_path)
        except Exception as e:
            return False, f"写入文件失败：{e}"

    @staticmethod
    def is_directory_path(path: str) -> bool:
        """
        判断路径是否为目录标识符
        
        Args:
            path: 待检查的路径
            
        Returns:
            是否为目录标识符
        """
        return path in ['.', './', '../']

    @classmethod
    def run(cls, resources: List[Dict[str, Any]],
            base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        results = []

        for res_data in resources:
            if 'type' not in res_data:
                res_data['type'] = 'file'  # 默认值

            resource = ResourceSpec.from_dict(res_data)
            success, msg = cls._run_resource(resource, base_dir)
            if success:
                results.append(msg)
            else:
                return False, msg

        if results:
            return True, f"已完成：{', '.join(results)}"
        return False, "未找到有效的资源操作"

    @classmethod
    def _run_resource(cls, resource: ResourceSpec,
                      base_dir: Optional[Path] = None) -> Tuple[bool, str]:
        """
        运行单个资源操作
            
        Args:
            resource: ResourceSpec 对象
            base_dir: 基础目录
                
        Returns:
            (成功标志，消息)
        """
        if resource.action == FileAction.CREATE_DIR:
            success, msg = cls.create_directory(resource.path, base_dir)
            if success:
                logger.success(f"创建目录：{msg}")
            return success, msg

        elif resource.action == FileAction.CREATE_EMPTY_FILE:
            success, msg = cls.create_empty_file(resource.path, base_dir)
            if success:
                logger.success(f"创建空文件：{msg}")
            return success, msg

        elif resource.action == FileAction.WRITE_CONTENT:
            if not resource.content:
                return False, f"写入内容不能为空：{resource.path}"
            success, msg = cls.write_content(resource.path, resource.content, base_dir)
            if success:
                logger.success(f"写入内容：{msg}")
            return success, msg

        else:
            return False, f"不支持的操作类型：{resource.action}"
