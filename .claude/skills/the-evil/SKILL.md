---
name: the-evil
description: 微博数据爬取与AI智能分析工具，支持爬取微博用户数据并进行7项并行AI分析
---

# the-evil（至阴至邪）

微博数据爬取与AI智能分析工具，支持爬取微博用户数据（使用 weibo.cn 移动端API）、7个并行AI分析任务（使用GLM-4模型）、生成Markdown格式的详细分析报告。

> ⚠️ **强制要求**：本 skill **必须使用编译后的二进制文件 `the-evil.exe`**，禁止直接运行 Python 源码。

## AI 使用前必须执行的检查

> ⚠️ **AI 必须首先执行此检查，才能进行任何操作**

在使用本工具之前，AI **必须** 先执行以下命令验证 `the-evil.exe` 是否在 PATH 环境变量中：

```powershell
# 必须首先执行此命令检查工具是否可用
Get-Command the-evil.exe -ErrorAction SilentlyContinue
```

**如果命令返回空（未找到），AI 必须执行以下步骤：**

### 步骤1：询问用户项目目录

**AI 必须先使用 question 工具询问用户项目目录位置：**

```
请提供 the-evil 项目的完整路径，例如：D:\code\python\the_evil
```

获取用户回复的项目路径后，继续执行下一步。

### 步骤2：检查项目目录中的二进制文件

使用用户提供的项目目录路径，检查是否已存在编译好的 `the-evil.exe`：

```powershell
# 检查用户提供的项目目录
ls <用户提供的路径>\the-evil.exe
```

如果存在，跳过步骤3，直接执行步骤4。

### 步骤3：编译二进制文件

如果文件不存在，需要编译：

```powershell
# 1. 进入用户提供的项目目录
cd <用户提供的路径>

# 2. 安装 PyInstaller（如果未安装）
uv pip install pyinstaller

# 3. 编译项目
uv run pyinstaller the_evil.spec --noconfirm --distpath .
```

编译完成后，会在用户提供的项目目录中生成 `the-evil.exe` 文件。

### 步骤4：添加到系统环境变量

将 `the-evil.exe` 所在目录添加到系统 PATH：

```powershell
# 使用用户提供的项目路径
$exePath = "<用户提供的路径>"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$exePath", "Machine")

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
```

### 步骤5：再次验证

```powershell
# 再次执行检查命令，确认工具可用
Get-Command the-evil.exe -ErrorAction SilentlyContinue
```

**只有当检查通过后，才能继续执行后续操作。**

---

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

### 3. 运行程序

> ⚠️ **必须使用 `the-evil.exe` 命令**，不能使用 `uv run python main.py`

```bash
# 基本用法（所有参数必填）
the-evil.exe <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

# 示例：爬取胡歌的微博
the-evil.exe "你的Cookie" 1223178222 output.csv 100 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"
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

## 模型选择

| 模型 | API地址 |
|------|---------|
| GLM-4 | `https://open.bigmodel.cn/api/coding/paas/v4` |
| GLM-4-Flash | `https://open.bigmodel.cn/api/coding/paas/v4` |
| GPT-4 | `https://api.openai.com/v1` |
| Claude-3 | `https://api.anthropic.com/v1` |

示例：

```bash
# 使用GLM-4-Flash（免费快速）
the-evil.exe "cookie" 1223178222 output.csv 100 glm-4-flash "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"

# 或使用OpenAI GPT-4
the-evil.exe "cookie" 1223178222 output.csv 100 gpt-4 "sk-xxx" "https://api.openai.com/v1"
```

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
- **社工攻击方案**（自动生成）：
  - `{文件名}_social_engineering.md` - 社会工程学攻击方案（基于综合报告和CSV数据生成，仅供安全研究）

### 流程优化（跳过已有分析）

如果文件夹中已有综合报告（`{文件名}_report.md`）和CSV文件，程序会**自动跳过**信息收集和报告生成流程，直接生成社工攻击方案，避免重复消耗API tokens。
