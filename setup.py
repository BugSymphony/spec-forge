from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="specforge",
    version="0.1.0",
    author="SpecForge Team",
    author_email="17278327036@163.com",
    description="规范驱动的多模态内容生成系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BugSymphony/spec-forge",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        'forge': [
            '../templates/**/*.md',
            '../templates/**/*.yaml',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Natural Language :: Chinese (Simplified)",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "jinja2>=3.0",
        "pyyaml>=6.0",
        "openai>=1.0",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "forge=forge.cli.entry:main",
        ],
    },
    keywords=["规范生成", "多模态", "内容创作", "AI 生成", "模板引擎"],
)
