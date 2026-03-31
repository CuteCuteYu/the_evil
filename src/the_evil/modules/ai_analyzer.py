#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
AI分析器模块

该模块负责调用AI接口进行分析，包含以下功能：
1. 单个AI对话调用
2. 并行多个AI分析任务
3. 结果整合

使用方式：
    from modules.ai_analyzer import AIAnalyzer

    analyzer = AIAnalyzer()
    result = analyzer.analyze_csv("test.csv", "user_id")

作者: CuteCuteYu
版本: 1.0.0
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI


class AIAnalyzer:
    """
    AI分析器类

    负责管理与AI的交互，包括：
    - API连接管理
    - 并行任务调度
    - 结果收集和整合
    """

    def __init__(self, api_key=None, base_url=None):
        """
        初始化AI分析器

        参数:
            api_key: API密钥，默认从环境变量读取
            base_url: API基础URL，默认从环境变量读取
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get(
            "OPENAI_BASE_URL", "https://open.bigmodel.cn/api/coding/paas/v4"
        )

        if not self.api_key:
            raise ValueError("未设置OPENAI_API_KEY环境变量")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def call_ai(self, system_prompt, user_prompt, model="glm-4", temperature=0.7):
        """
        调用AI接口进行单次对话

        参数:
            system_prompt: 系统提示词，定义AI角色
            user_prompt: 用户提示词，包含分析要求
            model: 使用的模型名称，默认glm-4
            temperature: 温度参数，控制输出随机性，默认0.7

        返回:
            AI回复内容字符串
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def parallel_analyze(self, tasks, max_workers=None, model="glm-4"):
        """
        并行执行多个AI分析任务

        参数:
            tasks: 任务列表，每个任务是一个元组 (system_prompt, user_prompt, task_name)
            max_workers: 最大并行数，默认根据任务数量自动设置
            model: 使用的模型名称，默认glm-4

        返回:
            任务结果字典，key为task_name，value为分析结果
        """
        if max_workers is None:
            max_workers = len(tasks)

        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for system_prompt, user_prompt, task_name in tasks:
                future = executor.submit(
                    self.call_ai, system_prompt, user_prompt, model=model
                )
                future_to_task[future] = task_name

            # 收集结果
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    results[task_name] = future.result()
                    print(f"  [{task_name}] 分析完成")
                except Exception as e:
                    print(f"  [{task_name}] 分析失败: {e}")
                    results[task_name] = f"分析失败: {e}"

        return results


def create_analysis_tasks(csv_content, prompts_module):
    """
    创建所有分析任务

    参数:
        csv_content: CSV文件内容字符串
        prompts_module: 提示词模块对象

    返回:
        任务列表，每个元素是 (system_prompt, user_prompt, task_name) 元组
    """
    tasks = []

    # 1. 总体统计分析
    tasks.append(
        (
            prompts_module.STATISTICS_SYSTEM_PROMPT,
            prompts_module.STATISTICS_USER_PROMPT.format(content=csv_content),
            "statistics",
        )
    )

    # 2-1. 性格特点分析
    tasks.append(
        (
            prompts_module.PERSONALITY_SYSTEM_PROMPT,
            prompts_module.PERSONALITY_USER_PROMPT.format(content=csv_content),
            "personality",
        )
    )

    # 2-2. 兴趣爱好分析
    tasks.append(
        (
            prompts_module.INTEREST_SYSTEM_PROMPT,
            prompts_module.INTEREST_USER_PROMPT.format(content=csv_content),
            "interest",
        )
    )

    # 2-3. 活动轨迹分析
    tasks.append(
        (
            prompts_module.TRAJECTORY_SYSTEM_PROMPT,
            prompts_module.TRAJECTORY_USER_PROMPT.format(content=csv_content),
            "trajectory",
        )
    )

    # 2-4. 社交圈子分析
    tasks.append(
        (
            prompts_module.SOCIAL_SYSTEM_PROMPT,
            prompts_module.SOCIAL_USER_PROMPT.format(content=csv_content),
            "social",
        )
    )

    # 2-5. 情感表达分析
    tasks.append(
        (
            prompts_module.EMOTION_SYSTEM_PROMPT,
            prompts_module.EMOTION_USER_PROMPT.format(content=csv_content),
            "emotion",
        )
    )

    return tasks


def format_report_prompt(prompts_module, results):
    """
    格式化综合报告生成提示词

    参数:
        prompts_module: 提示词模块对象
        results: 分析结果字典

    返回:
        格式化后的用户提示词字符串
    """
    template = prompts_module.REPORT_USER_PROMPT

    return template.format(
        result1=results.get("statistics", ""),
        result2_1=results.get("personality", ""),
        result2_2=results.get("interest", ""),
        result2_3=results.get("trajectory", ""),
        result2_4=results.get("social", ""),
        result2_5=results.get("emotion", ""),
    )
