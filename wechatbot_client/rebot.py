from wechatbot_client.action_manager import (
    ActionManager,
    ActionRequest,
    ActionResponse,
    check_action_params,
)
from wechatbot_client.typing import overrides
from wechatbot_client.wechat.adapter import Adapter
from wechatbot_client.utils import logger_wrapper
from wechatbot_client.admin import Admin
from wechatbot_client.group.group import Group
from wechatbot_client.sign.sign import Sign
from wechatbot_client.consts import SUPERADMIN_USER_ID, REBOT_NAME
from wechatbot_client.speechStatistics.main import SpeechStatistics
from wechatbot_client.speechStatistics.message import MessageDb


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
    
    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.admin = Admin()
        self.group = Group()
        self.sign = Sign()
        self.speechstatistics = SpeechStatistics()
        self.messagedb = MessageDb()
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
        # await self.action_request(
        #     ActionRequest(action="send_message", params={
        #         "detail_type": "group",
        #         "group_id": group_id,
        #         "message": [
        #             {
        #                 "type": "text",
        #                 "data": {
        #                     "text": msg
        #                 }
        #             }
        #         ]
        #     })
        # )

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
            ActionRequest(action="get_user_info", params={
                "user_id": user_id
            })
        )
        
    async def getSupportedActions(self):
        return await self.action_request(
            ActionRequest(action="get_supported_actions", params={
            })
        )

# 验证是否是管理
    async def AdminVerification(self, group_id, user_id):
        isAdmin = False
        adminList = await self.admin.read()
        for admin in adminList:
            if admin[2] == user_id:
                isAdmin = True
                break
        if not isAdmin:
            # await self.sedGroupMsg(group_id, self.isNotAdminMsg)
            pass
        return isAdmin

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
            await self.recordChat(group_id, sender_user_id, messageText,
                              msg['time'])
        # if sender_user_id != SUPERADMIN_USER_ID and mesageType == "mention":
        #     # await self.sedGroupMsg(group_id, "老大还在测试，别急哈！")
        #     return
        if messageText == "开通记录":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.startRecordChat(group_id)
        if messageText == "关闭记录":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.stopRecordChat(group_id)
        if not await self.speechstatistics.checkOpenGroupList(group_id):
            if mesageType == "mention":
                print("有人艾特，但群没有开通功能")
            return
        if messageText == "功能菜单" or messageText == "功能列表":
            await self.menuList(group_id, sender_user_id)
        elif messageText == "增加管理" or messageText == "新增管理":
            if await self.AdminVerification(group_id, sender_user_id):
                if not mention_userId:
                    await self.sedGroupMsg(group_id, "艾特一下谁当管理啊")
                else:
                    await self.addAdmin(group_id, mention_userId)
        elif messageText == "删除管理":
            if await self.AdminVerification(group_id, sender_user_id):
                if not mention_userId:
                    await self.sedGroupMsg(group_id, "艾特一下删除哪个管理呀")
                else:
                    await self.deleteAdmin(group_id, mention_userId)
        elif messageText == "管理列表":
            message = "下面是管理员列表：\n"
            adminList = await self.admin.read()
            for admin in adminList:
                message = message + "用户名：" + admin[1] + "\n"
            await self.sedGroupMsg(group_id, message)
        elif messageText == "查看退群成员":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.getQuitGroupList(group_id)
        elif messageText == "签到":
            await self.signIn(group_id, sender_user_id)
        elif messageText == "开通机器人":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.addOpenGroup(group_id)
        elif messageText == "关闭机器人":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.deleteOpenGroup(group_id)
        elif messageText == "日活跃度":
            await self.getMessageRanking_today(group_id)
        elif messageText == "月活跃度":
            await self.getMessageRanking_month(group_id)
        elif messageText == "总活跃度":
            await self.getMessageRanking_all(group_id)
        else:
            pass

# 菜单
    async def menuList(self, group_id, user_id):
        message = '''
        -------功能菜单-------\n
        ----群管理特权区----\n
        1. 口令：查看退群成员；\n
        2. 口令：艾特新管理员 增加管理；\n
        3. 口令：艾特管理员 删除管理；\n
        ----群成员功能区----\n
        1. 口令：艾特我 管理列表；\n
        '''
        await self.sedGroupMentionMsg(group_id, user_id)
        await self.sedGroupMsg(group_id, message)

# 增加管理员
    async def addAdmin(self, group_id, user_id):
        ad = await self.admin.search(user_id)
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
            status = await self.admin.addAdmin(name=user_name, user_id=user_id)
            if status:
                await self.sedGroupMsg(group_id, "添加成功，权力越大，责任越大！")
            else:
                await self.sedGroupMsg(group_id, "咦？添加失败，老大快来看看")
                await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 移除管理员
    async def deleteAdmin(self, group_id, user_id):
        ad = await self.admin.search(user_id)
        if not ad:
            await self.sedGroupMsg(group_id, "ta本来就不是管理员")
        else:
            status = await self.admin.deleteAdmin(user_id=user_id)
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
        res = await self.sign.signIn(user_id)
        if res['status'] == 0:
            # msg = "今天已经签到过了,明天再来吧；累计签到" + str(res['sign_count']) +\
            #     "天;"+"连续签到" + str(res['count']) + "天"
            msg = """
            今天已经签到过了,明天再来吧\n
            ╭┈┈🏡签到🏡┈┈╮
            🗒连续签到：{} \n
            🗓累计签到：{} \n
            ╰┈┈┈┈┈┈┈┈┈╯
            """.format(str(res['count']), str(res['sign_count']))
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
        for a in result:
            mess = mess + "✨" + a['user_name'] + " ： " + str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖日活跃度🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈╯
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
        for a in result:
            mess = mess + "✨" + a['user_name'] + " ： " + str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖月活跃度🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈╯
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
        for a in result:
            mess = mess + "✨" + a['user_name'] + "   " + str(a['number']) + "次✨\n"
        msg = """
╭┈┈🎖总活跃度🎖┈┈╮
""" + mess + """
╰┈┈┈┈┈┈┈┈┈╯
"""
        await self.sedGroupMsg(group_id, msg)