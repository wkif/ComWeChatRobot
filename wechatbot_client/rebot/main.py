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
from .utils import RebotUtils
from wechatbot_client.admin import Admin
from wechatbot_client.consts import SUPERADMIN_USER_ID, REBOT_NAME


class Rebot(Adapter):
    action_manager: ActionManager
    utils: RebotUtils
    admin: Admin
    """管理员模块"""

    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.utils = RebotUtils(self.action_manager)
        self.admin = Admin()
        self.isNotAdminMsg = "你不是管理员哦！"
        self.name = REBOT_NAME

    async def rebotMain(self, msg):
        sender_user_id, group_id, messageText, mention_userId, mesageType = (
            await self.utils.messageDeal(msg)
        ).values()
        if messageText == "功能菜单":
            await self.menuList(group_id, sender_user_id)

        if messageText == "增加管理" or messageText == "新增管理":
            await self.addAdmin(sender_user_id, group_id, mention_userId)
        if messageText == "删除管理":
            await self.delAdmin(sender_user_id, group_id, mention_userId)

        if "管理列表" in messageText:
            await self.adminList(group_id)

    # 功能菜单处理模块
    async def menuList(self, group_id, sender_user_id):
        message = (
            """
您好，我是小助手"""
            + self.name
            + """  

|-------功能菜单-------|

|----群管理特权区----|

1. 开通机器人；

2. 关闭机器人；

3. 开通记录；

4. 关闭记录；

5. @某某 增加管理；

6. @某某 删除管理；

7. 查看退群成员；

|----群成员功能区----|

1. 签到；

2. 日活；

3. 月活；

4. 总活；

5. 一言；

6. 去水印 + 抖音等分享链接；

7. 解梦 + 梦语；

8. 微博热搜；

9. 城市+天气；（eg:北京天气）

10. 吃什么；(eg:今天吃什么)

11. 推荐早餐+菜名；（eg:推荐早餐曼龄粥）

12. 推荐午餐+菜名；

13. 推荐晚餐+菜名；

14. 听歌+歌名；（eg:听歌稻香）

15. 新闻；（eg:新闻）

16. 星期四（eg:星期四）

17. 日报）
"""
        )
        img = await self.utils.text2img(message)
        res = await self.utils.upload_file(type="path", name="menu.jpg", path=img)
        file_id = ""
        if res.dict()["retcode"] == 0:
            file_id = res.dict()["data"]["file_id"]
        else:
            return
        await self.utils.sedGroupMentionMsg(group_id, sender_user_id)
        await self.utils.sedImageMsg(group_id, file_id)

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
