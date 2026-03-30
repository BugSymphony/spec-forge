"""
Implementation Agent - 执行阶段
负责按照 tasks.md 逐条执行任务并生成最终产物
"""
from typing import Optional, Dict, Any, List, Tuple
import yaml

from .base_agent import BaseAgent
from ..config.constants import Stage
from ..llm.base import BaseLLM
from ..utils.file_tools import FileSystemTools
from ..utils.logging import logger


class ImplementationAgent(BaseAgent):
    """
    Implementation Agent - 任务执行器
    
    核心职责:
    1. 解析 tasks.md，提取任务列表
    2. 逐个执行任务
    3. 更新任务状态
    4. 支持循环执行和单步执行
    5. 与用户交互确认
    """

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(llm)
        self.tasks_data_path = None
        self.tasks_data = None
        self.completed_tasks = set()

    # ========================================
    # 任务加载与查询
    # ========================================

    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        获取所有任务列表.

        支持从以下阶段收集任务：
        - setup.tasks[] - Setup 阶段任务
        - foundation.tasks[] - Foundation 阶段任务
        - stories[].tasks[] - Stories 阶段任务
        - polish.tasks[] - Polish 阶段任务

        Returns:
            所有任务的扁平列表
        """
        if not self.tasks_data:
            return []

        tasks = []

        # 1. 收集 setup 阶段任务
        if 'setup' in self.tasks_data and isinstance(self.tasks_data['setup'], dict):
            setup_tasks = self.tasks_data['setup'].get('tasks', [])
            tasks.extend(setup_tasks)

        # 2. 收集 foundation 阶段任务
        if 'foundation' in self.tasks_data and isinstance(self.tasks_data['foundation'], dict):
            foundation_tasks = self.tasks_data['foundation'].get('tasks', [])
            tasks.extend(foundation_tasks)

        # 3. 收集 stories 阶段任务
        if 'stories' in self.tasks_data and isinstance(self.tasks_data['stories'], list):
            for story in self.tasks_data['stories']:
                story_tasks = story.get('tasks', [])
                tasks.extend(story_tasks)

        # 4. 收集 polish 阶段任务
        if 'polish' in self.tasks_data and isinstance(self.tasks_data['polish'], dict):
            polish_tasks = self.tasks_data['polish'].get('tasks', [])
            tasks.extend(polish_tasks)

        return tasks

    def load_tasks(self) -> bool:
        """
        加载 tasks_data.yaml 文件
            
        Returns:
            是否成功加载
        """
        self.tasks_data_path = self.specs_manager.get_tasks_data_path(must_exist=True)
        if not self.tasks_data_path:
            return False

        # 加载 YAML 数据
        with open(self.tasks_data_path, 'r', encoding='utf-8') as f:
            self.tasks_data = yaml.safe_load(f)

        # 初始化已完成任务集合
        for task in self._get_all_tasks():
            if task.get('status') == 'completed':
                self.completed_tasks.add(task['id'])

        return True

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        获取下一个可执行的任务
            
        Returns:
            任务字典或 None
        """
        if not self.tasks_data:
            return None

        # 遍历所有任务
        for task in self._get_all_tasks():
            if task.get('status') == 'completed':
                continue

            # 检查依赖
            depends = task.get('depends', [])
            if not depends:
                return task

            # 检查所有依赖是否已完成
            all_deps_completed = all(
                dep in self.completed_tasks
                for dep in depends
            )

            if all_deps_completed:
                return task

        return None

    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取任务
                
        Args:
            task_id: 任务 ID
                    
        Returns:
            任务字典或 None
        """
        if not self.tasks_data:
            return None

        # 从所有任务中查找
        for task in self._get_all_tasks():
            if task['id'] == task_id:
                return task

        return None

    # ========================================
    # 任务执行核心
    # ========================================

    def execute_task(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """
        执行单个任务

        Args:
            task: 任务字典

        Returns:
            成功标志，输出内容
        """
        logger.step(f"执行任务：{task['id']}\n")
        logger.info(f"  描述：{task['description']}")
        logger.info(f"  阶段：{task['phase']}")
        logger.info(f"  目标：{task['goal']}")

        try:
            # 1. 构建 Prompt
            context = {
                'current_task': task,
                'completed_tasks': list(self.completed_tasks)
            }
            content_type = self.config.get_content_type()
            prompt = self.build_prompt(Stage.IMPL, content_type, context)

            # 2. 调用 LLM 并解析结果
            result = self.call_llm(prompt)
            task_data = self.parse_yaml(result)

            if not isinstance(task_data, dict):
                return False, f"LLM 返回的数据格式错误：期望 dict，实际为 {type(task_data).__name__}"

            # 3. 统一处理执行结果
            success, msg = self._handle_task_result(task, task_data)

            if success:
                # 4. 标记完成并更新文件
                self.mark_task_completed(task['id'])
                self.update_tasks_file()
                logger.success(f"任务 {task['id']} 已完成")

            return success, msg

        except Exception as e:
            return False, f"执行失败：{e}"

    def _handle_task_result(self, task: Dict[str, Any], task_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        统一处理任务执行结果

        Args:
            task: 任务字典
            task_data: 解析后的任务数据

        Returns: 成功标志，消息
        """
        resources = task_data.get('resources', [])
        if not resources:
            return False, "没有指定资源"

        success, msg = FileSystemTools.run(resources)
        if not success:
            return False, msg
        return True, msg

    # ========================================
    # 任务状态管理
    # ========================================

    def mark_task_completed(self, task_id: str):
        """
        标记任务为已完成（更新 YAML 数据）
            
        Args:
            task_id: 任务 ID
        """
        self.completed_tasks.add(task_id)

        # 更新 YAML 数据中的状态
        task = self.get_task_by_id(task_id)
        if task:
            task['status'] = 'completed'

    def save_yaml_data(self):
        """保存 YAML 数据到文件"""
        if not self.tasks_data_path or not self.tasks_data:
            return

        with open(self.tasks_data_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.tasks_data, f, allow_unicode=True, default_flow_style=False)

        logger.success("tasks_data.yaml 已更新")

    def render_tasks_markdown(self):
        """
        根据 YAML 数据重新渲染 tasks.md
        """
        try:
            template_path = self.get_output_template(Stage.TASKS, self.config.get_content_type())
            output = self.render(template_path, self.tasks_data)

            # 保存到 tasks.md
            tasks_md_path = self.specs_manager.get_tasks_path(must_exist=False)
            if tasks_md_path:
                with open(tasks_md_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                logger.success("tasks.md 已重新渲染\n")
        except Exception as e:
            logger.error(f"渲染 tasks.md 错误：{e}")

    def update_tasks_file(self):
        """
        更新 tasks 数据
        """

        # 保存 YAML 数据
        self.save_yaml_data()

        # 重新渲染 tasks.md
        self.render_tasks_markdown()

    # ========================================
    # 任务执行入口
    # ========================================

    def run_single(self, task_id: Optional[str] = None) -> bool:
        """
        执行单个任务
        
        Args:
            task_id: 指定任务 ID（可选，不指定则自动选择下一个）
            
        Returns:
            是否成功
        """

        if not self.load_tasks():
            logger.error("错误：无法加载 tasks.md\n")
            return False

        # 获取任务
        if task_id:
            # 查找指定任务
            task = self.get_task_by_id(task_id)
            if not task:
                logger.error(f"错误：未找到任务 {task_id}")
                return False
        else:
            # 自动获取下一个可执行任务
            task = self.get_next_task()
            if not task:
                logger.warning("没有可执行的任务")
                return True

        # 执行任务
        success, output = self.execute_task(task)

        if not success:
            logger.error(f"任务执行失败：{output}")
            return False

        return True

    def run_loop(self, auto_confirm: bool = False) -> bool:
        """
        循环执行任务
            
        Args:
            auto_confirm: 是否自动确认
        Returns:
            是否全部成功
        """
        if not self.load_tasks():
            logger.error("错误：无法加载 tasks_data.yaml\n")
            return False

        all_success = False

        while True:
            # 获取下一个任务
            task = self.get_next_task()
            if not task:
                logger.success("所有任务已完成！")
                break

            # 显示任务信息
            logger.info(f"\n{'=' * 60}")
            logger.info(f"下一个任务：{task['id']}")
            logger.info(f"描述：{task['description']}")
            logger.info(f"目标：{task['goal']}")
            logger.info(f"{'=' * 60}\n")

            # 询问用户是否继续
            if not auto_confirm:
                response = input("是否执行此任务？(Y/n/q): ").strip().lower()
                if response == 'q':
                    logger.warning("用户中断执行")
                    break
                elif response == 'n':
                    logger.warning(f"跳过任务 {task['id']}")
                    continue

            # 执行任务
            success, output = self.execute_task(task)

            if not success:
                logger.error(f"任务执行失败 {task['id']} 执行失败: {output}")
                all_success = False

                if not auto_confirm:
                    retry = input("是否重试？(y/N): ").strip().lower()
                    if retry == 'y':
                        continue
                    else:
                        logger.warning(f"跳过任务 {task['id']}，继续下一个")

        return all_success

    def generate(self, mode: str = 'loop', task_id: Optional[str] = None,
                 auto_confirm: bool = False) -> bool:
        """
        主执行入口
        
        Args:
            mode: 执行模式 ('single' | 'loop')
            task_id: 指定任务 ID（single 模式使用）
            auto_confirm: 是否自动确认
            
        Returns:
            是否成功
        """
        if mode == 'single':
            return self.run_single(task_id)
        elif mode == 'loop':
            return self.run_loop(auto_confirm)
        else:
            logger.error(f"错误：未知的执行模式 '{mode}'")
            return False
