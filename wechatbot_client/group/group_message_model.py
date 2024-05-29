from pathlib import Path
from tortoise import Tortoise, fields
from tortoise.models import Model

from wechatbot_client.consts import DATABASE_PATH
from wechatbot_client.log import logger


class GROUPMessage(Model):
    id = fields.IntField(pk=True, generated=True)
    sender_user_id = fields.CharField(max_length=255)
    sender_user_name = fields.CharField(max_length=255)
    group_id = fields.CharField(max_length=255)
    group_name = fields.CharField(max_length=255)
    message = fields.CharField(max_length=255)
    time = fields.CharField(max_length=255)

    class Meta:
        table = "groupMessage"
        table_description = "群组消息表"


async def group_message_init() -> None:
    """
    数据库初始化
    """
    logger.debug("<y>正在注册groupMessage数据库...</y>")
    Path(f"./{DATABASE_PATH}/group/").mkdir(exist_ok=True)
    database_path = f"./{DATABASE_PATH}/group/groupMessage.db"
    db_url = f"sqlite://{database_path}"
    # 这里填要加载的表
    models = [
        "wechatbot_client.group.group_message_model",
    ]
    modules = {"models": models}
    await Tortoise.init(db_url=db_url, modules=modules)
    await Tortoise.generate_schemas()
    logger.info("<g>groupMessage数据库初始化成功...</g>")


async def group_message_close() -> None:
    """
    关闭数据库
    """
    await Tortoise.close_connections()
