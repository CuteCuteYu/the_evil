#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
AI分析器模块

该模块负责调用AI接口进行分析，包含以下功能：
1. 单个AI对话调用
2. 并行多个AI分析任务
3. 结果整合
4. 质量检查与自动补充（核心功能，强制启用）

使用方式：
    from modules.ai_analyzer import AIAnalyzer

    analyzer = AIAnalyzer()
    # 质量检查自动启用
    result = analyzer.parallel_analyze_with_quality_check(
        tasks
    )

作者: CuteCuteYu
版本: 2.0.0
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from openai import OpenAI

# 导入统一配置
try:
    from the_evil.modules.config import (
        DEFAULT_MODEL,
        DEFAULT_TEMPERATURE,
        MAX_WORKERS,
        API_KEY_ENV_VAR,
        DEFAULT_BASE_URL,
    )
except ImportError:
    # 回退到相对导入（当作为包直接导入时）
    from .config import (
        DEFAULT_MODEL,
        DEFAULT_TEMPERATURE,
        MAX_WORKERS,
        API_KEY_ENV_VAR,
        DEFAULT_BASE_URL,
    )

# 导入质量检查模块（核心功能，强制启用）
QUALITY_CHECK_AVAILABLE = False
QualityChecker = None
create_quality_checker = None

try:
    from the_evil.modules.quality_checker import QualityChecker, create_quality_checker

    QUALITY_CHECK_AVAILABLE = True
except ImportError:
    try:
        from .quality_checker import QualityChecker, create_quality_checker

        QUALITY_CHECK_AVAILABLE = True
    except ImportError:
        import warnings

        warnings.warn(
            "质量检查模块未找到，分析质量可能无法保证。"
            "请确保 quality_checker.py 文件存在于 modules 目录中。",
            ImportWarning,
        )


class AIAnalyzer:
    """
    AI分析器类

    负责管理与AI的交互，包括：
    - API连接管理
    - 并行任务调度
    - 结果收集和整合
    - 质量检查与自动补充（核心功能，强制启用）
    - 单个任务报告保存（核心功能，强制启用）
    """

    def __init__(self, api_key=None, base_url=None):
        """
        初始化AI分析器

        参数:
            api_key: API密钥，默认从环境变量读取
            base_url: API基础URL，默认从环境变量读取
        """
        self.api_key = api_key or os.environ.get(API_KEY_ENV_VAR)
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)

        if not self.api_key:
            raise ValueError(f"未设置{API_KEY_ENV_VAR}环境变量")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def call_ai(self, system_prompt, user_prompt, model=None, temperature=None):
        """
        调用AI接口进行单次对话

        参数:
            system_prompt: 系统提示词，定义AI角色
            user_prompt: 用户提示词，包含分析要求
            model: 使用的模型名称，默认使用配置文件中的DEFAULT_MODEL
            temperature: 温度参数，控制输出随机性，默认使用配置文件中的DEFAULT_TEMPERATURE

        返回:
            AI回复内容字符串
        """
        # 使用配置文件的默认值
        if model is None:
            model = DEFAULT_MODEL
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def parallel_analyze(self, tasks, max_workers=None, model=None):
        """
        并行执行多个AI分析任务

        参数:
            tasks: 任务列表，每个任务是一个元组 (system_prompt, user_prompt, task_name)
            max_workers: 最大并行数，默认使用配置文件中的MAX_WORKERS
            model: 使用的模型名称，默认使用配置文件中的DEFAULT_MODEL

        返回:
            任务结果字典，key为task_name，value为分析结果
        """
        # 使用配置文件的默认值
        if max_workers is None:
            max_workers = MAX_WORKERS
        if model is None:
            model = DEFAULT_MODEL

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

    def parallel_analyze_with_quality_check(
        self,
        tasks,
        max_workers=None,
        model=None,
        enable_quality_check=True,
        quality_config=None,
        save_individual_reports=True,
        output_dir=None,
        base_filename=None,
    ):
        """
        并行执行多个AI分析任务（带质量检查，强制启用）

        在原有并行分析的基础上，增加了质量检查和自动补充功能。
        每个任务完成后会进行质量检查，如果不合格会自动请求AI补充。
        每个任务通过质量检查后，会自动保存单个任务报告到本地（强制执行）。

        参数:
            tasks: 任务列表，每个任务是一个元组 (system_prompt, user_prompt, task_name)
            max_workers: 最大并行数，默认使用配置文件中的MAX_WORKERS
            model: 使用的模型名称，默认使用配置文件中的DEFAULT_MODEL
            enable_quality_check: 是否启用质量检查（保留参数用于兼容，默认强制True）
            quality_config: 质量检查配置字典，如不指定则使用配置文件中的默认值
            save_individual_reports: 是否保存单个任务报告（强制启用，保留参数仅用于兼容）
            output_dir: 输出目录路径，与CSV文件同目录
            base_filename: 基础文件名（不含扩展名），用于生成子报告文件名

        返回:
            增强版任务结果字典，每个结果包含:
            - 'content': 最终内容
            - 'quality_info': 质量检查信息
            - 'supplement_rounds': 补充轮数
            - 'report_file': 单个任务报告文件路径（如果保存成功）

        异常:
            RuntimeError: 当质量检查模块不可用时抛出
        """
        # 导入质量检查配置
        try:
            from the_evil.modules.config import QualityCheckConfig
        except ImportError:
            from .config import QualityCheckConfig

        # 质量检查是核心功能，如果不可用则抛出错误
        if not QUALITY_CHECK_AVAILABLE:
            raise RuntimeError(
                "质量检查模块不可用，无法继续执行分析。"
                "请确保 quality_checker.py 文件存在于 modules 目录中。"
            )

        # 使用配置文件的默认值
        if max_workers is None:
            max_workers = MAX_WORKERS
        if model is None:
            model = DEFAULT_MODEL

        # 创建质量检查器（使用配置文件的默认值或用户提供的配置）
        config = quality_config or {}
        quality_checker = create_quality_checker(
            min_length=config.get("min_length", QualityCheckConfig.MIN_LENGTH),
            require_evidence=config.get(
                "require_evidence", QualityCheckConfig.REQUIRE_EVIDENCE
            ),
            max_supplement_rounds=config.get(
                "max_supplement_rounds", QualityCheckConfig.MAX_SUPPLEMENT_ROUNDS
            ),
        )

        results = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for system_prompt, user_prompt, task_name in tasks:
                future = executor.submit(
                    self._analyze_single_with_quality,
                    system_prompt,
                    user_prompt,
                    task_name,
                    model,
                    quality_checker,
                )
                future_to_task[future] = task_name

            # 收集结果
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result()
                    results[task_name] = result

                    # 输出进度信息（质量检查信息）
                    score = result["quality_info"].get("score", 0)
                    rounds = result.get("supplement_rounds", 0)
                    print(
                        f"  [{task_name}] 分析完成 (质量评分: {score:.0f}, 补充轮数: {rounds})"
                    )

                    # 保存单个任务报告（强制执行）
                    if save_individual_reports and base_filename:
                        report_file = self._save_individual_report(
                            task_name=task_name,
                            content=result["content"],
                            output_dir=output_dir or ".",
                            base_filename=base_filename,
                            quality_info=result["quality_info"],
                        )
                        result["report_file"] = report_file
                        if report_file:
                            print(f"  [{task_name}] 报告已保存至: {report_file}")

                except Exception as e:
                    print(f"  [{task_name}] 分析失败: {e}")
                    results[task_name] = {"content": f"分析失败: {e}", "error": str(e)}

        return results

    def _analyze_single_with_quality(
        self, system_prompt, user_prompt, task_name, model, quality_checker
    ):
        """
        执行单个任务的分析（带质量检查）

        这是一个内部方法，被 parallel_analyze_with_quality_check 调用
        质量检查是强制执行的，确保所有分析结果都符合质量标准

        参数:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            task_name: 任务名称
            model: 模型名称（使用配置文件的默认值）
            quality_checker: 质量检查器实例（必传）

        返回:
            包含content和quality_info的字典
        """
        # 使用配置文件的默认模型（如果传入的model为None）
        if model is None:
            model = DEFAULT_MODEL

        # 执行初始分析
        content = self.call_ai(system_prompt, user_prompt, model=model)

        # 执行质量检查和自动补充（核心功能，强制执行）
        supplement_result = quality_checker.check_and_supplement(
            analyzer=self, content=content, task_name=task_name, model=model
        )

        return {
            "content": supplement_result["final_content"],
            "quality_info": supplement_result["check_result"],
            "supplement_rounds": supplement_result["supplement_rounds"],
            "history": supplement_result.get("history", []),
        }

    def _save_individual_report(
        self,
        task_name: str,
        content: str,
        output_dir: str,
        base_filename: str,
        quality_info: dict,
    ) -> str:
        """
        保存单个任务的分析报告到本地Markdown文件

        这是强制执行的功能，每个任务通过质量检查后都会保存独立报告。
        文件命名规则：{base_filename}_{task_name}.md

        参数:
            task_name: 任务名称（statistics, personality等）
            content: 分析内容
            output_dir: 输出目录路径
            base_filename: 基础文件名（不含扩展名）
            quality_info: 质量检查信息

        返回:
            保存的文件路径
        """
        import os

        # 任务名称中文映射
        task_name_map = {
            "statistics": "统计分析",
            "personality": "性格特点分析",
            "interest": "兴趣爱好分析",
            "trajectory": "活动轨迹分析",
            "social": "社交圈子分析",
            "emotion": "情感表达分析",
            "social_engineering": "社会工程学攻击方案",
        }

        # 处理output_dir为空的情况
        if not output_dir:
            output_dir = "."

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 生成文件名
        report_filename = f"{base_filename}_{task_name}.md"
        report_path = os.path.join(output_dir, report_filename)

        # 转换为绝对路径便于显示
        abs_report_path = os.path.abspath(report_path)

        # 生成报告内容
        score = quality_info.get("score", 0)
        passed_checks = quality_info.get("passed_checks", [])
        failed_checks = quality_info.get("failed_checks", [])
        supplement_rounds = quality_info.get("supplement_rounds", 0)

        report_content = f"""# {task_name_map.get(task_name, task_name)}报告

## 质量检查信息

- **质量评分**: {score:.0f}/100
- **补充轮数**: {supplement_rounds}
- **通过检查**: {", ".join(passed_checks) if passed_checks else "无"}
- **未通过检查**: {", ".join(failed_checks) if failed_checks else "无"}

## 分析结果

{content}

---
*报告生成时间: {self._get_current_time()}*
*分析模型: {DEFAULT_MODEL}*
"""

        # 保存文件
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            return abs_report_path
        except Exception as e:
            print(f"  [{task_name}] 保存报告失败: {e}")
            print(f"  [{task_name}] 尝试保存路径: {abs_report_path}")
            return ""

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def generate_social_engineering_plan(
    analyzer, report_content, csv_content, prompts_module, model=None
):
    """
    生成社会工程学攻击方案

    在综合报告生成后，基于报告和原始CSV数据生成攻击方案。

    参数:
        analyzer: AIAnalyzer实例
        report_content: 综合分析报告内容
        csv_content: 原始CSV数据（用于提取敏感信息）
        prompts_module: 提示词模块对象
        model: 模型名称，默认使用配置文件的DEFAULT_MODEL

    返回:
        社会工程学攻击方案内容字符串
    """
    if model is None:
        model = DEFAULT_MODEL

    user_prompt = prompts_module.SOCIAL_ENGINEERING_USER_PROMPT.format(
        report_content=report_content, csv_content=csv_content[:10000]
    )

    result = analyzer.call_ai(
        prompts_module.SOCIAL_ENGINEERING_SYSTEM_PROMPT, user_prompt, model=model
    )

    return result


def generate_detailed_se_plan(
    analyzer, se_plan_content, target_profile, prompts_module, model=None
):
    """
    生成详细的社工攻击方案（5个Agent并行）

    参数:
        analyzer: AIAnalyzer实例
        se_plan_content: 社工攻击方案内容
        target_profile: 目标画像信息（综合报告摘要）
        prompts_module: 提示词模块对象
        model: 模型名称

    返回:
        包含5个详细方案的字典
    """
    if model is None:
        model = DEFAULT_MODEL

    tasks = [
        (
            prompts_module.IDENTITY_DISGUISE_SYSTEM_PROMPT,
            prompts_module.IDENTITY_DISGUISE_USER_PROMPT.format(
                se_plan=se_plan_content, target_profile=target_profile
            ),
            "identity_disguise",
        ),
        (
            prompts_module.SOCIAL_MEDIA_CHANNEL_SYSTEM_PROMPT,
            prompts_module.SOCIAL_MEDIA_CHANNEL_USER_PROMPT.format(
                se_plan=se_plan_content, target_profile=target_profile
            ),
            "social_media_channel",
        ),
        (
            prompts_module.SCRIPT_PREPARATION_SYSTEM_PROMPT,
            prompts_module.SCRIPT_PREPARATION_USER_PROMPT.format(
                se_plan=se_plan_content, target_profile=target_profile
            ),
            "script_preparation",
        ),
        (
            prompts_module.SCENARIO_CONSTRUCTION_SYSTEM_PROMPT,
            prompts_module.SCENARIO_CONSTRUCTION_USER_PROMPT.format(
                se_plan=se_plan_content, target_profile=target_profile
            ),
            "scenario_construction",
        ),
        (
            prompts_module.EMOTION_GUIDANCE_SYSTEM_PROMPT,
            prompts_module.EMOTION_GUIDANCE_USER_PROMPT.format(
                se_plan=se_plan_content, target_profile=target_profile
            ),
            "emotion_guidance",
        ),
    ]

    results = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {}
        for system_prompt, user_prompt, task_name in tasks:
            future = executor.submit(
                analyzer.call_ai, system_prompt, user_prompt, model=model
            )
            future_to_task[future] = task_name

        for future in as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                results[task_name] = future.result()
                print(f"  [{task_name}] 详细方案生成完成")
            except Exception as e:
                print(f"  [{task_name}] 生成失败: {e}")
                results[task_name] = f"生成失败: {e}"

    return results


def save_detailed_se_reports(detailed_results, output_dir, base_filename):
    """
    保存5个详细社工方案报告

    参数:
        detailed_results: 详细方案字典
        output_dir: 输出目录
        base_filename: 基础文件名

    返回:
        保存的文件路径列表
    """
    import os

    if not output_dir:
        output_dir = "."

    os.makedirs(output_dir, exist_ok=True)

    task_name_map = {
        "identity_disguise": "身份伪装",
        "social_media_channel": "社交媒体渠道管理",
        "script_preparation": "话术准备",
        "scenario_construction": "场景构造",
        "emotion_guidance": "情绪引导",
    }

    saved_files = []

    for task_name, content in detailed_results.items():
        report_filename = f"{base_filename}_detailed_{task_name}.md"
        report_path = os.path.join(output_dir, report_filename)

        report_content = f"""# 详细社工攻击方案 - {task_name_map.get(task_name, task_name)}

## 伦理声明

⚠️ **本报告仅供安全研究和防御演练使用**

- 请勿将本方案用于未经授权的渗透测试
- 旨在帮助目标人物加强安全意识，而非助长攻击行为
- 生成的攻击方案应妥善保管，**不要分享给第三方**

---

## 方案内容

{content}

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*分析模型: {DEFAULT_MODEL}*
"""

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_content)
            saved_files.append(os.path.abspath(report_path))
            print(f"  [{task_name}] 报告已保存至: {report_path}")
        except Exception as e:
            print(f"  [{task_name}] 保存失败: {e}")

    return saved_files


def save_social_engineering_report(content, output_dir, base_filename):
    """
    保存社会工程学攻击方案报告

    参数:
        content: 攻击方案内容
        output_dir: 输出目录
        base_filename: 基础文件名

    返回:
        保存的文件路径
    """
    import os

    if not output_dir:
        output_dir = "."

    os.makedirs(output_dir, exist_ok=True)

    report_filename = f"{base_filename}_social_engineering.md"
    report_path = os.path.join(output_dir, report_filename)

    abs_report_path = os.path.abspath(report_path)

    report_content = f"""# 社会工程学攻击方案

## 伦理声明

⚠️ **本报告仅供安全研究和防御演练使用**

- 请勿将本方案用于未经授权的渗透测试
- 旨在帮助目标人物加强安全意识，而非助长攻击行为
- 生成的攻击方案应妥善保管，**不要分享给第三方**

---

## 攻击方案内容

{content}

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*分析模型: {DEFAULT_MODEL}*
"""

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        return abs_report_path
    except Exception as e:
        print(f"保存社工攻击方案失败: {e}")
        return ""
