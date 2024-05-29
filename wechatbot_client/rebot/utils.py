import os
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
from PIL import Image, ImageDraw, ImageFont


class RebotUtils(Adapter):

    def __init__(self, action_manager):
        self.action_manager = action_manager
        self.isNotAdminMsg = "你不是管理员哦！"

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
            ActionRequest(
                action="send_message",
                params={
                    "detail_type": "group",
                    "group_id": group_id,
                    "message": [{"type": "text", "data": {"text": msg}}],
                },
            )
        )

    # 获取群成员信息
    async def getGroupMemberInfo(self, group_id, user_id):
        return await self.action_request(
            ActionRequest(
                action="get_group_member_info",
                params={"user_id": user_id, "group_id": group_id},
            )
        )

    # 上传文件
    async def upload_file(self, type, name, url=None, path=None, data=None):
        params = {}
        if type == "url":
            params = {"type": "url", "name": name, "url": url}
        if type == "path":
            params = {"type": "path", "name": name, "path": path}
        if type == "data":
            params = {"type": "data", "name": name, "data": data}
        return await self.action_request(
            ActionRequest(action="upload_file", params=params)
        )

    # 发送图片
    async def sedImageMsg(self, group_id, file_id):
        return await self.action_request(
            ActionRequest(
                action="send_message",
                params={
                    "detail_type": "group",
                    "group_id": group_id,
                    "message": [{"type": "image", "data": {"file_id": file_id}}],
                },
            )
        )

    # 在群里艾特某人
    async def sedGroupMentionMsg(self, group_id, user_id):
        await self.action_request(
            ActionRequest(
                action="send_message",
                params={
                    "detail_type": "group",
                    "group_id": group_id,
                    "message": [{"type": "mention", "data": {"user_id": user_id}}],
                },
            )
        )

    # # 验证是否是管理
    # async def AdminVerification(self, group_id, user_id):
    #     isAdmin = False
    #     adminList = await self.admin.read()
    #     for admin in adminList:
    #         if admin[2] == user_id:
    #             isAdmin = True
    #             break
    #     if not isAdmin:
    #         await self.sedGroupMsg(group_id, self.isNotAdminMsg)
    #     return isAdmin

    # 消息分解
    async def messageDeal(self, message):
        print("原始信息：")
        print(message)
        mesageType = message["message"][0].type
        sender_user_id = message["user_id"]
        mention_userId = ""
        if mesageType == "mention":
            # at类型
            mention_userId = message["message"][0].data["user_id"]
            messageText = message["message"][1].data["text"]
        else:
            messageText = message["message"][0].data["text"]
        group_id = message["group_id"]
        return {
            "sender_user_id": sender_user_id,
            "group_id": group_id,
            "messageText": messageText,
            "mention_userId": mention_userId,
            "mesageType": mesageType,
        }

    # 文字转图片
    async def text2img(self, text):
        fontSize = 30
        width = 30
        lines = text.count("\n") + 1
        # 创建一个空白图片
        image = Image.new(
            "RGB", ((fontSize * width), (lines) * (fontSize + 5)), (255, 255, 255)
        )
        draw = ImageDraw.Draw(image)
        # 设置字体和字号
        # 字体样式
        fontPath = os.path.join("C:\\Windows\\Fonts\\", "simkai.ttf")
        font = ImageFont.truetype(fontPath, fontSize)
        draw.text((10, 10), text, fill="black", font=font)
        # 保存图片到file_cache/image目录
        imagePath = os.path.join(os.getcwd(), "file_cache/image")
        if not os.path.exists(imagePath):
            os.makedirs(imagePath)
        image.save(f"{imagePath}/menu.jpg")
        path = os.path.join(os.getcwd(), "file_cache/image/menu.jpg")
        return path
