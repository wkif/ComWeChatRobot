from wechatbot_client.action_manager import (
    ActionManager,
    ActionRequest,
    ActionResponse,
    WsActionRequest,
    WsActionResponse,
    check_action_params,
)
from wechatbot_client.typing import overrides
from wechatbot_client.wechat.adapter import Adapter
from wechatbot_client.admin import Admin
from wechatbot_client.group.group import Group
from wechatbot_client.sign.sign import Sign
from wechatbot_client.consts import SUPERADMIN_USER_ID, REBOT_NAME
from wechatbot_client.speechStatistics.main import SpeechStatistics


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
    
    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.admin = Admin()
        self.group = Group()
        self.sign = Sign()
        self.speechstatistics = SpeechStatistics()
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

# 验证是否是管理
    async def AdminVerification(self, group_id, user_id):
        isAdmin = False
        adminList = await self.admin.read()
        for admin in adminList:
            if admin[2] == user_id:
                isAdmin = True
                break
        if not isAdmin:
            await self.sedGroupMsg(group_id, self.isNotAdminMsg)
        return isAdmin

# 主处理模块
    async def deal(self, msg):
        print(msg)
        # self.wechatManager.action_request(self.msg)
        print(msg["message"][0].type, msg["message"][0].data)
        mesageType = msg["message"][0].type
        print("mesageType："+mesageType)
        # if mesageType != "mention":
        #     return
        sender_user_id = msg['user_id']
        if mesageType == "mention":
            mention_userId = msg["message"][0].data['user_id']
            print("mention_userId:"+mention_userId)
            messageText = msg["message"][1].data['text']
        else:
            messageText = msg["message"][0].data['text']
        group_id = msg['group_id']
        print("sender_user_id："+sender_user_id)
        print("group_id："+group_id)
        print("messageText："+messageText)
        if messageText == "功能菜单":
            await self.menuList(group_id, sender_user_id)
        if messageText == "增加管理":
            if await self.AdminVerification(group_id, sender_user_id):
                if not mention_userId:
                    await self.sedGroupMsg(group_id, "艾特一下谁当管理啊")
                else:
                    await self.addAdmin(group_id, mention_userId)
        if messageText == "删除管理":
            if await self.AdminVerification(group_id, sender_user_id):
                if not mention_userId:
                    await self.sedGroupMsg(group_id, "艾特一下删除哪个管理呀")
                else:
                    await self.deleteAdmin(group_id, mention_userId)
        if messageText == "管理列表":
            message = "下面是管理员列表：\n"
            adminList = await self.admin.read()
            for admin in adminList:
                message = message + "用户名：" + admin[1] + "\n"
            await self.sedGroupMsg(group_id, message)
        if messageText == "查看退群成员":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.getQuitGroupList(group_id)
        if messageText == "签到":
            await self.signIn(group_id, sender_user_id)
        if messageText == "开通聊天数据统计":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.addOpenGroup(group_id)
        if messageText == "关闭聊天数据统计":
            if await self.AdminVerification(group_id, sender_user_id):
                await self.deleteOpenGroup(group_id)

    async def menuList(self, group_id, user_id):
        message = '''
        -------功能菜单-------\n
        ----群管理特权区----\n
        1. 口令：艾特我 查看退群成员；\n
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
# 签到

    async def signIn(self, group_id, user_id):
        res = await self.sign.signIn(user_id)
        print(res)
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

# 新增聊天记录群组
    async def addOpenGroup(self, group_id):
        currentStatus = await self.speechstatistics.changeOpenGroupList(group_id)
        if currentStatus:
            await self.sedGroupMsg(group_id, "已经开通过啦！")
            return
        status = await self.speechstatistics.addOpenGroupList(group_id)
        if status:
            await self.sedGroupMsg(group_id, "开通成功，将对群聊天记录进行加密统计，看看谁是屁话王，你放心！")
        else:
            await self.sedGroupMsg(group_id, "哦豁，开通失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)

# 关闭群组聊天记录
    async def deleteOpenGroup(self, group_id):
        currentStatus = await self.speechstatistics.changeOpenGroupList(group_id)
        if not currentStatus:
            await self.sedGroupMsg(group_id, "本来就没开通啊")
            return
        status = await self.speechstatistics.deleteOpenGroupList(group_id)
        if status:
            await self.sedGroupMsg(group_id, "关闭成功")
        else:
            await self.sedGroupMsg(group_id, "哦豁，关闭失败，老大来看看")
            await self.sedGroupMentionMsg(group_id, user_id=SUPERADMIN_USER_ID)
