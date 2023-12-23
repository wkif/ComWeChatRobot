from datetime import datetime
import re
from wechatbot_client.action_manager import (
    ActionManager,
    ActionRequest,
    ActionResponse,
    check_action_params,
)
from wechatbot_client.file_manager import FileCache, FileManager
from wechatbot_client.typing import overrides
from wechatbot_client.wechat.adapter import Adapter
from wechatbot_client.utils import logger_wrapper
from wechatbot_client.admin import Admin
from wechatbot_client.group.group import Group
from wechatbot_client.sign.sign import Sign
from wechatbot_client.consts import SUPERADMIN_USER_ID, REBOT_NAME, REBOT_USER_ID
from wechatbot_client.speechStatistics.main import SpeechStatistics
from wechatbot_client.speechStatistics.message import MessageDb
from wechatbot_client.food.main import Food
from wechatbot_client.networkInterface.YiYan import getYiYanApi
from wechatbot_client.networkInterface.DouYin import getDouYinWaterMarkApi
from wechatbot_client.networkInterface.Meng import MengApi
from wechatbot_client.networkInterface.WeiBoHot import WeiBoHotApi
from wechatbot_client.networkInterface.Weather import WeatherApi
from wechatbot_client.networkInterface.Morning import MorningApi

log = logger_wrapper("WeChat Manager")


class Rebot(Adapter):
    action_manager: ActionManager
    admin: Admin
    """管理员模块"""
    group: Group
    """群聊模块"""
    sign: Sign
    """签到模块"""
    speechstatistics: SpeechStatistics
    """聊天统计"""
    messagedb: MessageDb
    file_manager: FileManager
    """文件管理器"""
    food: Food
    
    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.file_manager = FileManager()
        self.admin = Admin()
        self.group = Group()
        self.sign = Sign()
        self.speechstatistics = SpeechStatistics()
        self.messagedb = MessageDb()
        self.food = Food()
        self.isNotAdminMsg = "你不是管理员哦！"
        self.name = REBOT_NAME
        
    @overrides(Adapter)
    async def action_request(self, request: ActionRequest) -> ActionResponse:
        """
        发起action请求
        """
        # 验证action
        try:
            action_name, action_model = check_action_params(request)
        except TypeError:
            return ActionResponse(
                status="failed",
                retcode=10002,
                data=None,
                message=f"未实现的action: {request.action}",
            )
        except ValueError:
            return ActionResponse(
                status="failed",
                retcode=10003,
                data=None,
                message="Param参数错误",
            )
        # 调用api
        return await self.action_manager.request(action_name, action_model)

# 发送群消息
    async def sedGroupMsg(self, group_id, msg):
        print("发送")
        print(msg)
        return
        await self.action_request(
            ActionRequest(action="send_message", params={
                "detail_type": "group",
                "group_id": group_id,
                "message": [
                    {
                        "type": "text",
                        "data": {
                            "text": msg
                        }
                    }
                ]
            })
        )

# 在群里艾特某人
    async def sedGroupMentionMsg(self, group_id, user_id):
        await self.action_request(
            ActionRequest(action="send_message", params={
                "detail_type": "group",
                "group_id": group_id,
                "message": [
                    {
                        "type": "mention",
                        "data": {
                            "user_id": user_id
                        }
                    }
                ]
            })
        )

# 获取群信息
    async def getGroupInfo(self, group_id):
        return await self.action_request(
            ActionRequest(action="get_group_info", params={
                "group_id": group_id,
            })
        )

# 获取群成员信息
    async def getGroupMemberInfo(self, group_id, user_id):
        return await self.action_request(
            ActionRequest(action="get_group_member_info", params={
                "user_id": user_id,
                "group_id": group_id
            })
        )

    async def getSupportedActions(self):
        return await self.action_request(
            ActionRequest(action="get_supported_actions", params={
            })
        )

# 验证是否是管理
    async def AdminVerification(self, group_id, user_id):
        return await self.admin.checkIsAdmin(user_id, group_id)

# 主处理模块
    async def deal(self, msg):
        print(msg)
        mesageType = ""
        # if mesageType != "mention":
        #     return
        if "message" in msg:
            mesageType = msg["message"][0].type
            print("mesageType："+mesageType)
        sender_user_id = msg['user_id']
        mention_userId = None
        if msg['detail_type'] == "wx.get_group_redbag":
            messageText = "wx.get_group_redbag"
        elif mesageType == "mention":
            mention_userId = msg["message"][0].data['user_id']
            print("mention_userId:"+mention_userId)
            messageText = msg["message"][1].data['text']
        elif mesageType == "text" or mesageType == "reply":
            messageText = msg["message"][-1].data['text']
        elif mesageType == "wx.emoji":
            messageText = "wx.emoji"
        else:
            return
        group_id = msg['group_id']
        print("sender_user_id："+sender_user_id)
        print("group_id："+group_id)
        print("messageText："+messageText)
        # 聊天内容记录
        if await self.speechstatistics.checkRecordChat(group_id):
            print("记录！！！")
            await self.recordChat(group_id, sender_user_id, messageText, msg['time'])
        # if sender_user_id != SUPERADMIN_USER_ID and mesageType == "mention":
        #     # await self.sedGroupMsg(group_id, "老大还在测试，别急哈！")
        #     return
        # 特定命令区----------------start
        if messageText == "开通记录":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.startRecordChat(group_id)
            else:
                await self.sedGroupMsg(group_id, self.isNotAdminMsg)
        if messageText == "关闭记录":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.stopRecordChat(group_id)
            else:
                await self.sedGroupMsg(group_id, self.isNotAdminMsg)
        if messageText == "开通机器人":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.addOpenGroup(group_id)
            else:
                await self.sedGroupMsg(group_id, self.isNotAdminMsg)
        if messageText == "关闭机器人":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.deleteOpenGroup(group_id)
            else:
                await self.sedGroupMsg(group_id, self.isNotAdminMsg)

        if "功能菜单" in messageText or "功能列表" in messageText:
            await self.menuList(group_id, sender_user_id)
        # 特定命令区----------------end
        # 艾特成员功能区--------------start
        elif messageText == "增加管理" or messageText == "新增管理":
            if await self.AdminVerification(group_id, sender_user_id) or sender_user_id == SUPERADMIN_USER_ID:
                if sender_user_id == SUPERADMIN_USER_ID and not mention_userId:
                    await self.addAdmin(group_id, SUPERADMIN_USER_ID)
                else:
                    if not mention_userId:
                        await self.sedGroupMsg(group_id, "艾特一下谁当管理啊")
                    else:
                        await self.addAdmin(group_id, mention_userId)
        elif messageText == "删除管理":
            if await self.AdminVerification(group_id, sender_user_id) or sender_user_id == SUPERADMIN_USER_ID:
                if not mention_userId:
                    await self.sedGroupMsg(group_id, "艾特一下删除哪个管理呀")
                else:
                    await self.deleteAdmin(group_id, mention_userId)
        if "管理列表" in messageText:
            message = "下面是管理员列表：\n"
            adminList = await self.admin.read(group_id)
            for admin in adminList:
                message = message + "用户名：" + admin[3] + "\n"
            await self.sedGroupMsg(group_id, message)
        # 艾特成员功能区--------------end
        if not await self.speechstatistics.checkOpenGroupList(group_id):
            print(group_id+"没有开通功能,不处理")
            # if mesageType == "mention" and mention_userId  == REBOT_USER_ID:
            return
        # 以下功能需要开通机器人才执行-----
        # 以下功能需要叫机器人名字
        # if REBOT_NAME not in messageText:
        #     # 没有叫我，不做处理
        #     print("没有叫我，不做处理")
        #     return
        elif "查看退群成员" in messageText:
            if await self.AdminVerification(group_id, sender_user_id):
                await self.getQuitGroupList(group_id)
            else:
                await self.sedGroupMsg(group_id, self.isNotAdminMsg)
        elif "签到" in messageText:
            await self.signIn(group_id, sender_user_id)
        elif "日活" in messageText:
            await self.getMessageRanking_today(group_id)
        elif "月活" in messageText:
            await self.getMessageRanking_month(group_id)
        elif "总活" in messageText:
            await self.getMessageRanking_all(group_id)
        elif "一言" in messageText:
            await self.getYiYan(group_id)
        elif "去水印" in messageText:
            await self.getVideoWaterMark(group_id, messageText)
        elif "解梦" in messageText:
            await self.getMeng(group_id, messageText)
        elif "微博热搜" in messageText:
            await self.getWeiBoHot(group_id)
        elif "天气" in messageText:
            await self.getWeather(group_id, messageText)
        elif "吃什么" in messageText:
            await self.getRandomFood(group_id)
        elif "推荐早餐" in messageText:
            await self.addFood(sender_user_id, group_id, messageText, type=1)
        elif "推荐午餐" in messageText:
            await self.addFood(sender_user_id, group_id, messageText, type=2)
        elif "推荐晚餐" in messageText:
            await self.addFood(sender_user_id, group_id, messageText, type=3)
        elif "推荐零食" in messageText:
            await self.addFood(sender_user_id, group_id, messageText, type=4)
        elif "吃什么" in messageText:
            await self.getRandomFood(group_id)
        else:
            pass

# 菜单
    async def menuList(self, group_id, user_id):
        message = '''
|       你好，我是       |
|   ''' + REBOT_NAME + '''   |
|     可以帮你管理群聊    |
|-------功能菜单-------|
|----群管理特权区----|
|1. 开通机器人；          |
|2. 关闭机器人；          |
|3. 开通记录；            |
|4. 关闭通记录；          |
|5. @某某 增加管理；     |
|6. @某某 删除管理；     |
|7. 查看退群成员；       |
|----群成员功能区----|
|1. 签到；                 |
|2. 日活；                 |
|3. 月活；                 |
|4. 总活；                 |
|5. 一言；                 |
|6. 去水印 + 抖音等分享链接；|
|7. 解梦 + 梦语；        |
|8. 微博热搜；           |
|9. 城市+天气；（eg:北京天气）|
|10.吃什么；(eg:今天吃什么) |
|11.推荐早餐+菜名；（eg:推荐早餐曼龄粥）|
|12.推荐午餐+菜名；      |
|13.推荐晚餐+菜名；      |
        '''
        await self.sedGroupMentionMsg(group_id, user_id)
        await self.sedGroupMsg(group_id, message)

# 增加管理员
    async def addAdmin(self, group_id, user_id):
        ad = await self.admin.search(user_id,  group_id)
        if ad:
            await self.sedGroupMsg(group_id, "人家早就已经是管理员了")
        else:
            user_name = ""
            response = await self.action_request(ActionRequest(
                action="get_group_member_info",
                params={
                    "group_id": group_id,
                    "user_id": user_id
                }
            ))
            if response.dict()['retcode'] == 0:
                user_name = response.dict()['data']['user_name']
            else:
                await self.sedGroupMsg(group_id, "添加失败,你看看群成员列表有没有该成员嘞！")
                return
            status = await self.admin.addAdmin(name=user_name, user_id=user_id, group_id=group_id)
            if status:
                await self.sedGroupMsg(group_id, "添加成功，权力越大，责任越大！")
            else:
                await self.sedGroupMsg(group_id, "咦？添加失败，老大快来看看")
                await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 移除管理员
    async def deleteAdmin(self, group_id, user_id):
        ad = await self.admin.search(user_id,  group_id)
        if not ad:
            await self.sedGroupMsg(group_id, "ta本来就不是管理员")
        else:
            status = await self.admin.deleteAdmin(user_id=user_id, group_id=group_id)
            if status:
                await self.sedGroupMsg(group_id, "去除成功")
            else:
                await self.sedGroupMsg(group_id, "去除失败，请联系老大手动去除")
                await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 查看退群成员
    async def getQuitGroupList(self, group_id):
        current_number_list = []
        response = await self.action_request(ActionRequest(
            action="get_group_member_list",
            params={"group_id": group_id}
        ))
        if response.dict()['retcode'] == 0:
            current_number_list = response.dict()['data']
            await self.updateAllNumberList(group_id)
            quitList = await self.group.getQuitGroupList(
                group_id, current_number_list
            )
            if not len(quitList):
                await self.sedGroupMsg(group_id, "没有退群历史记录，你给大伙退一个试试哈哈哈")
                return
            massage = '以下是退群历史成员：\n'
            for i in quitList:
                massage = massage + i['user_name'] + '\n'
            await self.sedGroupMsg(group_id, massage)
            return

# 更新群历史成员
    async def updateAllNumberList(self, group_id):
        current_number_list = []
        response = await self.action_request(ActionRequest(
            action="get_group_member_list",
            params={"group_id": group_id}
        ))
        if response.dict()['retcode'] == 0:
            current_number_list = response.dict()['data']
            status = await self.group.updateAllNumberList(
                group_id, current_number_list
            )
            if status:
                log("SUCCESS", "更新群"+group_id+"历史成员成功")
            else:
                log("ERROR", "更新群"+group_id+"历史成员失败")

# 签到
    async def signIn(self, group_id, user_id):
        sender_user_name = ""
        userInfo = await self.getGroupMemberInfo(group_id, user_id)
        if userInfo and userInfo.dict()['retcode'] == 0:
            sender_user_name = userInfo.dict()['data']['user_name']
        res = await self.sign.signIn(user_id)
        if res['status'] == 0:
            # msg = "今天已经签到过了,明天再来吧；累计签到" + str(res['sign_count']) +\
            #     "天;"+"连续签到" + str(res['count']) + "天"
            msg = """
            {},今天已经签到过了,明天再来吧\n
            ╭┈┈🏡签到🏡┈┈╮
            🗒连续签到：{} \n
            🗓累计签到：{} \n
            ╰┈┈┈┈┈┈┈┈┈╯
            """.format(sender_user_name, str(res['count']), str(res['sign_count']))
        elif res['status'] == 1:
            # msg = "签到成功!累计签到" + str(res['sign_count']) +\
            #     "天;"+"连续签到" + str(res['count']) + "天"
            msg = """
            签到成功!\n
            ╭┈┈🏡签到🏡┈┈╮
            🗒连续签到：{} \n
            🗓累计签到：{} \n
            ╰┈┈┈┈┈┈┈┈┈╯
            """.format(str(res['count']), str(res['sign_count']))
        else:
            msg = "签到失败"
        await self.sedGroupMsg(group_id, msg)

# 开通机器人
    async def addOpenGroup(self, group_id):
        currentStatus = await self.speechstatistics.checkOpenGroupList(group_id)
        if currentStatus:
            await self.sedGroupMsg(group_id, "已经开通过啦！")
            return
        status = await self.speechstatistics.addOpenGroupList(group_id)
        if status:
            await self.sedGroupMsg(group_id, "开通成功")
        else:
            await self.sedGroupMsg(group_id, "哦豁，开通失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 关闭机器人
    async def deleteOpenGroup(self, group_id):
        currentStatus = await self.speechstatistics.checkOpenGroupList(group_id)
        if not currentStatus:
            await self.sedGroupMsg(group_id, "本来就没开通啊")
            return
        status = await self.speechstatistics.deleteOpenGroupList(group_id)
        if status:
            await self.sedGroupMsg(group_id, "关闭成功")
        else:
            await self.sedGroupMsg(group_id, "哦豁，关闭失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 开通记录
    async def startRecordChat(self, group_id):
        status = await self.speechstatistics.startRecordChat(group_id)
        if status == 1:
            await self.sedGroupMsg(group_id, "开通成功")
        elif status == 2:
            await self.sedGroupMsg(group_id, "已经开通了")
        else:
            await self.sedGroupMsg(group_id, "哦豁，开通失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 关闭记录
    async def stopRecordChat(self, group_id):
        status = await self.speechstatistics.stopRecordChat(group_id)
        if status == 1:
            await self.sedGroupMsg(group_id, "关闭成功")
        elif status == 2:
            await self.sedGroupMsg(group_id, "已经关闭了")
        else:
            await self.sedGroupMsg(group_id, "哦豁，关闭失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 聊天内容记录
    async def recordChat(self, group_id, sender_user_id, message, time):
        if await self.speechstatistics.checkRecordChat(group_id):
            detail_type = "group"
            group_name = ""
            groupInfo = await self.getGroupInfo(group_id)
            if groupInfo and groupInfo.dict()['retcode'] == 0:
                group_name = groupInfo.dict()['data']['group_name']
            sender_user_name = ""
            userInfo = await self.getGroupMemberInfo(group_id, sender_user_id)
            if userInfo and userInfo.dict()['retcode'] == 0:
                sender_user_name = userInfo.dict()['data']['user_name']
            await self.messagedb.listenMessage(sender_user_id,
                                               sender_user_name, message, time,
                                               detail_type, group_id,
                                               group_name)
        return True

# 日活跃度
    async def getMessageRanking_today(self, group_id):
        RankingMap = await self.messagedb.getMessageRanking_today(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()['retcode'] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()['data']['user_name']
            result.append(RankingMap[key])
        mess = ""
        # result取前10
        result = result[0:20]
        for a in result:
            mess = mess + "✨" + a['user_name'] + " ： 发言" + str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖日活跃度(top 20)🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╯
"""
        await self.sedGroupMsg(group_id, msg)

# 月活跃度
    async def getMessageRanking_month(self, group_id):
        RankingMap = await self.messagedb.getMessageRanking_month(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()['retcode'] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()['data']['user_name']
            result.append(RankingMap[key])
        mess = ""
        result = result[0:20]
        for a in result:
            mess = mess + "✨" + a['user_name'] + " ： 发言" + str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖月活跃度(top 20)🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╯
"""
        await self.sedGroupMsg(group_id, msg)

# 总活跃度
    async def getMessageRanking_all(self, group_id):
        RankingMap = await self.messagedb.getMessageRanking_all(group_id)
        result = []
        for key in RankingMap:
            if not RankingMap[key]["user_name"]:
                numberInfo = await self.getGroupMemberInfo(group_id, key)
                if numberInfo and numberInfo.dict()['retcode'] == 0:
                    RankingMap[key]["user_name"] = numberInfo.dict()['data']['user_name']
            result.append(RankingMap[key])
        mess = ""
        result = result[0:20]
        for a in result:
            mess = mess + "✨" + a['user_name'] + "   发言" +\
                str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖总活跃度(top 20)🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈╯
"""
        await self.sedGroupMsg(group_id, msg)

# 一言
    async def getYiYan(self, group_id):
        res = await getYiYanApi()
        await self.sedGroupMsg(group_id, res)

# 去水印
    async def getVideoWaterMark(self, group_id, messageText):
        # 从 messageText 提取https网址
        urls = re.findall(r'https?://\S+', messageText)
        if len(urls):
            douyinurl = urls[-1]
            res = await getDouYinWaterMarkApi(douyinurl)
            if 'data' in res:
                data = res['data']
                title = data['title']
                author = data['author']
                videoUrl = data['url']
                cover = data['cover']
                music = data['music']['url']
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
                mess = "💌  标题： " + title + "\n" + "😀   作者： " + \
                    author + "\n" + "🎦  视频链接： " + videoUrl + "\n" + \
                    "📷  封面链接： " + cover + "\n" + "📼 音频链接： " + music + "\n"
                await self.sedGroupMsg(group_id, mess)
            else:
                await self.sedGroupMsg(group_id, res)
            
        else:
            await self.sedGroupMsg(group_id, "没有找到抖音链接")

# 解梦
    async def getMeng(self, group_id, messageText):
        word = messageText.replace("解梦", "")
        res = await MengApi(word)
        if "data" in res:
            data = res['data']
            mess = ""
            for i in data:
                mess = mess + "💭梦到： " + i['title'] + "\n" +\
                    "------------\n" + "解梦： " + i['text'] +\
                    "\n------------\n"
            await self.sedGroupMsg(group_id, mess)
        else:
            await self.sedGroupMsg(group_id, res)

# 微博热搜
    async def getWeiBoHot(self, group_id):
        res = await WeiBoHotApi()
        if "data" in res:
            data = res['data']
            mess = "下面是热搜榜单\n-----------------------------\n"
            for i in data:
                mess = mess + "🎈   "+i['title'] +\
                    ":" + "热度： " + i['hot'] + "  ❤️‍🔥\n"
            mess = mess + "-----------------------------\n"
            await self.sedGroupMsg(group_id, mess)
        else:
            await self.sedGroupMsg(group_id, res)

# 天气
    async def getWeather(self, group_id, messageText):
        city = messageText.replace("天气", "")
        res = await WeatherApi(city)
        if "data" in res:
            data = res['data']
            if data['last_update']:
                dt = datetime.fromisoformat(data['last_update'])
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_time = ""
            mess = city + "🌕现在"+data['now']['text'] +\
                ",🌡温度"+data['now']['temperature'] +\
                ",⏱更新时间："+formatted_time
            await self.sedGroupMsg(group_id, mess)
        else:
            await self.sedGroupMsg(group_id, res)

# # 早晚招呼
#     async def MorningNight(self, group_id):
#         imgData = await MorningApi()
#         # 当前时间戳
#         time = datetime.now()
#         name = "imgData" + str(time)
#         dataId = await self.file_manager.cache_file_id_from_url(imgData,
#                                                           name, headers=None)
#         print(dataId)
#         pass
#  吃什么
    async def getRandomFood(self, group_id):
        current_time = datetime.now().time()
        morning_start = datetime.strptime('06:00:00', '%H:%M:%S').time()
        morning_end = datetime.strptime('10:00:00', '%H:%M:%S').time()
        noon_start = datetime.strptime('10:00:00', '%H:%M:%S').time()
        noon_end = datetime.strptime('15:00:00', '%H:%M:%S').time()
        type  = 4
        msg = ""
        if morning_start <= current_time < morning_end:
            type = 1
            msg = "现在是早餐时间，"
        elif noon_start <= current_time < noon_end:
            type = 2
            msg = "现在是午餐时间，"
        else:
            type = 3
            msg = "现在是晚餐时间，"
        food = await self.food.getRandomFood(type)
        msg += "🍇可以试试"+food[4]+"推荐的"+food[1]+"🥙"
        await self.sedGroupMsg(group_id, msg)

    #  新增美食
    async def addFood(self, sender_user_id, group_id, messageText, type):
        a = ""
        if type == 1:
            a = "推荐早餐"
        elif type == 2:
            a = "推荐午餐"
        elif type == 3:
            a = "推荐晚餐"
        else:
            a = "推荐零食"
        food = messageText.replace(a, "").replace(" ","")
        userInfo = await self.getGroupMemberInfo(group_id, sender_user_id)
        username = ""
        if userInfo and userInfo.dict()['retcode'] == 0:
            username = userInfo.dict()['data']['user_name']
        status = await self.food.addFood(sender_user_id, username, food, type)
        if status:
            await self.sedGroupMsg(group_id, "新增成功🎉")
        else:
            await self.sedGroupMsg(group_id, "已经有啦")
    # 删除 美食
    async def deleteFood(self, group_id, messageText):
        food = messageText.replace("删除美食", "").replace(" ","")
        status = await self.food.deleteFood(food)
        if status:
            await self.sedGroupMsg(group_id, "删除成功🎉")
        else:
            await self.sedGroupMsg(group_id, "好像没有这个菜？")