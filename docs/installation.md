# 安装指引

## 环境要求

- **Python**: 3.10 或更高版本
- **pip**: 最新版本推荐
- **git**: 用于克隆仓库

## 源码安装

```bash
git clone https://github.com/your-org/specforge.git
cd specforge
pip install -e .
```

安装完成后验证：

```bash
specforge --version
```

## 依赖说明

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| click | >= 8.1 | CLI 命令框架 |
| pyyaml | >= 6.0 | YAML 配置文件解析 |
| questionary | >= 2.0 | 交互式命令行提示 |
| rich | >= 13.0 | 终端格式化输出 |

## 环境检查

```bash
specforge check
```

该命令会检查后端工具可用性、模板完整性和文件系统权限。
