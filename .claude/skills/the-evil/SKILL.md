---
name: the-evil
description: 微博数据爬取与AI智能分析工具，支持爬取微博用户数据并进行7项并行AI分析
---

# the-evil（至阴至邪）

微博数据爬取与AI智能分析工具，支持爬取微博用户数据（使用 weibo.cn 移动端API）、7个并行AI分析任务（使用GLM-4模型）、生成Markdown格式的详细分析报告。

## 环境要求

- Python 3.13+
- UV 包管理器

## 安装依赖

1. **检查当前目录**：先判断当前工作目录是否包含 `pyproject.toml` 文件
2. 如果不在项目目录中，使用 question 工具询问用户项目目录路径
3. 使用 `workdir` 参数指定项目路径后执行 `uv sync`

```bash
# 检查当前目录是否有 pyproject.toml
ls pyproject.toml
```

**如果不在项目目录**：使用 question 工具询问用户：

```
请提供 the-evil 项目的完整路径，例如：D:\code\python\the_evil
```

获取路径后执行：

```bash
# 使用用户提供的路径安装依赖
uv sync --workdir "用户提供的路径"
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

### 2. 获取UID

在微博用户主页的URL中可以找到UID，例如：
- `https://weibo.com/u/1223178222` → UID = 1223178222
- `https://weibo.com/1223178222` → UID = 1223178222

### 4. 运行程序

```bash
# 基本用法（所有参数必填）
uv run python main.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

# 示例：爬取胡歌的微博
uv run python main.py "你的Cookie" 1223178222 output.csv 0 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| cookie | 微博登录Cookie | 是 |
| uid | 微博用户ID | 是 |
| output_file | 输出CSV文件名 | 是 |
| max_weibos | 最大获取微博数（0表示全部） | 是 |
| model | AI模型名称 | 是 |
| api_key | API密钥 | 是 |
| base_url | API地址 | 是 |

## 模型选择

通过环境变量配置AI模型：

| 模型 | API地址 |
|------|---------|
| GLM-4 | `https://open.bigmodel.cn/api/coding/paas/v4` |
| GLM-4-Flash | `https://open.bigmodel.cn/api/coding/paas/v4` |
| GPT-4 | `https://api.openai.com/v1` |
| Claude-3 | `https://api.anthropic.com/v1` |

示例：

```bash
# 使用GLM-4-Flash（免费快速）
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"

# 或使用OpenAI GPT-4
$env:OPENAI_API_KEY="sk-xxx"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

## 输出文件

- **CSV文件** - 微博原始数据（如文件已存在则自动跳过爬取）
- **Markdown报告** - AI分析结果（自动生成在CSV同目录下）

## AI分析功能

程序会自动进行7项并行AI分析：
1. 统计分析 - 微博数量、互动数据、发布时间分布等
2. 性格分析 - 从社会工程学角度分析用户性格特征
3. 兴趣分析 - 从情报收集角度分析用户兴趣爱好
4. 轨迹分析 - 从OSINT角度分析用户活动轨迹和生活习惯
5. 社交分析 - 从社交网络角度分析用户社交圈子
6. 情感分析 - 从心理分析角度用户情感表达方式
7. 综合报告 - 生成完整的Markdown分析报告
