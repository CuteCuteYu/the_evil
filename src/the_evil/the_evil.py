#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
the-evil 主程序

微博数据爬取和分析工具，支持：
1. 爬取微博用户数据
2. AI智能分析（7个并行任务）
3. 质量检查与自动补充（强制启用）
4. 生成Markdown分析报告

使用方法:
    python -m the_evil.the_evil <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

示例:
    python -m the_evil.the_evil "cookie" 1223178222 output.csv 100 glm-4.7 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"

注意：所有模型相关配置可在 modules/config.py 中统一修改

作者: CuteCuteYu
版本: 2.0.0
"""

import os
import sys
import importlib.util

# 将src目录添加到sys.path，使绝对导入可以工作
# 这样 from the_evil.modules.xxx import ... 就能正常工作
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


# 动态导入模块，避免包导入问题
def import_module_from_path(module_name, file_path):
    """从文件路径动态导入模块"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


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
generate_social_engineering_plan = ai_analyzer.generate_social_engineering_plan
save_social_engineering_report = ai_analyzer.save_social_engineering_report

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

    注意：质量检查功能强制启用，确保AI分析结果的完整性和可靠性
    """

    # 参数解析
    if len(sys.argv) < 8:
        print(
            "用法: python the_evil.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>"
        )
        print(
            '示例: python the_evil.py "cookie" 1223178222 output.csv 100 glm-4.7 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"'
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

    # AI分析（质量检查强制启用）
    analyze_with_ai(output_file, model, api_key, base_url)


def analyze_with_ai(csv_file, model, api_key, base_url):
    """
    使用AI分析CSV文件（质量检查和单任务报告保存强制启用）

    优化流程：
    - 如果已存在综合报告和CSV文件，跳过信息收集和报告生成，直接生成社工攻击方案

    参数:
        csv_file: CSV文件路径
        model: AI模型名称
        api_key: API密钥
        base_url: API地址

    注意：
    - 本函数强制启用质量检查功能，确保AI分析结果的完整性和可靠性
    - 本函数强制保存每个任务的分析报告，便于调试和查看
    """
    if not api_key:
        print("警告: 未设置API密钥，跳过AI分析")
        return

    # 获取输出目录和基础文件名
    csv_dir = os.path.dirname(csv_file)
    if not csv_dir:
        csv_dir = "."
    csv_filename = os.path.basename(csv_file)
    base_filename = csv_filename.replace(".csv", "")
    report_file = os.path.join(csv_dir, f"{base_filename}_report.md")

    # 检查是否已有综合报告和CSV文件，跳过信息收集直接生成社工方案
    skip_analysis = os.path.exists(csv_file) and os.path.exists(report_file)

    if skip_analysis:
        print(f"检测到已有综合报告和CSV文件，跳过信息收集和报告生成...")
        print(f"直接生成社会工程学攻击方案...\n")
    else:
        # 读取CSV内容（供分析任务和社工方案生成使用）
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

        # 强制使用带质量检查的并行分析，并保存单个任务报告
        print(
            f"正在调用AI进行分析（7个任务并行，使用模型: {model}，质量检查已强制启用）..."
        )

        enhanced_results = analyzer.parallel_analyze_with_quality_check(
            tasks,
            max_workers=7,
            model=model,
            enable_quality_check=True,
            save_individual_reports=True,  # 强制保存单个任务报告
            output_dir=csv_dir,
            base_filename=base_filename,
        )

        # 从增强结果中提取内容用于报告生成
        results = {}
        quality_summary = []

        for task_name, result_data in enhanced_results.items():
            results[task_name] = result_data.get("content", "")

            # 收集质量检查信息
            quality_info = result_data.get("quality_info")
            if quality_info:
                rounds = result_data.get("supplement_rounds", 0)
                score = quality_info.get("score", 0)
                quality_summary.append(
                    {"task": task_name, "score": score, "rounds": rounds}
                )

        # 输出质量检查摘要
        if quality_summary:
            print("\n=== 质量检查摘要 ===")
            for item in quality_summary:
                print(
                    f"  [{item['task']}] 评分: {item['score']:.0f}, 补充轮数: {item['rounds']}"
                )
            print("====================\n")

        # 生成综合报告
        print("正在生成综合报告...")

        report_prompt = format_report_prompt(prompts_module, results)
        final_report = analyzer.call_ai(
            prompts_module.REPORT_SYSTEM_PROMPT, report_prompt, model=model
        )

        # 保存报告
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(final_report)

        print(f"综合报告已保存至: {report_file}\n")

    # ===== 以下是公共流程：生成社工攻击方案 =====
    # 创建AI分析器（如未创建）
    try:
        analyzer = AIAnalyzer(api_key=api_key, base_url=base_url)
    except ValueError as e:
        print(f"AI分析器初始化失败: {e}")
        return

    # 读取CSV内容和综合报告
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        csv_content = f.read()

    with open(report_file, "r", encoding="utf-8") as f:
        report_content = f.read()

    # 生成社会工程学攻击方案
    print("正在生成社会工程学攻击方案...")
    se_plan = generate_social_engineering_plan(
        analyzer=analyzer,
        report_content=report_content,
        csv_content=csv_content,
        prompts_module=prompts_module,
        model=model,
    )

    # 保存社会工程学攻击方案
    se_report_file = save_social_engineering_report(
        content=se_plan, output_dir=csv_dir, base_filename=base_filename
    )

    # 输出结果
    print("=== 分析完成 ===")
    if se_report_file:
        print(f"社工攻击方案已保存至: {se_report_file}")


# 程序入口
if __name__ == "__main__":
    main()
