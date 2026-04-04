#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
AI分析结果质量检查模块

该模块负责对AI生成的分析结果进行质量检查和补充完善。
核心功能：
1. 多维度质量检查（长度、完整性、结构、内容）
2. 自动生成补充请求提示词（使用任务特定的质量检查提示词）
3. 结果合并与整合
4. 可配置的检查标准和阈值

使用方式：
    from modules.quality_checker import QualityChecker

    checker = QualityChecker()
    result = checker.check_and_supplement(
        analyzer=ai_analyzer,
        content=ai_result,
        task_name="personality"
    )

作者: CuteCuteYu
版本: 2.0.0
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable
from enum import Enum

# 导入统一配置
try:
    from the_evil.modules.config import (
        DEFAULT_MODEL,
        QualityCheckConfig
    )
except ImportError:
    from .config import (
        DEFAULT_MODEL,
        QualityCheckConfig
    )

# 导入质量检查提示词模块
QUALITY_PROMPTS_AVAILABLE = False
QUALITY_CHECK_PROMPTS = None
get_quality_check_prompt = None
format_quality_check_prompt = None

try:
    from the_evil.modules.quality_check_prompts import (
        QUALITY_CHECK_PROMPTS,
        get_quality_check_prompt,
        format_quality_check_prompt
    )
    QUALITY_PROMPTS_AVAILABLE = True
except ImportError:
    try:
        from .quality_check_prompts import (
            QUALITY_CHECK_PROMPTS,
            get_quality_check_prompt,
            format_quality_check_prompt
        )
        QUALITY_PROMPTS_AVAILABLE = True
    except ImportError:
        pass


class CheckStatus(Enum):
    """检查状态枚举"""
    PASSED = "passed"           # 检查通过
    FAILED = "failed"           # 检查失败
    NEED_SUPPLEMENT = "need_supplement"  # 需要补充


@dataclass
class CheckIssue:
    """
    检查问题项

    属性:
        check_name: 检查项名称
        description: 问题描述
        severity: 严重程度 (low/medium/high)
        suggestion: 改进建议
    """
    check_name: str
    description: str
    severity: str = "medium"
    suggestion: str = ""

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "check_name": self.check_name,
            "description": self.description,
            "severity": self.severity,
            "suggestion": self.suggestion
        }


@dataclass
class CheckResult:
    """
    检查结果

    属性:
        status: 检查状态
        score: 质量评分 (0-100)
        issues: 问题列表
        passed_checks: 通过的检查项列表
        failed_checks: 未通过的检查项列表
    """
    status: CheckStatus
    score: float
    issues: List[CheckIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)

    @property
    def is_passed(self) -> bool:
        """是否通过检查"""
        return self.status == CheckStatus.PASSED

    def add_issue(self, issue: CheckIssue):
        """添加问题"""
        self.issues.append(issue)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "status": self.status.value,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks
        }


class QualityChecker:
    """
    AI分析结果质量检查器

    支持的质量检查维度：
    1. 长度检查 - 检查内容长度是否符合最低要求
    2. 完整性检查 - 检查是否包含必需的关键要素
    3. 结构检查 - 检查是否符合预期的格式结构
    4. 内容检查 - 检查是否包含具体的数据引用和证据

    可通过继承此类来扩展自定义检查逻辑
    """

    # 各类任务的必需关键词配置
    REQUIRED_KEYWORDS = {
        "statistics": ["统计", "数据", "分析"],
        "personality": ["性格", "分析依据", "行为"],
        "interest": ["兴趣", "爱好", "分析依据"],
        "trajectory": ["轨迹", "时间", "分析依据"],
        "social": ["社交", "互动", "分析依据"],
        "emotion": ["情感", "表达", "分析依据"],
        "report": ["报告", "分析", "建议"]
    }

    # 分析依据关键词
    EVIDENCE_KEYWORDS = ["分析依据", "基于", "根据", "数据显示", "从微博"]

    def __init__(
        self,
        min_length: int = None,
        require_evidence: bool = None,
        max_supplement_rounds: int = None
    ):
        """
        初始化质量检查器

        参数:
            min_length: 最小内容长度（字符数），默认使用配置文件中的QualityCheckConfig.MIN_LENGTH
            require_evidence: 是否要求包含分析依据，默认使用配置文件中的QualityCheckConfig.REQUIRE_EVIDENCE
            max_supplement_rounds: 最大补充轮数，默认使用配置文件中的QualityCheckConfig.MAX_SUPPLEMENT_ROUNDS
        """
        # 使用配置文件的默认值
        self.min_length = min_length if min_length is not None else QualityCheckConfig.MIN_LENGTH
        self.require_evidence = require_evidence if require_evidence is not None else QualityCheckConfig.REQUIRE_EVIDENCE
        self.max_supplement_rounds = max_supplement_rounds if max_supplement_rounds is not None else QualityCheckConfig.MAX_SUPPLEMENT_ROUNDS

        # 注册所有检查函数
        self._check_functions: List[Callable[[str, str], CheckIssue]] = [
            self._check_length,
            self._check_completeness,
            self._check_structure,
            self._check_content
        ]

    def check_all(self, content: str, task_name: str) -> CheckResult:
        """
        执行所有质量检查

        参数:
            content: 待检查的AI分析结果
            task_name: 任务名称（用于获取特定配置）

        返回:
            CheckResult 检查结果对象
        """
        issues = []
        passed_checks = []
        failed_checks = []

        # 执行所有检查
        for check_func in self._check_functions:
            try:
                issue = check_func(content, task_name)
                if issue:
                    issues.append(issue)
                    failed_checks.append(issue.check_name)
                else:
                    passed_checks.append(check_func.__name__)
            except Exception as e:
                # 检查函数出错，记录问题但不中断
                issues.append(CheckIssue(
                    check_name=check_func.__name__,
                    description=f"检查执行出错: {str(e)}",
                    severity="low"
                ))
                failed_checks.append(check_func.__name__)

        # 计算质量评分
        total_checks = len(self._check_functions)
        passed_ratio = len(passed_checks) / total_checks if total_checks > 0 else 0
        score = passed_ratio * 100

        # 确定检查状态
        if len(issues) == 0:
            status = CheckStatus.PASSED
        elif any(issue.severity == "high" for issue in issues):
            status = CheckStatus.NEED_SUPPLEMENT
        else:
            # 中低严重度问题，根据数量决定
            status = CheckStatus.NEED_SUPPLEMENT if len(issues) >= 2 else CheckStatus.FAILED

        return CheckResult(
            status=status,
            score=score,
            issues=issues,
            passed_checks=passed_checks,
            failed_checks=failed_checks
        )

    def _check_length(self, content: str, task_name: str) -> Optional[CheckIssue]:
        """
        检查1: 长度检查

        检查内容长度是否达到最低要求
        过短的内容通常意味着分析不够深入

        参数:
            content: 待检查内容
            task_name: 任务名称

        返回:
            CheckIssue 如果检查失败，否则返回None
        """
        content_length = len(content.strip())

        if content_length < self.min_length:
            return CheckIssue(
                check_name="长度检查",
                description=f"内容长度({content_length}字符)低于最低要求({self.min_length}字符)",
                severity="high",
                suggestion=f"请补充更多分析内容，建议至少{self.min_length}字符"
            )

        return None

    def _check_completeness(self, content: str, task_name: str) -> Optional[CheckIssue]:
        """
        检查2: 完整性检查

        检查是否包含必需的关键要素
        重点检查是否包含"分析依据"部分

        参数:
            content: 待检查内容
            task_name: 任务名称

        返回:
            CheckIssue 如果检查失败，否则返回None
        """
        if not self.require_evidence:
            return None

        # 检查是否包含分析依据相关关键词
        has_evidence = any(keyword in content for keyword in self.EVIDENCE_KEYWORDS)

        if not has_evidence:
            return CheckIssue(
                check_name="完整性检查",
                description="缺少分析依据部分，未找到数据来源说明",
                severity="high",
                suggestion="请在每个分析结论后添加'分析依据'部分，说明基于哪些数据得出该结论"
            )

        # 检查是否包含任务相关的必需关键词
        required_keywords = self.REQUIRED_KEYWORDS.get(task_name, [])
        if required_keywords:
            missing_keywords = [
                kw for kw in required_keywords if kw not in content
            ]
            if missing_keywords:
                return CheckIssue(
                    check_name="完整性检查",
                    description=f"缺少关键要素: {', '.join(missing_keywords)}",
                    severity="medium",
                    suggestion=f"请确保分析包含: {', '.join(required_keywords)}"
                )

        return None

    def _check_structure(self, content: str, task_name: str) -> Optional[CheckIssue]:
        """
        检查3: 结构检查

        检查内容结构是否合理
        例如：是否有编号、分段等结构性标记

        参数:
            content: 待检查内容
            task_name: 任务名称

        返回:
            CheckIssue 如果检查失败，否则返回None
        """
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        if len(lines) < 3:
            return CheckIssue(
                check_name="结构检查",
                description="内容结构过于简单，缺乏层次",
                severity="medium",
                suggestion="建议使用编号、分段等方式组织内容"
            )

        # 检查是否有结构性标记（编号、标题等）
        has_structure = any(
            line[0].isdigit() or line.startswith('#') or line.startswith('##')
            for line in lines if line
        )

        if not has_structure:
            return CheckIssue(
                check_name="结构检查",
                description="缺少结构性标记（编号、标题等）",
                severity="low",
                suggestion="建议使用数字编号或标题来组织各个分析要点"
            )

        return None

    def _check_content(self, content: str, task_name: str) -> Optional[CheckIssue]:
        """
        检查4: 内容检查

        检查是否包含具体的数据引用和证据
        避免空泛的结论

        参数:
            content: 待检查内容
            task_name: 任务名称

        返回:
            CheckIssue 如果检查失败，否则返回None
        """
        # 检查是否包含具体数据引用（如数字、引号等）
        has_data_reference = (
            '微博' in content or
            any(char.isdigit() for char in content) or
            '"' in content or '"' in content or
            '：' in content
        )

        if not has_data_reference:
            return CheckIssue(
                check_name="内容检查",
                description="缺少具体数据引用或证据支撑",
                severity="high",
                suggestion="请在分析中引用具体的微博内容、数据或统计结果"
            )

        # 检查是否有过短的分段（可能是敷衍的回答）
        lines = content.split('\n')
        short_lines = [line for line in lines if 3 < len(line.strip()) < 20]

        if len(short_lines) > len(lines) * 0.5:
            return CheckIssue(
                check_name="内容检查",
                description="内容过于碎片化，存在大量短句",
                severity="medium",
                suggestion="请提供更详细完整的分析内容"
            )

        return None

    def generate_supplement_prompt(
        self,
        original_content: str,
        check_result: CheckResult,
        task_name: str
    ) -> str:
        """
        生成补充请求提示词

        根据检查结果和任务类型生成针对性的补充请求。
        如果存在专门的质量检查提示词，将优先使用；否则使用通用提示词。

        参数:
            original_content: 原始AI分析结果
            check_result: 质量检查结果
            task_name: 任务名称（用于获取专门的质量检查提示词）

        返回:
            补充请求提示词字符串
        """
        # 优先使用专门的质量检查提示词
        if QUALITY_PROMPTS_AVAILABLE and task_name in QUALITY_CHECK_PROMPTS:
            # 使用任务特定的质量检查提示词
            prompts = get_quality_check_prompt(task_name)
            user_template = prompts.get("user", "")

            # 格式化提示词，填充原始内容
            if "{original_content}" in user_template:
                return user_template.format(original_content=original_content)

        # 如果没有专门的提示词，使用通用提示词
        # 基础提示词
        base_prompt = f"""【补充请求】你之前的分析结果存在以下问题，需要进行补充：

原始分析结果：
{original_content}

【需要改进的问题】
"""

        # 添加具体问题
        for i, issue in enumerate(check_result.issues, 1):
            base_prompt += f"\n{i}. {issue.check_name}: {issue.description}"
            if issue.suggestion:
                base_prompt += f"\n   建议: {issue.suggestion}"

        # 补充要求
        base_prompt += f"""

【补充要求】
1. 请基于上述问题，对原始分析进行补充和完善
2. 保留原始分析中正确的部分
3. 重点补充缺失的"分析依据"部分
4. 确保每个结论都有具体的数据或内容支撑
5. 请直接输出补充完善后的完整分析结果，不需要说明修改了哪些地方
6. 补充后的内容应当详细、具体、有深度

请输出完整的、补充完善后的分析结果：
"""

        return base_prompt

    def merge_content(
        self,
        original_content: str,
        supplement_content: str
    ) -> str:
        """
        合并原始内容和补充内容

        参数:
            original_content: 原始分析内容
            supplement_content: 补充内容

        返回:
            合并后的内容
        """
        # 如果补充内容看起来像是完整版本，直接使用
        if len(supplement_content) > len(original_content) * 0.8:
            return supplement_content

        # 否则拼接
        return f"{original_content}\n\n【补充内容】\n{supplement_content}"

    def check_and_supplement(
        self,
        analyzer: object,
        content: str,
        task_name: str,
        model: str = None,
        system_prompt: str = None
    ) -> Dict[str, any]:
        """
        执行质量检查并自动请求补充

        这是质量检查器的主要对外接口，
        会循环执行检查和补充，直到结果通过或达到最大轮数

        参数:
            analyzer: AI分析器实例（需要有call_ai方法）
            content: 待检查的AI分析结果
            task_name: 任务名称（用于获取专门的质量检查提示词）
            model: AI模型名称，默认使用配置文件中的DEFAULT_MODEL
            system_prompt: 补充请求的系统提示词，如不指定则使用专门的质量检查提示词

        返回:
            包含以下键的字典:
            - 'final_content': 最终内容
            - 'check_result': 最后的检查结果
            - 'supplement_rounds': 补充轮数
            - 'history': 历史记录列表
        """
        # 使用配置文件的默认模型
        if model is None:
            model = DEFAULT_MODEL

        # 获取专门的质量检查提示词（如果可用）
        if system_prompt is None and QUALITY_PROMPTS_AVAILABLE and task_name in QUALITY_CHECK_PROMPTS:
            prompts = get_quality_check_prompt(task_name)
            system_prompt = prompts.get("system", "你是一个专业的分析助手，擅长补充和完善分析内容。")
        elif system_prompt is None:
            system_prompt = "你是一个专业的分析助手，擅长补充和完善分析内容。"

        current_content = content
        history = []
        supplement_rounds = 0

        while supplement_rounds < self.max_supplement_rounds:
            # 执行质量检查
            check_result = self.check_all(current_content, task_name)

            # 记录历史
            history.append({
                "round": supplement_rounds,
                "score": check_result.score,
                "status": check_result.status.value,
                "issues": [issue.to_dict() for issue in check_result.issues]
            })

            # 如果检查通过，返回结果
            if check_result.is_passed:
                return {
                    "final_content": current_content,
                    "check_result": check_result.to_dict(),
                    "supplement_rounds": supplement_rounds,
                    "history": history
                }

            # 如果是最后一轮，不再请求补充
            if supplement_rounds >= self.max_supplement_rounds - 1:
                break

            # 生成补充请求
            supplement_prompt = self.generate_supplement_prompt(
                current_content,
                check_result,
                task_name
            )

            try:
                # 调用AI进行补充
                supplement_content = analyzer.call_ai(
                    system_prompt=system_prompt,
                    user_prompt=supplement_prompt,
                    model=model
                )

                # 合并内容
                current_content = self.merge_content(current_content, supplement_content)
                supplement_rounds += 1

            except Exception as e:
                # 补充请求失败，终止循环
                history.append({
                    "error": f"补充请求失败: {str(e)}"
                })
                break

        # 达到最大轮数仍未通过，返回当前结果
        return {
            "final_content": current_content,
            "check_result": check_result.to_dict(),
            "supplement_rounds": supplement_rounds,
            "history": history,
            "warning": "已达到最大补充轮数，结果可能未完全满足要求"
        }


def create_quality_checker(
    min_length: int = None,
    require_evidence: bool = None,
    max_supplement_rounds: int = None
) -> QualityChecker:
    """
    创建质量检查器实例的工厂函数

    参数:
        min_length: 最小内容长度（字符数），默认使用配置文件中的值
        require_evidence: 是否要求包含分析依据，默认使用配置文件中的值
        max_supplement_rounds: 最大补充轮数，默认使用配置文件中的值

    返回:
        QualityChecker 实例
    """
    return QualityChecker(
        min_length=min_length,
        require_evidence=require_evidence,
        max_supplement_rounds=max_supplement_rounds
    )
