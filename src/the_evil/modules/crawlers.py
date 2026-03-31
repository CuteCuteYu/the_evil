#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
爬虫基类模块

定义爬虫接口和数据结构，用于扩展新的网站爬取功能。

设计原则：
1. 统一的爬虫接口
2. 抽象的数据模型
3. 便于扩展新的网站

使用方式：
    from modules.crawlers import WeiboCrawler

    crawler = WeiboCrawler(cookie="your_cookie")
    weibos = crawler.crawl(uid="123456789", max_count=100)

作者: CuteCuteYu
版本: 1.0.0
"""

import os
import re
import csv
import requests
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from lxml import html


# =============================================================================
# 数据模型
# =============================================================================


class WeiboData:
    """
    微博数据模型

    属性:
        id: 微博ID
        content: 微博内容
        is_original: 是否原创
        publish_time: 发布时间
        publish_tool: 发布工具
        up_num: 点赞数
        retweet_num: 转发数
        comment_num: 评论数
        publish_place: 发布位置
        picture_url: 图片URL
        video_url: 视频URL
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "")
        self.content = kwargs.get("content", "")
        self.is_original = kwargs.get("is_original", True)
        self.publish_time = kwargs.get("publish_time", "")
        self.publish_tool = kwargs.get("publish_tool", "")
        self.up_num = kwargs.get("up_num", 0)
        self.retweet_num = kwargs.get("retweet_num", 0)
        self.comment_num = kwargs.get("comment_num", 0)
        self.publish_place = kwargs.get("publish_place", "")
        self.picture_url = kwargs.get("picture_url", "")
        self.video_url = kwargs.get("video_url", "")

    def to_dict(self):
        """转换为字典"""
        return {
            "微博ID": self.id,
            "内容": self.content,
            "是否原创": "原创" if self.is_original else "转发",
            "发布时间": self.publish_time,
            "发布工具": self.publish_tool,
            "点赞数": self.up_num,
            "转发数": self.retweet_num,
            "评论数": self.comment_num,
            "发布位置": self.publish_place,
            "图片URL": self.picture_url,
            "视频URL": self.video_url,
        }

    def to_csv_row(self):
        """转换为CSV行"""
        return [
            self.id,
            self.content,
            "原创" if self.is_original else "转发",
            self.publish_time,
            self.publish_tool,
            self.up_num,
            self.retweet_num,
            self.comment_num,
            self.publish_place,
            self.picture_url,
            self.video_url,
        ]


class UserInfo:
    """
    用户信息模型

    属性:
        id: 用户ID
        nickname: 昵称
        weibo_num: 微博数
        following: 关注数
        followers: 粉丝数
        gender: 性别
        location: 所在地
        birthday: 生日
        description: 简介
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "")
        self.nickname = kwargs.get("nickname", "")
        self.weibo_num = kwargs.get("weibo_num", 0)
        self.following = kwargs.get("following", 0)
        self.followers = kwargs.get("followers", 0)
        self.gender = kwargs.get("gender", "")
        self.location = kwargs.get("location", "")
        self.birthday = kwargs.get("birthday", "")
        self.description = kwargs.get("description", "")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "nickname": self.nickname,
            "weibo_num": self.weibo_num,
            "following": self.following,
            "followers": self.followers,
            "gender": self.gender,
            "location": self.location,
            "birthday": self.birthday,
            "description": self.description,
        }


# =============================================================================
# 爬虫基类
# =============================================================================


class BaseCrawler(ABC):
    """
    爬虫基类

    抽象方法:
        get_user_info: 获取用户信息
        get_weibo_count: 获取微博总数
        parse_weibo: 解析单条微博
        get_weibos: 获取微博列表
    """

    def __init__(self, cookie=None):
        """
        初始化爬虫

        参数:
            cookie: 网站登录cookie
        """
        self.cookie = cookie
        self.headers = self._build_headers()

    def _build_headers(self):
        """构建请求头"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": self.cookie or "",
        }

    def save_to_csv(self, user_info, weibos, output_file):
        """
        保存数据到CSV文件

        参数:
            user_info: 用户信息对象
            weibos: 微博列表
            output_file: 输出文件路径
        """
        if not weibos:
            print("没有微博数据可保存")
            return

        headers = [
            "微博ID",
            "内容",
            "是否原创",
            "发布时间",
            "发布工具",
            "点赞数",
            "转发数",
            "评论数",
            "发布位置",
            "图片URL",
            "视频URL",
        ]

        with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for weibo in weibos:
                writer.writerow(weibo.to_csv_row())

        print(f"已保存 {len(weibos)} 条微博到 {output_file}")

    @abstractmethod
    def get_user_info(self, user_id):
        """
        获取用户信息

        参数:
            user_id: 用户ID

        返回:
            UserInfo对象
        """
        pass

    @abstractmethod
    def get_weibos(self, user_id, max_count=0):
        """
        获取用户微博

        参数:
            user_id: 用户ID
            max_count: 最大获取数量，0表示全部

        返回:
            WeiboData对象列表
        """
        pass


# =============================================================================
# 微博爬虫实现
# =============================================================================


class WeiboCrawler(BaseCrawler):
    """
    微博爬虫类

    实现weibo.cn网站的微博数据爬取功能。
    使用方法:
        crawler = WeiboCrawler(cookie="your_cookie")
        user_info = crawler.get_user_info("123456789")
        weibos = crawler.get_weibos("123456789", max_count=100)
    """

    def __init__(self, cookie):
        """
        初始化微博爬虫

        参数:
            cookie: 微博登录cookie
        """
        super().__init__(cookie)
        self.base_url = "https://weibo.cn"

    def _fetch_page(self, url):
        """
        获取页面内容

        参数:
            url: 目标URL

        返回:
            lxml HTML解析后的页面对象
        """
        response = requests.get(url, headers=self.headers)
        response.encoding = "utf-8"
        return html.fromstring(response.text.encode("utf-8"))

    def get_user_info(self, user_id):
        """
        获取用户信息

        参数:
            user_id: 微博用户ID

        返回:
            UserInfo对象
        """
        url = f"{self.base_url}/{user_id}/info"
        selector = self._fetch_page(url)

        nickname = selector.xpath("//title/text()")
        if not nickname:
            raise ValueError("无法获取用户信息，请检查cookie是否有效")

        nickname = nickname[0]
        if "登录" in nickname:
            raise ValueError("Cookie错误或已过期")
        nickname = nickname[:-3]

        user = UserInfo(
            id=user_id,
            nickname=nickname,
        )

        # 解析基本信息
        basic_info = selector.xpath("//div[@class='c'][3]/text()")
        zh_to_en = {
            "性别": "gender",
            "地区": "location",
            "生日": "birthday",
            "简介": "description",
        }
        for info in basic_info:
            if ":" in info:
                key = info.split(":")[0]
                if key in zh_to_en:
                    setattr(
                        user, zh_to_en[key], info.split(":")[1].replace("\u3000", "")
                    )

        # 获取统计信息
        profile_selector = self._fetch_page(f"{self.base_url}/{user_id}/profile")
        stats = profile_selector.xpath("//div[@class='tip'][2]/text()")
        if stats:
            text = stats[0]
            weibo_match = re.search(r"微博\[(\d+)\]", text)
            following_match = re.search(r"关注\[(\d+)\]", text)
            followers_match = re.search(r"粉丝\[(\d+)\]", text)

            if weibo_match:
                user.weibo_num = int(weibo_match.group(1))
            if following_match:
                user.following = int(following_match.group(1))
            if followers_match:
                user.followers = int(followers_match.group(1))

        return user

    def _get_weibo_count(self, user_id):
        """
        获取微博总页数

        参数:
            user_id: 用户ID

        返回:
            总页数
        """
        url = f"{self.base_url}/{user_id}/profile"
        selector = self._fetch_page(url)

        try:
            mp = selector.xpath("//input[@name='mp']")
            if mp:
                return int(mp[0].attrib.get("value", 1))
        except:
            pass

        try:
            page_info = selector.xpath('//div[@class="pa"]/form/div/text()')
            for text in page_info:
                match = re.search(r"(\d+)/(\d+)页", text)
                if match:
                    return int(match.group(2))
        except:
            pass

        return 1

    def _parse_publish_time(self, info):
        """
        解析发布时间

        参数:
            info: 微博HTML元素

        返回:
            时间字符串
        """
        try:
            str_time = info.xpath("div/span[@class='ct']")
            if not str_time:
                return ""

            str_time_elem = str_time[0]
            str_time_text = str_time_elem.text or ""
            publish_time = str_time_text.split("来自")[0]

            if "刚刚" in publish_time:
                publish_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            elif "分钟" in publish_time:
                minute = int(publish_time[: publish_time.find("分钟")])
                publish_time = (datetime.now() - timedelta(minutes=minute)).strftime(
                    "%Y-%m-%d %H:%M"
                )
            elif "今天" in publish_time:
                today = datetime.now().strftime("%Y-%m-%d")
                time = publish_time[3:]
                publish_time = today + " " + time
            elif "月" in publish_time:
                year = datetime.now().strftime("%Y")
                month = publish_time[0:2]
                day = publish_time[3:5]
                time = publish_time[7:12]
                publish_time = f"{year}-{month}-{day} {time}"

            return publish_time[:16]
        except:
            return ""

    def _parse_weibo_footer(self, info):
        """
        解析微博互动数据（点赞、转发、评论）

        参数:
            info: 微博HTML元素

        返回:
            包含三项数据的字典
        """
        try:
            footer_text = info.xpath("div")[-1].text_content()
            footer_text = footer_text[footer_text.rfind("赞") :]

            nums = re.findall(r"\d+", footer_text)
            if len(nums) >= 3:
                return {
                    "up_num": int(nums[0]),
                    "retweet_num": int(nums[1]),
                    "comment_num": int(nums[2]),
                }
        except:
            pass
        return {"up_num": 0, "retweet_num": 0, "comment_num": 0}

    def _parse_one_weibo(self, info):
        """
        解析单条微博

        参数:
            info: 微博HTML元素

        返回:
            WeiboData对象或None
        """
        try:
            weibo_id = info.xpath("@id")
            if not weibo_id:
                return None
            weibo_id = weibo_id[0][2:]

            content = info.xpath("div/span[@class='ctt']")
            if not content:
                return None
            content_text = content[0].text_content()

            is_original = not info.xpath("div/span[@class='cmt']")

            if not is_original:
                content_text = content_text[content_text.find(":") + 1 :]

            content_text = (
                content_text[: content_text.rfind("赞")]
                if "赞" in content_text
                else content_text
            )

            publish_place = ""
            a_list = info.xpath("div//a/text()")
            for a in a_list:
                if "显示地图" in a:
                    publish_place_links = info.xpath("span[@class='ctt']/a/text()")
                    if publish_place_links:
                        publish_place = publish_place_links[-1]
                    break

            video_url = "无"
            video_link = info.xpath("./div[1]//a/@href")
            for link in video_link:
                if "video" in link:
                    video_url = link
                    break

            picture_url = "无"
            pics = info.xpath(".//img/@src")
            if pics:
                picture_url = pics[0]

            publish_time = self._parse_publish_time(info)
            publish_tool = ""
            ct = info.xpath("div/span[@class='ct']")
            if ct and "来自" in ct[0].text:
                publish_tool = ct[0].text.split("来自")[1]

            footer = self._parse_weibo_footer(info)

            return WeiboData(
                id=weibo_id,
                content=content_text,
                is_original=is_original,
                publish_place=publish_place,
                video_url=video_url,
                picture_url=picture_url,
                publish_time=publish_time,
                publish_tool=publish_tool,
                up_num=footer["up_num"],
                retweet_num=footer["retweet_num"],
                comment_num=footer["comment_num"],
            )
        except Exception as e:
            print(f"解析微博出错: {e}")
            return None

    def get_weibos(self, user_id, max_count=0):
        """
        获取用户微博

        参数:
            user_id: 微博用户ID
            max_count: 最大获取数量，0表示获取全部

        返回:
            WeiboData对象列表
        """
        weibos = []
        page_num = self._get_weibo_count(user_id)

        print(f"共 {page_num} 页微博...")

        for page in range(1, page_num + 1):
            url = f"{self.base_url}/{user_id}/profile?page={page}"
            try:
                selector = self._fetch_page(url)
                info_list = selector.xpath("//div[@class='c']")

                for info in info_list:
                    weibo = self._parse_one_weibo(info)
                    if weibo and weibo.content:
                        weibos.append(weibo)
                        if max_count > 0 and len(weibos) >= max_count:
                            print(f"已获取 {len(weibos)} 条微博 (达到上限)")
                            return weibos

                print(f"已获取第 {page} 页 ({len(weibos)} 条微博)")

            except Exception as e:
                print(f"获取第 {page} 页失败: {e}")

        return weibos


# =============================================================================
# 爬虫工厂
# =============================================================================


def create_crawler(platform, cookie):
    """
    创建爬虫实例

    参数:
        platform: 平台名称，如"weibo"
        cookie: 登录cookie

    返回:
        对应的爬虫实例

    示例:
        crawler = create_crawler("weibo", "your_cookie")
    """
    crawlers = {
        "weibo": WeiboCrawler,
    }

    crawler_class = crawlers.get(platform.lower())
    if not crawler_class:
        raise ValueError(
            f"不支持的平台: {platform}，支持的平台: {list(crawlers.keys())}"
        )

    return crawler_class(cookie)
