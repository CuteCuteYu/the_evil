#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
the-evil 主程序

微博数据爬取和分析工具，支持：
1. 爬取微博用户数据
2. AI智能分析（7个并行任务）
3. 生成Markdown分析报告

使用方法:
    python -m the_evil.the_evil <cookie> <uid> [output_file] [max_weibos]

示例:
    python -m the_evil.the_evil "cookie" 1223178222
    python -m the_evil.the_evil "cookie" 1223178222 output.csv 100

作者: CuteCuteYu
版本: 1.0.0
"""

import os
import sys
import importlib.util


# 动态导入模块，避免包导入问题
def import_module_from_path(module_name, file_path):
    """从文件路径动态导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# 获取当前文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 导入crawlers模块
crawlers = import_module_from_path(
    "crawlers", os.path.join(current_dir, "modules", "crawlers.py")
)
WeiboCrawler = crawlers.WeiboCrawler

# 导入ai_analyzer模块
ai_analyzer = import_module_from_path(
    "ai_analyzer", os.path.join(current_dir, "modules", "ai_analyzer.py")
)
AIAnalyzer = ai_analyzer.AIAnalyzer
create_analysis_tasks = ai_analyzer.create_analysis_tasks
format_report_prompt = ai_analyzer.format_report_prompt

# 导入prompts模块
prompts = import_module_from_path(
    "prompts", os.path.join(current_dir, "modules", "prompts.py")
)
prompts_module = prompts


def main():
    """
    主函数

    命令行参数:
        sys.argv[1]: cookie - 微博登录cookie（必填）
        sys.argv[2]: uid - 微博用户ID（必填）
        sys.argv[3]: output_file - 输出文件路径（必填）
        sys.argv[4]: max_weibos - 最大获取微博数（必填，0表示全部）
        sys.argv[5]: model - AI模型名称（必填）
        sys.argv[6]: api_key - API密钥（必填）
        sys.argv[7]: base_url - API地址（必填）
    """

    # 参数解析
    if len(sys.argv) < 8:
        print(
            "用法: python the_evil.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>"
        )
        print(
            '示例: python the_evil.py "cookie" 1223178222 output.csv 0 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"'
        )
        sys.exit(1)

    cookie = sys.argv[1]
    user_id = sys.argv[2]
    output_file = sys.argv[3]
    max_weibos = int(sys.argv[4])
    model = sys.argv[5]
    api_key = sys.argv[6]
    base_url = sys.argv[7]

    # 验证用户ID
    if not user_id.isdigit():
        print("错误: 请输入数字UID")
        sys.exit(1)

    print(f"正在获取用户 {user_id} 的微博...")

    # 爬取数据
    crawler = WeiboCrawler(cookie)
    user_info = crawler.get_user_info(user_id)
    print(f"用户: {user_info.nickname}")
    print(f"粉丝: {user_info.followers}, 微博: {user_info.weibo_num}")

    # 检查文件是否存在
    if os.path.exists(output_file):
        print(f"文件 {output_file} 已存在，跳过爬取，直接进行分析...")
    else:
        weibos = crawler.get_weibos(user_id, max_count=max_weibos)
        crawler.save_to_csv(user_info, weibos, output_file)
        print("完成!")

    # AI分析
    analyze_with_ai(output_file, model, api_key, base_url)


def analyze_with_ai(csv_file, model, api_key, base_url):
    """
    使用AI分析CSV文件

    参数:
        csv_file: CSV文件路径
        model: AI模型名称
        api_key: API密钥
        base_url: API地址
    """
    if not api_key:
        print("警告: 未设置API密钥，跳过AI分析")
        return

    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量，跳过AI分析")
        return

    # 读取CSV内容
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        csv_content = f.read()

    # 创建AI分析器
    try:
        analyzer = AIAnalyzer(api_key=api_key, base_url=base_url)
    except ValueError as e:
        print(f"AI分析器初始化失败: {e}")
        return

    # 创建分析任务
    tasks = create_analysis_tasks(csv_content, prompts_module)

    print(f"正在调用AI进行分析（7个任务并行，使用模型: {model}）...")

    # 并行执行分析任务
    results = analyzer.parallel_analyze(tasks, max_workers=7, model=model)

    # 生成综合报告
    print("正在生成综合报告...")

    report_prompt = format_report_prompt(prompts_module, results)
    final_report = analyzer.call_ai(
        prompts_module.REPORT_SYSTEM_PROMPT, report_prompt, model=model
    )

    # 保存报告
    csv_filename = os.path.basename(csv_file)
    base_name = csv_filename.replace(".csv", "")
    md_file = os.path.join(os.path.dirname(csv_file), f"{base_name}_report.md")

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(final_report)

    # 输出结果
    print("\n=== AI分析结果 ===")
    print(final_report)
    print("=== 分析完成 ===")
    print(f"报告已保存至: {md_file}")


# 程序入口
if __name__ == "__main__":
    main()
