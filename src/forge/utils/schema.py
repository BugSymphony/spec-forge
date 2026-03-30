"""
YAML Schema 解析器
用于加载和解析内容类型的 YAML Schema 定义
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class SchemaParser:
    """YAML Schema 解析器"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """
        初始化 Schema 解析器
        
        Args:
            schema_path: Schema 文件路径（可选）
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema: Optional[Dict[str, Any]] = None
    
    def load(self, schema_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载 YAML Schema 文件
        
        Args:
            schema_path: Schema 文件路径
            
        Returns:
            Schema 字典
            
        Raises:
            FileNotFoundError: 文件不存在
            yaml.YAMLError: YAML 解析失败
        """
        path = Path(schema_path) if schema_path else self.schema_path
        
        if not path.exists():
            raise FileNotFoundError(f"Schema 文件不存在：{path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.schema = yaml.safe_load(f)
            return self.schema
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 解析失败：{str(e)}")
    
    def get_required_fields(self) -> list:
        """
        获取必填字段列表
        
        Returns:
            必填字段名称列表
        """
        if not self.schema:
            return []
        
        # 支持两种格式：
        # 1. 顶层 required 字段
        # 2. properties 中每个字段的 required 属性
        required = self.schema.get('required', [])
        
        # 如果没有顶层 required，尝试从 properties 提取
        if not required and 'properties' in self.schema:
            props = self.schema['properties']
            for field_name, field_def in props.items():
                if isinstance(field_def, dict) and field_def.get('required', False):
                    required.append(field_name)
        
        return required
    
    def get_optional_fields(self) -> list:
        """
        获取可选字段列表
        
        Returns:
            可选字段名称列表
        """
        if not self.schema or 'properties' not in self.schema:
            return []
        
        required = set(self.get_required_fields())
        all_fields = set(self.schema['properties'].keys())
        
        return list(all_fields - required)
    
    def get_field_definition(self, field_name: str) -> Optional[Dict[str, Any]]:
        """
        获取字段定义
        
        Args:
            field_name: 字段名称
            
        Returns:
            字段定义字典
        """
        if not self.schema or 'properties' not in self.schema:
            return None
        
        return self.schema['properties'].get(field_name)
    
    def validate_structure(self, data: Dict[str, Any]) -> tuple[bool, list]:
        """
        验证数据结构是否符合 Schema
        
        Args:
            data: 待验证的数据字典
            
        Returns:
            (是否有效，错误信息列表)
        """
        errors = []
        
        if not self.schema:
            errors.append("Schema 未加载")
            return False, errors
        
        # 检查必填字段
        required_fields = self.get_required_fields()
        for field in required_fields:
            if field not in data:
                errors.append(f"缺少必填字段：{field}")
        
        # 如果数据中有字段不在 Schema 中，警告但不报错
        if 'properties' in self.schema:
            allowed_fields = set(self.schema['properties'].keys())
            for key in data.keys():
                if key not in allowed_fields:
                    errors.append(f"警告：未知字段 '{key}' 不在 Schema 中")
        
        return len(errors) == 0, errors
