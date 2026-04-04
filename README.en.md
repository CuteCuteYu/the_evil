# the-evil

> ⚠️ **Warning**: This project's AI analysis feature consumes a lot of tokens. It is recommended to use the **codingplan mode** subscription to reduce costs.

Weibo Data Crawler and AI Intelligent Analysis Tool

Author: CuteCuteYu

## Project Introduction

**the-evil** is a modular Weibo data crawler and AI intelligent analysis tool, supporting:

- Crawling Weibo user data (using weibo.cn mobile API)
- 7 parallel AI analysis tasks (using GLM-4 model)
- Generating detailed analysis reports in Markdown format

## Directory Structure

```
the-evil/
├── src/the_evil/
│   ├── the_evil.py          # Main program entry
│   ├── __init__.py          # Package initialization
│   └── modules/
│       ├── __init__.py     # Module initialization
│       ├── crawlers.py     # Crawler module (extensible to other sites)
│       ├── ai_analyzer.py  # AI analyzer (parallel task execution)
│       └── prompts.py      # AI analysis prompts (7 analysis types)
├── main.py                  # Program entry
├── pyproject.toml          # Project configuration
└── README.md               # Documentation
```

## Environment Requirements

- Python 3.13+
- UV package manager

## Installation

```bash
# Install dependencies using UV
uv sync
```

## Usage

### 1. Get Cookie

After logging into Weibo, follow these steps to get the Cookie:

1. Open your browser and visit [weibo.cn](https://weibo.cn)
2. Log in to your Weibo account
3. Press **F12** to open developer tools
4. Switch to the **Network** tab
5. Refresh the page and find any request in the list
6. Click on the request and find **Request Headers** in the right panel
7. Find the content after `Cookie:` and copy the complete Cookie string

### 2. Run Program

```bash
# Basic usage (all parameters required)
uv run python main.py <cookie> <uid> <output_file> <max_weibos> <model> <api_key> <base_url>

# Example: crawl Hu Ge's Weibo
uv run python main.py "your_cookie" 1223178222 output.csv 100 glm-4 "your_api_key" "https://open.bigmodel.cn/api/coding/paas/v4"
```

### Parameter Description

| Parameter   | Description                                      | Required |
|-------------|--------------------------------------------------|----------|
| cookie      | Weibo login Cookie                               | Yes      |
| uid         | Weibo user ID                                    | Yes      |
| output_file | Output CSV filename                              | Yes      |
| max_weibos  | Maximum number of Weibos (recommended 100, 0 means all) | Yes |
| model       | AI model name                                    | Yes      |
| api_key     | API key                                          | Yes      |
| base_url    | API address                                      | Yes      |

## Get UID

The UID can be found in the URL of the Weibo user homepage:
- `https://weibo.com/u/1223178222` → UID = 1223178222
- `https://weibo.com/1223178222` → UID = 1223178222

## AI Analysis Features

The program automatically performs 8 parallel AI analysis tasks with **mandatory quality checking**:

1. **Statistical Analysis** - Weibo count, interaction data, publish time distribution, etc.
2. **Personality Analysis** - Analyze user personality traits from social engineering perspective
3. **Interest Analysis** - Analyze user interests from intelligence gathering perspective
4. **Trajectory Analysis** - Analyze user activity patterns and lifestyle from OSINT perspective
5. **Social Analysis** - Analyze user social circle from social network perspective
6. **Emotion Analysis** - Analyze user's emotional expression from psychological perspective
7. **Comprehensive Report** - Generate complete Markdown analysis report
8. **Social Engineering Plan** - Generate social engineering attack plan based on analysis results (for security research only)
9. **Detailed SE Plan (5 AI agents)** - Generate 5 detailed implementation plans based on the base SE plan

### Analysis Evidence Requirements

Each analysis conclusion must include an "**Analysis Evidence**" section, explaining:
- Data source (which column in the CSV)
- Specific evidence (quoting specific Weibo content)
- Analysis logic

## Output Files

- **CSV File** - Raw Weibo data (if file exists, crawling will be skipped automatically)
- **Comprehensive Markdown Report** - Complete AI analysis results (`{filename}_report.md`)
- **Individual Task Reports** (auto-generated):
  - `{filename}_statistics.md` - Statistical analysis report
  - `{filename}_personality.md` - Personality analysis report
  - `{filename}_interest.md` - Interest analysis report
  - `{filename}_trajectory.md` - Trajectory analysis report
  - `{filename}_social.md` - Social analysis report
  - `{filename}_emotion.md` - Emotion analysis report
- **Social Engineering Report** (auto-generated):
  - `{filename}_social_engineering.md` - Social engineering attack plan (generated based on comprehensive report and CSV data, for security research only)
- **Detailed SE Plan (5 AI agents, auto-generated)**:
  - `{filename}_detailed_identity_disguise.md` - Identity disguise plan
  - `{filename}_detailed_social_media_channel.md` - Social media channel management plan
  - `{filename}_detailed_script_preparation.md` - Script preparation plan
  - `{filename}_detailed_scenario_construction.md` - Scenario construction plan
  - `{filename}_detailed_emotion_guidance.md` - Emotion guidance plan

### Workflow Optimization (Skip Existing Analysis)

If the folder already contains detailed SE plan files, the program will **automatically skip** all analysis. If only comprehensive report exists, it will directly generate the social engineering plan and 5 detailed plans. If only CSV exists, it will execute all 8 AI analysis tasks.

### Test Files Example

- CSV data: [胡歌_the_evil.csv](胡歌_the_evil.csv)
- Analysis report: [胡歌_the_evil_report.md](胡歌_the_evil_report.md)

## Related Documentation

- [Project Structure Diagram](项目结构图.md) - Detailed architecture design, data flow diagrams, class structure
- [SKILL Usage Guide](.claude/skills/the-evil/SKILL.md) - Claude/OpenCode Skill configuration and usage

## Modular Design

### Extend New Crawlers

This project uses a modular design and supports extending crawlers for other websites. Here are the detailed steps to add a custom crawler.

#### 1. Data Model

The project defines a unified data model for standardizing data across different platforms:

```python
# Weibo data model
class WeiboData:
    id: str           # Content ID
    content: str      # Content text
    is_original: bool # Is original
    publish_time: str  # Publish time
    publish_tool: str  # Publish tool
    up_num: int       # Likes count
    retweet_num: int  # Reposts count
    comment_num: int  # Comments count
    publish_place: str # Publish location
    picture_url: str  # Picture URL
    video_url: str    # Video URL

# User info model
class UserInfo:
    id: str           # User ID
    nickname: str     # Nickname
    weibo_num: int    # Content count
    following: int    # Following count
    followers: int    # Followers count
    gender: str       # Gender
    location: str     # Location
    birthday: str     # Birthday
    description: str  # Bio
```

#### 2. Create Crawler Class

Create a new crawler class in `modules/crawlers.py`, inheriting from `BaseCrawler`:

```python
class DouyinCrawler(BaseCrawler):
    """Douyin crawler class"""

    def __init__(self, cookie):
        super().__init__(cookie)
        self.base_url = "https://www.douyin.com"

    def get_user_info(self, user_id):
        """
        Get user information

        Args:
            user_id: User ID

        Returns:
            UserInfo object
        """
        url = f"{self.base_url}/user/{user_id}"
        selector = self._fetch_page(url)
        
        nickname = selector.xpath('//span[@class="nickname"]/text()')[0]
        
        return UserInfo(
            id=user_id,
            nickname=nickname,
        )

    def get_weibos(self, user_id, max_count=0):
        """
        Get user content list

        Args:
            user_id: User ID
            max_count: Maximum number to fetch, 0 means all

        Returns:
            List of WeiboData objects
        """
        weibos = []
        page = 1
        
        while True:
            url = f"{self.base_url}/aweme/v1/web/aweme/v1/web/aweme/post/?user_id={user_id}&cursor={page}"
            data = self._fetch_json(url)
            
            for item in data.get("aweme_list", []):
                weibo = self._parse_weibo(item)
                weibos.append(weibo)
                
                if max_count > 0 and len(weibos) >= max_count:
                    return weibos
            
            if not data.get("has_more"):
                break
            page += 1
        
        return weibos
```

#### 3. Register Crawler

Register the new crawler in the `create_crawler` function:

```python
def create_crawler(platform, cookie):
    """
    Create crawler instance

    Args:
        platform: Platform name, e.g., "weibo", "douyin"
        cookie: Login cookie

    Returns:
        Corresponding crawler instance
    """
    crawlers = {
        "weibo": WeiboCrawler,
        "douyin": DouyinCrawler,
    }

    crawler_class = crawlers.get(platform.lower())
    if not crawler_class:
        raise ValueError(
            f"Unsupported platform: {platform}, supported platforms: {list(crawlers.keys())}"
        )

    return crawler_class(cookie)
```

#### 4. Abstract Methods

Required abstract methods:

| Method                          | Description                      | Return Value              |
|---------------------------------|-----------------------------------|---------------------------|
| `get_user_info(user_id)`        | Get user basic information       | `UserInfo` object        |
| `get_weibos(user_id, max_count)`| Get user content list            | `List[WeiboData]`        |

#### 5. Helper Methods

Helper methods provided by `BaseCrawler`:

| Method                                   | Description                    |
|------------------------------------------|--------------------------------|
| `_build_headers()`                       | Build request headers          |
| `save_to_csv(user_info, weibos, output_file)` | Save data to CSV      |

## Notes

1. **Cookie Validity**: Cookies expire. If you encounter login errors, please get a new cookie.
2. **Request Frequency**: The program has reasonable request intervals to avoid being blocked.
3. **Data Security**: Please keep your Cookie safe and do not share it with others.
4. **Compliance**: Please abide by Weibo's terms of service and use only for learning and research.

## Version History

- **v2.1.0** - Detailed SE Plan Version
  - Added 5 AI Agent detailed implementation plans (identity disguise, social media channel management, script preparation, scenario construction, emotion guidance)
  - Added intelligent skip logic to avoid repeated API token consumption
  - Optimized workflow to skip corresponding steps when partial files exist
- v2.0.0 - Quality check version, supports Weibo data crawling and 7 AI analyses
- v1.0.0 - Initial version

## License

For learning and research purposes only

## Claude/OpenCode Skill Usage

This project provides a Claude/OpenCode skill for more convenient use of this tool.

### Install Skill

Copy the `.claude/skills/the-evil` directory to Claude's global skills directory:

```bash
# Copy skill directory to global location
cp -r .claude/skills/the-evil C:/Users/j4543/.claude/skills/
```

### Using the Skill

When using this project in Claude/OpenCode, the AI will automatically load the skill and provide guidance:
- Check if the project directory is correct
- Use `uv sync` to install dependencies
- Use `uv run python main.py` to run the program

### Skill Features

- Automatically detect if current directory contains `pyproject.toml`
- If not in project directory, ask user for project path
- Use `uv run` to execute Python scripts
- Provide complete usage parameter instructions
