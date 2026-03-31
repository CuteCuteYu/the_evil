# the-evil（至阴至邪）

> ⚠️ **警告**：本项目AI分析功能会消耗大量Token，建议使用 **codingplan模式** 的订阅来使用本项目以降低成本。

微博数据爬取与AI智能分析工具

作者：CuteCuteYu

## 项目简介

**the-evil** 是一个模块化的微博数据爬取和AI智能分析工具，支持：

- 爬取微博用户数据（使用 weibo.cn 移动端API）
- 7个并行AI分析任务（使用GLM-4模型）
- 生成Markdown格式的详细分析报告

## 目录结构

```
the-evil/
├── src/the_evil/
│   ├── the_evil.py          # 主程序入口
│   ├── __init__.py          # 包初始化
│   └── modules/
│       ├── __init__.py     # 模块初始化
│       ├── crawlers.py     # 爬虫模块（可扩展到其他网站）
│       ├── ai_analyzer.py  # AI分析器（并行任务执行）
│       └── prompts.py      # AI分析提示词（7种分析类型）
├── main.py                  # 程序入口
├── pyproject.toml          # 项目配置
└── README.md               # 说明文档
```

## 环境要求

- Python 3.13+
- UV 包管理器

## 安装

```bash
# 使用UV安装依赖
uv sync
```

## 使用方法

### 1. 获取Cookie

登录微博后，按以下步骤获取Cookie：

1. 打开浏览器，访问 [weibo.cn](https://weibo.cn)
2. 登录你的微博账号
3. 按 **F12** 打开开发者工具
4. 切换到 **Network（网络）** 标签
5. 刷新页面，在请求列表中找到任意一个请求
6. 点击该请求，在右侧详情中找到 **Request Headers**
7. 找到 `Cookie:` 后面的内容，复制完整Cookie字符串

### 2. 设置环境变量

```bash
# 设置OpenAI API密钥
export OPENAI_API_KEY="your_api_key"

# 设置API地址（可选）
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
```

### 3. 模型选择设置

程序支持多种AI模型，可以通过环境变量配置：

#### 默认模型（智谱GLM-4）

```bash
export OPENAI_API_KEY="your_zhipu_api_key"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"
```

#### 支持的模型

| 模型 | API地址 | 说明 |
|------|---------|------|
| GLM-4 | `https://open.bigmodel.cn/api/coding/paas/v4` | 默认模型 |
| GLM-4-Flash | `https://open.bigmodel.cn/api/coding/paas/v4` | 免费版，速度快 |
| GPT-4 | `https://api.openai.com/v1` | OpenAI官方 |
| Claude-3 | `https://api.anthropic.com/v1` | Anthropic官方 |

#### 自定义模型示例

```bash
# 使用GLM-4-Flash（免费快速）
export OPENAI_API_KEY="your_api_key"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"

# 或使用OpenAI GPT-4
export OPENAI_API_KEY="sk-xxx"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### 代码中修改默认模型

在 `modules/ai_analyzer.py` 中修改默认模型：

```python
# 修改 call_ai 方法的 model 参数
def call_ai(self, system_prompt, user_prompt, model="glm-4-flash", temperature=0.7):
    # 将 model="glm-4" 改为 "glm-4-flash" 或其他模型
    pass
```

### 4. 运行程序

```bash
# 基本用法
python main.py <cookie> <uid> [output_file] [max_weibos]

# 示例：爬取胡歌的微博
python main.py "你的Cookie" 1223178222

# 指定输出文件名
python main.py "你的Cookie" 1223178222 output.csv

# 指定最大微博数
python main.py "你的Cookie" 1223178222 output.csv 100
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| cookie | 微博登录Cookie | 是 |
| uid | 微博用户ID | 是 |
| output_file | 输出CSV文件名 | 否 |
| max_weibos | 最大获取微博数（0表示全部） | 否 |

## 获取UID

在微博用户主页的URL中可以找到UID，例如：
- `https://weibo.com/u/1223178222` → UID = 1223178222
- `https://weibo.com/1223178222` → UID = 1223178222

## AI分析功能

程序会自动进行7项并行AI分析：

1. **统计分析** - 微博数量、互动数据、发布时间分布等
2. **性格分析** - 从社会工程学角度分析用户性格特征
3. **兴趣分析** - 从情报收集角度分析用户兴趣爱好
4. **轨迹分析** - 从OSINT角度分析用户活动轨迹和生活习惯
5. **社交分析** - 从社交网络角度分析用户社交圈子
6. **情感分析** - 从心理分析角度用户情感表达方式
7. **综合报告** - 生成完整的Markdown分析报告

### 分析依据要求

每个分析结论都要求包含"**分析依据**"部分，说明：
- 数据来源（CSV的哪一列）
- 具体证据（引用具体微博内容）
- 分析逻辑

## 输出文件

- **CSV文件** - 微博原始数据
- **Markdown报告** - AI分析结果

### 测试文件示例

- CSV数据：[胡歌_the_evil.csv](胡歌_the_evil.csv)
- 分析报告：[胡歌_the_evil_report.md](胡歌_the_evil_report.md)

## 模块化设计

### 扩展新的爬虫

在 `modules/crawlers.py` 中添加新的爬虫类：

```python
class NewPlatformCrawler(BaseCrawler):
    def get_user_info(self, user_id):
        # 实现获取用户信息
        pass
    
    def get_weibos(self, user_id, max_count=0):
        # 实现获取微博列表
        pass
```

然后在 `create_crawler` 函数中注册：

```python
def create_crawler(platform, cookie):
    crawlers = {
        "weibo": WeiboCrawler,
        "new_platform": NewPlatformCrawler,
    }
    return crawlers[platform.lower()](cookie)
```

### 修改AI分析提示词

在 `modules/prompts.py` 中修改或添加新的提示词：

```python
NEW_ANALYSIS_SYSTEM_PROMPT = """你是一个xxx专家..."""

NEW_ANALYSIS_USER_PROMPT = """请分析xxx..."""
```

## 注意事项

1. **Cookie有效期**：Cookie会过期，如遇到登录错误请重新获取
2. **请求频率**：程序已设置合理的请求间隔，避免被封禁
3. **数据安全**：请妥善保管Cookie，不要泄露给他人
4. **合规使用**：请遵守微博服务条款，仅用于学习研究

## 版本历史

- v1.0.0 - 初始版本，支持微博数据爬取和7项AI分析

## 许可证

仅供学习研究使用
