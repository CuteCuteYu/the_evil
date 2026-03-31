#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
the-evil模块

微博数据爬取和分析工具包

子模块:
    - crawlers: 网站爬虫实现
    - prompts: AI分析提示词
    - ai_analyzer: AI分析器

使用示例:
    from the_evil.modules.crawlers import WeiboCrawler
    from the_evil.modules.ai_analyzer import AIAnalyzer

    # 爬取数据
    crawler = WeiboCrawler(cookie="your_cookie")
    weibos = crawler.get_weibos("123456789")

    # AI分析
    analyzer = AIAnalyzer()
    result = analyzer.analyze_csv("data.csv")

作者: CuteCuteYu
版本: 1.0.0
"""

from .crawlers import WeiboCrawler, UserInfo, WeiboData, create_crawler
from .ai_analyzer import AIAnalyzer
from .prompts import PROMPTS_CONFIG, get_prompt, format_prompt

__all__ = [
    "WeiboCrawler",
    "UserInfo",
    "WeiboData",
    "create_crawler",
    "AIAnalyzer",
    "PROMPTS_CONFIG",
    "get_prompt",
    "format_prompt",
]
