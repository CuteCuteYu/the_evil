#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
the-evil模块

微博数据爬取和分析工具包

子模块:
    - crawlers: 网站爬虫实现
    - prompts: AI分析提示词
    - ai_analyzer: AI分析器
    - quality_checker: AI结果质量检查器（核心功能，强制启用）
    - quality_check_prompts: 质量检查提示词（为每个分析任务定制的检查提示词）
    - config: 统一配置模块

使用示例:
    from the_evil.modules.crawlers import WeiboCrawler
    from the_evil.modules.ai_analyzer import AIAnalyzer
    from the_evil.modules.config import DEFAULT_MODEL, MAX_WORKERS

    # 爬取数据
    crawler = WeiboCrawler(cookie="your_cookie")
    weibos = crawler.get_weibos("123456789")

    # AI分析（质量检查自动启用，使用配置文件的默认模型和专门的质量检查提示词）
    analyzer = AIAnalyzer()
    result = analyzer.parallel_analyze_with_quality_check(tasks)

作者: CuteCuteYu
版本: 2.0.0
"""

from .crawlers import WeiboCrawler, UserInfo, WeiboData, create_crawler
from .ai_analyzer import AIAnalyzer
from .prompts import PROMPTS_CONFIG, get_prompt, format_prompt

# 导入统一配置模块
from .config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_BASE_URL,
    MAX_WORKERS,
    API_KEY_ENV_VAR,
    QualityCheckConfig,
    CrawlerConfig,
    ANALYSIS_TASKS
)

# 导入质量检查模块（核心功能）
try:
    from .quality_checker import (
        QualityChecker,
        CheckStatus,
        CheckIssue,
        CheckResult,
        create_quality_checker
    )
    _quality_check_available = True
except ImportError:
    _quality_check_available = False
    import warnings
    warnings.warn(
        "质量检查模块未找到，这是核心功能！"
        "请确保 quality_checker.py 文件存在于 modules 目录中。",
        ImportWarning
    )

# 导入质量检查提示词模块
try:
    from .quality_check_prompts import (
        QUALITY_CHECK_PROMPTS,
        get_quality_check_prompt,
        format_quality_check_prompt
    )
    _quality_check_prompts_available = True
except ImportError:
    _quality_check_prompts_available = False

__all__ = [
    "WeiboCrawler",
    "UserInfo",
    "WeiboData",
    "create_crawler",
    "AIAnalyzer",
    "PROMPTS_CONFIG",
    "get_prompt",
    "format_prompt",
    # 配置相关
    "DEFAULT_MODEL",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_BASE_URL",
    "MAX_WORKERS",
    "API_KEY_ENV_VAR",
    "QualityCheckConfig",
    "CrawlerConfig",
    "ANALYSIS_TASKS",
]

# 如果质量检查模块可用，添加到导出列表
if _quality_check_available:
    __all__.extend([
        "QualityChecker",
        "CheckStatus",
        "CheckIssue",
        "CheckResult",
        "create_quality_checker",
    ])

# 如果质量检查提示词模块可用，添加到导出列表
if _quality_check_prompts_available:
    __all__.extend([
        "QUALITY_CHECK_PROMPTS",
        "get_quality_check_prompt",
        "format_quality_check_prompt",
    ])
