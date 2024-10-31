from datetime import datetime
import json
import re

import requests
from wechatbot_client.action_manager import (
    ActionManager,
    ActionRequest,
    ActionResponse,
    WsActionRequest,
    WsActionResponse,
    check_action_params,
)
from wechatbot_client.typing import overrides
from wechatbot_client.utils import logger_wrapper
from wechatbot_client.wechat.adapter import Adapter
from .utils import RebotUtils
from wechatbot_client.admin import Admin
from wechatbot_client.group import OpenGroup, GroupMessage
from wechatbot_client.consts import SUPERADMIN_USER_ID, REBOT_NAME, REBOT_USER_ID
from wechatbot_client.networkInterface.main import NetworkInterface

log = logger_wrapper("WeChat Manager")


class Rebot(Adapter):
    action_manager: ActionManager
    utils: RebotUtils
    admin: Admin
    openGroup: OpenGroup
    groupMessage: GroupMessage
    networkInterface: NetworkInterface

    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.utils = RebotUtils(self.action_manager)
        self.admin = Admin()
        self.openGroup = OpenGroup()
        self.groupMessage = GroupMessage()
        self.networkInterface = NetworkInterface()
        self.isNotAdminMsg = "你不是管理员哦！"
        self.name = REBOT_NAME

    async def rebotMain(self, msg):
        sender_user_id, group_id, messageText, mention_userId, mesageType = (
            await self.utils.messageDeal(msg)
        ).values()
        # 消息记录
        await self.listenMessage(group_id, sender_user_id, messageText)
        if messageText == "功能菜单":
            await self.menuList(group_id, sender_user_id)
        if messageText == "增加管理" or messageText == "新增管理":
            await self.addAdmin(sender_user_id, group_id, mention_userId)
        if messageText == "删除管理":
            await self.delAdmin(sender_user_id, group_id, mention_userId)
        if "管理列表" in messageText:
            await self.adminList(group_id)
        if messageText == "开通机器人":
            await self.enableRobot(group_id, sender_user_id)
        if messageText == "关闭机器人":
            await self.disableRobot(group_id, sender_user_id)
        if messageText == "清除缓存" or messageText == "清理缓存":
            await self.clearCache(sender_user_id, group_id)
        #     # 以下功能需要开通机器人才执行------------
        if not await self.openGroup.isOpen(group_id):
            if mention_userId == REBOT_USER_ID:
                await self.utils.sedGroupMsg(group_id, "机器人未开通")
                return
            else:
                return
        if "日活" in messageText:
            await self.getMessageRanking_today(group_id)
        if "月活" in messageText:
            await self.getMessageRanking_month(group_id)
        if "总活" in messageText:
            await self.getMessageRanking_all(group_id)
        if "去水印" in messageText:
            await self.getVideoWaterMark(group_id, messageText)
        if "微博热搜" in messageText:
            await self.getWeiBoHot(group_id)
        if "天气" in messageText:
            await self.getWeather(group_id, messageText)
        if "星期四" in messageText:
            await self.getKfc(group_id)
        if "日报" in messageText:
            await self.getMoyuApi(group_id)
        if "新闻" in messageText:
            await self.getNews(group_id)
        if "星座" in messageText:
            await self.getXingZuoYunShi(group_id)
        # if "test" in messageText:
        #     await self.utils.sendMusic(
        #         sender_user_id,
        #         "wxid_ijmga1yqj5ug22",
        #         "http://music.163.com/song/media/outer/url?id=1365898499.mp3",
        #     )

    # 功能菜单处理模块
#     |----群管理特权区----|

# 1. 开通机器人；

# 2. 关闭机器人；

# 3. 开通记录；

# 4. 关闭记录；

# 5. @某某 增加管理；

# 6. @某某 删除管理；

# 7. 查看退群成员；
    async def menuList(self, group_id, sender_user_id):
        message = (
            """
您好，我是小助手"""
            + self.name
            + """  

|-------功能菜单-------|


|----群成员功能区----|

1. 吃什么

2. 日活；

3. 月活；

4. 总活；

5. 一言；

6. 去水印 + 抖音等分享链接；

7. 解梦 + 梦语；

8. 微博热搜；

9. 城市+天气；（eg:北京天气）

10. 听歌+歌名；（eg:听歌稻香）

11. 新闻；（eg:新闻）

12. 星座运势；（eg:星座）

13. 星期四（eg:星期四）

14. 日报
"""
        )
        img = await self.utils.text2img(message, "menu.jpg")
        if not img:
            return
        await self.utils.sedGroupMentionMsg(group_id, sender_user_id)
        await self.utils.sedImageMsgByPath(group_id, img)

    # 新增管理处理模块
    async def addAdmin(self, sender_user_id, group_id, mention_userId):
        isAdmin = (
            await self.admin.isAdmin(sender_user_id, group_id)
            or sender_user_id == SUPERADMIN_USER_ID
        )
        if isAdmin:
            if mention_userId:
                # 艾特人员
                if await self.admin.isAdmin(mention_userId, group_id):
                    await self.utils.sedGroupMsg(group_id, "该用户已经是管理员")
                    return
                userInfo = await self.utils.getGroupMemberInfo(group_id, mention_userId)
                username = ""
                if userInfo and userInfo.dict()["retcode"] == 0:
                    username = userInfo.dict()["data"]["user_name"]
                else:
                    await self.utils.sedGroupMsg(
                        group_id, "添加失败,你看看群成员列表有没有该成员嘞！"
                    )
                    return
                status = await self.admin.addAdmin(mention_userId, group_id, username)
                if status:
                    await self.utils.sedGroupMsg(group_id, "添加成功")
                else:
                    await self.utils.sedGroupMsg(group_id, "咦？添加失败，老大快来看看")
                    await self.utils.sedGroupMentionMsg(
                        group_id, user_id=SUPERADMIN_USER_ID
                    )
            elif sender_user_id == SUPERADMIN_USER_ID:
                # 超级管理员
                if await self.admin.isAdmin(sender_user_id, group_id):
                    await self.utils.sedGroupMsg(group_id, "你已经是管理员")
                    return
                userInfo = await self.utils.getGroupMemberInfo(group_id, sender_user_id)
                username = ""
                if userInfo and userInfo.dict()["retcode"] == 0:
                    username = userInfo.dict()["data"]["user_name"]
                status = await self.admin.addAdmin(sender_user_id, group_id)
                if status:
                    await self.utils.sedGroupMsg(group_id, "添加成功")
                else:
                    await self.utils.sedGroupMsg(group_id, "咦？添加失败，老大快来看看")
                    await self.utils.sedGroupMentionMsg(
                        group_id, user_id=SUPERADMIN_USER_ID
                    )
            else:
                await self.utils.sedGroupMsg(group_id, "艾特一下谁当管理啊")
        else:
            await self.utils.sedGroupMsg(group_id, self.isNotAdminMsg)

    # 删除管理处理模块
    async def delAdmin(self, sender_user_id, group_id, mention_userId):
        isAdmin = (
            await self.admin.isAdmin(sender_user_id, group_id)
            or sender_user_id == SUPERADMIN_USER_ID
        )
        if isAdmin:
            if mention_userId:
                if not await self.admin.isAdmin(mention_userId, group_id):
                    await self.utils.sedGroupMsg(group_id, "该用户不是管理员")
                    return
                status = await self.admin.deleteAdmin(mention_userId, group_id)
                if status:
                    await self.utils.sedGroupMsg(group_id, "删除成功")
                else:
                    await self.utils.sedGroupMsg(group_id, "咦？删除失败，老大快来看看")
                    await self.utils.sedGroupMentionMsg(
                        group_id, user_id=SUPERADMIN_USER_ID
                    )
            else:
                await self.utils.sedGroupMsg(group_id, "艾特一下删谁管理啊")
        else:
            await self.utils.sedGroupMsg(group_id, self.isNotAdminMsg)

    # 管理列表处理模块
    async def adminList(self, group_id):
        adminList = await self.admin.searchByGroup(group_id)
        message = "下面是管理员列表：\n"
        for admin in adminList:
            _, group_id, userid, _ = admin
            userInfo = await self.utils.getGroupMemberInfo(group_id, userid)
            username = ""
            if userInfo and userInfo.dict()["retcode"] == 0:
                username = userInfo.dict()["data"]["user_name"]
            else:
                username = "未知"
            message = message + username + "\n"
        await self.utils.sedGroupMsg(group_id, message)

    # 开通机器人处理模块
    async def enableRobot(self, group_id, sender_user_id):
        isAdmin = (
            await self.admin.isAdmin(sender_user_id, group_id)
            or sender_user_id == SUPERADMIN_USER_ID
        )
        if isAdmin:
            isOpen = await self.openGroup.isOpen(group_id)
            if isOpen:
                await self.utils.sedGroupMsg(group_id, "机器人已经开通")
                return
            status = await self.openGroup.open(group_id)
            if status:
                await self.utils.sedGroupMsg(group_id, "开通成功")
            else:
                await self.utils.sedGroupMsg(group_id, "开通失败")
        else:
            await self.utils.sedGroupMsg(group_id, self.isNotAdminMsg)

    # 关闭机器人处理模块
    async def disableRobot(self, group_id, sender_user_id):
        isAdmin = (
            await self.admin.isAdmin(sender_user_id, group_id)
            or sender_user_id == SUPERADMIN_USER_ID
        )
        if isAdmin:
            isOpen = await self.openGroup.isOpen(group_id)
            if not isOpen:
                await self.utils.sedGroupMsg(group_id, "机器人未开通")
                return
            status = await self.openGroup.close(group_id)
            if status:
                await self.utils.sedGroupMsg(group_id, "关闭成功")
            else:
                await self.utils.sedGroupMsg(group_id, "关闭失败")
        else:
            await self.utils.sedGroupMsg(group_id, self.isNotAdminMsg)

    # 清除缓存
    async def clearCache(self, sender_user_id, group_id):
        if sender_user_id == SUPERADMIN_USER_ID:
            res = await self.utils.clean_cache()
            if res:
                await self.utils.sedGroupMsg(group_id, "已经清除全部缓存")
            else:
                await self.utils.sedGroupMsg(group_id, "清理失败，看看日志咋回事")
        else:
            await self.utils.sedGroupMsg(group_id, "让老大来清理吧！")

    async def listenMessage(self, group_id, sender_user_id, messageText):
        if await self.openGroup.isOpen(group_id):
            userInfo = await self.utils.getGroupMemberInfo(group_id, sender_user_id)
            username = ""
            if userInfo and userInfo.dict()["retcode"] == 0:
                username = userInfo.dict()["data"]["user_name"]
            else:
                username = "未知"
            group_name = ""
            groupInfo = await self.utils.getGroupInfo(group_id)
            if groupInfo and groupInfo.dict()["retcode"] == 0:
                group_name = groupInfo.dict()["data"]["group_name"]
            await self.groupMessage.listenMessage(
                sender_user_id=sender_user_id,
                sender_user_name=username,
                message=messageText,
                time=datetime.now().date(),
                group_id=group_id,
                group_name=group_name,
            )

    # 日活
    async def getMessageRanking_today(self, group_id):
        RankingMap = await self.groupMessage.getMessageRanking_today(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.utils.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()["retcode"] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()["data"][
                        "user_name"
                    ]
            result.append(RankingMap[key])
        mess = ""
        # result取前10
        result = result[0:20]
        for a in result:
            mess = (
                mess + "✨" + a["user_name"] + " ： 发言" + str(a["number"]) + "次✨\n"
            )
        msg = (
            """
╭┈┈🎖日活跃度(top 20)🎖┈┈╮
"""
            + mess
            + """
╰┈┈┈┈┈┈┈┈┈┈╯
"""
        )
        await self.utils.sedGroupMsg(group_id, msg)

    # 月活
    async def getMessageRanking_month(self, group_id):
        RankingMap = await self.groupMessage.getMessageRanking_month(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.utils.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()["retcode"] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()["data"][
                        "user_name"
                    ]
            result.append(RankingMap[key])
        mess = ""
        result = result[0:20]
        for a in result:
            mess = (
                mess + "✨" + a["user_name"] + " ： 发言" + str(a["number"]) + "次✨\n"
            )
        msg = (
            """
╭┈┈🎖月活跃度(top 20)🎖┈┈╮
"""
            + mess
            + """
╰┈┈┈┈┈┈┈┈┈┈╯
"""
        )
        await self.utils.sedGroupMsg(group_id, msg)

    # 总活
    async def getMessageRanking_all(self, group_id):
        RankingMap = await self.groupMessage.getMessageRanking_all(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.utils.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()["retcode"] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()["data"][
                        "user_name"
                    ]
            result.append(RankingMap[key])
        mess = ""
        result = result[0:20]
        for a in result:
            mess = (
                mess + "✨" + a["user_name"] + "   发言" + str(a["number"]) + "次✨\n"
            )
        msg = (
            """
╭┈┈🎖总活跃度(top 20)🎖┈┈╮
"""
            + mess
            + """
╰┈┈┈┈┈┈┈┈┈┈╯
"""
        )

        await self.utils.sedGroupMsg(group_id, msg)

    # 去水印
    async def getVideoWaterMark(self, group_id, messageText):
        # 从 messageText 提取https网址
        urls = re.findall(r"https?://\S+", messageText)
        if len(urls):
            douyinurl = urls[-1]
            print(douyinurl)
            res = await self.networkInterface.getDouYinWaterMarkApi(douyinurl)
            if "data" in res:
                data = res["data"]
                if "title" in data:
                    title = data["title"]
                if "author" in data:
                    author = data["author"]
                if "url" in data:
                    videoUrl = data["url"]
                if "cover" in data:
                    cover = data["cover"]
                if "music" in data:
                    if "url" in data["music"]:
                        music = data["music"]["url"]
                    else:
                        music = None
                else:
                    music = None
                # 为 none 时不显示
                if music is None:
                    music = ""
                if cover is None:
                    cover = ""
                if author is None:
                    author = ""
                if title is None:
                    title = ""
                if videoUrl is None:
                    videoUrl = ""
                mess = (
                    "💌  标题： "
                    + title
                    + "\n"
                    + "😀   作者： "
                    + author
                    + "\n"
                    + "🎦  视频链接： "
                    + videoUrl
                    + "\n"
                    + "📷  封面链接： "
                    + cover
                    + "\n"
                    + "📼 音频链接： "
                    + music
                    + "\n"
                )
                await self.utils.sedGroupMsg(group_id, mess)
                await self.utils.sedGroupMsg(
                    group_id, "复制链接太麻烦？正在发送视频，稍等..."
                )
                # 去除title里面所有符号，只保留汉字，用于上传
                response = requests.head(videoUrl, allow_redirects=True)
                long_url = response.url
                res = await self.utils.upload_file(
                    type="url",
                    name=re.sub(r"[^\u4e00-\u9fa5]", "", title) + ".mp4",
                    url=long_url,
                )
                file_id = ""
                if res.dict()["retcode"] == 0:
                    file_id = res.dict()["data"]["file_id"]
                    await self.utils.sedFileMsg(group_id, file_id)
                else:
                    await self.utils.sedGroupMsg(
                        group_id, "哦豁，好像没有拿到视频，自己复制打开试试？"
                    )
            else:
                await self.utils.sedGroupMsg(group_id, res)

        else:
            await self.utils.sedGroupMsg(group_id, "没有找到抖音链接")

    # 微博热搜
    async def getWeiBoHot(self, group_id):
        res = await self.networkInterface.WeiBoHotApi()
        if "data" in res:
            data = res["data"]
            mess = "下面是热搜榜单\n-----------------------------\n"
            for i in data:
                mess = (
                    mess + "🎈   " + i["title"] + ":" + "热度： " + i["hot"] + "  ❤️‍🔥\n"
                )
            mess = mess + "-----------------------------\n"
            img = await self.utils.text2img(mess, "weibo.jpg")
            await self.utils.sedImageMsgByPath(group_id, img)
        else:
            await self.utils.sedGroupMsg(group_id, res)

    # 天气
    async def getWeather(self, group_id, messageText):
        city = messageText.replace("天气", "")
        res = await self.networkInterface.WeatherApi(city)
        if "data" in res:
            data = res["data"]
            if data["last_update"]:
                dt = datetime.fromisoformat(data["last_update"])
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = ""
            mess = (
                city
                + "🌕现在"
                + data["now"]["text"]
                + ",🌡温度"
                + data["now"]["temperature"]
                + ",⏱更新时间："
                + formatted_time
            )
            await self.utils.sedGroupMsg(group_id, mess)
        else:
            await self.utils.sedGroupMsg(group_id, res)

    # KFC
    async def getKfc(self, group_id):
        data = await self.networkInterface.KfcApi()
        await self.utils.sedGroupMsg(group_id, data)

    # 摸鱼日报
    async def getMoyuApi(self, group_id):
        file_path = await self.networkInterface.MoyuApi()
        await self.utils.sedImageMsgByPath(group_id, file_path)

    # 新闻
    async def getNews(self, group_id):
        file_path = await self.networkInterface.NewsApi()
        await self.utils.sedImageMsgByPath(group_id, file_path)
    # 星座运势
    async def getXingZuoYunShi(self, group_id):
        file_path = await self.networkInterface.xingzuoyunshi()
        await self.utils.sedImageMsgByPath(group_id, file_path)
