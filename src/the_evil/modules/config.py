#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
统一配置模块

该模块集中管理所有模型和AI相关的配置参数。
用户只需修改此文件即可更新所有默认配置。

配置项:
    - DEFAULT_MODEL: 默认AI模型名称
    - DEFAULT_TEMPERATURE: 默认温度参数
    - DEFAULT_BASE_URL: 默认API地址
    - MAX_WORKERS: 并行任务的最大并发数
    - QUALITY_CHECK_CONFIG: 质量检查配置

使用方式:
    from modules.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE

    # 使用配置
    result = analyzer.call_ai(system_prompt, user_prompt, model=DEFAULT_MODEL)

作者: CuteCuteYu
版本: 1.0.0
"""

# =============================================================================
# AI模型配置
# =============================================================================

# 默认AI模型名称
# 可选值: glm-4.7, glm-4, glm-4-flash, gpt-4, gpt-4o, claude-3 等
DEFAULT_MODEL = "glm-4.7"

# 默认温度参数（控制输出随机性）
# 范围: 0.0（确定性）~ 1.0（创造性），推荐值: 0.7
DEFAULT_TEMPERATURE = 0.7

# 默认API基础URL
# 智谱AI: https://open.bigmodel.cn/api/coding/paas/v4
# OpenAI: https://api.openai.com/v1
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/coding/paas/v4"

# API密钥环境变量名称
API_KEY_ENV_VAR = "OPENAI_API_KEY"


# =============================================================================
# 并发配置
# =============================================================================

# 并行任务的最大并发数
# 建议值: 7（对应7个分析任务），可根据API限制调整
MAX_WORKERS = 7


# =============================================================================
# 质量检查配置
# =============================================================================

class QualityCheckConfig:
    """
    质量检查配置类

    包含所有质量检查相关的配置参数
    """

    # 最小内容长度（字符数）
    # 分析结果必须达到的最小长度，低于此值会触发补充
    MIN_LENGTH = 100

    # 是否要求包含分析依据
    # True: 强制要求AI在结论后说明"分析依据"
    # False: 不强制要求
    REQUIRE_EVIDENCE = True

    # 最大补充轮数
    # 质量检查不通过时，最多请求AI补充的次数
    MAX_SUPPLEMENT_ROUNDS = 3


# =============================================================================
# 数据爬取配置
# =============================================================================

class CrawlerConfig:
    """
    爬虫配置类

    包含所有数据爬取相关的配置参数
    """

    # 默认获取微博数量
    # 0表示获取全部，建议设置为100进行测试
    DEFAULT_MAX_WEIBOS = 100

    # 请求间隔（秒）
    # 避免请求过快被封禁
    REQUEST_INTERVAL = 1


# =============================================================================
# 分析任务配置
# =============================================================================

# 分析任务列表
# 每个任务对应一个分析维度
ANALYSIS_TASKS = [
    "statistics",      # 统计分析
    "personality",     # 性格分析
    "interest",        # 兴趣分析
    "trajectory",      # 轨迹分析
    "social",          # 社交分析
    "emotion",         # 情感分析
]


# =============================================================================
# 配置验证
# =============================================================================

def validate_config():
    """
    验证配置的有效性

    如果配置无效，会抛出 ValueError 异常

    异常:
        ValueError: 当配置参数不符合要求时
    """
    if not DEFAULT_MODEL or not isinstance(DEFAULT_MODEL, str):
        raise ValueError("DEFAULT_MODEL 必须是非空字符串")

    if not 0.0 <= DEFAULT_TEMPERATURE <= 2.0:
        raise ValueError("DEFAULT_TEMPERATURE 必须在 0.0 到 2.0 之间")

    if QualityCheckConfig.MIN_LENGTH < 0:
        raise ValueError("MIN_LENGTH 必须大于等于 0")

    if QualityCheckConfig.MAX_SUPPLEMENT_ROUNDS < 1:
        raise ValueError("MAX_SUPPLEMENT_ROUNDS 必须大于等于 1")

    if MAX_WORKERS < 1:
        raise ValueError("MAX_WORKERS 必须大于等于 1")


# 自动验证配置（模块导入时执行）
validate_config()
