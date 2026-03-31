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
# 基本用法（所有参数必填）
python main.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

# 示例：爬取胡歌的微博
python main.py "你的Cookie" 1223178222 output.csv 0 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"
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

- **CSV文件** - 微博原始数据（如文件已存在则自动跳过爬取）
- **Markdown报告** - AI分析结果

### 测试文件示例

- CSV数据：[胡歌_the_evil.csv](胡歌_the_evil.csv)
- 分析报告：[胡歌_the_evil_report.md](胡歌_the_evil_report.md)

## 模块化设计

### 扩展新的爬虫

本项目采用模块化设计，支持扩展新的网站爬虫。以下是添加自定义爬虫的详细步骤。

#### 1. 数据模型

项目定义了统一的数据模型，用于不同平台的数据标准化：

```python
# 微博数据模型
class WeiboData:
    id: str           # 内容ID
    content: str      # 内容文本
    is_original: bool # 是否原创
    publish_time: str  # 发布时间
    publish_tool: str  # 发布工具
    up_num: int       # 点赞数
    retweet_num: int  # 转发数
    comment_num: int  # 评论数
    publish_place: str # 发布位置
    picture_url: str  # 图片URL
    video_url: str    # 视频URL

# 用户信息模型
class UserInfo:
    id: str           # 用户ID
    nickname: str     # 昵称
    weibo_num: int    # 内容数
    following: int    # 关注数
    followers: int    # 粉丝数
    gender: str       # 性别
    location: str     # 所在地
    birthday: str     # 生日
    description: str  # 简介
```

#### 2. 创建爬虫类

在 `modules/crawlers.py` 中创建新的爬虫类，继承 `BaseCrawler`：

```python
class DouyinCrawler(BaseCrawler):
    """抖音爬虫类"""

    def __init__(self, cookie):
        super().__init__(cookie)
        self.base_url = "https://www.douyin.com"

    def get_user_info(self, user_id):
        """
        获取用户信息

        参数:
            user_id: 用户ID

        返回:
            UserInfo对象
        """
        url = f"{self.base_url}/user/{user_id}"
        # 实现获取用户信息的逻辑
        selector = self._fetch_page(url)
        
        # 解析用户信息并返回UserInfo对象
        nickname = selector.xpath('//span[@class="nickname"]/text()')[0]
        # ... 其他字段解析
        
        return UserInfo(
            id=user_id,
            nickname=nickname,
            # ... 其他参数
        )

    def get_weibos(self, user_id, max_count=0):
        """
        获取用户内容列表

        参数:
            user_id: 用户ID
            max_count: 最大获取数量，0表示全部

        返回:
            WeiboData对象列表
        """
        weibos = []
        page = 1
        
        while True:
            url = f"{self.base_url}/aweme/v1/web/aweme/v1/web/aweme/post/?user_id={user_id}&cursor={page}"
            data = self._fetch_json(url)  # 假设添加了_fetch_json方法
            
            for item in data.get("aweme_list", []):
                weibo = self._parse_weibo(item)
                weibos.append(weibo)
                
                if max_count > 0 and len(weibos) >= max_count:
                    return weibos
            
            if not data.get("has_more"):
                break
            page += 1
        
        return weibos

    def _parse_weibo(self, item):
        """解析单条内容"""
        return WeiboData(
            id=item.get("aweme_id"),
            content=item.get("desc"),
            is_original=True,
            publish_time=item.get("create_time"),
            # ... 其他字段
        )
```

#### 3. 注册爬虫

在 `create_crawler` 函数中注册新的爬虫：

```python
def create_crawler(platform, cookie):
    """
    创建爬虫实例

    参数:
        platform: 平台名称，如"weibo"、"douyin"
        cookie: 登录cookie

    返回:
        对应的爬虫实例
    """
    crawlers = {
        "weibo": WeiboCrawler,
        "douyin": DouyinCrawler,  # 添加新爬虫
        "bilibili": BilibiliCrawler,  # 再添加一个
    }

    crawler_class = crawlers.get(platform.lower())
    if not crawler_class:
        raise ValueError(
            f"不支持的平台: {platform}，支持的平台: {list(crawlers.keys())}"
        )

    return crawler_class(cookie)
```

#### 4. 抽象方法说明

必须实现的抽象方法：

| 方法 | 说明 | 返回值 |
|------|------|--------|
| `get_user_info(user_id)` | 获取用户基本信息 | `UserInfo` 对象 |
| `get_weibos(user_id, max_count)` | 获取用户内容列表 | `List[WeiboData]` |

#### 5. 辅助方法

`BaseCrawler` 提供的辅助方法：

| 方法 | 说明 |
|------|------|
| `_build_headers()` | 构建请求头 |
| `save_to_csv(user_info, weibos, output_file)` | 保存数据到CSV |

#### 6. 完整示例：添加Twitter/X爬虫

```python
class TwitterCrawler(BaseCrawler):
    """Twitter爬虫类"""

    def __init__(self, cookie):
        super().__init__(cookie)
        self.base_url = "https://twitter.com"

    def get_user_info(self, user_id):
        url = f"{self.base_url}/{user_id}"
        selector = self._fetch_page(url)
        
        nickname = selector.xpath('//div[@data-testid="UserName"]//span/text()')[0]
        # ... 获取其他信息
        
        return UserInfo(id=user_id, nickname=nickname, ...)

    def get_weibos(self, user_id, max_count=0):
        weibos = []
        # 实现获取推文列表的逻辑
        return weibos
```

然后在 `create_crawler` 中注册即可使用：

```python
crawler = create_crawler("twitter", "your_cookie")
user_info = crawler.get_user_info("elonmusk")
tweets = crawler.get_weibos("elonmusk", max_count=100)
```

### 修改AI分析提示词

在 `modules/prompts.py` 中修改或添加新的提示词：

```python
NEW_ANALYSIS_SYSTEM_PROMPT = """你是一个xxx专家..."""

NEW_ANALYSIS_USER_PROMPT = """请分析xxx..."""
```

> 📚 学习参考：[B站 AI 分析提示词教程](https://www.bilibili.com/video/BV13T4y1e7TK/)

## 注意事项

1. **Cookie有效期**：Cookie会过期，如遇到登录错误请重新获取
2. **请求频率**：程序已设置合理的请求间隔，避免被封禁
3. **数据安全**：请妥善保管Cookie，不要泄露给他人
4. **合规使用**：请遵守微博服务条款，仅用于学习研究

## 版本历史

- v1.0.0 - 初始版本，支持微博数据爬取和7项AI分析

## 许可证

仅供学习研究使用

## Claude/OpenCode Skill 使用

本项目提供了 Claude/OpenCode 的 skill，可以更方便地使用本工具。

### 安装 Skill

将 `.claude/skills/the-evil` 目录复制到 Claude 的全局 skills 目录：

```bash
# 复制 skill 目录到全局位置
cp -r .claude/skills/the-evil C:/Users/j4543/.claude/skills/
```

### 使用 Skill

当在 Claude/OpenCode 中使用本项目时，AI 会自动加载 skill 并提供以下指导：
- 检查项目目录是否正确
- 使用 `uv sync` 安装依赖
- 使用 `uv run python main.py` 运行程序

### Skill 功能

- 自动检测当前目录是否包含 `pyproject.toml`
- 如果不在项目目录，询问用户项目路径
- 使用 `uv run` 执行 Python 脚本
- 提供完整的使用参数说明
