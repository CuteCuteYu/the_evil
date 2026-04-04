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
│       ├── prompts.py      # AI分析提示词（7种分析类型）
│       ├── quality_checker.py      # 质量检查模块（核心功能，强制启用）
│       ├── quality_check_prompts.py # 质量检查提示词（为每个分析任务定制）
│       └── config.py       # 统一配置模块（集中管理所有模型配置）
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

本项目仅支持兼容 OpenAI Python SDK 格式的 API（必须为 `https://xxx/v1` 格式）。只要 API 符合 OpenAI 格式，都可以正常使用，包括：

- 智谱 GLM 系列模型（如 glm-4, glm-4-flash）
- OpenAI GPT 系列模型（如 gpt-4, gpt-4o）
- Anthropic Claude 系列模型（如 claude-3）
- 其他兼容 OpenAI 格式的 API（如硅基流动、阿里的通义等）

#### 自定义模型示例

本项目通过设置 `base_url` 和 `api_key` 环境变量来使用不同的 AI 模型：

```bash
# 使用智谱 GLM-4-Flash（免费快速）
export OPENAI_API_KEY="your_zhipu_api_key"
export OPENAI_BASE_URL="https://open.bigmodel.cn/api/coding/paas/v4"

# 或使用 OpenAI GPT-4
export OPENAI_API_KEY="sk-xxx"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### 代码中修改默认模型

在 `modules/config.py` 中统一修改所有模型相关配置：

```python
# 修改默认模型
DEFAULT_MODEL = "glm-4.7"  # 改为你想使用的模型

# 修改温度参数
DEFAULT_TEMPERATURE = 0.7

# 修改默认API地址
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/coding/paas/v4"

# 修改并发数
MAX_WORKERS = 7
```

修改 `config.py` 后，所有使用这些配置的代码会自动使用新值，无需逐个修改。

### 4. 运行程序

```bash
# 基本用法（所有参数必填）
uv run python main.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

# 示例：爬取胡歌的微博
uv run python main.py "你的Cookie" 1223178222 output.csv 100 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"
```

### 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| cookie | 微博登录Cookie | 是 |
| uid | 微博用户ID | 是 |
| output_file | 输出CSV文件名 | 是 |
| max_weibos | 最大获取微博数（建议100，0表示全部） | 是 |
| model | AI模型名称 | 是 |
| api_key | API密钥 | 是 |
| base_url | API地址 | 是 |

## 获取UID

在微博用户主页的URL中可以找到UID，例如：
- `https://weibo.com/u/1223178222` → UID = 1223178222
- `https://weibo.com/1223178222` → UID = 1223178222

## AI分析功能

程序会自动进行7项并行AI分析，并包含**强制启用的质量检查**功能：

1. **统计分析** - 微博数量、互动数据、发布时间分布等
2. **性格分析** - 从社会工程学角度分析用户性格特征
3. **兴趣分析** - 从情报收集角度分析用户兴趣爱好
4. **轨迹分析** - 从OSINT角度分析用户活动轨迹和生活习惯
5. **社交分析** - 从社交网络角度分析用户社交圈子
6. **情感分析** - 从心理分析角度用户情感表达方式
7. **综合报告** - 生成完整的Markdown分析报告

### 质量检查功能（强制启用）

每个AI分析任务完成后，会自动进行质量检查：
- **长度检查** - 确保内容长度达标
- **完整性检查** - 确保包含所有必需的分析维度
- **分析依据检查** - 确保每个结论都有数据支撑
- **自动补充** - 如果检查不通过，自动请求AI补充缺失内容

### 单个任务报告（强制保存）

每个分析任务通过质量检查后，会自动保存独立的Markdown报告：
- 文件命名：`{基础文件名}_{任务名称}.md`
- 例如：`用户名_statistics.md`、`用户名_personality.md`
- 报告包含：质量评分、补充轮数、完整的分析结果

### 分析依据要求

每个分析结论都要求包含"**分析依据**"部分，说明：
- 数据来源（CSV的哪一列）
- 具体证据（引用具体微博内容）
- 分析逻辑

## 输出文件

- **CSV文件** - 微博原始数据（如文件已存在则自动跳过爬取）
- **综合Markdown报告** - 完整的AI分析结果（`{文件名}_report.md`）
- **单个任务报告**（自动生成）：
  - `{文件名}_statistics.md` - 统计分析报告
  - `{文件名}_personality.md` - 性格分析报告
  - `{文件名}_interest.md` - 兴趣分析报告
  - `{文件名}_trajectory.md` - 轨迹分析报告
  - `{文件名}_social.md` - 社交分析报告
  - `{文件名}_emotion.md` - 情感分析报告

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

- **v2.0.0** - 质量检查版本
  - 新增强制启用的质量检查功能
  - 新增单个任务报告自动保存
  - 新增统一配置模块（config.py）
  - 新增任务特定的质量检查提示词
  - 修改默认模型为 glm-4.7
  - 修复导入问题（支持绝对导入和相对导入自动回退）
- v1.0.0 - 初始版本，支持微博数据爬取和7项AI分析

## 许可证

仅供学习研究使用

## Claude/OpenCode Skill 使用（必须使用二进制版本）

> ⚠️ **强制要求**：本项目的 skill **必须使用编译后的二进制文件**，禁止直接运行 Python 源码。使用前请务必完成以下步骤。

### 第一步：下载或编译二进制文件

#### 方式A：直接使用已编译的二进制文件

下载项目 release 中的 `the-evil.exe` 文件。

#### 方式B：自行编译二进制文件

```bash
# 1. 安装 PyInstaller
uv pip install pyinstaller

# 2. 编译项目
uv run pyinstaller the_evil.spec --noconfirm --distpath .

# 3. 编译完成后，会在当前目录生成 the-evil.exe 文件
```

### 第二步：添加到系统环境变量

将 `the-evil.exe` 所在目录添加到系统 PATH 环境变量：

#### Windows PowerShell（管理员模式）

```powershell
# 假设 the-evil.exe 在 D:\code\python\the-evil 目录
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;D:\code\python\the-evil", "Machine")

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
```

#### Windows CMD

```cmd
# 假设 the-evil.exe 在 D:\code\python\the-evil 目录
setx PATH "%PATH%;D:\code\python\the-evil" /M
```

#### 验证安装

```bash
# 在任意目录打开命令行，输入以下命令验证
the-evil.exe

# 如果显示帮助信息，说明安装成功
```

### 第三步：安装 Skill

将 `.claude/skills/the-evil` 目录复制到 Claude 的全局 skills 目录：

```bash
# 复制 skill 目录到全局位置
cp -r .claude/skills/the-evil C:/Users/j4543/.claude/skills/
```

### 使用 Skill

当在 Claude/OpenCode 中使用本项目时，AI 会自动加载 skill 并提供以下指导：
- 检查项目目录是否正确
- **验证 the-evil.exe 是否在 PATH 中**（强制检查）
- 提示用户使用二进制文件运行程序

### Skill 功能

- 检测 the-evil.exe 是否存在于 PATH 中
- 如果不存在，提示用户按照上述步骤编译并添加到 PATH
- 使用 `the-evil.exe` 命令执行程序
